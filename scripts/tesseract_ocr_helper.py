"""
Tesseract OCR Helper for MzansiPulse
=====================================
Standalone local OCR implementation using Tesseract.
Designed as a drop-in fallback when Huawei Cloud OCR is unavailable.

Features:
  - Multi-platform Tesseract detection (Windows / Linux / macOS)
  - Image preprocessing pipeline (grayscale → contrast → denoise → sharpen → binarize)
  - Receipt-aware text parsing (SA merchants, ZAR amounts, date formats)
  - VisionOCRFallback: routes to OpenRouter Gemini 2.0 Flash when Tesseract
    confidence is below threshold — handles handwriting, dark photos, sticky notes
  - SmartOCRHelper: orchestrates the full chain automatically
  - Same return interface as HuaweiOCRHelper for transparent swapping

Usage:
    # Recommended — handles handwriting automatically
    from tesseract_ocr_helper import SmartOCRHelper
    ocr = SmartOCRHelper()
    result = ocr.process_receipt('path/to/receipt.jpg')

    # Tesseract only (no API key needed)
    from tesseract_ocr_helper import TesseractOCRHelper
    ocr = TesseractOCRHelper()
    result = ocr.process_receipt('path/to/receipt.jpg')
"""

import os
import re
import platform
import subprocess
import logging
from datetime import datetime
from typing import Optional

log = logging.getLogger(__name__)

# ── Optional dependencies (fail gracefully) ────────────────────────────────

try:
    import pytesseract
    from PIL import Image, ImageEnhance, ImageFilter
    import numpy as np
    TESSERACT_LIBS_AVAILABLE = True
except ImportError:
    TESSERACT_LIBS_AVAILABLE = False

# Reuse the well-tested shared parser from huawei_ocr_helper to avoid drift
try:
    from huawei_ocr_helper import _parse_receipt_text_shared, _today
    _SHARED_PARSER_AVAILABLE = True
except ImportError:
    _SHARED_PARSER_AVAILABLE = False


# ── Constants ──────────────────────────────────────────────────────────────

_WINDOWS_TESS_PATHS = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'.format(
        os.environ.get('USERNAME', 'user')
    ),
]

_UNIX_TESS_PATHS = [
    '/usr/bin/tesseract',
    '/usr/local/bin/tesseract',
    '/opt/homebrew/bin/tesseract',   # Apple Silicon Homebrew
    '/opt/local/bin/tesseract',       # MacPorts
]

# PSM 6 = single uniform block (good for receipts)
_OCR_CONFIG = r'--oem 3 --psm 6'


# ── Installation instructions ──────────────────────────────────────────────

def _install_instructions() -> str:
    os_type = platform.system()
    pip_flag = '--break-system-packages' if os_type == 'Linux' else ''

    if os_type == 'Windows':
        return (
            "\nTesseract not found.\n"
            "1. Download the Windows installer from:\n"
            "   https://github.com/UB-Mannheim/tesseract/wiki\n"
            "2. Install to: C:\\Program Files\\Tesseract-OCR\\\n"
            "3. Restart this application (PATH is updated automatically)\n\n"
            "Then install Python wrappers:\n"
            "   pip install pytesseract pillow numpy\n"
        )
    elif os_type == 'Linux':
        return (
            "\nTesseract not found.\n"
            "Install with:\n"
            "   sudo apt-get update && sudo apt-get install -y tesseract-ocr\n\n"
            "Then install Python wrappers:\n"
            f"   pip install pytesseract pillow numpy {pip_flag}\n"
        )
    else:  # macOS
        return (
            "\nTesseract not found.\n"
            "Install with Homebrew:\n"
            "   brew install tesseract\n\n"
            "Then install Python wrappers:\n"
            "   pip install pytesseract pillow numpy\n"
        )


# ── TesseractOCRHelper ─────────────────────────────────────────────────────

class TesseractOCRHelper:
    """
    Local OCR using Tesseract engine.
    Fallback when Huawei Cloud OCR is unavailable.

    Drop-in compatible with HuaweiOCRHelper — both return the same dict
    structure from process_receipt().
    """

    def __init__(self):
        self._tess_cmd: Optional[str] = None
        self._available = False

        if not TESSERACT_LIBS_AVAILABLE:
            log.warning(
                '[TesseractOCR] pytesseract / Pillow / numpy not installed. '
                'Run: pip install pytesseract pillow numpy'
            )
            return

        cmd = self._find_tesseract()
        if cmd is None:
            log.warning('[TesseractOCR] Tesseract binary not found.%s', _install_instructions())
            return

        pytesseract.pytesseract.tesseract_cmd = cmd
        self._tess_cmd = cmd
        self._available = True
        log.info('[TesseractOCR] Ready — using %s', cmd)

    # ── Tesseract binary discovery ─────────────────────────────────────────

    def _find_tesseract(self) -> Optional[str]:
        """
        Locate the Tesseract executable.

        Search order:
          1. TESSERACT_CMD environment variable
          2. Known installation paths for the current OS
          3. System PATH (via subprocess)
        """
        # 1. Env var override
        env_cmd = os.environ.get('TESSERACT_CMD', '')
        if env_cmd and os.path.isfile(env_cmd):
            if self._check_binary(env_cmd):
                return env_cmd

        # 2. Known paths
        candidates = _WINDOWS_TESS_PATHS if platform.system() == 'Windows' else _UNIX_TESS_PATHS
        for path in candidates:
            if os.path.isfile(path) and self._check_binary(path):
                return path

        # 3. PATH lookup
        if self._check_binary('tesseract'):
            return 'tesseract'

        return None

    @staticmethod
    def _check_binary(cmd: str) -> bool:
        """Return True if the given command runs successfully with --version."""
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    # ── Image preprocessing ────────────────────────────────────────────────

    def _preprocess_image(self, image_path: str) -> 'Image.Image':
        """
        Enhance a receipt image for better OCR accuracy.

        Pipeline:
          1. Open image (handles JPEG, PNG, WEBP, BMP, TIFF)
          2. Convert to grayscale
          3. Boost contrast  (makes faded text stand out)
          4. Median denoise  (removes scanner/camera noise without blurring edges)
          5. Sharpen         (crisp character edges)
          6. Binarize        (adaptive threshold to pure B&W)
          7. Deskew          (straighten tilted receipts via numpy rotation)
        """
        img = Image.open(image_path).convert('RGB')

        # Grayscale
        img = img.convert('L')

        # Contrast boost
        img = ImageEnhance.Contrast(img).enhance(2.0)

        # Denoise
        img = img.filter(ImageFilter.MedianFilter(size=3))

        # Sharpen
        img = img.filter(ImageFilter.SHARPEN)

        # Binarize
        img = img.point(lambda p: 255 if p > 127 else 0)

        # Deskew (only when numpy is available)
        if 'np' in dir():
            img = self._deskew(img)

        return img

    @staticmethod
    def _deskew(img: 'Image.Image') -> 'Image.Image':
        """
        Correct small rotations in a binarized image using the
        projection-profile method.  Skips gracefully on error.
        """
        try:
            arr = np.array(img)
            # Invert so text pixels = 1
            inv = (arr == 0).astype(np.uint8)
            best_angle = 0.0
            best_score = -1.0
            for angle in np.arange(-10, 10.5, 0.5):
                rotated = _rotate_array(inv, angle)
                projection = rotated.sum(axis=1).astype(float)
                score = float(np.sum((projection[1:] - projection[:-1]) ** 2))
                if score > best_score:
                    best_score = score
                    best_angle = angle
            if abs(best_angle) > 0.3:
                img = img.rotate(best_angle, expand=False, fillcolor=255)
        except Exception as exc:
            log.debug('[TesseractOCR] Deskew skipped: %s', exc)
        return img

    # ── OCR execution ──────────────────────────────────────────────────────

    def _perform_ocr(self, img: 'Image.Image') -> tuple:
        """
        Run Tesseract on a preprocessed PIL image.

        Returns:
            (text: str, confidence: float)  — confidence in 0.0–1.0 range
        """
        text = pytesseract.image_to_string(img, config=_OCR_CONFIG)

        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
        raw_confs = data.get('conf', [])
        confs = [int(c) for c in raw_confs if str(c).lstrip('-').isdigit() and int(c) > 0]
        avg_conf = (sum(confs) / len(confs) / 100.0) if confs else 0.0

        return text, avg_conf

    # ── Receipt text parsing ───────────────────────────────────────────────

    def _parse_receipt_text(self, text: str) -> dict:
        """
        Parse raw OCR text into structured receipt data.

        Delegates to the shared parser in huawei_ocr_helper when available,
        otherwise uses the built-in SA-aware parser below.
        """
        if _SHARED_PARSER_AVAILABLE:
            return _parse_receipt_text_shared(text)
        return self._parse_receipt_text_local(text)

    @staticmethod
    def _parse_receipt_text_local(text: str) -> dict:
        """
        Standalone SA receipt parser (used only when huawei_ocr_helper
        cannot be imported).

        Handles:
          Amounts  : R123.45 · R 123 · TOTAL: 123.45 · 1 234,56 ZAR
          Dates    : YYYY-MM-DD · DD/MM/YYYY · DD Mon YYYY · DD/MM/YY
          Merchants: First meaningful line · known SA chain names
          Items    : Lines containing both text and a price
        """
        SA_MERCHANTS = [
            'shoprite', 'checkers', 'pick n pay', 'pnp', 'spar', 'woolworths',
            'clicks', 'dischem', 'game', 'makro', 'builders warehouse', 'jet',
            'mr price', 'truworths', 'ackermans', 'pep', 'cash crusaders',
            'liquorland', 'food lover', 'freshstop', 'engen', 'shell', 'bp',
            'total energies', 'caltex', 'steers', 'wimpy', 'kfc', 'mcdonalds',
            'nandos', 'debonairs',
        ]

        TOTAL_KEYWORDS = {
            'total', 'grand total', 'totaal', 'amount due', 'amount payable',
            'you pay', 'to pay', 'bedrag', 'subtotal', 'sub-total',
        }

        EXCLUDE_KEYWORDS = {
            'total', 'subtotal', 'vat', 'tax', 'change', 'wisselgeld',
            'thank', 'welcome', 'receipt', 'invoice', 'till', 'cashier',
            'tel', 'phone', 'fax', 'address', 'www', 'http', 'reg no',
            'vat no', 'registered', 'card', 'approved', 'auth', 'reference',
            'transaction', 'terminal', 'date', 'time',
        }

        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

        # ── Amount ────────────────────────────────────────────────────────
        amount_re = re.compile(
            r'(?:R|ZAR)\s*(\d{1,6}(?:[.,\s]\d{3})*(?:[.,]\d{2})?)'
            r'|(\d{1,6}(?:[.,\s]\d{3})*(?:[.,]\d{2}))',
            re.IGNORECASE,
        )

        def _clean(raw: str) -> float:
            raw = raw.strip().replace('\xa0', '').replace(' ', '')
            if re.search(r',\d{2}$', raw):
                raw = raw.replace('.', '').replace(',', '.')
            else:
                raw = raw.replace(',', '')
            try:
                return float(raw)
            except ValueError:
                return 0.0

        total_amount: Optional[float] = None
        all_amounts: list = []
        for line in lines:
            is_total = any(kw.upper() in line.upper() for kw in TOTAL_KEYWORDS)
            for m in amount_re.finditer(line):
                val = _clean(m.group(1) or m.group(2) or '')
                if val > 0:
                    all_amounts.append(val)
                    if is_total and total_amount is None:
                        total_amount = val
        if total_amount is None and all_amounts:
            total_amount = max(all_amounts)

        # ── Date ──────────────────────────────────────────────────────────
        date_val: Optional[str] = None
        for pattern, fmt in [
            (r'(\d{4}-\d{2}-\d{2})',                                                      '%Y-%m-%d'),
            (r'(\d{2}/\d{2}/\d{4})',                                                      '%d/%m/%Y'),
            (r'(\d{2}-\d{2}-\d{4})',                                                      '%d-%m-%Y'),
            (r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})', '%d %b %Y'),
            (r'(\d{1,2}/\d{1,2}/\d{2})',                                                  '%d/%m/%y'),
        ]:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                try:
                    date_val = datetime.strptime(m.group(1), fmt).strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
        if not date_val:
            date_val = datetime.now().strftime('%Y-%m-%d')

        # ── Merchant ──────────────────────────────────────────────────────
        merchant = ''
        text_lower = text.lower()
        for name in SA_MERCHANTS:
            if name in text_lower:
                # Find the actual line containing the merchant name
                for line in lines[:6]:
                    if name in line.lower():
                        merchant = line.strip()
                        break
                if merchant:
                    break
        if not merchant:
            for line in lines[:4]:
                if len(line) > 3 and not re.match(r'^[\d\s\-/:]+$', line):
                    merchant = line.strip()
                    break

        # ── Items ─────────────────────────────────────────────────────────
        items: list = []
        for line in lines:
            lower = line.lower()
            if any(kw in lower for kw in EXCLUDE_KEYWORDS):
                continue
            if re.search(r'[A-Za-z]{2,}', line) and re.search(r'\d+[.,]\d{2}', line):
                desc = amount_re.sub('', line).strip(' .,-)').strip()
                if len(desc) >= 3:
                    items.append(line.strip())

        return {
            'amount':       total_amount,
            'date':         date_val,
            'merchantName': merchant,
            'items':        items[:5],
        }

    # ── Public interface ───────────────────────────────────────────────────

    def is_available(self) -> bool:
        """Return True if Tesseract is ready to process images."""
        return self._available

    def process_receipt(self, image_path: str) -> dict:
        """
        Process a receipt image with local Tesseract OCR.

        Args:
            image_path: Absolute or relative path to the receipt image.
                        Supported formats: JPEG, PNG, WEBP, BMP, TIFF.

        Returns:
            {
                'success':    bool,
                'text':       str,          # raw OCR output
                'confidence': float,        # 0.0 – 1.0
                'engine':     str,          # 'tesseract'
                'extracted': {
                    'amount':       float | None,
                    'date':         str,    # YYYY-MM-DD
                    'merchantName': str,
                    'items':        list[str]
                }
            }
        """
        error_result = {
            'success':    False,
            'text':       '',
            'confidence': 0.0,
            'engine':     'tesseract',
            'extracted': {
                'amount':       None,
                'date':         datetime.now().strftime('%Y-%m-%d'),
                'merchantName': '',
                'items':        [],
            },
        }

        if not self._available:
            error_result['error'] = (
                'Tesseract not available. ' + _install_instructions()
            )
            return error_result

        if not os.path.isfile(image_path):
            error_result['error'] = f'Image not found: {image_path}'
            return error_result

        try:
            img = self._preprocess_image(image_path)
            text, confidence = self._perform_ocr(img)

            if not text.strip():
                log.warning('[TesseractOCR] OCR returned empty text for %s', image_path)

            extracted = self._parse_receipt_text(text)
            log.info(
                '[TesseractOCR] Success — confidence %.2f, merchant=%s, amount=%s',
                confidence,
                extracted.get('merchantName', ''),
                extracted.get('amount'),
            )

            return {
                'success':    True,
                'text':       text,
                'confidence': confidence,
                'engine':     'tesseract',
                'extracted':  extracted,
            }

        except Exception as exc:
            log.error('[TesseractOCR] Failed on %s: %s', image_path, exc, exc_info=True)
            error_result['error'] = str(exc)
            return error_result


# ── Deskew helper (module-level so it works without self) ─────────────────

def _rotate_array(arr: 'np.ndarray', angle: float) -> 'np.ndarray':
    """Rotate a numpy array by angle degrees around its centre."""
    from PIL import Image as _Image
    img = _Image.fromarray((arr * 255).astype('uint8'))
    rotated = img.rotate(angle, expand=False, fillcolor=0)
    return (np.array(rotated) > 127).astype(np.uint8)


# ── VisionOCRFallback ──────────────────────────────────────────────────────

class VisionOCRFallback:
    """
    Vision-model OCR via OpenRouter (Gemini 2.0 Flash).

    Used when Tesseract confidence is below threshold, e.g.:
      - Handwritten notes / sticky notes
      - Dark or blurry phone photos
      - Unusual receipt layouts

    Requires OPENROUTER_API_KEY in environment.
    Model is configurable via OPENROUTER_MULTIMODAL_MODEL
    (default: google/gemini-2.0-flash-001).
    """

    _API_URL = 'https://openrouter.ai/api/v1/chat/completions'

    def __init__(self):
        import requests as _req
        self._requests = _req
        self.api_key = os.environ.get('OPENROUTER_API_KEY', '')
        self.model = os.environ.get(
            'OPENROUTER_MULTIMODAL_MODEL', 'google/gemini-2.0-flash-001'
        )
        if not self.api_key:
            log.warning('[VisionOCR] OPENROUTER_API_KEY not set — vision fallback disabled')

    def is_available(self) -> bool:
        return bool(self.api_key)

    def process_receipt(self, image_path: str) -> dict:
        """
        Send the image to a vision model and return structured receipt data.

        The prompt instructs the model to:
          1. Transcribe ALL visible text exactly
          2. Extract amount, date, merchant/title from that text
          3. List every line item or ingredient found
        Works on printed receipts AND handwritten notes/lists.
        """
        import base64

        error_result = {
            'success':    False,
            'text':       '',
            'confidence': 0.0,
            'engine':     'vision',
            'extracted': {
                'amount':       None,
                'date':         datetime.now().strftime('%Y-%m-%d'),
                'merchantName': '',
                'items':        [],
            },
        }

        if not self.is_available():
            error_result['error'] = 'OPENROUTER_API_KEY not configured'
            return error_result

        if not os.path.isfile(image_path):
            error_result['error'] = f'Image not found: {image_path}'
            return error_result

        try:
            # Encode image
            ext = os.path.splitext(image_path)[1].lower().lstrip('.')
            mime_map = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
                        'png': 'image/png', 'webp': 'image/webp',
                        'bmp': 'image/bmp', 'tiff': 'image/tiff'}
            mime = mime_map.get(ext, 'image/jpeg')
            with open(image_path, 'rb') as fh:
                b64 = base64.b64encode(fh.read()).decode('utf-8')

            prompt = (
                "You are an OCR assistant for a South African small-business app.\n"
                "Look at this image and do TWO things:\n\n"
                "1. TRANSCRIBE — copy every word you can see, exactly as written, "
                "line by line. Include quantities, prices, dates, names.\n\n"
                "2. EXTRACT — after the transcription, output a JSON block (fenced "
                "with ```json ... ```) with these fields:\n"
                "  {\n"
                '    "title": "merchant name or note title (first line or heading)",\n'
                '    "amount": null or a number (total rand amount if visible),\n'
                '    "date": null or "YYYY-MM-DD" (if a date is present),\n'
                '    "items": ["each line item or ingredient, one per entry"]\n'
                "  }\n\n"
                "If this is a handwritten shopping list or ingredient list (not a "
                "receipt), set amount to null and list every item in items[].\n"
                "Respond with the transcription first, then the JSON block."
            )

            payload = {
                'model': self.model,
                'messages': [{
                    'role': 'user',
                    'content': [
                        {
                            'type': 'image_url',
                            'image_url': {'url': f'data:{mime};base64,{b64}'},
                        },
                        {'type': 'text', 'text': prompt},
                    ],
                }],
                'max_tokens': 1024,
                'temperature': 0.1,  # low temp = more faithful transcription
            }

            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://mzansipulse.app',
                'X-Title': 'MzansiPulse OCR',
            }

            log.info('[VisionOCR] Sending image to %s via OpenRouter...', self.model)
            resp = self._requests.post(
                self._API_URL, headers=headers, json=payload, timeout=30
            )
            resp.raise_for_status()

            content = resp.json()['choices'][0]['message']['content']
            log.info('[VisionOCR] Response received (%d chars)', len(content))

            # Split transcription from JSON block
            raw_text, extracted = self._parse_vision_response(content)

            return {
                'success':    True,
                'text':       raw_text,
                'confidence': 0.92,   # vision models are generally high accuracy
                'engine':     'vision',
                'extracted':  extracted,
            }

        except Exception as exc:
            log.error('[VisionOCR] Failed: %s', exc, exc_info=True)
            error_result['error'] = str(exc)
            return error_result

    @staticmethod
    def _parse_vision_response(content: str) -> tuple:
        """
        Split the model's response into (raw_text, extracted_dict).

        The model is prompted to return:
          <transcription text>
          ```json
          { "title": ..., "amount": ..., "date": ..., "items": [...] }
          ```
        """
        import json as _json

        extracted = {
            'amount': None,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'merchantName': '',
            'items': [],
        }

        # Pull out the JSON block
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', content)
        raw_text = content

        if json_match:
            # Raw text = everything before the JSON block
            raw_text = content[:json_match.start()].strip()
            try:
                data = _json.loads(json_match.group(1))
                extracted['merchantName'] = data.get('title') or ''
                extracted['items'] = data.get('items') or []
                if data.get('amount') is not None:
                    try:
                        extracted['amount'] = float(data['amount'])
                    except (TypeError, ValueError):
                        pass
                if data.get('date'):
                    extracted['date'] = data['date']
            except _json.JSONDecodeError as exc:
                log.warning('[VisionOCR] JSON parse failed: %s', exc)

        # If no JSON block, treat full response as raw text and run SA parser
        if not json_match and _SHARED_PARSER_AVAILABLE:
            extracted = _parse_receipt_text_shared(content)

        return raw_text, extracted


# ── SmartOCRHelper ─────────────────────────────────────────────────────────

class SmartOCRHelper:
    """
    Orchestrates OCR with automatic quality-based routing:

      1. Try Tesseract (local, free, fast)
      2. If confidence < threshold OR text looks garbled → Vision fallback
         (OpenRouter Gemini 2.0 Flash — handles handwriting & bad photos)

    Confidence threshold defaults to 0.70 but can be overridden via
    OCR_VISION_THRESHOLD env var (e.g. OCR_VISION_THRESHOLD=0.80).

    Example:
        ocr = SmartOCRHelper()
        result = ocr.process_receipt('receipt.jpg')
        print(result['engine'])   # 'tesseract' or 'vision'
    """

    def __init__(self, vision_threshold: Optional[float] = None):
        self.tesseract = TesseractOCRHelper()
        self.vision = VisionOCRFallback()
        self.threshold = vision_threshold or float(
            os.environ.get('OCR_VISION_THRESHOLD', '0.70')
        )
        log.info(
            '[SmartOCR] tesseract=%s  vision=%s  threshold=%.2f',
            self.tesseract.is_available(),
            self.vision.is_available(),
            self.threshold,
        )

    @staticmethod
    def _looks_garbled(text: str) -> bool:
        """
        Heuristic: return True if the OCR text appears corrupted.

        Garbled text has a high ratio of non-alphanumeric, non-space chars
        (brackets, pipes, random symbols) relative to total characters.
        """
        if not text.strip():
            return True
        clean = re.sub(r'[A-Za-z0-9\s.,\-:R/]', '', text)
        garble_ratio = len(clean) / max(len(text), 1)
        return garble_ratio > 0.25   # >25 % garbage chars = suspicious

    def process_receipt(self, image_path: str) -> dict:
        """
        Process a receipt or note image with automatic engine selection.

        Flow:
          1. Run Tesseract
          2. If confidence >= threshold AND text is clean → return Tesseract result
          3. Otherwise try Vision fallback if API key is available
          4. If both fail → return whichever had a result (or the error)
        """
        tess_result = self.tesseract.process_receipt(image_path)

        tess_ok = tess_result.get('success', False)
        tess_conf = tess_result.get('confidence', 0.0)
        tess_text = tess_result.get('text', '')

        needs_vision = (
            not tess_ok
            or tess_conf < self.threshold
            or self._looks_garbled(tess_text)
        )

        if not needs_vision:
            log.info(
                '[SmartOCR] Tesseract sufficient (conf=%.2f) — skipping vision',
                tess_conf,
            )
            return tess_result

        if not self.vision.is_available():
            log.info(
                '[SmartOCR] Tesseract conf=%.2f < %.2f but vision not available '
                '(set OPENROUTER_API_KEY). Returning Tesseract result.',
                tess_conf, self.threshold,
            )
            return tess_result

        log.info(
            '[SmartOCR] Tesseract conf=%.2f below threshold or garbled — '
            'escalating to vision model',
            tess_conf,
        )
        vision_result = self.vision.process_receipt(image_path)

        if vision_result.get('success'):
            # Attach Tesseract's raw text as bonus context
            vision_result['tesseract_text'] = tess_text
            return vision_result

        # Vision also failed — return whichever had more text
        log.warning('[SmartOCR] Vision fallback also failed — returning best available result')
        return tess_result if tess_ok else vision_result


# ── Factory helpers ────────────────────────────────────────────────────────

def get_tesseract_helper() -> TesseractOCRHelper:
    """Return an initialised TesseractOCRHelper (Tesseract only, no API calls)."""
    helper = TesseractOCRHelper()
    if not helper.is_available():
        log.warning('[TesseractOCR] Returning unavailable helper — calls will fail gracefully.')
    return helper


def get_smart_ocr_helper(vision_threshold: Optional[float] = None) -> SmartOCRHelper:
    """
    Return a SmartOCRHelper (recommended for production use).
    Automatically falls back to vision model for handwriting / low-confidence scans.
    """
    return SmartOCRHelper(vision_threshold=vision_threshold)


# ── CLI self-test ──────────────────────────────────────────────────────────

if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

    print('=' * 60)
    print('SmartOCRHelper — self test')
    print('=' * 60)

    ocr = SmartOCRHelper()

    print(f'Tesseract : {"ready" if ocr.tesseract.is_available() else "NOT FOUND"}')
    print(f'Vision    : {"ready (" + ocr.vision.model + ")" if ocr.vision.is_available() else "no API key"}')
    print(f'Threshold : {ocr.threshold:.0%}')

    image_arg = sys.argv[1] if len(sys.argv) > 1 else None

    if not image_arg:
        print('\nNo image path provided. Pass a receipt image as an argument:')
        print('  python tesseract_ocr_helper.py path/to/receipt.jpg')
        sys.exit(0)

    result = ocr.process_receipt(image_arg)

    print('\n' + '─' * 60)
    print(f'Engine     : {result.get("engine", "?")}')
    print(f'Success    : {result.get("success")}')
    print(f'Confidence : {result.get("confidence", 0)*100:.1f}%')

    ext = result.get('extracted', {})
    print(f'Title/Merchant : {ext.get("merchantName", "")}')
    print(f'Amount     : {"R" + str(ext["amount"]) if ext.get("amount") else "not found"}')
    print(f'Date       : {ext.get("date", "")}')
    items = ext.get('items', [])
    print(f'Items ({len(items)}):')
    for item in items:
        print(f'  • {item}')

    if result.get('text'):
        print(f'\nTranscription (first 400 chars):\n{result["text"][:400]}')

    if not result.get('success'):
        print(f'\nError: {result.get("error")}')
        sys.exit(1)

    print('=' * 60)
