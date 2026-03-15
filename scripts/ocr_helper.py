"""
OCR Helper for Receipt/Logbook Scanning
Uses Tesseract OCR for text extraction
"""

import os
import re
from datetime import datetime

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("⚠️  Tesseract not available. Install: pip install pytesseract pillow --break-system-packages")

class OCRHelper:
    """Extract transaction data from receipt/logbook images"""
    
    def __init__(self):
        """Initialize OCR"""
        if TESSERACT_AVAILABLE:
            # Configure Tesseract path (Windows)
            # Download from: https://github.com/UB-Mannheim/tesseract/wiki
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            if os.path.exists(tesseract_path):
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
                print("✅ Tesseract OCR initialized")
            else:
                print("⚠️  Tesseract not found at default path")
        else:
            print("⚠️  Tesseract libraries not installed")
    
    def process_receipt_ocr(image_path: str) -> dict:
        """Process image with OCR"""
        try:
            from ocr_helper import OCRHelper
            
            ocr = OCRHelper()
            result = ocr.process_receipt(image_path)
            
            if result['success']:
                return {
                    'text': result['text'],
                    'confidence': result['confidence'],
                    'extracted': result['extracted']
                }
            else:
                # Fallback if OCR fails
                return {
                    'text': 'OCR processing failed',
                    'confidence': 0.0,
                    'extracted': {
                        'amount': None,
                        'date': None,
                        'items': []
                    }
                }
        except Exception as e:
            print(f"OCR error: {e}")
            return {
                'text': f'Error: {str(e)}',
                'confidence': 0.0,
                'extracted': {
                    'amount': None,
                    'date': None,
                    'items': []
                }
            }
    
    def _extract_transaction_data(self, text: str) -> dict:
        """
        Extract structured transaction data from OCR text
        
        Looks for:
        - Amounts (R123.45, R 123, etc.)
        - Dates (2026-03-03, 03/03/2026, etc.)
        - Item descriptions
        - Total amount
        """
        
        extracted = {
            'amount': None,
            'date': None,
            'items': [],
            'total': None
        }
        
        # Extract amounts (R format)
        amount_pattern = r'R\s*(\d{1,6}(?:[.,]\d{2})?)'
        amounts = re.findall(amount_pattern, text, re.IGNORECASE)
        
        if amounts:
            # Clean amounts (replace comma with period)
            cleaned_amounts = [float(amt.replace(',', '.')) for amt in amounts]
            
            # Assume last/largest amount is total
            extracted['total'] = max(cleaned_amounts)
            extracted['amount'] = extracted['total']
        
        # Extract dates
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',           # 2026-03-03
            r'(\d{2}/\d{2}/\d{4})',           # 03/03/2026
            r'(\d{2}-\d{2}-\d{4})',           # 03-03-2026
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})'  # 3 Mar 2026
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            if dates:
                extracted['date'] = dates[0]
                break
        
        # If no date found, use today
        if not extracted['date']:
            extracted['date'] = datetime.now().strftime('%Y-%m-%d')
        
        # Extract item descriptions (lines with amounts)
        lines = text.split('\n')
        for line in lines:
            if re.search(amount_pattern, line, re.IGNORECASE):
                # Clean and add to items
                cleaned_line = line.strip()
                if len(cleaned_line) > 3:  # Skip very short lines
                    extracted['items'].append(cleaned_line)
        
        return extracted


# ════════════════════════════════════════════════════════════════════════════
# TEST FUNCTION
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Test OCR on sample receipt"""
    
    print("=" * 80)
    print("📷 Testing OCR Helper")
    print("=" * 80)
    
    ocr = OCRHelper()
    
    # Test with sample image (you'll need to provide actual receipt image)
    sample_image = os.path.join('..', 'uploads', 'receipts', 'sample_receipt.jpg')
    
    if os.path.exists(sample_image):
        result = ocr.process_receipt(sample_image)
        
        if result['success']:
            print(f"\n✅ OCR Success!")
            print(f"📝 Confidence: {result['confidence']*100:.1f}%")
            print(f"\n💰 Extracted Data:")
            print(f"   Amount: R{result['extracted']['amount']}")
            print(f"   Date: {result['extracted']['date']}")
            print(f"   Items: {len(result['extracted']['items'])}")
            print(f"\n📄 Raw Text:\n{result['text'][:200]}...")
        else:
            print(f"❌ OCR Failed: {result.get('error')}")
    else:
        print("⚠️  Sample receipt not found")
        print(f"   Expected: {sample_image}")
    
    print("\n" + "=" * 80)