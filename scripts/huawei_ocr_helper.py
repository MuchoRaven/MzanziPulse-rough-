"""
Huawei Cloud OCR Helper for MzansiPulse
========================================
Integrates with Huawei Cloud General Text Recognition API.
Falls back to local Tesseract OCR when Huawei is unavailable.

Auth hierarchy (tried in order):
  1. Huawei Cloud Python SDK  (huaweicloudsdkocr) — AK/SK signing
  2. Raw HTTPS + X-Auth-Token — token from .env
  3. Local Tesseract           — pytesseract + Pillow
"""

import os
import re
import base64
import logging
from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
load_dotenv()

log = logging.getLogger(__name__)

# ── Optional dependencies ─────────────────────────────────────────────────────

try:
    from huaweicloudsdkcore.auth.credentials import BasicCredentials
    from huaweicloudsdkcore.exceptions.exceptions import ClientRequestException
    from huaweicloudsdkocr.v1 import OcrClient
    from huaweicloudsdkocr.v1.region.ocr_region import OcrRegion
    from huaweicloudsdkocr.v1.model import (
        RecognizeGeneralTextRequest,
        GeneralTextRequestBody,
    )
    HUAWEI_SDK_AVAILABLE = True
except ImportError:
    HUAWEI_SDK_AVAILABLE = False

try:
    import requests as _requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


# ── South-African receipt knowledge ──────────────────────────────────────────

SA_MERCHANTS = [
    'shoprite', 'checkers', 'pick n pay', 'pnp', 'spar', 'woolworths',
    'clicks', 'dischem', 'game', 'makro', 'builders warehouse', 'jet',
    'mr price', 'truworths', 'ackermans', 'pep', 'cash crusaders',
    'liquorland', 'food lover', 'freshstop', 'engen', 'shell', 'bp',
    'total energies', 'caltex', 'steers', 'wimpy', 'kfc', 'mcdonalds',
    'nandos', 'debonairs', 'capitec', 'fnb', 'absa', 'standard bank',
    'nedbank',
]

TOTAL_KEYWORDS = {
    'total', 'grand total', 'totaal', 'amount due', 'amount payable',
    'you pay', 'to pay', 'bedrag', 'subtotal', 'sub-total',
}

EXCLUDE_LINE_KEYWORDS = {
    'total', 'subtotal', 'vat', 'tax', 'change', 'wisselgeld',
    'thank', 'welcome', 'receipt', 'invoice', 'till', 'cashier',
    'tel', 'phone', 'fax', 'address', 'www', 'http', 'reg no',
    'vat no', 'registered', 'card', 'approved', 'auth', 'reference',
    'transaction', 'terminal', 'date', 'time', 'road', 'street',
    'avenue', 'drive', 'lane', 'crescent', 'place', 'soweto',
    'johannesburg', 'cape town', 'durban', 'pretoria',
}


# ── Shared helpers ────────────────────────────────────────────────────────────

def _today() -> str:
    return datetime.now().strftime('%Y-%m-%d')


def _clean_amount(raw: str) -> float:
    """
    Convert various SA amount formats to float.
    Handles: '1 234,56'  '1,234.56'  '1234.56'  '1234,56'
    """
    raw = raw.strip().replace('\xa0', '').replace(' ', '')
    # Comma is decimal separator when followed by exactly 2 digits at end
    if re.search(r',\d{2}$', raw):
        raw = raw.replace('.', '').replace(',', '.')
    else:
        raw = raw.replace(',', '')
    try:
        return float(raw)
    except ValueError:
        return 0.0


def _parse_receipt_text_shared(text: str) -> dict:
    """
    Parse raw OCR text into structured receipt data.
    Returns: {amount, date, merchantName, items}
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]

    # ── Amount extraction ────────────────────────────────────────────────────
    # Matches: R123.45  R 123  ZAR123  1 234,56  1,234.56
    amount_re = re.compile(
        r'(?:R|ZAR)\s*(\d{1,6}(?:[.,\s]\d{3})*(?:[.,]\d{2})?)'
        r'|(\d{1,6}(?:[.,\s]\d{3})*(?:[.,]\d{2}))',
        re.IGNORECASE,
    )
    total_amount: Optional[float] = None
    all_amounts: list[float] = []

    for line in lines:
        upper = line.upper()
        is_total_line = any(kw.upper() in upper for kw in TOTAL_KEYWORDS)
        for m in amount_re.finditer(line):
            raw = m.group(1) or m.group(2) or ''
            val = _clean_amount(raw)
            if val > 0:
                all_amounts.append(val)
                if is_total_line and total_amount is None:
                    total_amount = val

    # Largest amount = most likely total if no "TOTAL" line found
    if total_amount is None and all_amounts:
        total_amount = max(all_amounts)

    # ── Date extraction ──────────────────────────────────────────────────────
    date_val: Optional[str] = None
    date_patterns = [
        (r'(\d{4}-\d{2}-\d{2})',                                                   '%Y-%m-%d'),
        (r'(\d{2}/\d{2}/\d{4})',                                                   '%d/%m/%Y'),
        (r'(\d{2}-\d{2}-\d{4})',                                                   '%d-%m-%Y'),
        (r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})', '%d %b %Y'),
        (r'(\d{1,2}/\d{1,2}/\d{2})',                                               '%d/%m/%y'),
    ]
    for pattern, fmt in date_patterns:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            try:
                date_val = datetime.strptime(m.group(1), fmt).strftime('%Y-%m-%d')
                break
            except ValueError:
                continue
    if not date_val:
        date_val = _today()

    # ── Merchant name ────────────────────────────────────────────────────────
    merchant = ''
    # Check first 4 lines against known SA merchant list
    for line in lines[:4]:
        lower = line.lower()
        for name in SA_MERCHANTS:
            if name in lower:
                merchant = line.strip()
                break
        if merchant:
            break
    # Fallback: first non-empty, non-numeric line
    if not merchant:
        for line in lines[:3]:
            if len(line) > 3 and not re.match(r'^[\d\s\-/:]+$', line):
                merchant = line.strip()
                break

    # ── Line items ───────────────────────────────────────────────────────────
    item_amount_re = re.compile(r'(?:R|ZAR)?\s*\d{1,6}(?:[.,]\d{2})?', re.IGNORECASE)
    items: list[str] = []
    for line in lines:
        lower = line.lower()
        if any(kw in lower for kw in EXCLUDE_LINE_KEYWORDS):
            continue
        if item_amount_re.search(line):
            # Strip price leaving just description
            desc = item_amount_re.sub('', line).strip(' .-,')
            if len(desc) > 2 and merchant.lower() not in line.lower():
                items.append(line.strip())

    return {
        'amount':       total_amount,
        'date':         date_val,
        'merchantName': merchant,
        'items':        items[:5],
    }


# ── HuaweiOCRHelper ───────────────────────────────────────────────────────────

class HuaweiOCRHelper:
    """
    OCR via Huawei Cloud General Text Recognition API.

    Auth priority:
      1. huaweicloudsdkocr (AK/SK BasicCredentials)
      2. Raw requests + X-Auth-Token from .env
    """

    def __init__(self):
        self.ak         = os.getenv('HUAWEI_AK') or os.getenv('OBS_ACCESS_KEY', '')
        self.sk         = os.getenv('HUAWEI_SK') or os.getenv('OBS_SECRET_KEY', '')
        self.project_id = os.getenv('HUAWEI_PROJECT_ID') or os.getenv('PROJECT_ID', '')
        self.region     = os.getenv('HUAWEI_REGION', 'af-south-1')
        self._token     = os.getenv('HUAWEI_X_SUBJECT_TOKEN', '')
        self._client    = None

        if HUAWEI_SDK_AVAILABLE:
            self._client = self._build_client()

    def _build_client(self):
        try:
            creds = BasicCredentials(self.ak, self.sk, self.project_id)
            return (
                OcrClient.new_builder()
                .with_credentials(creds)
                .with_region(OcrRegion.value_of(self.region))
                .build()
            )
        except Exception as exc:
            log.warning('Huawei SDK client failed: %s', exc)
            return None

    # ── SDK call ──────────────────────────────────────────────────────────────
    def _call_sdk(self, b64: str) -> dict:
        req = RecognizeGeneralTextRequest()
        req.body = GeneralTextRequestBody(image=b64, detect_direction=True)
        resp = self._client.recognize_general_text(req)
        blocks = resp.result.words_block_list or []
        words = [blk.words for blk in blocks]
        confs = [blk.confidence for blk in blocks if blk.confidence is not None]
        avg_conf = sum(confs) / len(confs) if confs else 0.0
        return {'text': '\n'.join(words), 'confidence': avg_conf, 'words': words}

    # ── Token (raw HTTP) call ─────────────────────────────────────────────────
    def _call_token(self, b64: str) -> dict:
        if not REQUESTS_AVAILABLE:
            raise RuntimeError('requests library not installed')
        if not self._token:
            raise RuntimeError('No Huawei IAM token in .env (HUAWEI_X_SUBJECT_TOKEN)')

        url = (
            f'https://ocr.{self.region}.myhuaweicloud.com'
            f'/v2/{self.project_id}/ocr/general-text'
        )
        resp = _requests.post(
            url,
            headers={'X-Auth-Token': self._token, 'Content-Type': 'application/json'},
            json={'image': b64, 'detect_direction': True},
            timeout=15,
        )
        resp.raise_for_status()
        blocks = resp.json().get('result', {}).get('words_block_list', [])
        words = [b.get('words', '') for b in blocks]
        confs = [b.get('confidence', 0.0) for b in blocks]
        avg_conf = sum(confs) / len(confs) if confs else 0.0
        return {'text': '\n'.join(words), 'confidence': avg_conf, 'words': words}

    def _call_api(self, b64: str) -> dict:
        if HUAWEI_SDK_AVAILABLE and self._client:
            return self._call_sdk(b64)
        return self._call_token(b64)

    # ── Public ────────────────────────────────────────────────────────────────
    def process_receipt(self, image_path: str) -> dict:
        """
        Process a receipt image and return structured data.

        Returns:
            {
                'success': bool,
                'text': str,
                'confidence': float,   # 0.0 – 1.0
                'extracted': {
                    'amount': float | None,
                    'date': str,           # YYYY-MM-DD
                    'merchantName': str,
                    'items': list[str]
                }
            }
        """
        try:
            with open(image_path, 'rb') as fh:
                b64 = base64.b64encode(fh.read()).decode('utf-8')

            ocr = self._call_api(b64)
            extracted = _parse_receipt_text_shared(ocr['text'])
            log.info('Huawei OCR success — confidence %.2f', ocr['confidence'])
            return {
                'success':    True,
                'text':       ocr['text'],
                'confidence': ocr['confidence'],
                'extracted':  extracted,
            }

        except Exception as exc:
            log.error('Huawei OCR failed: %s', exc)
            return {
                'success':    False,
                'text':       '',
                'confidence': 0.0,
                'error':      str(exc),
                'extracted': {
                    'amount':       None,
                    'date':         _today(),
                    'merchantName': '',
                    'items':        [],
                },
            }


# ── LocalOCRHelper (Tesseract fallback) ──────────────────────────────────────

class LocalOCRHelper:
    """Tesseract-based OCR — no cloud credentials required."""

    def __init__(self):
        if TESSERACT_AVAILABLE:
            tess_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tess_path):
                pytesseract.pytesseract.tesseract_cmd = tess_path
            print('[OCR] Local Tesseract OCR initialised')
        else:
            print('[OCR] pytesseract not installed - run: pip install pytesseract pillow')

    def process_receipt(self, image_path: str) -> dict:
        if not TESSERACT_AVAILABLE:
            return {
                'success':    False,
                'text':       '',
                'confidence': 0.0,
                'error':      'pytesseract not installed',
                'extracted': {
                    'amount':       None,
                    'date':         _today(),
                    'merchantName': '',
                    'items':        [],
                },
            }
        try:
            img = Image.open(image_path)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            confs = [c for c in data['conf'] if isinstance(c, (int, float)) and c != -1]
            avg_conf = (sum(confs) / len(confs) / 100.0) if confs else 0.0
            text = pytesseract.image_to_string(img, config='--psm 6')
            extracted = _parse_receipt_text_shared(text)
            log.info('Tesseract OCR success — confidence %.2f', avg_conf)
            return {
                'success':    True,
                'text':       text,
                'confidence': avg_conf,
                'extracted':  extracted,
            }
        except Exception as exc:
            log.error('Tesseract OCR failed: %s', exc)
            return {
                'success':    False,
                'text':       '',
                'confidence': 0.0,
                'error':      str(exc),
                'extracted': {
                    'amount':       None,
                    'date':         _today(),
                    'merchantName': '',
                    'items':        [],
                },
            }


# ── Smart selector ────────────────────────────────────────────────────────────

def get_ocr_helper():
    """
    Return the best available OCR helper:
      • Huawei Cloud OCR  (if credentials present)
      • Local Tesseract   (fallback)

    Override with OCR_PROVIDER=tesseract in .env to force local.
    """
    provider = os.getenv('OCR_PROVIDER', 'huawei').lower()
    if provider == 'tesseract':
        print('[OCR] OCR_PROVIDER=tesseract - using local Tesseract')
        return LocalOCRHelper()

    ak = os.getenv('HUAWEI_AK') or os.getenv('OBS_ACCESS_KEY', '')
    sk = os.getenv('HUAWEI_SK') or os.getenv('OBS_SECRET_KEY', '')
    token = os.getenv('HUAWEI_X_SUBJECT_TOKEN', '')

    if ak and sk:
        if HUAWEI_SDK_AVAILABLE:
            print('[OCR] Using Huawei Cloud OCR (SDK - AK/SK)')
        elif token:
            print('[OCR] Using Huawei Cloud OCR (token fallback)')
        else:
            print('[OCR] Huawei SDK not installed and no token - falling back to Tesseract')
            return LocalOCRHelper()
        return HuaweiOCRHelper()

    print('[OCR] No Huawei credentials found - falling back to Tesseract')
    return LocalOCRHelper()
