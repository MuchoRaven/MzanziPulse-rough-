"""
Biz-Seed Investment Readiness API
The 4 Pillars: Compliance, Investor-Ready Vault, Funding Matching, Market Access
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from db import get_db

load_dotenv()

bizseed_bp = Blueprint('bizseed', __name__, url_prefix='/api/bizseed')

# ═══════════════════════════════════════════════════════════════════════════
# PILLAR 1: COMPLIANCE & FORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════

@bizseed_bp.route('/compliance/status/<int:user_id>', methods=['GET'])
def get_compliance_status(user_id):
    """
    Get business compliance status
    Checks: CIPC Registration, SARS Tax, B-BBEE, POPIA
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get business info
        cursor.execute('''
            SELECT b.*, u.email, u.phone_number
            FROM businesses b
            JOIN users u ON b.user_id = u.user_id
            WHERE b.user_id = %s
        ''', (user_id,))
        
        business = cursor.fetchone()
        
        if not business:
            return jsonify({'success': False, 'error': 'Business not found'}), 404
        
        # Mock compliance data (you'll replace with real API checks)
        compliance_status = {
            'cipc': {
                'status': 'NOT_REGISTERED',
                'registrationNumber': None,
                'entityType': None,
                'action': 'Register your business with CIPC',
                'urgency': 'HIGH',
                'estimatedCost': 'R175 - R500',
                'estimatedTime': '2-5 business days'
            },
            'sars': {
                'status': 'NOT_REGISTERED',
                'taxNumber': None,
                'taxClearance': None,
                'taxClearanceExpiry': None,
                'action': 'Register for Income Tax',
                'urgency': 'HIGH',
                'nextDeadline': None
            },
            'bbbee': {
                'status': 'NOT_STARTED',
                'level': None,
                'affidavitValid': False,
                'action': 'Get EME Affidavit (R0 - R10M turnover)',
                'urgency': 'MEDIUM',
                'estimatedCost': 'R500 - R2,000'
            },
            'popia': {
                'status': 'PARTIAL',
                'consentFormsInPlace': False,
                'dataProtectionOfficer': None,
                'action': 'Implement customer consent system',
                'urgency': 'MEDIUM',
                'estimatedCost': 'R0 (DIY Template)'
            },
            'coida': {
                'status': 'NOT_APPLICABLE',
                'registered': False,
                'action': 'Register when you hire first employee',
                'urgency': 'LOW'
            },
            'overallScore': 15,  # Out of 100
            'readinessLevel': 'INFORMAL',  # INFORMAL, PARTIALLY_FORMAL, FORMAL, INVESTOR_READY
            'nextSteps': [
                'Register with CIPC as PTY Ltd',
                'Apply for SARS Tax Number',
                'Get basic POPIA consent forms'
            ]
        }
        
        conn.close()
        
        return jsonify({
            'success': True,
            'compliance': compliance_status
        }), 200
        
    except Exception as e:
        print(f"❌ Compliance status error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# PILLAR 2: INVESTOR-READY VAULT
# ═══════════════════════════════════════════════════════════════════════════

@bizseed_bp.route('/vault/documents/<int:user_id>', methods=['GET'])
def get_vault_documents(user_id):
    """
    Get all investor-ready documents
    """
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get business analytics for document generation
        cursor.execute('''
            SELECT 
                b.business_name,
                b.business_type,
                COUNT(DISTINCT ct.cash_transaction_id) as transaction_count,
                SUM(CASE WHEN ct.transaction_type IN ('CASH_IN', 'DIGITAL_IN') 
                    THEN ct.amount_cents ELSE 0 END) as total_revenue,
                SUM(CASE WHEN ct.transaction_type = 'CASH_OUT' 
                    THEN ct.amount_cents ELSE 0 END) as total_expenses
            FROM businesses b
            LEFT JOIN cash_wallets cw ON b.business_id = cw.business_id
            LEFT JOIN cash_transactions ct ON cw.wallet_id = ct.wallet_id
            WHERE b.user_id = %s
            GROUP BY b.business_id, b.business_name, b.business_type
        ''', (user_id,))
        
        business_data = cursor.fetchone()
        conn.close()
        
        if not business_data:
            return jsonify({'success': False, 'error': 'Business not found'}), 404
        
        # Calculate key metrics
        revenue = business_data['total_revenue'] / 100 if business_data['total_revenue'] else 0
        expenses = business_data['total_expenses'] / 100 if business_data['total_expenses'] else 0
        profit = revenue - expenses
        
        # Available documents
        documents = {
            'pitchDeck': {
                'name': 'Investor Pitch Deck',
                'status': 'READY',
                'format': 'PowerPoint',
                'lastUpdated': datetime.now().isoformat(),
                'canGenerate': True,
                'description': f'Professional pitch deck for {business_data["business_name"]}'
            },
            'financialStatements': {
                'name': 'Financial Statements',
                'status': 'READY',
                'format': 'PDF',
                'includes': ['Income Statement', 'Balance Sheet', 'Cash Flow'],
                'lastUpdated': datetime.now().isoformat(),
                'canGenerate': True
            },
            'businessPlan': {
                'name': 'Business Plan',
                'status': 'DRAFT',
                'format': 'Word Document',
                'lastUpdated': None,
                'canGenerate': True,
                'description': 'Full 15-page business plan'
            },
            'growthForecast': {
                'name': 'Growth Forecast Model',
                'status': 'READY',
                'format': 'Excel',
                'period': '12 months',
                'lastUpdated': datetime.now().isoformat(),
                'canGenerate': True
            }
        }
        
        # Vault summary
        vault_summary = {
            'documents': documents,
            'readinessScore': 65,  # Out of 100
            'missingDocuments': ['Proof of Address', 'Bank Statements (6 months)'],
            'keyMetrics': {
                'monthlyRevenue': revenue,
                'monthlyExpenses': expenses,
                'monthlyProfit': profit,
                'profitMargin': (profit / revenue * 100) if revenue > 0 else 0,
                'transactionCount': business_data['transaction_count']
            }
        }
        
        return jsonify({
            'success': True,
            'vault': vault_summary
        }), 200
        
    except Exception as e:
        print(f"❌ Vault error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@bizseed_bp.route('/vault/generate/pitch-deck', methods=['POST'])
def generate_pitch_deck():
    """Generate a real PowerPoint pitch deck using business data from the DB."""
    try:
        data = request.json
        user_id = data.get('userId')

        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400

        # Fetch business data
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                b.business_name, b.business_type,
                b.township, b.province,
                u.first_name, u.last_name,
                COUNT(DISTINCT ct.cash_transaction_id)                                  AS transaction_count,
                SUM(CASE WHEN ct.transaction_type IN ('CASH_IN', 'DIGITAL_IN')
                         THEN ct.amount_cents ELSE 0 END)                               AS total_revenue,
                SUM(CASE WHEN ct.transaction_type = 'CASH_OUT'
                         THEN ct.amount_cents ELSE 0 END)                               AS total_expenses,
                AVG(CASE WHEN ct.transaction_type IN ('CASH_IN', 'DIGITAL_IN')
                         THEN ct.amount_cents ELSE NULL END)                            AS avg_daily_revenue
            FROM businesses b
            JOIN users u ON b.user_id = u.user_id
            LEFT JOIN cash_wallets cw ON b.business_id = cw.business_id
            LEFT JOIN cash_transactions ct ON cw.wallet_id = ct.wallet_id
            WHERE b.user_id = %s
            GROUP BY b.business_id, b.business_name, b.business_type,
                     b.township, b.province, u.user_id, u.first_name, u.last_name
        ''', (user_id,))

        business = cursor.fetchone()
        conn.close()

        if not business:
            return jsonify({'success': False, 'error': 'Business not found'}), 404

        revenue  = (business['total_revenue']  or 0) / 100
        expenses = (business['total_expenses'] or 0) / 100
        location = f"{business['township'] or ''}, {business['province'] or ''}".strip(', ')

        doc_data = {
            'userId':          user_id,
            'businessName':    business['business_name'],
            'businessType':    business['business_type'] or 'GENERAL',
            'location':        location or 'South Africa',
            'ownerName':       f"{business['first_name']} {business['last_name']}".strip(),
            'revenue':         revenue,
            'expenses':        expenses,
            'profit':          revenue - expenses,
            'transactionCount': business['transaction_count'] or 0,
            'dailySales':      (business['avg_daily_revenue'] or 0) / 100,
        }

        from document_generator import DocumentGenerator
        generator = DocumentGenerator()
        filename = generator.generate_pitch_deck(doc_data)

        return jsonify({
            'success':  True,
            'filename': filename,
            'downloadUrl': f'/api/bizseed/downloads/{filename}',
            'message':  'Pitch deck generated successfully'
        }), 200

    except Exception as e:
        print(f"❌ Pitch deck generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bizseed_bp.route('/vault/generate/financials', methods=['POST'])
def generate_financials():
    """Generate financial statements PDF"""
    try:
        data = request.json
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        # Get business data
        from business_intelligence import BusinessIntelligence
        bi = BusinessIntelligence()
        business_context = bi.get_user_business_context(user_id)
        
        if 'error' in business_context:
            return jsonify({'success': False, 'error': 'Business not found'}), 404
        
        # Prepare data for document generator
        doc_data = {
            'userId': user_id,
            'businessName': business_context['businessName'],
            'revenue': business_context['analytics']['totalSales'],
            'expenses': business_context['analytics']['totalExpenses'],
            'profit': business_context['analytics']['profit']
        }
        
        # Generate document
        from document_generator import DocumentGenerator
        generator = DocumentGenerator()
        filename = generator.generate_financial_statements(doc_data)

        return jsonify({
            'success': True,
            'filename': filename,
            'downloadUrl': f'/api/bizseed/downloads/{filename}',
            'message': 'Financial statements generated'
        }), 200
        
    except Exception as e:
        print(f"❌ Financials generation error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bizseed_bp.route('/vault/generate/business-plan', methods=['POST'])
def generate_business_plan():
    """Generate a structured business plan PDF."""
    try:
        data = request.json
        user_id = data.get('userId')

        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400

        from business_intelligence import BusinessIntelligence
        bi = BusinessIntelligence()
        business_context = bi.get_user_business_context(user_id)

        if 'error' in business_context:
            return jsonify({'success': False, 'error': 'Business not found'}), 404

        doc_data = {
            'userId':          user_id,
            'businessName':    business_context['businessName'],
            'businessType':    business_context.get('businessType', 'GENERAL'),
            'location':        business_context.get('location', 'South Africa'),
            'ownerName':       business_context.get('ownerName', ''),
            'revenue':         business_context['analytics']['totalSales'],
            'expenses':        business_context['analytics']['totalExpenses'],
            'profit':          business_context['analytics']['profit'],
            'transactionCount': business_context['analytics']['transactionCount'],
        }

        from document_generator import DocumentGenerator
        generator = DocumentGenerator()
        filename = generator.generate_business_plan(doc_data)

        return jsonify({
            'success':     True,
            'filename':    filename,
            'downloadUrl': f'/api/bizseed/downloads/{filename}',
            'message':     'Business plan generated successfully'
        }), 200

    except Exception as e:
        print(f"❌ Business plan error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@bizseed_bp.route('/vault/generate/forecast', methods=['POST'])
def generate_forecast():
    """Generate growth forecast Excel"""
    try:
        data = request.json
        user_id = data.get('userId')
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        # Get historical data
        from business_intelligence import BusinessIntelligence
        bi = BusinessIntelligence()
        business_context = bi.get_user_business_context(user_id)
        
        # Prepare data
        doc_data = {
            'userId': user_id,
            'businessName': business_context['businessName'],
            'revenue': business_context['analytics']['totalSales'],
            'expenses': business_context['analytics']['totalExpenses'],
            'profit': business_context['analytics']['profit']
        }
        
        # Generate forecast
        from document_generator import DocumentGenerator
        generator = DocumentGenerator()
        filename = generator.generate_growth_forecast(doc_data)

        return jsonify({
            'success': True,
            'filename': filename,
            'downloadUrl': f'/api/bizseed/downloads/{filename}',
            'message': 'Growth forecast generated'
        }), 200
        
    except Exception as e:
        print(f"❌ Forecast error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def get_db_path():
    """Legacy — kept for any remaining references."""
    return "Supabase PostgreSQL"


# ═══════════════════════════════════════════════════════════════════════════
# FILE DOWNLOADS
# ═══════════════════════════════════════════════════════════════════════════

@bizseed_bp.route('/downloads/<path:filename>', methods=['GET'])
def download_document(filename):
    """Serve a generated document from the downloads/bizseed directory."""
    try:
        downloads_dir = os.path.abspath(os.path.join('..', 'downloads', 'bizseed'))
        filepath = os.path.join(downloads_dir, filename)

        # Security: ensure the resolved path stays inside downloads_dir
        if not os.path.abspath(filepath).startswith(downloads_dir):
            return jsonify({'error': 'Forbidden'}), 403

        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404

        return send_file(filepath, as_attachment=True, download_name=filename)

    except Exception as e:
        print(f"❌ Download error: {e}")
        return jsonify({'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# PILLAR 3: FUNDING & GRANT MATCHING
# ═══════════════════════════════════════════════════════════════════════════

@bizseed_bp.route('/grants/matches/<int:user_id>', methods=['GET'])
def get_grant_matches(user_id):
    """
    Find grants the business qualifies for — personalised to this user's
    actual age, gender, location, turnover, and formalisation status.
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        # ── Step 1: fetch user + business profile ──────────────────────────
        # Fix: pull u.date_of_birth + u.gender in a separate scalar select,
        # then do the aggregate separately to avoid GROUP BY explosion.
        cursor.execute('''
            SELECT
                b.business_id,
                b.business_name,
                b.business_type,
                b.province,
                b.township,
                b.cipc_registered,
                b.tax_number,
                b.vat_registered,
                b.verification_status,
                b.employee_count,
                u.date_of_birth,
                u.gender
            FROM businesses b
            JOIN users u ON b.user_id = u.user_id
            WHERE b.user_id = %s
        ''', (user_id,))

        business = cursor.fetchone()

        if not business:
            conn.close()
            return jsonify({'success': False, 'error': 'Business not found'}), 404

        # ── Step 2: annual turnover (last 12 months from transactions) ──────
        cursor.execute('''
            SELECT COALESCE(SUM(ct.amount_cents), 0) as annual_turnover_cents
            FROM cash_transactions ct
            JOIN cash_wallets cw ON ct.wallet_id = cw.wallet_id
            WHERE cw.business_id = %s
              AND ct.transaction_type IN ('CASH_IN', 'DIGITAL_IN')
              AND ct.transaction_date >= CURRENT_DATE - INTERVAL '365 days'
        ''', (business['business_id'],))

        turnover_row = cursor.fetchone()
        conn.close()

        annual_turnover = float(turnover_row['annual_turnover_cents'] or 0) / 100
        monthly_turnover = annual_turnover / 12

        # ── Step 3: derive profile fields ──────────────────────────────────
        from datetime import date as date_type
        import re

        # Age from date_of_birth
        age = None
        dob_raw = business['date_of_birth']
        if dob_raw:
            try:
                dob_str = str(dob_raw)[:10]   # handles date objects and strings
                dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
                today = date_type.today()
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            except Exception:
                pass

        gender = (business['gender'] or '').strip().lower()   # 'male' / 'female'
        is_female = gender == 'female'
        is_youth  = age is not None and age <= 35

        province  = business['province'] or ''
        township  = business['township'] or ''
        is_township = bool(township)   # all our demo users are in townships

        is_cipc      = bool(business['cipc_registered'])
        has_tax      = bool(business['tax_number'])
        is_vat       = bool(business['vat_registered'])
        is_formal    = is_cipc and has_tax
        biz_type     = (business['business_type'] or '').lower()
        employees    = int(business['employee_count'] or 1)

        # ── Step 4: grant catalogue ─────────────────────────────────────────
        # Sources: NYDA, SEDFA, NEF, DSBD, TEF official websites (verified 2025/2026)
        # fundingType: GRANT (non-repayable) | LOAN (must repay) | REVENUE_ADVANCE (repay from sales)
        # checks: list of (condition_passes, points, fail_message)
        grants_catalogue = [
            # ── TIER 1: GENUINELY ACCESSIBLE TO INFORMAL/MICRO ENTREPRENEURS ──
            {
                'id': 1,
                'name': 'NYDA Business Grant',
                'provider': 'National Youth Development Agency',
                'fundingType': 'GRANT',
                'amount': {'min': 1000, 'max': 200000},
                'deadlineLabel': 'Rolling — apply year-round',
                'applicationUrl': 'https://erp.nyda.gov.za',
                'description': (
                    'Non-repayable grant for SA youth entrepreneurs aged 18–35. '
                    'Micro tier (R1,000–R50,000) does not require CIPC registration. '
                    'Free NYDA business training must be completed before funds are released.'
                ),
                'notes': (
                    'This is a genuine grant — you do not pay it back. '
                    'Apply only at erp.nyda.gov.za. '
                    'WARNING: Viral posts claiming an R12,500 government grant are a scam — '
                    'confirmed false by both SASSA and NYDA.'
                ),
                'tags': ['Non-repayable', 'Youth 18–35', 'Any sector'],
                'checks': [
                    (is_youth, 50, f'Must be aged 18–35 at time of application (your age: {age})'),
                    (annual_turnover <= 750_000, 30, f'Turnover must be under R750,000/yr (yours: R{annual_turnover:,.0f}/yr)'),
                    (True, 20, None),
                ],
            },
            {
                'id': 2,
                'name': 'DSBD Spaza Shop Support Fund',
                'provider': 'Dept. of Small Business Development',
                'fundingType': 'GRANT',
                'amount': {'min': 40000, 'max': 80000},
                'deadlineLabel': 'Rolling — apply at spazashopfund.co.za',
                'applicationUrl': 'https://www.spazashopfund.co.za',
                'description': (
                    'R40,000 non-repayable stock grant plus up to R40,000 in equipment/infrastructure '
                    'support for township spaza shops and informal retailers. '
                    'Registered businesses can access up to R300,000 (blended grant and loan). '
                    'A municipal business licence is required before disbursement.'
                ),
                'notes': (
                    'R500 million has been allocated by government. '
                    'As of late 2025 only R6.3M of R150M budgeted has been disbursed due to '
                    'municipal licensing delays — apply now but expect 4–12 weeks for licence processing. '
                    'Call 011 305 8080 for assistance.'
                ),
                'tags': ['Non-repayable', 'Spaza/Retail', 'Township'],
                'checks': [
                    (is_township, 50, 'Business must operate in a township or informal settlement'),
                    (annual_turnover <= 1_000_000, 30, f'Fund targets micro-retailers (yours: R{annual_turnover:,.0f}/yr)'),
                    (True, 20, None),
                ],
            },
            {
                'id': 3,
                'name': 'SEDFA Micro Finance (via MFIs)',
                'provider': 'Small Enterprise Development & Finance Agency',
                'fundingType': 'LOAN',
                'amount': {'min': 500, 'max': 50000},
                'deadlineLabel': 'Rolling — apply year-round',
                'applicationUrl': 'https://www.sedfa.org.za',
                'description': (
                    'Low-interest micro loans (8–12% p.a., far below bank rates of 15–20%) '
                    'for micro and survivalist businesses at any formalisation level. '
                    'Accessed through local Micro Finance Intermediary (MFI) partners. '
                    'CIPC registration is NOT required for this tier.'
                ),
                'notes': (
                    'This is a loan — repayment is required. '
                    'SEFA merged with SEDA and CBDA to form SEDFA in October 2024 — '
                    'sefa.org.za still works but sedfa.org.za is the current entity. '
                    'Call 012 748 9600 to find your nearest MFI partner.'
                ),
                'tags': ['Loan', 'Any formality level', 'Any sector'],
                'checks': [
                    (monthly_turnover >= 500, 60, f'Need at least R500/month in revenue (yours: R{monthly_turnover:,.0f}/mo)'),
                    (True, 40, None),
                ],
            },
            {
                'id': 4,
                'name': 'Tony Elumelu Foundation Grant',
                'provider': 'Tony Elumelu Foundation (Pan-African)',
                'fundingType': 'GRANT',
                'amount': {'min': 90000, 'max': 90000},
                'deadlineLabel': 'Next cycle opens January 2027 at tefconnect.com',
                'applicationUrl': 'https://tefconnect.com',
                'description': (
                    'USD $5,000 (~R90,000) non-repayable seed grant for African entrepreneurs, '
                    'plus free 12-week online business training and 1-on-1 mentorship. '
                    'Open to ALL South Africans — no CIPC required, no sector restriction, no age limit.'
                ),
                'notes': (
                    'The 2026 application window closed March 2026. '
                    'The 2027 cycle opens approximately January 2027 — set a reminder and prepare your application early. '
                    'This is one of the most accessible non-repayable grants on the continent. '
                    'Tens of thousands apply each cycle from across Africa.'
                ),
                'tags': ['Non-repayable', 'Pan-African', 'Any sector', 'Opens Jan 2027'],
                'checks': [
                    (True, 60, None),
                    (annual_turnover <= 5_000_000, 40, f'Aimed at micro-to-small enterprises (yours: R{annual_turnover:,.0f}/yr)'),
                ],
            },
            # ── TIER 2: REQUIRES SOME FORMALITY ─────────────────────────────
            {
                'id': 5,
                'name': 'SEDFA Small Business Loan',
                'provider': 'Small Enterprise Development & Finance Agency',
                'fundingType': 'LOAN',
                'amount': {'min': 50000, 'max': 1_000_000},
                'deadlineLabel': 'Rolling — apply year-round',
                'applicationUrl': 'https://www.sedfa.org.za',
                'description': (
                    'Below-market-rate loans (8–12% p.a.) for formally registered SMEs '
                    'with a trading track record. Requires CIPC registration, tax number, '
                    'a written business plan, and 3–6 months of bank statements.'
                ),
                'notes': (
                    'This is a loan — repayment is required. '
                    'You need a fixed business address, proof of trading history, and collateral '
                    'may be required for larger amounts. Contact SEDFA at 012 748 9600 or helpline@sefa.org.za.'
                ),
                'tags': ['Loan', 'Formal required', 'Growth stage'],
                'checks': [
                    (is_formal, 40, 'Business must be CIPC-registered with a valid tax number'),
                    (annual_turnover >= 60_000, 35, f'Need at least R5,000/month trading history (yours: R{monthly_turnover:,.0f}/mo)'),
                    (True, 25, None),
                ],
            },
            {
                'id': 6,
                'name': 'SEDFA Cooperative Incentive Scheme',
                'provider': 'Small Enterprise Development & Finance Agency',
                'fundingType': 'GRANT',
                'amount': {'min': 50000, 'max': 350000},
                'deadlineLabel': 'Rolling — apply year-round',
                'applicationUrl': 'https://www.sedfa.org.za',
                'description': (
                    '90:10 matching grant for registered primary cooperatives — SEDFA pays 90%, '
                    'the co-op contributes only 10%. For equipment, machinery, tools, or working capital. '
                    'Cooperative must be black-majority owned and CIPC-registered under the Cooperatives Act.'
                ),
                'notes': (
                    'This grant requires that your business is structured as a registered cooperative (not a sole trader or Pty Ltd). '
                    'Groups of township entrepreneurs who pool their businesses into a co-op can access this together. '
                    'SEDFA covers 90% — you only need to contribute 10%.'
                ),
                'tags': ['Non-repayable (90%)', 'Co-ops only', 'Black-majority owned'],
                'checks': [
                    (is_formal, 40, 'Cooperative must be CIPC-registered under the Cooperatives Act'),
                    (employees >= 2, 35, f'Cooperatives need at least 2 members (yours: {employees})'),
                    (True, 25, None),
                ],
            },
            {
                'id': 7,
                'name': 'Yoco Capital',
                'provider': 'Yoco Technologies (Private)',
                'fundingType': 'REVENUE_ADVANCE',
                'amount': {'min': 1000, 'max': 1_000_000},
                'deadlineLabel': 'Rolling — apply through your Yoco dashboard',
                'applicationUrl': 'https://www.yoco.com/za/yoco-capital/',
                'description': (
                    'Revenue-based cash advance for existing Yoco card machine merchants. '
                    'Amount is based on your card transaction history. '
                    'Repaid automatically as a small percentage of future card sales — '
                    'no fixed monthly payment, no CIPC required.'
                ),
                'notes': (
                    'This is a revenue advance — repayment is required from future card sales. '
                    'You must already be processing card payments through a Yoco device. '
                    'Adopting card payments through Yoco is a fast path to unlocking this funding. '
                    'No minimum turnover threshold is published — offer is based on actual Yoco transaction history.'
                ),
                'tags': ['Revenue advance', 'Yoco merchants only', 'Fast approval'],
                'checks': [
                    (monthly_turnover >= 3000, 60, f'Need meaningful monthly card transactions (yours: R{monthly_turnover:,.0f}/mo)'),
                    (True, 40, None),
                ],
            },
            # ── TIER 3: ESTABLISHED / HIGHER-TURNOVER BUSINESSES ─────────────
            {
                'id': 8,
                'name': 'NEF Imbewu Fund',
                'provider': 'National Empowerment Fund',
                'fundingType': 'LOAN',
                'amount': {'min': 250000, 'max': 10_000_000},
                'deadlineLabel': 'Rolling — apply year-round',
                'applicationUrl': 'https://www.nefcorp.co.za',
                'description': (
                    'Loan and equity finance for black-owned SA businesses at start-up or early growth stage. '
                    'Minimum 50.1% black ownership required. '
                    'Hard minimum deal size is R250,000 — not a programme for micro or informal businesses.'
                ),
                'notes': (
                    'This is a loan (with some equity options) — repayment is required. '
                    'You need CIPC registration, tax clearance, audited or management accounts, '
                    'and a detailed business plan demonstrating repayment capacity. '
                    'R250,000 is a hard floor — not suitable for survivalist or informal operators.'
                ),
                'tags': ['Loan/Equity', 'Black-owned 51%+', 'Formal required', 'R250K minimum'],
                'checks': [
                    (is_formal, 35, 'Business must be CIPC-registered with a tax number'),
                    (annual_turnover >= 300_000, 40, f'Need ~R300K+/yr turnover for minimum deal (yours: R{annual_turnover:,.0f}/yr)'),
                    (employees >= 2, 25, f'Must demonstrate employment creation (yours: {employees} employees)'),
                ],
            },
            {
                'id': 9,
                'name': 'NEF Women Empowerment Fund',
                'provider': 'National Empowerment Fund',
                'fundingType': 'LOAN',
                'amount': {'min': 250000, 'max': 75_000_000},
                'deadlineLabel': 'Rolling — apply year-round',
                'applicationUrl': 'https://www.nefcorp.co.za/products-services/',
                'description': (
                    'NEF financing prioritising businesses with 51%+ black women ownership. '
                    'Same structure as the Imbewu Fund with additional priority for women-led businesses. '
                    'R250,000 minimum. Requires CIPC registration and formal financial records.'
                ),
                'notes': (
                    'This is a loan — repayment is required. '
                    'The R250,000 minimum is a hard floor. Best for established women entrepreneurs '
                    'looking to scale, not for micro or informal start-ups.'
                ),
                'tags': ['Loan/Equity', 'Women-owned 51%+', 'Formal required', 'R250K minimum'],
                'checks': [
                    (is_female, 40, 'Business must be 51%+ black women-owned'),
                    (is_formal, 35, 'Business must be CIPC-registered with a tax number'),
                    (annual_turnover >= 300_000, 25, f'Need ~R300K+/yr turnover (yours: R{annual_turnover:,.0f}/yr)'),
                ],
            },
            {
                'id': 10,
                'name': 'Lula (Lulalend) Business Loan',
                'provider': 'Lula / Lulalend (Private Fintech)',
                'fundingType': 'LOAN',
                'amount': {'min': 10000, 'max': 5_000_000},
                'deadlineLabel': 'Rolling — 48-hour approval',
                'applicationUrl': 'https://www.lula.co.za',
                'description': (
                    'Fast online business loans approved within 48 hours '
                    'for businesses with at least R40,000/month turnover and 12 months of trading history. '
                    'Requires 3 months of bank statements. Repayment over 3–12 months at 5–12% fee.'
                ),
                'notes': (
                    'This is a loan — repayment is required. '
                    'R40,000/month (R480,000/year) is a hard minimum — cash-only businesses '
                    'without formal bank statements cannot access this. '
                    'Lulalend is now part of the Yoco ecosystem and branded as "Lula".'
                ),
                'tags': ['Loan', 'Fast approval (48 hrs)', 'R40K/month minimum'],
                'checks': [
                    (monthly_turnover >= 40_000, 70, f'Need at least R40,000/month turnover (yours: R{monthly_turnover:,.0f}/mo)'),
                    (True, 30, None),
                ],
            },
            {
                'id': 11,
                'name': 'Business Partners Limited',
                'provider': 'Business Partners (Private)',
                'fundingType': 'LOAN',
                'amount': {'min': 500000, 'max': 50_000_000},
                'deadlineLabel': 'Rolling — apply year-round',
                'applicationUrl': 'https://www.businesspartners.co.za',
                'description': (
                    'Tailored loan and equity financing for established owner-managed businesses, '
                    'with mentorship and technical assistance included. '
                    'Minimum R500,000. Requires CIPC registration, audited accounts, and collateral.'
                ),
                'notes': (
                    'Repayment is required. This is for established entrepreneurs who have grown beyond micro stage. '
                    'You need full CIPC registration, audited financials, and a viable business plan '
                    'demonstrating repayment capacity. Not suitable for survivalist or start-up businesses.'
                ),
                'tags': ['Loan/Equity', 'Established businesses', 'R500K minimum'],
                'checks': [
                    (is_formal, 35, 'Business must be formally registered (CIPC)'),
                    (annual_turnover >= 500_000, 40, f'Need at least R500K/yr turnover (yours: R{annual_turnover:,.0f}/yr)'),
                    (employees >= 1, 25, f'Must have at least 1 full-time employee (yours: {employees})'),
                ],
            },
        ]

        # ── Step 5: score each grant ────────────────────────────────────────
        matched_grants = []

        for grant in grants_catalogue:
            total_points   = 0
            earned_points  = 0
            fail_reasons   = []
            pass_reasons   = []

            for (passes, points, fail_msg) in grant['checks']:
                total_points += points
                if passes:
                    earned_points += points
                else:
                    if fail_msg:
                        fail_reasons.append(fail_msg)

            match_pct = int((earned_points / total_points) * 100) if total_points else 0
            eligible  = len(fail_reasons) == 0

            # Build why-you-qualify list from passing checks
            if eligible:
                if is_youth:
                    pass_reasons.append(f'You qualify as a youth entrepreneur (age {age})')
                if is_female:
                    pass_reasons.append('Women-owned business qualifies')
                if is_township:
                    pass_reasons.append(f'Operating in {township} township')
                if is_formal:
                    pass_reasons.append('CIPC registered and tax compliant')
                if annual_turnover > 0:
                    pass_reasons.append(f'Annual turnover R{annual_turnover:,.0f} meets requirements')

            grant_out = {
                'id':             grant['id'],
                'name':           grant['name'],
                'provider':       grant['provider'],
                'fundingType':    grant['fundingType'],
                'amount':         grant['amount'],
                'deadlineLabel':  grant['deadlineLabel'],
                'applicationUrl': grant['applicationUrl'],
                'description':    grant['description'],
                'notes':          grant.get('notes', ''),
                'tags':           grant['tags'],
                'match':          match_pct,
                'eligible':       eligible,
                'qualifyReasons': pass_reasons,
                'failReasons':    fail_reasons,
            }

            if match_pct >= 40:   # show grants where at least 40% criteria are met
                matched_grants.append(grant_out)

        matched_grants.sort(key=lambda x: x['match'], reverse=True)

        # ── Step 6: profile summary for the frontend ────────────────────────
        profile_summary = {
            'age':             age,
            'isYouth':         is_youth,
            'isFemale':        is_female,
            'isTownship':      is_township,
            'isFormal':        is_formal,
            'annualTurnover':  round(annual_turnover, 2),
            'monthlyTurnover': round(monthly_turnover, 2),
            'province':        province,
            'township':        township,
            'businessType':    business['business_type'],
        }

        return jsonify({
            'success':          True,
            'grants':           matched_grants,
            'totalMatches':     len([g for g in matched_grants if g['eligible']]),
            'estimatedFunding': sum(g['amount']['max'] for g in matched_grants if g['eligible']),
            'profile':          profile_summary,
        }), 200

    except Exception as e:
        print(f"❌ Grant matching error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# PILLAR 4: SUPPLY CHAIN & MARKET ACCESS
# ═══════════════════════════════════════════════════════════════════════════

@bizseed_bp.route('/market/analysis/<int:user_id>', methods=['GET'])
def get_market_analysis(user_id):
    """
    Real supply chain & market access analytics derived entirely from the user's
    own transaction history and business profile. No mocked data.
    """
    DOW_NAMES = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    # Supplier catalogue keyed by business_type string (lowercase match)
    SUPPLIERS = {
        'hair salon': [
            {'company': 'Hair Health & Beauty',   'type': 'Professional Salon Wholesale',
             'description': 'SA\'s largest trade-only salon supplier — 11,000+ products including Wella, Schwarzkopf, OPI. No consumer sales, professionals only.',
             'minOrder': 'R500', 'website': 'hairhealthbeauty.co.za',
             'requiredChecks': ['trading_history']},
            {'company': 'Hands Down SA',           'type': 'Professional Beauty & Hair Supplier',
             'description': 'One of SA\'s largest professional salon suppliers with nationwide delivery. Wide range of hair, nail and beauty products.',
             'minOrder': 'R800', 'website': 'handsdown.co.za',
             'requiredChecks': ['tax_number', 'trading_history']},
        ],
        'bakery': [
            {'company': 'Premier FMCG',            'type': 'Flour & Baking Ingredients Manufacturer',
             'description': 'SA manufacturer of Snowflake flour, Iwisa maize meal, and Blue Ribbon. Access through their distributor network — contact them to find your nearest wholesale outlet.',
             'minOrder': 'R1,500 (via distributors)', 'website': 'premierfmcg.com',
             'requiredChecks': ['tax_number', 'trading_history']},
            {'company': 'Tiger Brands',             'type': 'Branded Food Manufacturer',
             'description': 'Albany, Koo, All Gold, Jungle Oats and more. Sold through Makro/Cash & Carry wholesalers — contact tigerbrands.com to find your nearest distributor.',
             'minOrder': 'Via wholesale distributors', 'website': 'tigerbrands.com',
             'requiredChecks': ['cipc', 'tax_number', 'annual_turnover']},
        ],
        'auto repair': [
            {'company': 'Midas Auto Parts',        'type': 'Auto Parts Trade Account',
             'description': 'SA\'s leading auto parts chain with 300+ stores. Free delivery to registered workshops. Workshop portal available for trade pricing.',
             'minOrder': 'R500', 'website': 'midas.co.za',
             'requiredChecks': ['tax_number']},
            {'company': 'Goldwagen',                'type': 'Aftermarket Parts Distributor',
             'description': 'SA\'s largest aftermarket distributor with 130+ franchises. Covers VW, Audi, BMW, Mercedes, Toyota, Ford. Trade accounts available.',
             'minOrder': 'R1,000', 'website': 'goldwagen.com',
             'requiredChecks': ['cipc', 'tax_number', 'trading_history']},
        ],
        'mobile phone repair': [
            {'company': 'CellParts SA',             'type': 'Phone Parts Wholesale',
             'description': 'SA\'s leading iPhone, Android and Mac parts wholesaler — 20+ years in business, lifetime warranties. Branches in Cape Town and Johannesburg.',
             'minOrder': 'R500', 'website': 'cellparts.co.za',
             'requiredChecks': ['tax_number']},
            {'company': 'Rectron SA',               'type': 'ICT & Electronics Distributor',
             'description': 'Leading SA ICT distributor since 1995. Accessories, cables, cases and electronics at reseller/trade pricing. Register as a reseller partner.',
             'minOrder': 'R2,000', 'website': 'rectron.co.za',
             'requiredChecks': ['cipc', 'tax_number']},
        ],
        'fashion design': [
            {'company': 'SK Textiles',              'type': 'Fabric Wholesaler',
             'description': 'SA\'s broadest fabric range — 450+ fabric types for tailors, designers and manufacturers. Apparel, formal wear, African print and more.',
             'minOrder': 'R500', 'website': 'sktextiles.co.za',
             'requiredChecks': ['tax_number']},
            {'company': 'Da Gama Textiles',         'type': 'SA Textile Manufacturer',
             'description': 'Home of ShweShwe fabric — one of SA\'s oldest vertically-integrated textile producers. Designs and fabrics rooted in African heritage.',
             'minOrder': 'R1,000', 'website': 'dagama.co.za',
             'requiredChecks': ['cipc', 'tax_number', 'trading_history']},
        ],
    }

    # Universal suppliers available to all business types
    UNIVERSAL_SUPPLIERS = [
        {'company': 'Makro Business Account', 'type': 'General Wholesale (All categories)',
         'description': 'Business account for bulk buying across all product categories — 10–20% below retail. Free to open.',
         'minOrder': 'R0 (account is free)', 'website': 'makro.co.za',
         'requiredChecks': ['tax_number']},
        {'company': 'Cash & Carry Wholesalers', 'type': 'FMCG & General Merchandise',
         'description': 'Bulk household goods, food, cleaning products at wholesale prices. No formal registration required.',
         'minOrder': 'R0', 'website': 'cashandcarry.co.za',
         'requiredChecks': []},
        {'company': 'Builders Warehouse Trade', 'type': 'Hardware & Maintenance',
         'description': 'Trade account for building materials, tools, and maintenance supplies.',
         'minOrder': 'R500', 'website': 'builders.co.za',
         'requiredChecks': ['tax_number']},
    ]

    try:
        conn   = get_db()
        cursor = conn.cursor()

        # ── Query 1: Business + wallet context ──────────────────────────────
        cursor.execute('''
            SELECT
                b.business_id, b.business_name, b.business_type,
                b.township, b.province,
                b.cipc_registered, b.tax_number, b.vat_registered,
                b.employee_count, b.operating_since,
                cw.wallet_id,
                cw.total_cash_sales_cents,
                cw.total_digital_sales_cents,
                cw.total_expenses_cents
            FROM businesses b
            JOIN cash_wallets cw ON b.business_id = cw.business_id
            WHERE b.user_id = %s
        ''', (user_id,))
        biz = cursor.fetchone()

        if not biz:
            conn.close()
            return jsonify({'success': False, 'error': 'Business not found'}), 404

        wallet_id = biz['wallet_id']

        # ── Query 2: Revenue trend (this month vs last month) ───────────────
        cursor.execute('''
            SELECT
                COALESCE(SUM(CASE
                    WHEN transaction_date >= DATE_TRUNC('month', CURRENT_DATE)
                     AND transaction_type IN ('CASH_IN','DIGITAL_IN')
                    THEN amount_cents ELSE 0 END), 0)  AS this_month_cents,

                COALESCE(SUM(CASE
                    WHEN transaction_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
                     AND transaction_date <  DATE_TRUNC('month', CURRENT_DATE)
                     AND transaction_type IN ('CASH_IN','DIGITAL_IN')
                    THEN amount_cents ELSE 0 END), 0)  AS last_month_cents,

                COUNT(DISTINCT CASE
                    WHEN transaction_date >= DATE_TRUNC('month', CURRENT_DATE)
                     AND transaction_type IN ('CASH_IN','DIGITAL_IN')
                    THEN transaction_date END)          AS this_trading_days

            FROM cash_transactions
            WHERE wallet_id = %s
        ''', (wallet_id,))
        trend_row = cursor.fetchone()

        # ── Query 3: Day-of-week performance (last 90 days) ─────────────────
        cursor.execute('''
            SELECT
                EXTRACT(DOW FROM transaction_date)::INT AS dow,
                SUM(amount_cents)                        AS revenue_cents,
                COUNT(*)                                 AS txn_count,
                COUNT(DISTINCT transaction_date)         AS trading_days_for_dow
            FROM cash_transactions
            WHERE wallet_id = %s
              AND transaction_type IN ('CASH_IN','DIGITAL_IN')
              AND transaction_date >= CURRENT_DATE - INTERVAL '90 days'
            GROUP BY EXTRACT(DOW FROM transaction_date)
            ORDER BY dow
        ''', (wallet_id,))
        dow_rows = cursor.fetchall()

        # ── Query 4: Category breakdown (all time) ───────────────────────────
        cursor.execute('''
            SELECT
                category,
                COUNT(*)          AS txn_count,
                SUM(amount_cents) AS total_cents,
                AVG(amount_cents) AS avg_cents
            FROM cash_transactions
            WHERE wallet_id = %s
              AND transaction_type IN ('CASH_IN','DIGITAL_IN')
              AND category IS NOT NULL
            GROUP BY category
            ORDER BY total_cents DESC
        ''', (wallet_id,))
        cat_rows = cursor.fetchall()

        # ── Query 5: Transaction quality (all time) ──────────────────────────
        cursor.execute('''
            SELECT
                COUNT(*)                                                        AS total_txns,
                COUNT(DISTINCT transaction_date)                                AS active_days,
                COALESCE(SUM(CASE WHEN transaction_type IN ('CASH_IN','DIGITAL_IN')
                    THEN amount_cents ELSE 0 END), 0)                           AS total_revenue_cents,
                AVG(CASE WHEN transaction_type IN ('CASH_IN','DIGITAL_IN')
                    THEN amount_cents END)                                       AS avg_income_txn_cents,
                COUNT(CASE WHEN transaction_type IN ('CASH_IN','DIGITAL_IN')
                    AND amount_cents < 5000  THEN 1 END)                        AS micro_count,
                COUNT(CASE WHEN transaction_type IN ('CASH_IN','DIGITAL_IN')
                    AND amount_cents >= 50000 THEN 1 END)                       AS large_count,
                COUNT(CASE WHEN transaction_type IN ('CASH_IN','DIGITAL_IN')
                    THEN 1 END)                                                  AS income_count,
                COUNT(CASE WHEN transaction_type IN ('CASH_IN','DIGITAL_IN')
                    AND payment_method = 'DIGITAL' THEN 1 END)                  AS digital_count,
                COALESCE(SUM(CASE WHEN transaction_type = 'CASH_OUT'
                    THEN amount_cents ELSE 0 END), 0)                           AS total_expense_cents
            FROM cash_transactions
            WHERE wallet_id = %s
        ''', (wallet_id,))
        q_row = cursor.fetchone()

        # ── Query 6: Revenue consistency (monthly stddev) ────────────────────
        cursor.execute('''
            SELECT
                STDDEV(monthly_rev) AS rev_stddev,
                AVG(monthly_rev)    AS rev_avg
            FROM (
                SELECT
                    DATE_TRUNC('month', transaction_date) AS month,
                    SUM(amount_cents)                      AS monthly_rev
                FROM cash_transactions
                WHERE wallet_id = %s
                  AND transaction_type IN ('CASH_IN','DIGITAL_IN')
                GROUP BY DATE_TRUNC('month', transaction_date)
            ) m
        ''', (wallet_id,))
        consist_row = cursor.fetchone()

        # ── Query 7: First transaction date ─────────────────────────────────
        cursor.execute('''
            SELECT MIN(transaction_date) AS first_trade
            FROM cash_transactions
            WHERE wallet_id = %s
        ''', (wallet_id,))
        first_row = cursor.fetchone()

        conn.close()

        # ════════════════════════════════════════════════════════════════════
        # PYTHON DERIVATIONS
        # ════════════════════════════════════════════════════════════════════
        from datetime import date as date_type
        import math

        today = date_type.today()

        # ── Trading history ──────────────────────────────────────────────────
        first_trade = first_row['first_trade']
        if first_trade and hasattr(first_trade, 'toordinal'):
            months_trading = (today - first_trade).days / 30.44
        elif first_trade:
            try:
                first_trade = datetime.strptime(str(first_trade)[:10], '%Y-%m-%d').date()
                months_trading = (today - first_trade).days / 30.44
            except Exception:
                months_trading = 0.0
        else:
            months_trading = 0.0

        # ── Revenue trend ────────────────────────────────────────────────────
        this_month  = float(trend_row['this_month_cents']  or 0) / 100
        last_month  = float(trend_row['last_month_cents']  or 0) / 100
        trading_days_this_month = int(trend_row['this_trading_days'] or 0)

        if last_month > 0:
            change_pct = round((this_month - last_month) / last_month * 100, 1)
            direction  = 'UP' if change_pct > 0 else ('DOWN' if change_pct < 0 else 'FLAT')
        else:
            change_pct = None
            direction  = 'NO_DATA'

        daily_avg = round(this_month / trading_days_this_month, 2) if trading_days_this_month > 0 else 0.0

        revenue_trend = {
            'thisMonthRands':  round(this_month, 2),
            'lastMonthRands':  round(last_month, 2),
            'changePercent':   change_pct,
            'direction':       direction,
            'dailyAverageRands': daily_avg,
            'thisTradingDays': trading_days_this_month,
        }

        # ── Day-of-week performance ──────────────────────────────────────────
        dow_data = []
        for r in dow_rows:
            d = int(r['dow'])
            dow_days = int(r['trading_days_for_dow'] or 1)
            avg_rev  = float(r['revenue_cents'] or 0) / 100 / dow_days
            dow_data.append({
                'day':            DOW_NAMES[d],
                'dow':            d,
                'revenueRands':   round(float(r['revenue_cents'] or 0) / 100, 2),
                'avgRevenueRands':round(avg_rev, 2),
                'txnCount':       int(r['txn_count'] or 0),
            })

        best_dow  = max(dow_data, key=lambda x: x['avgRevenueRands'], default=None)
        worst_dow = min(dow_data, key=lambda x: x['avgRevenueRands'], default=None)

        if best_dow and worst_dow and worst_dow['avgRevenueRands'] > 0:
            peak_ratio = round(best_dow['avgRevenueRands'] / worst_dow['avgRevenueRands'], 1)
        else:
            peak_ratio = None

        # Restock recommendation: day before peak day
        if best_dow:
            restock_dow = (best_dow['dow'] - 1) % 7
            restock_day = DOW_NAMES[restock_dow]
            restock_msg = f"Restock on {restock_day} — your busiest day is {best_dow['day']}"
        else:
            restock_msg = "Not enough data yet — keep recording transactions"

        day_of_week = {
            'days':                  dow_data,
            'bestDay':               best_dow['day']  if best_dow  else None,
            'worstDay':              worst_dow['day'] if worst_dow else None,
            'peakToTroughRatio':     peak_ratio,
            'restockRecommendation': restock_msg,
        }

        # ── Category breakdown ───────────────────────────────────────────────
        grand_total_cents = sum(float(r['total_cents'] or 0) for r in cat_rows)
        categories_out = []
        seen_cats = set()
        for r in cat_rows:
            total_c = float(r['total_cents'] or 0)
            seen_cats.add(r['category'])
            categories_out.append({
                'category':           r['category'],
                'totalRands':         round(total_c / 100, 2),
                'pctOfRevenue':       round(total_c / grand_total_cents * 100, 1) if grand_total_cents > 0 else 0.0,
                'avgTransactionRands':round(float(r['avg_cents'] or 0) / 100, 2),
                'txnCount':           int(r['txn_count'] or 0),
            })

        top_cat = categories_out[0]['category'] if categories_out else None

        # Untapped category suggestions by business type
        UNTAPPED_MAP = {
            'Hair Salon':           ['HAIR_PRODUCTS', 'NAIL_SERVICES'],
            'Bakery':               ['CATERING_SERVICES', 'BAKING_CLASSES'],
            'Auto Repair':          ['TYRE_SALES', 'CAR_WASH'],
            'Mobile Phone Repair':  ['PHONE_ACCESSORIES', 'SMARTWATCH_REPAIR'],
            'Fashion Design':       ['ALTERATIONS', 'SEWING_CLASSES'],
        }
        biz_type_raw = biz['business_type'] or ''
        untapped = [
            c for c in UNTAPPED_MAP.get(biz_type_raw, [])
            if c not in seen_cats
        ]

        category_breakdown = {
            'categories':          categories_out,
            'topCategory':         top_cat,
            'untappedSuggestions': untapped,
        }

        # ── Transaction quality ──────────────────────────────────────────────
        income_count  = int(q_row['income_count']  or 0)
        digital_count = int(q_row['digital_count'] or 0)
        micro_count   = int(q_row['micro_count']   or 0)
        large_count   = int(q_row['large_count']   or 0)
        active_days   = int(q_row['active_days']   or 0)
        total_txns    = int(q_row['total_txns']    or 0)
        avg_txn_r     = float(q_row['avg_income_txn_cents'] or 0) / 100

        digital_pct = round(digital_count / income_count * 100, 1) if income_count > 0 else 0.0
        micro_pct   = round(micro_count   / income_count * 100, 1) if income_count > 0 else 0.0
        large_pct   = round(large_count   / income_count * 100, 1) if income_count > 0 else 0.0
        txns_per_day = round(total_txns / active_days, 1) if active_days > 0 else 0.0

        transaction_quality = {
            'avgTransactionRands':  round(avg_txn_r, 2),
            'microTransactionPct':  micro_pct,
            'largeTransactionPct':  large_pct,
            'txnsPerActiveDay':     txns_per_day,
            'digitalPct':           digital_pct,
            'cashPct':              round(100 - digital_pct, 1),
            'totalIncomeTxns':      income_count,
            'totalActiveDays':      active_days,
        }

        # ── Supply chain readiness score ─────────────────────────────────────
        total_rev_rands  = float(q_row['total_revenue_cents'] or 0) / 100
        annual_est_rands = total_rev_rands * (12 / max(months_trading, 1)) if months_trading > 0 else 0.0

        rev_avg    = float(consist_row['rev_avg']    or 0)
        rev_stddev = float(consist_row['rev_stddev'] or 0)
        is_consistent = rev_avg > 0 and (rev_stddev / rev_avg) < 0.5

        checks = {
            'cipc':             bool(biz['cipc_registered']),
            'tax_number':       bool(biz['tax_number']),
            'consistent_revenue': is_consistent,
            'annual_turnover':  annual_est_rands >= 100_000,
            'digital_payments': digital_pct > 20,
            'trading_history':  months_trading >= 6,
        }

        readiness_breakdown = {
            'cipc':             {'points': 25 if checks['cipc']             else 0, 'max': 25, 'met': checks['cipc'],
                                 'label': 'CIPC Registered', 'impact': 'Unlocks corporate and wholesale supply chains'},
            'taxNumber':        {'points': 20 if checks['tax_number']       else 0, 'max': 20, 'met': checks['tax_number'],
                                 'label': 'Tax Number (SARS)', 'impact': 'Required for all formal supplier accounts'},
            'consistentRevenue':{'points': 20 if checks['consistent_revenue'] else 0, 'max': 20, 'met': checks['consistent_revenue'],
                                 'label': 'Consistent Monthly Revenue', 'impact': 'Demonstrates business stability to suppliers'},
            'annualTurnover':   {'points': 15 if checks['annual_turnover']  else 0, 'max': 15, 'met': checks['annual_turnover'],
                                 'label': 'Annual Turnover R100K+', 'impact': 'Meets minimum threshold for bulk pricing',
                                 'estimatedAnnualRands': round(annual_est_rands, 2)},
            'digitalPayments':  {'points': 10 if checks['digital_payments'] else 0, 'max': 10, 'met': checks['digital_payments'],
                                 'label': 'Digital Payments (>20%)', 'impact': 'Required by most formal suppliers and corporates',
                                 'currentPct': digital_pct},
            'tradingHistory':   {'points': 10 if checks['trading_history']  else 0, 'max': 10, 'met': checks['trading_history'],
                                 'label': '6+ Months Trading', 'impact': 'Shows an established, operating business',
                                 'monthsTrading': round(months_trading, 1)},
        }

        readiness_score = sum(v['points'] for v in readiness_breakdown.values())

        def readiness_label(s):
            if s >= 80: return 'STRONG'
            if s >= 55: return 'MODERATE'
            if s >= 30: return 'DEVELOPING'
            return 'NOT_READY'

        supply_chain_readiness = {
            'score':      readiness_score,
            'scoreLabel': readiness_label(readiness_score),
            'breakdown':  readiness_breakdown,
        }

        # ── Supplier opportunities ────────────────────────────────────────────
        def check_met(k):
            return bool(checks.get(k, False))

        def compute_readiness(required_checks):
            if not required_checks:
                return 100
            met = sum(1 for k in required_checks if check_met(k))
            return int(met / len(required_checks) * 100)

        biz_type_key = biz_type_raw.lower()
        specific_suppliers = SUPPLIERS.get(biz_type_key, [])

        supplier_opportunities = []
        for s in specific_suppliers:
            supplier_opportunities.append({
                'company':       s['company'],
                'type':          s['type'],
                'description':   s['description'],
                'minOrder':      s['minOrder'],
                'website':       s['website'],
                'requirements':  s['requiredChecks'],
                'readinessPct':  compute_readiness(s['requiredChecks']),
            })
        supplier_opportunities.sort(key=lambda x: x['readinessPct'], reverse=True)

        # ── Growth opportunities ──────────────────────────────────────────────
        growth_opportunities = []

        # 1. Low digital payment adoption
        if digital_pct < 20:
            growth_opportunities.append({
                'suggestion': 'Start accepting card & SnapScan payments',
                'impact': 'HIGH',
                'reason': f'Only {digital_pct:.0f}% of your sales are digital — you\'re turning away cashless customers.',
                'actionStep': 'Get a Yoco card machine from R999. No monthly fees.',
            })

        # 2. Low average transaction value
        if avg_txn_r > 0 and avg_txn_r < 150:
            growth_opportunities.append({
                'suggestion': 'Introduce bundle deals to increase transaction size',
                'impact': 'MEDIUM',
                'reason': f'Your average sale is R{avg_txn_r:.0f}. Bundles or upsells can lift this by 20–40%.',
                'actionStep': f'Try a "combo deal" — e.g. bundle your two most popular items at a small discount.',
            })

        # 3. Strong day-of-week peak (best day 2.5x or more than worst)
        if peak_ratio and peak_ratio >= 2.5 and best_dow:
            growth_opportunities.append({
                'suggestion': f'Prepare more stock before {best_dow["day"]}',
                'impact': 'HIGH',
                'reason': f'Your {best_dow["day"]} revenue is {peak_ratio}x your slowest day — don\'t run out.',
                'actionStep': f'Restock every {DOW_NAMES[(best_dow["dow"] - 1) % 7]}. Set a weekly reminder.',
            })

        # 4. Not CIPC registered
        if not checks['cipc']:
            growth_opportunities.append({
                'suggestion': 'Register your business with CIPC',
                'impact': 'HIGH',
                'reason': 'Without CIPC registration you cannot open trade accounts with wholesalers or get formal contracts.',
                'actionStep': 'Register online at eservices.cipc.co.za from R175 for a sole proprietor.',
            })

        # 5. Township location — suggest mobile money
        if biz['township'] and 'MOBILE_MONEY' not in seen_cats and 'AIRTIME' not in seen_cats:
            growth_opportunities.append({
                'suggestion': 'Offer cash-out / mobile money services',
                'impact': 'MEDIUM',
                'reason': f'Township customers in {biz["township"]} need cash access — this can add R2,000–R5,000/month.',
                'actionStep': 'Apply to be a Capitec, FNB or Mama Money agent banking point.',
            })

        # 6. Revenue trending strongly upward
        if change_pct and change_pct >= 15:
            growth_opportunities.append({
                'suggestion': 'Consider extending your trading hours or hiring part-time help',
                'impact': 'MEDIUM',
                'reason': f'Your revenue grew {change_pct:.0f}% this month — you may be leaving sales on the table.',
                'actionStep': 'Track your busiest hours for 2 weeks, then decide if extended hours are worth it.',
            })

        # 7. Revenue dropping
        if change_pct and change_pct <= -10:
            growth_opportunities.append({
                'suggestion': 'Investigate why revenue dropped this month',
                'impact': 'HIGH',
                'reason': f'Revenue is down {abs(change_pct):.0f}% vs last month — act now before the trend continues.',
                'actionStep': 'Review which categories or days dropped most. Consider a temporary promotion.',
            })

        # 8. Business-type specific tips
        type_tips = {
            'Hair Salon': {
                'suggestion': 'Retail hair products between appointments',
                'impact': 'MEDIUM',
                'reason': 'Salons that sell products earn 20–30% more than service-only salons.',
                'actionStep': 'Stock 5–10 popular brands. Buy wholesale from Sorbet or Siyanda Beauty.',
            },
            'Bakery': {
                'suggestion': 'Take custom orders via WhatsApp with a 50% deposit',
                'impact': 'MEDIUM',
                'reason': 'Custom orders (birthdays, weddings) have 3–5x the margin of walk-in sales.',
                'actionStep': 'Create a simple WhatsApp catalogue. Require a 50% deposit to reduce no-shows.',
            },
            'Auto Repair': {
                'suggestion': 'Offer a basic annual service package',
                'impact': 'MEDIUM',
                'reason': 'Package deals create predictable revenue and build customer loyalty.',
                'actionStep': 'Bundle oil change + filter + basic check at a 10% discount vs individual pricing.',
            },
            'Mobile Phone Repair': {
                'suggestion': 'Add screen protection bundles at point of repair',
                'impact': 'LOW',
                'reason': 'Customers who just paid for a repair are primed to protect their phone.',
                'actionStep': 'Stock tempered glass and cases. Upsell at checkout for R50–R150 extra per job.',
            },
            'Fashion Design': {
                'suggestion': 'List your work on Instagram and Pinterest with pricing',
                'impact': 'HIGH',
                'reason': 'Fashion buyers research online before contacting a designer.',
                'actionStep': 'Post 3 photos per week with prices and your WhatsApp number in the caption.',
            },
        }
        if biz_type_raw in type_tips:
            growth_opportunities.append(type_tips[biz_type_raw])

        return jsonify({
            'success':      True,
            'generatedAt':  datetime.now().isoformat(),
            'business': {
                'businessName': biz['business_name'],
                'businessType': biz['business_type'],
                'township':     biz['township'],
                'province':     biz['province'],
            },
            'revenueTrend':         revenue_trend,
            'dayOfWeekPerformance': day_of_week,
            'categoryBreakdown':    category_breakdown,
            'transactionQuality':   transaction_quality,
            'supplyChainReadiness': supply_chain_readiness,
            'supplierOpportunities':supplier_opportunities,
            'growthOpportunities':  growth_opportunities,
        }), 200

    except Exception as e:
        print(f"❌ Market analysis error: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# DASHBOARD SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

@bizseed_bp.route('/dashboard/<int:user_id>', methods=['GET'])
def get_bizseed_dashboard(user_id):
    """Get complete Biz-Seed dashboard with REAL calculated scores"""
    try:
        from business_intelligence import BusinessIntelligence
        from compliance_helper import ComplianceHelper
        
        bi = BusinessIntelligence()
        compliance_helper = ComplianceHelper()
        
        # Get business context
        business_context = bi.get_user_business_context(user_id)
        
        if 'error' in business_context:
            return jsonify({'success': False, 'error': business_context['error']}), 404
        
        # ═══════════════════════════════════════════════════════════════
        # CALCULATE COMPLIANCE SCORE (0-100)
        # ═══════════════════════════════════════════════════════════════
        
        compliance_score = 0
        
        # Check CIPC (30 points)
        if business_context.get('cipcRegistered'):
            compliance_score += 30
        
        # Check SARS (30 points)
        if business_context.get('taxRegistered'):
            compliance_score += 30
        
        # Check B-BBEE (20 points)
        if business_context.get('hasBBBEE'):
            compliance_score += 20
        
        # Check POPIA (20 points)
        if business_context.get('hasPOPIA'):
            compliance_score += 20
        
        # Determine status
        if compliance_score < 25:
            compliance_status = 'CRITICAL'
        elif compliance_score < 50:
            compliance_status = 'NEEDS_WORK'
        elif compliance_score < 75:
            compliance_status = 'MODERATE'
        else:
            compliance_status = 'GOOD'
        
        # ═══════════════════════════════════════════════════════════════
        # CALCULATE INVESTOR VAULT SCORE (0-100)
        # ═══════════════════════════════════════════════════════════════
        
        vault_score = 0
        
        # Has transactions (25 points)
        if business_context['analytics']['transactionCount'] > 0:
            vault_score += 25
        
        # Has 30+ days of data (25 points)
        if business_context['analytics']['transactionCount'] >= 30:
            vault_score += 25
        
        # Positive profit (25 points)
        if business_context['analytics']['profit'] > 0:
            vault_score += 25
        
        # Regular transactions (25 points)
        if business_context['analytics']['transactionCount'] >= 50:
            vault_score += 25
        
        vault_status = 'GOOD' if vault_score >= 65 else 'MODERATE' if vault_score >= 40 else 'NEEDS_WORK'
        
        # ═══════════════════════════════════════════════════════════════
        # CALCULATE FUNDING ACCESS SCORE (0-100)
        # ═══════════════════════════════════════════════════════════════
        
        funding_score = 0
        
        # Has revenue (20 points)
        if business_context['analytics']['totalSales'] > 0:
            funding_score += 20
        
        # Profitable (20 points)
        if business_context['analytics']['profit'] > 0:
            funding_score += 20
        
        # CIPC registered (30 points)
        if business_context.get('cipcRegistered'):
            funding_score += 30
        
        # Tax registered (30 points)
        if business_context.get('taxRegistered'):
            funding_score += 30
        
        funding_status = 'GOOD' if funding_score >= 60 else 'MODERATE' if funding_score >= 40 else 'NEEDS_WORK'
        
        # ═══════════════════════════════════════════════════════════════
        # CALCULATE MARKET ACCESS SCORE (0-100)
        # ═══════════════════════════════════════════════════════════════
        
        market_score = 0
        
        # Consistent sales (25 points)
        if business_context['analytics']['averageDailySales'] > 0:
            market_score += 25
        
        # Multiple transactions (25 points)
        if business_context['analytics']['transactionCount'] >= 20:
            market_score += 25
        
        # Profit margin > 20% (25 points)
        profit_margin = business_context['analytics']['incomeVsExpenses']['profitMargin']
        if profit_margin >= 20:
            market_score += 25
        
        # Growing revenue (25 points) - simplified check
        if business_context['analytics']['totalSales'] > 1000:
            market_score += 25
        
        market_status = 'GOOD' if market_score >= 50 else 'MODERATE' if market_score >= 30 else 'NEEDS_WORK'
        
        # ═══════════════════════════════════════════════════════════════
        # CALCULATE OVERALL INVESTMENT READINESS (0-100)
        # ═══════════════════════════════════════════════════════════════
        
        investment_readiness = int((
            compliance_score * 0.30 +  # 30% weight
            vault_score * 0.30 +       # 30% weight
            funding_score * 0.25 +     # 25% weight
            market_score * 0.15        # 15% weight
        ))
        
        # ═══════════════════════════════════════════════════════════════
        # GENERATE NEXT STEPS (Priority Actions)
        # ═══════════════════════════════════════════════════════════════
        
        next_steps = []
        
        if not business_context.get('cipcRegistered'):
            next_steps.append({
                'action': 'Register with CIPC',
                'priority': 'HIGH',
                'pillar': 'compliance',
                'impact': '+30 points'
            })
        
        if not business_context.get('taxRegistered'):
            next_steps.append({
                'action': 'Register for SARS tax',
                'priority': 'HIGH',
                'pillar': 'compliance',
                'impact': '+30 points'
            })
        
        if vault_score < 50:
            next_steps.append({
                'action': 'Generate pitch deck',
                'priority': 'MEDIUM',
                'pillar': 'investorVault',
                'impact': '+15 points'
            })
        
        if business_context['analytics']['transactionCount'] < 30:
            next_steps.append({
                'action': 'Log more transactions',
                'priority': 'MEDIUM',
                'pillar': 'investorVault',
                'impact': '+25 points'
            })
        
        # Estimate available funding
        estimated_funding = 0
        if business_context.get('cipcRegistered') and business_context.get('taxRegistered'):
            estimated_funding = 100000  # Qualified for larger grants
        elif compliance_score >= 30:
            estimated_funding = 50000   # Qualified for some grants
        else:
            estimated_funding = 10000   # Only EME grants
        
        # ═══════════════════════════════════════════════════════════════
        # AI-POWERED INVESTMENT INSIGHTS (advanced_model)
        # ═══════════════════════════════════════════════════════════════

        ai_insight = None
        ai_weekly_actions = []
        try:
            from openrouter_helper import OpenRouterHelper
            ai = OpenRouterHelper()
            scores = {
                'compliance': compliance_score,
                'vault': vault_score,
                'funding': funding_score,
                'market': market_score,
                'overall': investment_readiness,
            }
            # Fetch lightweight market context to enrich AI narrative
            market_ctx = None
            try:
                conn_mc = get_db()
                cur_mc  = conn_mc.cursor()
                # wallet_id for this user
                cur_mc.execute('''
                    SELECT cw.wallet_id FROM cash_wallets cw
                    JOIN businesses b ON b.business_id = cw.business_id
                    WHERE b.user_id = %s LIMIT 1
                ''', (user_id,))
                wrow = cur_mc.fetchone()
                if wrow:
                    wid = wrow['wallet_id']
                    # Revenue trend
                    cur_mc.execute('''
                        SELECT
                            COALESCE(SUM(CASE WHEN transaction_date >= DATE_TRUNC('month', CURRENT_DATE)
                                AND transaction_type IN ('CASH_IN','DIGITAL_IN') THEN amount_cents ELSE 0 END),0) AS this_m,
                            COALESCE(SUM(CASE WHEN transaction_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '1 month'
                                AND transaction_date < DATE_TRUNC('month', CURRENT_DATE)
                                AND transaction_type IN ('CASH_IN','DIGITAL_IN') THEN amount_cents ELSE 0 END),0) AS last_m
                        FROM cash_transactions WHERE wallet_id = %s
                    ''', (wid,))
                    tr = cur_mc.fetchone()
                    this_m = float(tr['this_m'] or 0) / 100
                    last_m = float(tr['last_m'] or 0) / 100
                    if last_m > 0:
                        pct = (this_m - last_m) / last_m * 100
                        direction = 'UP' if pct >= 5 else 'DOWN' if pct <= -5 else 'FLAT'
                    else:
                        pct, direction = 0.0, 'FLAT'
                    # Top category
                    cur_mc.execute('''
                        SELECT category, SUM(amount_cents) AS total
                        FROM cash_transactions
                        WHERE wallet_id = %s AND transaction_type IN ('CASH_IN','DIGITAL_IN')
                          AND category IS NOT NULL
                        GROUP BY category ORDER BY total DESC LIMIT 1
                    ''', (wid,))
                    cat_row = cur_mc.fetchone()
                    top_cat = cat_row['category'].replace('_', ' ').title() if cat_row else 'General'
                    top_cat_rev = float(cat_row['total'] or 0) / 100 if cat_row else 0
                    # Digital %
                    cur_mc.execute('''
                        SELECT
                            COUNT(CASE WHEN payment_method = 'DIGITAL' THEN 1 END) AS digital_count,
                            COUNT(*) AS total_count
                        FROM cash_transactions
                        WHERE wallet_id = %s AND transaction_type IN ('CASH_IN','DIGITAL_IN')
                    ''', (wid,))
                    drow = cur_mc.fetchone()
                    total_c = int(drow['total_count'] or 0)
                    digital_pct = (int(drow['digital_count'] or 0) / total_c * 100) if total_c else 0
                    # Supply chain readiness score (reuse market_score from above)
                    market_ctx = {
                        'success': True,
                        'revenueTrend': {'direction': direction, 'percentageChange': round(pct, 1)},
                        'categoryBreakdown': [{'category': top_cat, 'revenue': top_cat_rev}],
                        'transactionQuality': {'digitalPercentage': round(digital_pct, 1)},
                        'supplyChainReadiness': {'score': market_score},
                        'dayOfWeekPerformance': [],
                    }
                conn_mc.close()
            except Exception as mc_err:
                print(f"⚠️  Market context fetch skipped: {mc_err}")
            ai_result = ai.get_investment_insights(business_context, scores, market_ctx)
            if ai_result.get('success'):
                ai_insight = ai_result.get('summary')
                ai_weekly_actions = ai_result.get('weeklyActions', [])
        except Exception as ai_err:
            print(f"⚠️  AI insights skipped: {ai_err}")

        # Build response
        summary = {
            'investmentReadiness': investment_readiness,
            'pillars': {
                'compliance': {
                    'score': compliance_score,
                    'status': compliance_status
                },
                'investorVault': {
                    'score': vault_score,
                    'status': vault_status
                },
                'fundingAccess': {
                    'score': funding_score,
                    'status': funding_status
                },
                'marketAccess': {
                    'score': market_score,
                    'status': market_status
                }
            },
            'nextSteps': next_steps[:4],  # Top 4 actions
            'estimatedFunding': estimated_funding,
            'documentsReady': vault_score // 25,  # Rough estimate
            'documentsMissing': 4 - (vault_score // 25),
            'grantsMatched': 3 if funding_score >= 50 else 2 if funding_score >= 30 else 1,
            'aiInsight': ai_insight,
            'aiWeeklyActions': ai_weekly_actions,
        }

        return jsonify({
            'success': True,
            'dashboard': summary
        }), 200
        
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    