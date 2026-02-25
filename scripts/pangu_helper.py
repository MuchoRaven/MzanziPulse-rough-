"""
Pangu AI Helper
Connects to Huawei Pangu AI for business advice
"""

import requests
import json
import os
from datetime import datetime, timedelta

class PanguAIHelper:
    """
    Helper class for Huawei Pangu AI API
    Provides business advice in multiple languages
    """
    
    def __init__(self, project_id: str, access_key: str, secret_key: str, region: str = 'af-south-1'):
        """
        Initialize Pangu AI connection
        
        Args:
            project_id: Your Huawei Cloud project ID
            access_key: Your AK
            secret_key: Your SK
            region: Cloud region
        """
        self.project_id = project_id
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        self.token = None
        self.token_expires = None
        
        # API endpoint (example - adjust based on actual Pangu endpoint)
        self.api_endpoint = f"https://pangu.{region}.myhuaweicloud.com/v1/{project_id}/infers"
        
        print(f"🤖 Pangu AI Helper initialized for project: {project_id}")
    
    # ════════════════════════════════════════════════════════════════════════
    # IAM TOKEN GENERATION
    # ════════════════════════════════════════════════════════════════════════
    
    def get_iam_token(self):
        """
        Get IAM token for API authentication
        Tokens expire after 24 hours and must be refreshed.
        """
        # Check if token is still valid
        if self.token and self.token_expires and datetime.now() < self.token_expires:
            return self.token
        
        print("🔑 Generating new IAM token...")
        
        try:
            # IAM endpoint
            iam_url = "https://iam.myhuaweicloud.com/v3/auth/tokens"
            
            # Request body for token
            auth_body = {
                "auth": {
                    "identity": {
                        "methods": ["hw_ak_sk"],
                        "hw_ak_sk": {
                            "access": {
                                "key": self.access_key
                            },
                            "secret": {
                                "key": self.secret_key
                            }
                        }
                    },
                    "scope": {
                        "project": {
                            "id": self.project_id
                        }
                    }
                }
            }
            
            # Request token
            response = requests.post(
                iam_url,
                json=auth_body,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.status_code == 201:
                # Token is in the response header
                self.token = response.headers.get('X-Subject-Token')
                self.token_expires = datetime.now() + timedelta(hours=23)
                
                print("✅ IAM token generated successfully")
                return self.token
            else:
                print(f"❌ IAM token generation failed: {response.status_code}")
                print(f"Response: {response.text}")
                
                # Use mock token for development
                self.token = "mock_token_for_demo"
                self.token_expires = datetime.now() + timedelta(hours=24)
                return self.token
                
        except Exception as e:
            print(f"❌ IAM token exception: {str(e)}")
            
            # Use mock token for development
            self.token = "mock_token_for_demo"
            self.token_expires = datetime.now() + timedelta(hours=24)
            return self.token
    
    # ════════════════════════════════════════════════════════════════════════
    # MAIN BUSINESS ADVICE FUNCTION
    # ════════════════════════════════════════════════════════════════════════
    
    def get_business_advice(self, 
                           question: str, 
                           user_context: dict = None,
                           language: str = 'en') -> dict:
        """
        Get business advice from Pangu AI
        
        Args:
            question: User's question
            user_context: Business context (type, location, score, etc.)
            language: Preferred response language (en, zu, st, etc.)
        
        Returns:
            dict: AI response with advice
        """
        
        # MODE SELECTION: Mock vs Real API
        USE_REAL_PANGU = os.environ.get('USE_REAL_PANGU', 'false').lower() == 'true'
        
        if USE_REAL_PANGU:
            # Real Pangu AI API call
            return self._call_pangu_api(question, user_context, language)
        else:
            # Mock responses for development
            return self._get_mock_response(question, user_context, language)
    
    # ════════════════════════════════════════════════════════════════════════
    # REAL PANGU API INTEGRATION
    # ════════════════════════════════════════════════════════════════════════
    
    def _call_pangu_api(self, question: str, user_context: dict, language: str) -> dict:
        """
        Call real Pangu AI API
        """
        try:
            # Build context-aware prompt
            system_prompt = self._build_system_prompt(user_context, language)
            
            # Get IAM token
            token = self.get_iam_token()
            
            # Prepare request
            headers = {
                'Content-Type': 'application/json',
                'X-Auth-Token': token
            }
            
            payload = {
                'model': os.environ.get('PANGU_MODEL', 'pangu-chat-v1'),
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    },
                    {
                        'role': 'user',
                        'content': question
                    }
                ],
                'temperature': 0.7,
                'max_tokens': 500,
                'top_p': 0.9
            }
            
            print(f"🤖 Calling Pangu AI API...")
            
            # Make API request
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Extract response text
                ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                
                print(f"✅ Pangu AI response received ({len(ai_response)} chars)")
                
                return {
                    'success': True,
                    'response': ai_response,
                    'timestamp': datetime.now().isoformat(),
                    'language': language,
                    'intent': self._detect_intent(question),
                    'suggestions': self._get_follow_up_suggestions(question),
                    'source': 'pangu-ai'
                }
            else:
                print(f"❌ Pangu API error: {response.status_code}")
                # Fallback to mock response
                return self._get_mock_response(question, user_context, language)
                
        except Exception as e:
            print(f"❌ Pangu API exception: {str(e)}")
            # Fallback to mock response
            return self._get_mock_response(question, user_context, language)
    
    # ════════════════════════════════════════════════════════════════════════
    # SYSTEM PROMPT BUILDER
    # ════════════════════════════════════════════════════════════════════════
    
    def _build_system_prompt(self, user_context: dict, language: str) -> str:
        """
        Build system prompt with business context
        """
        prompt = "You are Biz-Bantu, an AI business advisor for South African township entrepreneurs. "
        
        if user_context:
            if user_context.get('businessName'):
                prompt += f"You're helping {user_context['businessName']}, "
            if user_context.get('businessType'):
                prompt += f"a {user_context['businessType'].replace('_', ' ').lower()}, "
            if user_context.get('location'):
                prompt += f"located in {user_context['location']}. "
            if user_context.get('empowerScore'):
                prompt += f"Their EmpowerScore is {user_context['empowerScore']}/1000. "
        
        # Language instruction
        if language == 'zu':
            prompt += "Respond in isiZulu. "
        elif language == 'st':
            prompt += "Respond in Sesotho. "
        elif language == 'xh':
            prompt += "Respond in isiXhosa. "
        else:
            prompt += "Respond in English. "
        
        prompt += "Give practical, actionable advice specific to South African township businesses. "
        prompt += "Be encouraging, supportive, and culturally aware. "
        
        return prompt
    
    # ════════════════════════════════════════════════════════════════════════
    # MOCK RESPONSES (For Development)
    # ════════════════════════════════════════════════════════════════════════
    
    def _get_mock_response(self, question: str, user_context: dict, language: str) -> dict:
        """
        Mock responses for development
        Will be replaced with real Pangu API calls
        """
        
        # Detect question intent
        question_lower = question.lower()
        
        # Financial help
        if any(word in question_lower for word in ['grant', 'loan', 'funding', 'money', 'capital', 'imali', 'chelete']):
            if language == 'zu':
                response = """Yebo! Kunezindlela zokuthola usizo lwezimali:

1. **NYDA Business Grant** 🎯
   • R10,000 - R100,000
   • Amabhizinisi amasha
   • Isipesheli: 30 days left!

2. **SEFA Khula Loan** 💼
   • R5,000 - R3,000,000
   • Inzalo ephansi
   • Isikhathi sokubuyisela esingokomuso

3. **Township Entrepreneurship Fund** 🏦
   • R20,000 - R150,000
   • Kusebenza kahle kakhulu!

Ungathanda ukufaka isicelo esiphi?"""
            else:
                response = """Great question! Here are funding opportunities perfect for your business:

1. **NYDA Business Grant** 🎯
   • Amount: R10,000 - R100,000
   • For: Young entrepreneurs
   • Deadline: 30 days left!
   • Match: 85% (High chance!)

2. **SEFA Khula Loan** 💼
   • Amount: R5,000 - R3,000,000
   • Interest: Low rates
   • Flexible repayment

3. **Township Entrepreneurship Fund** 🏦
   • Amount: R20,000 - R150,000
   • Match: 100% (Perfect fit!)
   • Process: Fast approval

Would you like help applying to any of these?"""
        
        # Sales/marketing advice
        elif any(word in question_lower for word in ['sales', 'customers', 'marketing', 'grow', 'increase', 'ukuthengisa']):
            response = """Here are 5 proven strategies to boost your sales:

1. **Stock Fast-Moving Items** 📦
   • Bread, milk, eggs (daily needs)
   • Airtime (high demand)
   • Cigarettes (if licensed)
   
2. **Offer 'Book' Credit** 📓
   • Build loyalty with trusted customers
   • Track carefully in MzansiPulse
   • Set clear payment dates
   
3. **Extended Hours** ⏰
   • Open 6am-9pm if possible
   • Catch early workers & late shoppers
   • More hours = more sales
   
4. **Keep It Clean** ✨
   • Well-lit, organized shop
   • Customers prefer clean stores
   • Stock rotation (fresh products)
   
5. **Community Relationships** 🤝
   • Sponsor local sports teams
   • Support community events
   • Word-of-mouth marketing

Which strategy would you like to try first?"""
        
        # Cash flow advice
        elif any(word in question_lower for word in ['cash', 'money', 'profit', 'expenses', 'imali']):
            response = """Let's improve your cash flow! Here's what works:

💰 **Track Everything**
- Log EVERY sale in MzansiPulse (even R5)
- Use WhatsApp integration for quick logging
- Weekly reconciliation builds trust with banks

📊 **Separate Personal & Business**
- Don't mix personal expenses with business
- Pay yourself a salary (even if small)
- Keeps your EmpowerScore accurate

📉 **Reduce Wastage**
- Check expiry dates daily
- Sell near-expiry items at discount
- Better stock rotation

📈 **Increase Margins**
- Compare supplier prices
- Buy in bulk when possible
- Negotiate with your Makro/wholesaler

Your current EmpowerScore (542) is BUILDER tier. 
Keep consistent records and you'll reach PRIME tier (700+) soon!"""
        
        # EmpowerScore questions
        elif any(word in question_lower for word in ['score', 'credit', 'empowerscore', 'rating']):
            score = user_context.get('empowerScore', 542) if user_context else 542
            
            response = f"""Your EmpowerScore: {score}/1000 🎯

**What This Means:**
- Tier: BUILDER (Good progress!)
- Grant eligibility: Medium-High
- Bank trust: Building...

**How to Improve:**
1. Log transactions daily ✅
2. Do weekly cash reconciliation 📊
3. Add 2-3 product lines 🛒
4. Reduce personal withdrawals 💰
5. Collect credit on time 📓

**Quick Wins:**
- +15 points: Perfect week of logging
- +20 points: Accurate reconciliation
- +10 points: Diversify stock

Want specific advice on improving your score?"""
        
        # General greeting
        elif any(word in question_lower for word in ['hello', 'hi', 'hey', 'sawubona', 'dumela', 'molweni']):
            name = user_context.get('firstName', 'entrepreneur') if user_context else 'entrepreneur'
            business = user_context.get('businessName', 'your business') if user_context else 'your business'
            
            response = f"""Hello {name}! 👋

I'm **Biz-Bantu**, your AI business advisor!

I'm here to help {business} grow and succeed. I can help you with:

💰 Finding grants and funding
📈 Increasing sales and customers  
📊 Managing cash flow
🎯 Improving your EmpowerScore
📓 Managing 'book' credit
🏪 Stock management tips

**Ask me anything!** I speak English, isiZulu, Sesotho, and isiXhosa.

What would you like help with today?"""
        
        else:
            # Generic helpful response
            response = """I'm here to help! I can advise you on:

🎯 **Business Growth**
- Sales strategies
- Marketing tips
- Customer retention

💰 **Funding & Grants**
- NYDA, SEFA, Township Fund
- How to apply
- Eligibility requirements

📊 **Financial Management**
- Cash flow tracking
- Reducing expenses
- Profit optimization

📈 **EmpowerScore**
- How it's calculated
- Improving your score
- Grant matching

Could you tell me more about what you need help with?"""
        
        return {
            'success': True,
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'language': language,
            'intent': self._detect_intent(question),
            'suggestions': self._get_follow_up_suggestions(question)
        }
    
    # ════════════════════════════════════════════════════════════════════════
    # INTENT DETECTION
    # ════════════════════════════════════════════════════════════════════════
    
    def _detect_intent(self, question: str) -> str:
        """Detect user's question intent"""
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['grant', 'loan', 'funding', 'imali']):
            return 'FUNDING_INQUIRY'
        elif any(word in question_lower for word in ['sales', 'customers', 'marketing']):
            return 'SALES_ADVICE'
        elif any(word in question_lower for word in ['cash', 'profit', 'expenses']):
            return 'FINANCIAL_ADVICE'
        elif any(word in question_lower for word in ['score', 'credit', 'rating']):
            return 'SCORE_INQUIRY'
        else:
            return 'GENERAL_INQUIRY'
    
    # ════════════════════════════════════════════════════════════════════════
    # FOLLOW-UP SUGGESTIONS
    # ════════════════════════════════════════════════════════════════════════
    
    def _get_follow_up_suggestions(self, question: str) -> list:
        """Get suggested follow-up questions"""
        intent = self._detect_intent(question)
        
        suggestions = {
            'FUNDING_INQUIRY': [
                "Which grant should I apply for?",
                "How do I improve my chances?",
                "What documents do I need?"
            ],
            'SALES_ADVICE': [
                "How do I attract more customers?",
                "Should I offer credit?",
                "What products sell best?"
            ],
            'FINANCIAL_ADVICE': [
                "How can I reduce costs?",
                "Should I hire staff?",
                "How much profit is good?"
            ],
            'SCORE_INQUIRY': [
                "How can I reach PRIME tier?",
                "What hurts my score?",
                "How long to improve?"
            ],
            'GENERAL_INQUIRY': [
                "Tell me about grants",
                "How to increase sales?",
                "What's my EmpowerScore?"
            ]
        }
        
        return suggestions.get(intent, [
            "How can I grow my business?",
            "Show me funding options",
            "Tips for cash management"
        ])


# ════════════════════════════════════════════════════════════════════════════
# USAGE EXAMPLE / TEST
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Test Pangu AI Helper"""
    
    print("=" * 80)
    print("🤖 Testing Biz-Bantu AI Helper")
    print("=" * 80)
    
    # Initialize
    pangu = PanguAIHelper(
        project_id="demo-project",
        access_key="demo-ak",
        secret_key="demo-sk"
    )
    
    # Test questions
    questions = [
        ("Hello! I need help", "en"),
        ("How can I get funding for my spaza shop?", "en"),
        ("Ngicela usizo ngezimali", "zu"),
        ("How do I increase my sales?", "en"),
        ("What's my EmpowerScore?", "en")
    ]
    
    user_context = {
        'firstName': 'Thandi',
        'businessName': "Mama Thandi's Spaza Shop",
        'businessType': 'SPAZA_SHOP',
        'location': 'Soweto, Gauteng',
        'empowerScore': 542
    }
    
    for question, lang in questions:
        print(f"\n{'='*80}")
        print(f"Q: {question}")
        print(f"Language: {lang}")
        print(f"{'='*80}")
        
        response = pangu.get_business_advice(question, user_context, lang)
        
        print(f"\n{response['response']}")
        print(f"\n💡 Suggestions:")
        for suggestion in response['suggestions']:
            print(f"   • {suggestion}")
    
    print("\n" + "=" * 80)
    print("✅ Biz-Bantu Test Complete!")
    print("=" * 80)