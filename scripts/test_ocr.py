"""
OCR Test Script for MzansiPulse
================================
Usage:
    python test_ocr.py <image_path>
    python test_ocr.py                    # runs parser self-test on sample text

Examples:
    python test_ocr.py ../test_receipts/shoprite.jpg
    python test_ocr.py C:/Users/kamoh/Downloads/receipt.png
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from huawei_ocr_helper import get_ocr_helper, _parse_receipt_text_shared


# ── Sample SA receipt text for self-test (no image needed) ───────────────────
SAMPLE_RECEIPT = """
SHOPRITE
123 Main Road, Soweto
VAT No: 4640123456

DATE: 05/03/2026       TIME: 14:32
CASHIER: THABO         TILL: 03

White Bread 700g             R14.99
Full Cream Milk 2L           R24.99
Chicken Braai Pack 1kg       R89.99
Sunflower Oil 750ml          R39.99
Eggs Large 6pk               R34.99

SUBTOTAL                    R204.95
VAT (15%)                    R26.73
TOTAL                       R204.95

CASH TENDERED               R210.00
CHANGE                        R5.05

THANK YOU FOR SHOPPING AT SHOPRITE
"""


def test_parser():
    """Validate the receipt parser against a known SA receipt."""
    print('=' * 60)
    print('  PARSER SELF-TEST (no image required)')
    print('=' * 60)

    result = _parse_receipt_text_shared(SAMPLE_RECEIPT)

    checks = {
        'Amount extracted':  result['amount'] is not None,
        'Amount correct':    result['amount'] == 204.95,
        'Date extracted':    result['date'] == '2026-03-05',
        'Merchant found':    'shoprite' in result['merchantName'].lower(),
        'Items found':       len(result['items']) >= 3,
    }

    all_pass = True
    for label, passed in checks.items():
        status = '✅' if passed else '❌'
        print(f'  {status}  {label}')
        if not passed:
            all_pass = False

    print()
    print(f'  Amount:   R{result["amount"]}')
    print(f'  Date:     {result["date"]}')
    print(f'  Merchant: {result["merchantName"]}')
    print(f'  Items:    {len(result["items"])} found')
    for item in result['items']:
        print(f'    • {item}')

    print()
    print('  RESULT:', '✅ ALL TESTS PASS' if all_pass else '❌ SOME TESTS FAILED')
    print('=' * 60)
    return all_pass


def test_ocr(image_path: str):
    """Run OCR on a real image file."""
    if not os.path.exists(image_path):
        print(f'❌ Image not found: {image_path}')
        sys.exit(1)

    print('=' * 60)
    print(f'  OCR TEST: {os.path.basename(image_path)}')
    print('=' * 60)

    ocr = get_ocr_helper()
    result = ocr.process_receipt(image_path)

    if result['success']:
        ext = result['extracted']
        conf = result['confidence']
        threshold = float(os.getenv('OCR_CONFIDENCE_THRESHOLD', '0.7'))

        print()
        print(f'  ✅ OCR SUCCESS')
        print(f'  Confidence:  {conf:.1%}  {"✅" if conf >= threshold else "⚠️  below threshold"}')
        print()
        print('  EXTRACTED DATA:')
        amount = ext.get('amount')
        print(f'    Amount:   {"R{:.2f}".format(amount) if amount else "Not found ❌"}')
        print(f'    Date:     {ext["date"]}')
        print(f'    Merchant: {ext["merchantName"] or "Not found"}')
        print(f'    Items:    {len(ext["items"])} found')
        for item in ext['items']:
            print(f'      • {item}')
        print()
        if len(result['text']) > 0:
            preview = result['text'][:300].replace('\n', '\n  ')
            print(f'  RAW TEXT (first 300 chars):\n  {preview}')
            if len(result['text']) > 300:
                print('  ...')
    else:
        print()
        print(f'  ❌ OCR FAILED')
        print(f'  Error: {result.get("error", "unknown")}')

    print('=' * 60)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        # No image provided — run parser self-test
        test_parser()
    else:
        test_ocr(sys.argv[1])
