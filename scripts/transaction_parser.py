"""
MzansiPulse Transaction Parser
Cleans messy WhatsApp-style messages into structured data
Handles South African slang, multilingual input, and code-switching
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

class MzansiTransactionParser:
    """
    Parses informal transaction messages into structured data
    
    Example inputs:
    - "20 bread R60 cash yesterday"
    - "airtime vodacom 100 bucks izolo"
    - "stock from makro R1500 paid cash"
    """
    
    def __init__(self):
        # South African currency patterns
        self.currency_patterns = [
            r'R\s*(\d+(?:[,\.]\d{2})?)',        # R50, R1,500.00
            r'(\d+(?:[,\.]\d{2})?)\s*rand',     # 50 rand
            r'(\d+(?:[,\.]\d{2})?)\s*bucks?',   # 50 bucks (slang)
        ]
        
        # Product categories (township context)
        self.category_keywords = {
            'GROCERIES': [
                'bread', 'milk', 'maize', 'pap', 'rice', 'sugar', 
                'flour', 'cooking oil', 'oil', 'eggs', 'chicken',
                'vegetables', 'fruit', 'meat', 'fish', 'polony'
            ],
            'AIRTIME': [
                'airtime', 'data', 'mtn', 'vodacom', 'cell c', 
                'telkom', 'bundle', 'whatsapp bundle', 'wifi'
            ],
            'ELECTRICITY': [
                'electricity', 'prepaid', 'tokens', 'lights', 
                'power', 'eskom'
            ],
            'STOCK_PURCHASE': [
                'wholesaler', 'cash and carry', 'stock', 'inventory',
                'makro', 'cambridge', 'jumbo', 'mass mart', 'boxer'
            ],
            'CIGARETTES': [
                'cigarettes', 'smoke', 'stuyvesant', 'peter stuyvesant',
                'rothmans', 'dunhill', 'tobacco'
            ],
            'COLD_DRINKS': [
                'coke', 'coca cola', 'fanta', 'sprite', 'cool drink',
                'cooldrink', 'cold drink', 'juice', 'energy drink'
            ]
        }
        
        # Multilingual date patterns (isiZulu/Xhosa/English)
        self.date_keywords = {
            'yesterday': -1,
            'izolo': -1,          # isiZulu for yesterday
            'izolo kusasa': -1,   # isiZulu variant
            'today': 0,
            'namhlanje': 0,       # isiZulu for today
            'vandag': 0,          # Afrikaans for today
            'now': 0,
        }
        
        # Payment method keywords
        self.payment_keywords = {
            'CASH': ['cash', 'kontant', 'imali'],  # English, Afrikaans, Zulu
            'EWALLET': ['ewallet', 'capitec', 'fnb', 'nedbank', 'absa', 'standard bank'],
            'CARD': ['card', 'swipe', 'swiped'],
            'CREDIT': ['credit', 'book', 'owe', 'debt', 'owing']
        }
        
        # Common filler words to remove
        self.filler_words = [
            'the', 'a', 'an', 'bought', 'sold', 'from', 'to',
            'mama', 'baba', 'my', 'our', 'shop', 'spaza',
            'customer', 'paid', 'pay', 'give', 'gave'
        ]
    
    def parse(self, message: str, timestamp: datetime = None) -> Dict:
        """
        Main parsing function
        
        Args:
            message: Raw transaction message
            timestamp: When the message was sent (defaults to now)
        
        Returns:
            Dictionary with extracted transaction data
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Convert to lowercase for processing
        text = message.lower().strip()
        
        # Extract components
        amount = self._extract_amount(text)
        category = self._classify_category(text)
        transaction_date = self._extract_date(text, timestamp)
        payment_method = self._infer_payment_method(text)
        description_cleaned = self._clean_description(text)
        
        # Calculate confidence and flags
        confidence = self._calculate_confidence(text, amount, category)
        should_flag, flag_reason = self._should_flag(text, amount)
        
        # Determine transaction type
        trans_type = 'PURCHASE' if category == 'STOCK_PURCHASE' else 'SALE'
        
        return {
            'transaction_type': trans_type,
            'amount': amount,
            'category': category,
            'transaction_date': transaction_date.strftime('%Y-%m-%d'),
            'payment_method': payment_method,
            'description_original': message,
            'description_cleaned': description_cleaned,
            'data_source': 'WHATSAPP',
            'source_confidence': round(confidence, 2),
            'is_verified': 0,  # Needs manual verification
            'flagged_for_review': 1 if should_flag else 0,
            'flag_reason': flag_reason
        }
    
    def _extract_amount(self, text: str) -> Optional[float]:
        """Extract monetary amount using SA-specific patterns"""
        # Try each currency pattern
        for pattern in self.currency_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '').replace(' ', '')
                try:
                    return float(amount_str)
                except ValueError:
                    continue
        
        # Fallback: Look for any standalone number that might be an amount
        # Match numbers that are likely prices (10-10000)
        numbers = re.findall(r'\b(\d+(?:\.\d{2})?)\b', text)
        for num in numbers:
            try:
                val = float(num)
                if 5 <= val <= 50000:  # Reasonable transaction range
                    return val
            except ValueError:
                continue
        
        return None
    
    def _classify_category(self, text: str) -> str:
        """Classify transaction using keyword matching"""
        # Count matches for each category
        category_scores = {}
        
        for category, keywords in self.category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'OTHER'
    
    def _extract_date(self, text: str, fallback_timestamp: datetime) -> datetime:
        """Extract transaction date from multilingual keywords"""
        # Check for relative date keywords
        for keyword, days_offset in self.date_keywords.items():
            if keyword in text:
                return fallback_timestamp + timedelta(days=days_offset)
        
        # Try to find explicit date patterns (DD/MM or DD-MM)
        date_pattern = r'\b(\d{1,2})[/-](\d{1,2})\b'
        match = re.search(date_pattern, text)
        if match:
            day, month = int(match.group(1)), int(match.group(2))
            try:
                year = fallback_timestamp.year
                # Handle DD/MM format (common in SA)
                return datetime(year, month, day)
            except ValueError:
                # Try MM/DD if DD/MM fails
                try:
                    return datetime(year, day, month)
                except ValueError:
                    pass
        
        # Default to message timestamp
        return fallback_timestamp
    
    def _infer_payment_method(self, text: str) -> str:
        """Infer payment method from keywords"""
        for method, keywords in self.payment_keywords.items():
            if any(keyword in text for keyword in keywords):
                return method
        
        # Default assumption for spaza shops
        return 'CASH'
    
    def _clean_description(self, text: str) -> str:
        """Create a clean, professional description"""
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        
        # Remove filler words
        words = cleaned.split()
        words = [w for w in words if w not in self.filler_words]
        
        # Remove currency symbols and amounts (keep the description only)
        words = [w for w in words if not re.match(r'r?\d+', w)]
        
        # Capitalize first letter
        result = ' '.join(words)
        return result.capitalize() if result else cleaned.capitalize()
    
    def _calculate_confidence(self, text: str, amount: Optional[float], 
                             category: str) -> float:
        """
        Calculate confidence score based on data completeness
        Returns: 0.0 to 1.0
        """
        score = 0.3  # Base score
        
        # Amount found (+0.3)
        if amount is not None:
            score += 0.3
        
        # Category identified (+0.2)
        if category != 'OTHER':
            score += 0.2
        
        # Date indicator found (+0.1)
        if any(kw in text for kw in self.date_keywords.keys()):
            score += 0.1
        
        # Payment method mentioned (+0.1)
        for keywords in self.payment_keywords.values():
            if any(kw in text for kw in keywords):
                score += 0.1
                break
        
        return min(score, 1.0)
    
    def _should_flag(self, text: str, amount: Optional[float]) -> Tuple[bool, Optional[str]]:
        """
        Determine if transaction needs manual review
        
        Returns:
            (should_flag, reason)
        """
        # Flag if no amount found
        if amount is None:
            return True, "Missing amount - needs verification"
        
        # Flag if suspiciously large (potential data entry error)
        if amount > 10000:
            return True, f"Unusually high amount (R{amount:,.2f}) - verify"
        
        # Flag if suspiciously small
        if amount < 1:
            return True, f"Unusually low amount (R{amount:.2f}) - verify"
        
        # Flag if mentions personal withdrawal
        personal_keywords = ['draw', 'personal', 'withdraw', 'took out', 'my money']
        if any(keyword in text for keyword in personal_keywords):
            return True, "Possible personal withdrawal - verify business expense"
        
        # Flag if very low confidence
        # (This is a simplified check - in practice we'd calculate confidence first)
        
        return False, None
    
    def parse_batch(self, messages: list, timestamp: datetime = None) -> list:
        """
        Parse multiple messages at once
        
        Args:
            messages: List of message strings
            timestamp: Base timestamp (defaults to now)
        
        Returns:
            List of parsed transaction dictionaries
        """
        return [self.parse(msg, timestamp) for msg in messages]


# ============================================================================
# TESTING FUNCTIONS
# ============================================================================

def test_parser():
    """Test the parser with sample South African messages"""
    
    print("=" * 70)
    print("🧪 TESTING MZANSIPULSE TRANSACTION PARSER")
    print("=" * 70)
    
    parser = MzansiTransactionParser()
    
    # Test cases: Real messages a spaza owner might send
    test_messages = [
        "20 bread R60 cash yesterday",
        "airtime vodacom 100 bucks",
        "stock from makro R1500 paid cash izolo",
        "5 milk R110 customer paid",
        "electricity tokens R200 prepaid namhlanje",
        "2kg sugar R45 mama bought today",
        "coke fanta sprite R120 cold drinks",
        "cigarettes stuyvesant R850 carton",
        "data bundle mtn 50 ewallet capitec",
        "took out R500 personal",  # Should be flagged
        "bread 15",  # Missing currency symbol
        "R25000 stock cambridge",  # Should be flagged (high amount)
    ]
    
    print(f"\n📝 Testing {len(test_messages)} sample messages...\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"TEST {i}: \"{message}\"")
        print("-" * 70)
        
        result = parser.parse(message)
        
        print(f"   Amount:           R{result['amount'] if result['amount'] else 'NOT FOUND'}")
        print(f"   Category:         {result['category']}")
        print(f"   Date:             {result['transaction_date']}")
        print(f"   Payment:          {result['payment_method']}")
        print(f"   Cleaned:          {result['description_cleaned']}")
        print(f"   Confidence:       {result['source_confidence']:.0%}")
        
        if result['flagged_for_review']:
            print(f"   ⚠️  FLAGGED:        {result['flag_reason']}")
        else:
            print(f"   ✅ Status:         OK")
        
        print()
    
    print("=" * 70)
    print("✅ Parser testing complete!")
    print("=" * 70)


if __name__ == "__main__":
    # Run tests if this file is executed directly
    test_parser()