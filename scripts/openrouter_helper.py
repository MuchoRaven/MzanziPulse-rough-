"""
OpenRouter AI Helper
Integrates OpenRouter models for intelligent responses
Uses standard requests library (no openai package needed)
"""

import os
import requests
from datetime import datetime

class OpenRouterHelper:
    """
    Helper for OpenRouter AI models
    Provides intelligent business advice using various AI models
    """
    
    def __init__(self):
        """Initialize OpenRouter client"""
        self.api_key = os.environ.get('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        
        if not self.api_key:
            print("⚠️  OPENROUTER_API_KEY not found in environment")
        else:
            print("✅ OpenRouter AI initialized")
        
        # Model configuration
        self.biz_bantu_model = os.environ.get('OPENROUTER_BIZ_BANTU_MODEL', 'deepseek/deepseek-chat-v3.1')
        self.multimodal_model = os.environ.get('OPENROUTER_MULTIMODAL_MODEL', 'google/gemini-2.0-flash-001')
        self.fast_model = os.environ.get('OPENROUTER_FAST_MODEL', 'qwen/qwen3.5-flash-02-23')
        self.advanced_model = os.environ.get('OPENROUTER_ADVANCED_MODEL', 'deepseek/deepseek-chat-v3.1')
    
    # Models with strong South African language support
    MULTILINGUAL_LANGUAGES = {'st', 'xh'}  # Sesotho and isiXhosa need a better model

    def _select_model(self, language: str) -> str:
        """
        Route to the best model for the requested language.
        DeepSeek has very limited Sesotho/isiXhosa training data.
        Gemini 2.0 Flash handles African languages significantly better.
        """
        if language in self.MULTILINGUAL_LANGUAGES:
            return self.multimodal_model  # google/gemini-2.0-flash-001
        return self.biz_bantu_model       # deepseek/deepseek-chat-v3.1

    def get_business_advice(self, question: str, user_context: dict, language: str = 'en') -> dict:
        """
        Get intelligent business advice using OpenRouter AI

        Args:
            question: User's question
            user_context: Business context with real data
            language: Preferred response language

        Returns:
            dict: AI response with suggestions
        """

        if not self.api_key:
            return {
                'success': False,
                'error': 'OpenRouter API key not configured'
            }

        try:
            # Build context-aware system prompt
            system_prompt = self._build_system_prompt(user_context, language)

            # Pick the right model for the language
            model = self._select_model(language)

            print(f"🤖 Calling OpenRouter AI ({model}) [lang={language}]...")
            print(f"📝 Question: {question[:100]}...")

            # Prepare request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mzansipulse.app",
                "X-Title": "MzansiPulse Biz-Bantu",
            }

            # Prepend a language tag directly to the user message.
            # This is the strongest per-turn signal — the model sees it
            # immediately before generating its reply.
            lang_names_map = {'en': 'English', 'zu': 'isiZulu', 'st': 'Sesotho', 'xh': 'isiXhosa'}
            lang_label = lang_names_map.get(language, 'English')
            if language != 'en':
                tagged_question = f"[REPLY IN {lang_label.upper()} ONLY]\n{question}"
            else:
                tagged_question = question

            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": tagged_question}
                ],
                "temperature": 0.7,
                "max_tokens": 1500,
                "top_p": 0.9,
            }
            
            # Call OpenRouter API
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Check for errors
            if response.status_code != 200:
                print(f"❌ OpenRouter API error: {response.status_code}")
                print(f"Response: {response.text}")
                return {
                    'success': False,
                    'error': f'API error: {response.status_code} - {response.text}'
                }
            
            # Parse response
            result = response.json()
            ai_response = result['choices'][0]['message']['content']
            
            print(f"✅ AI response received ({len(ai_response)} chars)")
            
            # Detect intent from question
            intent = self._detect_intent(question, language)
            
            # Generate follow-up suggestions
            suggestions = self._get_follow_up_suggestions(intent, language)
            
            return {
                'success': True,
                'response': ai_response,
                'timestamp': datetime.now().isoformat(),
                'language': language,
                'intent': intent,
                'suggestions': suggestions,
                'source': 'openrouter-ai',
                'model': model,
                'usedRealData': True,
                'dataSource': 'business_intelligence'
            }
            
        except requests.exceptions.Timeout:
            print("❌ OpenRouter API timeout")
            return {
                'success': False,
                'error': 'AI request timed out. Please try again.'
            }
        except Exception as e:
            print(f"❌ OpenRouter API error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': f'AI error: {str(e)}'
            }
    
    def _build_system_prompt(self, user_context: dict, language: str) -> str:
        """Build comprehensive system prompt with real business data"""
        
        # Extract user data
        first_name = user_context.get('firstName', 'entrepreneur')
        business_name = user_context.get('businessName', 'your business')
        business_type = user_context.get('businessType', 'BUSINESS').replace('_', ' ').title()
        location = user_context.get('location', 'South Africa')
        
        wallet = user_context.get('wallet', {})
        analytics = user_context.get('analytics', {})
        credit = user_context.get('creditLedger', {})
        
        # Language map
        lang_names = {
            'en': 'English',
            'zu': 'isiZulu',
            'st': 'Sesotho',
            'xh': 'isiXhosa'
        }
        target_language = lang_names.get(language, 'English')

        # Language lock goes FIRST — before persona, before everything.
        # LLMs weight early instructions most heavily.
        lang_lock = f"""!! LANGUAGE LOCK — THIS OVERRIDES EVERYTHING ELSE !!
Your ONLY allowed response language is: {target_language}
Do NOT write a single word in English (unless {target_language} IS English).
Do NOT explain yourself in English.
Do NOT mix languages.
Even if your instructions below are written in English, your REPLY must be 100% {target_language}.
If you are unsure how to say something in {target_language}, simplify the idea and say it in {target_language}.
!! END LANGUAGE LOCK !!

"""
        # Build comprehensive prompt
        prompt = lang_lock + f"""You are Biz-Bantu, an expert AI business advisor for South African township solo entrepreneurs.

CRITICAL CONTEXT - YOU ARE ADVISING:
- Name: {first_name}
- Business: {business_name}
- Type: {business_type}
- Location: {location}

TARGET AUDIENCE:
You advise struggling individual entrepreneurs:
- Home bakers selling vetkoek from their homes
- Street cobblers fixing shoes under cheap gazebos  
- Seamstresses sewing clothes under trees
- Home salon hairdressers plaiting hair at home
- Car washers with buckets and sponges
- NOT spaza shop owners with bulk buying power

REAL BUSINESS DATA (Use this in your advice):
"""
        
        # Add financial data if available
        if wallet:
            prompt += f"""
FINANCIAL STATUS:
- Current Balance: R{wallet.get('totalBalance', 0):,.2f}
- Cash on Hand: R{wallet.get('cashBalance', 0):,.2f}
- Digital Balance: R{wallet.get('digitalBalance', 0):,.2f}
- Credit Owed to Business: R{wallet.get('creditOwed', 0):,.2f}
- 30-Day Sales: R{wallet.get('totalSales', 0):,.2f}
- 30-Day Expenses: R{wallet.get('totalExpenses', 0):,.2f}
"""
        
        # Add analytics if available
        if analytics:
            prompt += f"""
BUSINESS PERFORMANCE:
- Average Daily Sales: R{analytics.get('averageDailySales', 0):,.2f}
- Payment Split: {analytics.get('cashVsDigital', {}).get('cashPercentage', 0):.0f}% cash, {100 - analytics.get('cashVsDigital', {}).get('cashPercentage', 0):.0f}% digital
- 30-Day Profit: R{analytics.get('incomeVsExpenses', {}).get('profit', 0):,.2f}
- Transaction Count: {analytics.get('transactionCount', 0)} transactions
"""
        
        # Add credit concerns if applicable
        if credit and credit.get('outstandingAmount', 0) > 0:
            prompt += f"""
CREDIT MANAGEMENT:
- Total Outstanding: R{credit['outstandingAmount']:,.2f} (money owed TO the business)
- Overdue Accounts: {credit.get('overdueCount', 0)} customers
"""
        
        # Add top products if available
        top_products = user_context.get('topProducts', [])
        if top_products:
            prompt += "\nTOP SELLING ITEMS:\n"
            for i, product in enumerate(top_products[:5], 1):
                prompt += f"{i}. {product['category']}: R{product['revenue']:,.2f} revenue\n"
        
        # Build the language-specific guidance block
        prompt += self._build_language_guidance(language, target_language, wallet, first_name)

        return prompt

    def _build_language_guidance(self, language: str, target_language: str, wallet: dict, first_name: str) -> str:
        """Return a detailed, language-specific guidance block for the system prompt."""

        common = f"""
RESPONSE REQUIREMENTS:
1. ALWAYS respond ENTIRELY in {target_language} — every word, every sentence
2. Reference REAL DATA with actual numbers (e.g. "Chelete ea hao ea R{wallet.get('totalBalance', 0):,.2f}")
3. Be specific and actionable — give steps the user can take TODAY
4. Be warm, encouraging, and culturally aware of South African township life
5. Use local context: Makro, Shoprite, "book" credit, iBhola/stockvel, WhatsApp orders
6. Keep responses under 400 words — concise, conversational, never robotic
7. If data shows problems (negative profit, high credit), address them gently but honestly
8. Use emojis sparingly and naturally (👋 🎯 💡 ✅)

SOUTH AFRICAN FUNDING KNOWLEDGE (verified 2025/2026 — use accurate figures only):
- NYDA Business Grant: R1,000–R200,000 for youth entrepreneurs aged 18–35 (nyda.gov.za)
- SEDFA (formerly SEFA) Khula Loan: R10,000–R3,000,000 at below-market rates (sedfa.org.za)
- DSBD Spaza Shop Support Fund: R40,000 non-repayable grant for spaza/township traders (spazashopfund.co.za)
- NEF Imbewu Fund: R250,000–R10,000,000 for black-owned businesses (nefcorp.co.za)
- NEF Women Empowerment Fund: R250,000–R75,000,000 for women-led businesses
- Tony Elumelu Foundation: USD $5,000 (~R90,000) — annual cycle, next opens Jan 2027
- SEDA: Free business training, mentorship and CIPC/SARS registration help (seda.org.za)
- Yoco Capital: Revenue advance R5,000–R2,000,000 (repaid via card sales %) — no CIPC needed
- Business Partners Limited: R500,000–R50,000,000 for formalised SMEs
- Match recommendation to their actual revenue, business type, and registration status
"""

        if language == 'st':
            return common + f"""
===============================================
SESOTHO LANGUAGE GUIDE - READ THIS CAREFULLY
===============================================
You MUST write your ENTIRE response in Sesotho (Southern Sotho / Sesotho sa Leboa).
Do NOT write any English sentences. Do NOT mix languages mid-sentence.

CORE SESOTHO VOCABULARY FOR BUSINESS:
  Kgwebo          = business
  Chelete         = money
  Thekiso         = sales / selling
  Rekisa          = to sell
  Reka            = to buy
  Bareki          = customers
  Lijo            = food
  Lihlahisoa      = products / goods
  Litefiso        = expenses / costs
  Phaello         = profit
  Tshenyehelo     = losses
  Tjhelete e kenang = income / money coming in
  Tjhelete e tsoang = expenses / money going out
  Poloko          = savings
  Mokoloto        = credit / debt
  Baleheli        = debtors (customers who owe you)
  Sehlopha        = category
  Tlhahiso        = offer / supply
  Ntlha           = point / tip
  Thuso           = help / support
  Ntlafatso       = improvement
  Monyetla        = opportunity
  Bothata         = problem / challenge
  Phepelo         = supply chain
  Mmaraka         = market
  Liphihlelo      = grants / opportunities
  Kadimo          = loan
  Tefo            = payment
  Moruo           = economy / wealth
  Mosebetsi       = job / work / business operation

COMMON SESOTHO PHRASES YOU CAN USE:
  Dumela {first_name}!                    = Hello {first_name}!
  Ke mona ho u thusa.                    = I am here to help you.
  Chelete ea hao ea jwale ke ...         = Your current money is ...
  Ho ntlafatsa kgwebo ea hao, ...        = To improve your business, ...
  Ke keletso ea ka ...                   = My advice is ...
  Hoa molemo hore ...                    = It is good that ...
  U ka etsa tsena kajeno:               = You can do these things today:
  Tsebo e bohlokoa:                      = Important information:
  Monyetla o moholo:                     = A great opportunity:
  Leka ho ...                            = Try to ...
  U se ke ua lebala ...                  = Don't forget ...
  Re tla sebetsa hammoho.               = We will work together.
  Ke a u tshepisa.                       = I trust you / You can do it.
  Matla a hao a maholo!                 = Your strength is great!

GREETINGS & ACKNOWLEDGEMENTS:
  "Kea leboha" or "Kea boka" = Thank you → reply: "Ke a lebohile! ..."
  "Dumela" = Hello → reply: "Dumela! ..."
  "O phela joang?" = How are you? → reply: "Ke phela hantle, ..."
  "Re bua ka eng?" = What are we talking about? → clarify in Sesotho

GRAMMAR REMINDERS:
  - Sesotho uses noun classes — don't invent random prefixes
  - Stick to simple, clear Sesotho that a township entrepreneur understands
  - When unsure of a specific technical term, use a simple Sesotho phrase instead of English
  - Numbers stay as numerals (R250, 30%) — no need to spell them out
  - Use "le" for "and", "empa" for "but", "hobane" for "because"

CULTURAL CONTEXT FOR SESOTHO SPEAKERS:
  - Many Sesotho speakers are in Johannesburg's south (Orange Farm, Evaton, Sebokeng),
    Bloemfontein, and Lesotho border areas
  - Common businesses: kotas, fatcakes (makrumpfies), hair salons, spaza shops
  - "Stockvel" is known as "molapo" or "motshelo" in Sesotho communities
  - Reference local shops: Shoprite, Boxer, PEP, Makro

CRITICAL RULE: If you cannot say something in Sesotho, simplify the idea
and say it in Sesotho. NEVER fall back to English sentences.
"""

        elif language == 'xh':
            return common + f"""
===============================================
ISIXHOSA LANGUAGE GUIDE - READ THIS CAREFULLY
===============================================
You MUST write your ENTIRE response in isiXhosa.
Do NOT write any English sentences. Do NOT mix languages mid-sentence.

CORE ISIXHOSA VOCABULARY FOR BUSINESS:
  Ishishini        = business
  Imali            = money
  Ukuthengisa      = selling / sales
  Ukuthenga        = to buy
  Abathengi        = customers
  Iimpahla         = goods / products
  Iindleko         = expenses / costs
  Inzuzo           = profit
  Ukulahlekelwa    = losses
  Imali engenayo   = income
  Imali ephuma     = expenses / outgoings
  Ukonga           = savings
  Ityala           = credit / debt
  Abanecala        = debtors
  Udidi            = category
  Uncedo           = help / support
  Ithuba           = opportunity
  Ingxaki          = problem
  Imali-mpho       = grant
  Ikhredithi       = loan / credit
  Intengiselwano   = transaction
  Umrholo          = income / earnings
  Umsebenzi        = work / business

COMMON ISIXHOSA PHRASES:
  Molo {first_name}!                     = Hello {first_name}!
  Ndikho apha ukukunceda.               = I am here to help you.
  Imali yakho yangoku yi-...            = Your current money is ...
  Ukhuthazeke!                          = Be encouraged!
  Ingcebiso yam yi-...                  = My advice is ...
  Ungenza ezi zinto namhlanje:          = You can do these things today:
  Gcina le nto engqondweni:             = Keep this in mind:
  Ithuba elikhulu:                      = A great opportunity:
  Zama ...                              = Try to ...
  Musa ukulibala ...                    = Don't forget ...

GREETINGS:
  "Enkosi" = Thank you → reply: "Hayi enkosi! ..."
  "Molo" = Hello → reply: "Molo! ..."
  "Unjani?" = How are you? → reply: "Ndiphilile, ..."
"""

        else:
            # English and isiZulu — original guidance
            zulu_block = ""
            if language == 'zu':
                zulu_block = """
ISIZULU PHRASES YOU CAN USE:
  Sawubona {first_name}!    = Hello {first_name}!
  Imali yakho manje ...    = Your money right now ...
  Iseluleko sami ...       = My advice is ...
  Ngiyabonga               = Thank you → reply in isiZulu
  Ungakwenza lokhu namhlanje: = You can do this today:
""".format(first_name=first_name)

            return common + f"""
LANGUAGE: {target_language}
- ALWAYS respond in {target_language}
- Detect the language of the question and mirror it exactly
- Use culturally appropriate greetings: "Sawubona" (Zulu), "Hello" (English)
- NEVER switch to English unless the user writes in English
{zulu_block}
Remember: You have access to {first_name}'s REAL business data. Use specific numbers and personalised advice!
"""
        
        return prompt
    
    def _detect_intent(self, question: str, language: str = 'en') -> str:
        """AI-powered intent detection using fast_model, with keyword fallback."""
        if self.api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                payload = {
                    "model": self.fast_model,
                    "messages": [{
                        "role": "user",
                        "content": (
                            "Classify this business question into exactly one label.\n"
                            "Labels: FUNDING_INQUIRY, SALES_ADVICE, FINANCIAL_ADVICE, SCORE_INQUIRY, GENERAL_INQUIRY\n"
                            f"Question: {question}\n"
                            "Reply with only the label, nothing else."
                        )
                    }],
                    "temperature": 0,
                    "max_tokens": 20,
                }
                resp = requests.post(self.base_url, headers=headers, json=payload, timeout=8)
                if resp.status_code == 200:
                    label = resp.json()['choices'][0]['message']['content'].strip().upper()
                    valid = {'FUNDING_INQUIRY', 'SALES_ADVICE', 'FINANCIAL_ADVICE', 'SCORE_INQUIRY', 'GENERAL_INQUIRY'}
                    if label in valid:
                        print(f"🎯 Intent (AI): {label}")
                        return label
            except Exception as e:
                print(f"⚠️  Fast-model intent failed, falling back to keywords: {e}")

        return self._detect_intent_keywords(question)

    def _detect_intent_keywords(self, question: str) -> str:
        """Keyword-based intent fallback across all four supported languages."""
        q = question.lower()

        funding_words = [
            # English
            'grant', 'loan', 'funding', 'money', 'capital', 'finance', 'invest',
            # isiZulu
            'imali', 'mali', 'ikhredithi', 'isikweletu', 'ithenda',
            # Sesotho
            'chelete', 'kadimo', 'liphihlelo', 'tefo', 'monyetla', 'thuso ea chelete',
            'ntlafatso', 'poloko',
            # isiXhosa
            'imali-mpho', 'ikhredithi', 'uncedo', 'ithuba',
        ]
        sales_words = [
            # English
            'sales', 'sell', 'customers', 'grow', 'market', 'product', 'price',
            # isiZulu
            'ukuthengisa', 'amakhasimende', 'ukukhula', 'izimpahla',
            # Sesotho
            'thekiso', 'rekisa', 'bareki', 'kholo', 'lihlahisoa', 'tlhahiso',
            'mmaraka', 'ithekeng', 'hola', 'ntlafatsa thekiso',
            # isiXhosa
            'ukuthengisa', 'abathengi', 'iimpahla', 'ukukhula',
        ]
        financial_words = [
            # English
            'cash', 'profit', 'expenses', 'balance', 'cost', 'loss', 'budget',
            # isiZulu
            'inzuzo', 'izindleko', 'ibhalansi', 'ukulahlekelwa',
            # Sesotho
            'phaello', 'litefiso', 'tjhelete e kenang', 'tjhelete e tsoang',
            'tshenyehelo', 'tekanyetso', 'bhalansi', 'lekgetho', 'mokoloto',
            # isiXhosa
            'inzuzo', 'iindleko', 'ukulahlekelwa', 'ibhalansi',
        ]
        score_words = [
            # English
            'score', 'credit', 'rating', 'empowerscore', 'tier', 'prime',
            # isiZulu
            'isikweletu', 'amanani', 'izinga',
            # Sesotho
            'manane', 'boemo', 'lekhetho', 'empowerscore', 'tekanyo',
            # isiXhosa
            'amanqaku', 'isigaba',
        ]

        if any(w in q for w in funding_words):
            return 'FUNDING_INQUIRY'
        elif any(w in q for w in sales_words):
            return 'SALES_ADVICE'
        elif any(w in q for w in financial_words):
            return 'FINANCIAL_ADVICE'
        elif any(w in q for w in score_words):
            return 'SCORE_INQUIRY'
        else:
            return 'GENERAL_INQUIRY'
    
    def _get_follow_up_suggestions(self, intent: str, language: str) -> list:
        """Get follow-up suggestions based on intent"""
        
        suggestions = {
            'FUNDING_INQUIRY': {
                'en': ["Which grant should I apply for?", "What documents do I need?", "How do I improve my chances?"],
                'zu': ["Yimuphi i-grant engifanele?", "Ngidinga maphi amaphepha?", "Ngingakwenza kanjani ngibe better?"],
                'st': ["Ke grant efe eo nka e kenyang?", "Ke hloka litokomane life?", "Nka ntlafatsa joang monyetla?"],
                'xh': ["Ngowuphi umxhaso?", "Ndidinga amaxwebhu aphi?", "Ndingayenza njani ibe ngcono?"]
            },
            'SALES_ADVICE': {
                'en': ["How do I attract more customers?", "Should I offer credit?", "What products sell best?"],
                'zu': ["Ngingakhanga kanjani amakhasimende?", "Ngingapha ikhredithi?", "Yini ethengiseka kahle?"],
                'st': ["Nka hohela bareki joang?", "Nka fa mokoloto?", "Ke eng e rekiswang hantle?"],
                'xh': ["Ndingatsala njani abathengi?", "Ndinganika ityala?", "Yintoni ethengiswa kakuhle?"]
            },
            'FINANCIAL_ADVICE': {
                'en': ["How can I reduce costs?", "Should I hire staff?", "What's good profit?"],
                'zu': ["Nginganciphisa izindleko?", "Ngingaqasha abantu?", "Inzuzo enkulu?"],
                'st': ["Nka fokotsa litjeno?", "Nka hira batho?", "Phaello e ntle?"],
                'xh': ["Ndinganciphisa iindleko?", "Ndingaqesha abantu?", "Yimalini enzuzo?"]
            },
            'SCORE_INQUIRY': {
                'en': ["How can I reach PRIME tier?", "What hurts my score?", "How long to improve?"],
                'zu': ["Ngingafinyelela kanjani PRIME?", "Yini elimaza i-score?", "Kuthatha isikhathi esingakanani?"],
                'st': ["Nka fihlella joang PRIME?", "Ke eng e senyang score?", "E nka nako e kae?"],
                'xh': ["Ndingafikelela njani PRIME?", "Yintoni emonakalisa?", "Kuthatha ixesha elingakanani?"]
            },
            'GENERAL_INQUIRY': {
                'en': ["Tell me about grants", "How to grow sales?", "What's my EmpowerScore?"],
                'zu': ["Ngitshele nge-grants", "Ngingakwandisa ukuthengisa?", "I-EmpowerScore yami?"],
                'st': ["Mpolelele ka grants", "Nka eketsa thekiso?", "EmpowerScore ea ka?"],
                'xh': ["Ndixelele nge-grants", "Ndingayandisa intengiso?", "I-EmpowerScore yam?"]
            }
        }
        
        return suggestions.get(intent, {}).get(language, suggestions[intent]['en'])


    def get_investment_insights(self, business_context: dict, scores: dict, market_context: dict = None) -> dict:
        """
        Generate a personalised investment-readiness narrative using advanced_model.

        Args:
            business_context: Full business context from BusinessIntelligence
            scores: dict with keys compliance, vault, funding, market, overall
            market_context: Optional supply chain & market access data from get_market_analysis

        Returns:
            dict: {'success': bool, 'insight': str, 'weeklyActions': list}
        """
        if not self.api_key:
            return {'success': False, 'error': 'OpenRouter API key not configured'}

        try:
            analytics   = business_context.get('analytics', {})
            biz_name    = business_context.get('businessName', 'your business')
            biz_type    = business_context.get('businessType', 'GENERAL').replace('_', ' ').title()
            location    = business_context.get('location', 'South Africa')
            cipc        = business_context.get('cipcRegistered', False)
            tax         = business_context.get('taxRegistered', False)
            revenue     = analytics.get('totalSales', 0)
            expenses    = analytics.get('totalExpenses', 0)
            profit      = analytics.get('profit', 0)
            tx_count    = analytics.get('transactionCount', 0)
            margin      = analytics.get('incomeVsExpenses', {}).get('profitMargin', 0)

            # Build optional market/supply-chain section
            market_section = ""
            if market_context:
                trend       = market_context.get('revenueTrend', {})
                cat_bd      = market_context.get('categoryBreakdown', [])
                tx_qual     = market_context.get('transactionQuality', {})
                sc_ready    = market_context.get('supplyChainReadiness', {})
                dow         = market_context.get('dayOfWeekPerformance', [])

                top_cat     = cat_bd[0]['category'] if cat_bd else 'Unknown'
                top_cat_rev = cat_bd[0]['revenue'] if cat_bd else 0
                digital_pct = tx_qual.get('digitalPercentage', 0)
                sc_score    = sc_ready.get('score', 0)
                trend_dir   = trend.get('direction', 'FLAT')
                trend_pct   = trend.get('percentageChange', 0)
                best_day    = max(dow, key=lambda d: d.get('avgRevenue', 0))['day'] if dow else 'Unknown'

                market_section = f"""
SUPPLY CHAIN & MARKET ACCESS (from Biz-Seed analytics):
- Revenue Trend: {trend_dir} ({'+' if trend_pct >= 0 else ''}{trend_pct:.1f}% vs last month)
- Best Trading Day: {best_day}
- Top Revenue Category: {top_cat} (R{top_cat_rev:,.2f})
- Digital Payment Adoption: {digital_pct:.0f}% of transactions
- Supply Chain Readiness Score: {sc_score}/100
"""

            prompt = f"""You are an expert investment-readiness advisor for South African township small businesses.

BUSINESS PROFILE:
- Name: {biz_name} ({biz_type})
- Location: {location}
- CIPC Registered: {'Yes' if cipc else 'No'}
- SARS Tax Registered: {'Yes' if tax else 'No'}

FINANCIAL SNAPSHOT (last 30 days):
- Revenue:    R{revenue:,.2f}
- Expenses:   R{expenses:,.2f}
- Profit:     R{profit:,.2f}
- Margin:     {margin:.1f}%
- Transactions: {tx_count}
{market_section}
INVESTMENT READINESS SCORES (out of 100):
- Compliance:      {scores.get('compliance', 0)}
- Investor Vault:  {scores.get('vault', 0)}
- Funding Access:  {scores.get('funding', 0)}
- Market Access:   {scores.get('market', 0)}
- OVERALL:         {scores.get('overall', 0)}

TASK:
1. Write a 3-sentence personalised summary of where this business stands on its investment-readiness journey. Reference actual numbers including revenue trend and supply chain score if available. Be warm, honest, and South African in tone.
2. List exactly 3 specific actions the owner can take THIS WEEK (not someday) to improve their score. Each action must be concrete and achievable — e.g. "Go to cipc.co.za and start the Name Reservation step (R50 fee)" not just "Register with CIPC". Actions should align with what is shown in their Biz-Seed supply chain and funding pillars.

FORMAT your response as JSON with this exact structure:
{{
  "summary": "<3-sentence narrative>",
  "weeklyActions": [
    {{"action": "<what to do>", "why": "<why it matters / impact>", "effort": "LOW|MEDIUM|HIGH"}},
    {{"action": "<what to do>", "why": "<why it matters / impact>", "effort": "LOW|MEDIUM|HIGH"}},
    {{"action": "<what to do>", "why": "<why it matters / impact>", "effort": "LOW|MEDIUM|HIGH"}}
  ]
}}"""

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://mzansipulse.app",
                "X-Title": "MzansiPulse Biz-Seed",
            }
            payload = {
                "model": self.advanced_model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.5,
                "max_tokens": 600,
                "response_format": {"type": "json_object"},
            }

            print(f"🧠 Calling advanced model ({self.advanced_model}) for investment insights...")
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=25)

            if response.status_code != 200:
                print(f"❌ Advanced model error: {response.status_code} — {response.text}")
                return {'success': False, 'error': f'API error {response.status_code}'}

            import json as _json
            raw = response.json()['choices'][0]['message']['content']
            parsed = _json.loads(raw)

            print(f"✅ Investment insights generated")
            return {
                'success': True,
                'summary': parsed.get('summary', ''),
                'weeklyActions': parsed.get('weeklyActions', []),
                'model': self.advanced_model,
            }

        except Exception as e:
            print(f"❌ Investment insights error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}


# ════════════════════════════════════════════════════════════════════════════
# TEST FUNCTION
# ════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """Test OpenRouter AI"""
    
    from dotenv import load_dotenv
    load_dotenv()
    
    print("=" * 80)
    print("🤖 Testing OpenRouter AI Integration")
    print("=" * 80)
    
    ai = OpenRouterHelper()
    
    # Test context
    user_context = {
        'firstName': 'Lerato',
        'businessName': 'Lerato Home Salon',
        'businessType': 'HOME_SALON',
        'location': 'Orange Farm, Gauteng',
        'wallet': {
            'totalBalance': 2500.00,
            'cashBalance': 2300.00,
            'digitalBalance': 200.00,
            'creditOwed': 150.00
        },
        'analytics': {
            'averageDailySales': 350.00,
            'transactionCount': 67,
            'cashVsDigital': {'cashPercentage': 92},
            'incomeVsExpenses': {'profit': 1200.00}
        }
    }
    
    # Test questions
    questions = [
        ("How can I grow my salon business?", "en"),
        ("Ke nyulosa chelete ea kgwebo joang?", "st"),
        ("Ngifuna ukwazi ngezimali", "zu"),
    ]
    
    for question, lang in questions:
        print(f"\n{'='*80}")
        print(f"❓ Question: {question}")
        print(f"🗣️  Language: {lang}")
        print(f"{'='*80}")
        
        response = ai.get_business_advice(question, user_context, lang)
        
        if response['success']:
            print(f"\n💬 AI Response:\n{response['response']}")
            print(f"\n💡 Suggestions: {response['suggestions']}")
            print(f"🤖 Model: {response.get('model')}")
        else:
            print(f"\n❌ Error: {response.get('error')}")
    
    print("\n" + "=" * 80)
    print("✅ OpenRouter AI Test Complete!")
    print("=" * 80)