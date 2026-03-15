"""
MzansiPulse Authentication API
Flask server with OBS database integration
"""

from bizseed_api import bizseed_bp
from pangu_helper import PanguAIHelper
from business_intelligence import BusinessIntelligence
from empowerscore_calculator import EmpowerScoreCalculator
import sys
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from db import get_db, get_db_path
from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import OBS manager (will fail gracefully if not available)
try:
    from obs_db_manager import OBSDatabaseManager
    OBS_AVAILABLE = True
except ImportError:
    print("⚠️  obs_db_manager not found - OBS features disabled")
    OBS_AVAILABLE = False

app = Flask(__name__)
CORS(app)  # Allow requests from Vue frontend
app.register_blueprint(bizseed_bp)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Environment-based configuration
USE_OBS = os.environ.get('USE_OBS', 'false').lower() == 'true'

# OBS credentials (from environment variables for security)
OBS_AK = os.environ.get('OBS_ACCESS_KEY')
OBS_SK = os.environ.get('OBS_SECRET_KEY')
OBS_BUCKET = os.environ.get('OBS_BUCKET_NAME', 'mzansipulse-data')

# Local database path (fallback)
LOCAL_DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

# Initialize OBS manager if enabled
obs_manager = None
if USE_OBS and OBS_AVAILABLE and OBS_AK and OBS_SK:
    try:
        obs_manager = OBSDatabaseManager(
            access_key_id=OBS_AK,
            secret_access_key=OBS_SK,
            bucket_name=OBS_BUCKET
        )
        print("✅ OBS database manager initialized")
    except Exception as e:
        print(f"⚠️  OBS initialization failed: {e}")
        print("⚠️  Falling back to local database")
        obs_manager = None
else:
    if USE_OBS:
        print("⚠️  OBS enabled but credentials missing or module not available")
    print("ℹ️  Using local database")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

# get_db() and get_db_path() are imported from db.py (Supabase PostgreSQL)

def sync_to_obs():
    """Upload database to OBS after write operations. Non-blocking on failure."""
    if obs_manager:
        obs_manager.upload_to_obs()

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'MzansiPulse Auth API is running!',
        'database_mode': 'OBS' if obs_manager else 'Local',
        'database_path': get_db_path()
    })

@app.route('/api/backup-to-obs', methods=['POST'])
def backup_to_obs():
    """Manually trigger a database backup to OBS."""
    if not obs_manager:
        return jsonify({
            'success': False,
            'error': 'OBS is not configured. Set USE_OBS=true and provide credentials.'
        }), 503

    success = obs_manager.upload_to_obs()

    if success:
        return jsonify({
            'success': True,
            'message': 'Database backed up to OBS successfully.'
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'OBS upload failed. Check server logs for details.'
        }), 500


@app.route('/api/signup', methods=['POST'])
def signup():
    """
    Create new business owner account

    Expected JSON body:
    {
        "firstName": "Thandi",
        "lastName": "Molefe",
        "phone": "0821234567",
        "businessName": "Mama Thandi's Spaza",
        "businessType": "SPAZA_SHOP",
        "location": "Soweto, Gauteng",
        "email": "thandi@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.json

        # Validate required fields
        required_fields = ['firstName', 'lastName', 'phone', 'businessName',
                           'businessType', 'location', 'email', 'password']

        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400

        conn = get_db()
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute('SELECT user_id FROM users WHERE email = %s', (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 409

        # Check if phone already exists
        cursor.execute('SELECT user_id FROM users WHERE phone_number = %s', (data['phone'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Phone number already registered'
            }), 409

        # Hash password
        password_hash = hash_password(data['password'])

        # Insert user
        cursor.execute('''
            INSERT INTO users (
                phone_number, first_name, last_name, email,
                password_hash, preferred_language, consent_data_processing,
                consent_credit_check, consent_timestamp, kyc_status,
                is_active, account_created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING user_id
        ''', (
            data['phone'],
            data['firstName'],
            data['lastName'],
            data['email'],
            password_hash,
            'en',  # Default to English
            1,  # Consent given during signup
            1,
            datetime.now().isoformat(),
            'PENDING',  # Will be verified later
            1,
            datetime.now().isoformat()
        ))

        user_id = cursor.fetchone()['user_id']

        # Insert business
        cursor.execute('''
            INSERT INTO businesses (
                user_id, business_name, business_type, province,
                township, verification_status, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING business_id
        ''', (
            user_id,
            data['businessName'],
            data['businessType'],
            data['location'].split(',')[-1].strip() if ',' in data['location'] else data['location'],
            data['location'].split(',')[0].strip() if ',' in data['location'] else data['location'],
            'PENDING',
            datetime.now().isoformat()
        ))

        business_id = cursor.fetchone()['business_id']

        # Create cash wallet for the business
        cursor.execute('''
            INSERT INTO cash_wallets (
                business_id, virtual_balance_cents, cash_on_hand_cents,
                wallet_status, last_updated
            ) VALUES (%s, 0, 0, 'ACTIVE', %s)
        ''', (business_id, datetime.now().isoformat()))

        conn.commit()

        # Sync to OBS after creating user
        sync_to_obs()

        # Fetch the complete user data
        cursor.execute('''
            SELECT
                u.user_id, u.first_name, u.last_name, u.email, u.phone_number,
                b.business_id, b.business_name, b.business_type, b.township, b.province
            FROM users u
            JOIN businesses b ON u.user_id = b.user_id
            WHERE u.user_id = %s
        ''', (user_id,))

        user_row = cursor.fetchone()
        conn.close()

        # Build response
        user_data = {
            'id': user_row['user_id'],
            'email': user_row['email'],
            'firstName': user_row['first_name'],
            'lastName': user_row['last_name'],
            'phone': user_row['phone_number'],
            'businessId': user_row['business_id'],
            'businessName': user_row['business_name'],
            'businessType': user_row['business_type'],
            'location': f"{user_row['township']}, {user_row['province']}",
            'role': 'business'
        }

        print(f"✅ New user created: {user_data['firstName']} {user_data['lastName']}")

        return jsonify({
            'success': True,
            'user': user_data,
            'message': 'Account created successfully!'
        }), 201

    except Exception as e:
        print(f"❌ Signup error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/login', methods=['POST'])
def login():
    """
    Login existing user

    Expected JSON body:
    {
        "email": "thandi@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.json

        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # Fetch user by email (include wallet_id)
        cursor.execute('''
            SELECT
                u.user_id, u.first_name, u.last_name, u.email, u.phone_number,
                u.password_hash, u.is_active,
                b.business_id, b.business_name, b.business_type, b.township, b.province,
                cw.wallet_id
            FROM users u
            LEFT JOIN businesses b  ON u.user_id      = b.user_id
            LEFT JOIN cash_wallets cw ON b.business_id = cw.business_id
            WHERE u.email = %s
        ''', (data['email'],))

        user_row = cursor.fetchone()

        if not user_row:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401

        # Verify password
        if not verify_password(data['password'], user_row['password_hash']):
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401

        # Check if account is active
        if not user_row['is_active']:
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Account is inactive. Please contact support.'
            }), 403

        # Update last login
        cursor.execute('''
            UPDATE users
            SET last_login = %s
            WHERE user_id = %s
        ''', (datetime.now().isoformat(), user_row['user_id']))

        conn.commit()

        # Sync to OBS after updating last login
        sync_to_obs()

        conn.close()

        # Build response
        user_data = {
            'id': user_row['user_id'],
            'email': user_row['email'],
            'firstName': user_row['first_name'],
            'lastName': user_row['last_name'],
            'phone': user_row['phone_number'],
            'businessId': user_row['business_id'],
            'businessName': user_row['business_name'],
            'businessType': user_row['business_type'],
            'location': f"{user_row['township']}, {user_row['province']}" if user_row['township'] else 'Unknown',
            'walletId': user_row['wallet_id'],
            'role': 'business'
        }

        print(f"✅ User logged in: {user_data['firstName']} {user_data['lastName']}")

        return jsonify({
            'success': True,
            'user': user_data,
            'message': 'Login successful!'
        }), 200

    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details by ID"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT
                u.user_id, u.first_name, u.last_name, u.email, u.phone_number,
                b.business_id, b.business_name, b.business_type, b.township, b.province
            FROM users u
            LEFT JOIN businesses b ON u.user_id = b.user_id
            WHERE u.user_id = %s
        ''', (user_id,))

        user_row = cursor.fetchone()
        conn.close()

        if not user_row:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404

        user_data = {
            'id': user_row['user_id'],
            'email': user_row['email'],
            'firstName': user_row['first_name'],
            'lastName': user_row['last_name'],
            'phone': user_row['phone_number'],
            'businessId': user_row['business_id'],
            'businessName': user_row['business_name'],
            'businessType': user_row['business_type'],
            'location': f"{user_row['township']}, {user_row['province']}" if user_row['township'] else 'Unknown',
            'role': 'business'
        }

        return jsonify({
            'success': True,
            'user': user_data
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dashboard/<int:user_id>', methods=['GET'])
def get_dashboard_data(user_id):
    """Get complete dashboard data including latest transactions"""
    try:
        # Get business context (wallet, analytics)
        business_context = bi_helper.get_user_business_context(user_id)
        
        if 'error' in business_context:
            return jsonify({'success': False, 'error': business_context['error']}), 404
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get latest 5 transactions for dashboard preview
        cursor.execute('''
            SELECT 
                ct.cash_transaction_id as id,
                ct.transaction_type,
                ct.amount_cents,
                ct.payment_method,
                ct.source_destination,
                ct.category,
                ct.transaction_date,
                ct.recorded_at
            FROM cash_transactions ct
            JOIN cash_wallets cw ON ct.wallet_id = cw.wallet_id
            JOIN businesses b ON cw.business_id = b.business_id
            WHERE b.user_id = %s
            ORDER BY ct.recorded_at DESC
            LIMIT 5
        ''', (user_id,))
        
        recent_transactions = []
        for row in cursor.fetchall():
            recent_transactions.append({
                'id': row['id'],
                'type': row['transaction_type'],
                'amount': row['amount_cents'] / 100,
                'paymentMethod': row['payment_method'],
                'description': row['source_destination'],
                'category': row['category'],
                'date': row['transaction_date'],
                'recordedAt': row['recorded_at']
            })
        
        conn.close()

        # Calculate real EmpowerScore
        calculator = EmpowerScoreCalculator()
        empower_result = calculator.calculate_score(user_id)

        return jsonify({
            'success': True,
            'wallet': business_context['wallet'],
            'analytics': business_context['analytics'],
            'recentTransactions': recent_transactions,
            'empowerScore': empower_result['score'],
            'empowerTier': empower_result['tier'],
            'empowerBreakdown': empower_result['breakdown']
        }), 200
        
    except Exception as e:
        print(f"❌ Dashboard data error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500 
# ═══════════════════════════════════════════════════════════════════════════
# PANGU AI INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

PANGU_PROJECT_ID = os.environ.get('PANGU_PROJECT_ID', 'demo-project')
PANGU_AK = os.environ.get('PANGU_ACCESS_KEY', OBS_AK)
PANGU_SK = os.environ.get('PANGU_SECRET_KEY', OBS_SK)

pangu_helper = PanguAIHelper(
    project_id=PANGU_PROJECT_ID,
    access_key=PANGU_AK,
    secret_key=PANGU_SK
)

# Initialize BI helper after pangu_helper initialization
bi_helper = BusinessIntelligence()

# ═══════════════════════════════════════════════════════════════════════════
# TRANSACTION ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get user's transactions (privacy-protected)"""
    try:
        user_id = request.args.get('userId')
        limit = int(request.args.get('limit', 50))
        
        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # ✅ FIXED: Use correct column name 'cash_transaction_id'
        cursor.execute('''
            SELECT 
                ct.cash_transaction_id,
                ct.transaction_type,
                ct.amount_cents,
                ct.payment_method,
                ct.source_destination,
                ct.category,
                ct.transaction_date,
                ct.entry_method,
                ct.verified,
                ct.receipt_image_path
            FROM cash_transactions ct
            JOIN cash_wallets cw ON ct.wallet_id = cw.wallet_id
            JOIN businesses b ON cw.business_id = b.business_id
            WHERE b.user_id = %s
            ORDER BY ct.transaction_date DESC, ct.recorded_at DESC
            LIMIT %s
        ''', (user_id, limit))
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'id': row['cash_transaction_id'],  # ✅ Correct column name
                'type': row['transaction_type'],
                'amount': row['amount_cents'] / 100,
                'paymentMethod': row['payment_method'],
                'description': row['source_destination'],
                'category': row['category'],
                'date': row['transaction_date'],
                'entryMethod': row['entry_method'] or 'MANUAL',
                'verified': bool(row['verified']),
                'receiptImage': row['receipt_image_path']
            })
        
        conn.close()
        
        print(f"✅ Fetched {len(transactions)} transactions for user {user_id}")
        
        return jsonify({
            'success': True,
            'transactions': transactions,
            'count': len(transactions)
        }), 200
        
    except Exception as e:
        print(f"❌ Get transactions error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    """Add new transaction"""
    try:
        data = request.json
        required = ['userId', 'type', 'amount', 'paymentMethod', 'description']
        
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing {field}'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Get user's wallet
        cursor.execute('''
            SELECT cw.wallet_id 
            FROM cash_wallets cw
            JOIN businesses b ON cw.business_id = b.business_id
            WHERE b.user_id = %s
        ''', (data['userId'],))
        
        wallet = cursor.fetchone()
        if not wallet:
            return jsonify({'success': False, 'error': 'Wallet not found'}), 404
        
        wallet_id = wallet['wallet_id']
        amount_cents = int(float(data['amount']) * 100)
        
        # ✅ FIXED: Insert with correct columns
        cursor.execute('''
            INSERT INTO cash_transactions (
                wallet_id, transaction_type, amount_cents, payment_method,
                source_destination, category, transaction_date, entry_method,
                verified, receipt_image_path, ocr_raw_text, recorded_at, recorded_method
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING cash_transaction_id
        ''', (
            wallet_id,
            data['type'],
            amount_cents,
            data['paymentMethod'],
            data['description'],
            data.get('category', 'OTHER'),
            data.get('date', datetime.now().strftime('%Y-%m-%d')),
            data.get('entryMethod', 'MANUAL'),
            data.get('verified', 0),
            data.get('receiptImage'),
            data.get('ocrText'),
            datetime.now().isoformat(),
            'WEB_APP'
        ))

        transaction_id = cursor.fetchone()['cash_transaction_id']
        
        # Update wallet balance
        if data['type'] in ['CASH_IN', 'DIGITAL_IN']:
            cursor.execute('''
                UPDATE cash_wallets
                SET virtual_balance_cents = virtual_balance_cents + %s,
                    cash_on_hand_cents = cash_on_hand_cents + %s
                WHERE wallet_id = %s
            ''', (amount_cents, amount_cents if data['paymentMethod'] == 'CASH' else 0, wallet_id))
        else:
            cursor.execute('''
                UPDATE cash_wallets
                SET virtual_balance_cents = virtual_balance_cents - %s,
                    cash_on_hand_cents = cash_on_hand_cents - %s
                WHERE wallet_id = %s
            ''', (amount_cents, amount_cents if data['paymentMethod'] == 'CASH' else 0, wallet_id))
        
        conn.commit()
        conn.close()
        sync_to_obs()
        
        print(f"✅ Transaction added: {transaction_id}")
        
        return jsonify({
            'success': True,
            'transactionId': transaction_id,
            'message': 'Transaction added'
        }), 201
        
    except Exception as e:
        print(f"❌ Add transaction error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/transactions/ocr', methods=['POST'])
def process_receipt_ocr():
    """Process receipt image with Huawei Cloud OCR (falls back to Tesseract)."""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image uploaded'}), 400

        image_file = request.files['image']
        user_id    = request.form.get('userId')

        if not user_id:
            return jsonify({'success': False, 'error': 'User ID required'}), 400

        # Validate MIME type
        allowed = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'}
        if image_file.content_type and image_file.content_type not in allowed:
            return jsonify({'success': False, 'error': 'Invalid image format'}), 422

        # Save to uploads/receipts/
        import uuid
        ext      = os.path.splitext(image_file.filename or 'receipt.jpg')[1] or '.jpg'
        filename = f"receipt_{user_id}_{uuid.uuid4().hex}{ext}"
        save_dir = os.path.join('..', 'uploads', 'receipts')
        os.makedirs(save_dir, exist_ok=True)
        image_path = os.path.join(save_dir, filename)
        image_file.save(image_path)

        # Run OCR
        from huawei_ocr_helper import get_ocr_helper
        ocr    = get_ocr_helper()
        result = ocr.process_receipt(image_path)

        if not result['success']:
            # Return partial data with warning so the user can fill in manually
            return jsonify({
                'success':       False,
                'warning':       result.get('error', 'OCR processing failed'),
                'ocrText':       '',
                'confidence':    0.0,
                'extractedData': result['extracted'],
                'imagePath':     filename,
            }), 200

        return jsonify({
            'success':       True,
            'ocrText':       result['text'],
            'confidence':    result['confidence'],
            'extractedData': result['extracted'],
            'imagePath':     filename,
        }), 200

    except Exception as e:
        print(f"❌ OCR error: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

# ═══════════════════════════════════════════════════════════════════════════
# LEDGER ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/ledger/<int:user_id>', methods=['GET'])
def get_ledger(user_id):
    """
    Get detailed transaction ledger with running balance.

    Query params:
      start_date     YYYY-MM-DD  (default: 30 days ago)
      end_date       YYYY-MM-DD  (default: today)
      category       filter by category
      payment_method filter by payment method
      type           CASH_IN | CASH_OUT | DIGITAL_IN etc.
      sort           date_asc | date_desc | amount_asc | amount_desc
      page           page number  (default: 1)
      per_page       rows/page    (default: 50, max: 200)
    """
    try:
        from datetime import timedelta

        # ── Query parameters ─────────────────────────────────────────────
        today     = datetime.now().date()
        default_start = (today - timedelta(days=30)).isoformat()
        default_end   = today.isoformat()

        start_date     = request.args.get('start_date',     default_start)
        end_date       = request.args.get('end_date',       default_end)
        filter_category = request.args.get('category',      '').strip()
        filter_method   = request.args.get('payment_method','').strip()
        filter_type     = request.args.get('type',          '').strip()
        sort_param      = request.args.get('sort',          'date_desc')
        page            = max(1, int(request.args.get('page',     1)))
        per_page        = min(200, max(1, int(request.args.get('per_page', 50))))
        search          = request.args.get('search', '').strip()

        # Validate dates
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date,   '%Y-%m-%d')
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        conn   = get_db()
        cursor = conn.cursor()

        # ── Verify user exists ────────────────────────────────────────────
        cursor.execute('SELECT user_id FROM users WHERE user_id = %s', (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'User not found'}), 404

        # ── Opening balance: net of ALL transactions before start_date ────
        cursor.execute('''
            SELECT COALESCE(SUM(
                CASE
                    WHEN ct.transaction_type IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED')
                    THEN  ct.amount_cents
                    ELSE -ct.amount_cents
                END
            ), 0) AS net_before
            FROM cash_transactions ct
            JOIN cash_wallets cw  ON ct.wallet_id  = cw.wallet_id
            JOIN businesses  b    ON cw.business_id = b.business_id
            WHERE b.user_id = %s AND ct.transaction_date < %s
        ''', (user_id, start_date))
        opening_balance_cents = cursor.fetchone()['net_before']

        # ── Base query – unfiltered in-period totals for summary ──────────
        cursor.execute('''
            SELECT
                COALESCE(SUM(CASE WHEN ct.transaction_type IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED')
                                  THEN ct.amount_cents ELSE 0 END), 0) AS total_income_cents,
                COALESCE(SUM(CASE WHEN ct.transaction_type NOT IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED')
                                  THEN ct.amount_cents ELSE 0 END), 0) AS total_expense_cents,
                COUNT(*) AS tx_count
            FROM cash_transactions ct
            JOIN cash_wallets cw  ON ct.wallet_id  = cw.wallet_id
            JOIN businesses  b    ON cw.business_id = b.business_id
            WHERE b.user_id = %s
              AND ct.transaction_date BETWEEN %s AND %s
        ''', (user_id, start_date, end_date))
        summary_row = cursor.fetchone()
        total_income_cents  = summary_row['total_income_cents']
        total_expense_cents = summary_row['total_expense_cents']
        closing_balance_cents = opening_balance_cents + total_income_cents - total_expense_cents

        # ── Filtered query ────────────────────────────────────────────────
        conditions = [
            'b.user_id = %s',
            'ct.transaction_date BETWEEN %s AND %s'
        ]
        params = [user_id, start_date, end_date]

        if filter_category:
            conditions.append('ct.category = %s')
            params.append(filter_category)
        if filter_method:
            conditions.append('ct.payment_method = %s')
            params.append(filter_method)
        if filter_type:
            conditions.append('ct.transaction_type = %s')
            params.append(filter_type)
        if search:
            conditions.append("LOWER(ct.source_destination) LIKE %s")
            params.append(f'%{search.lower()}%')

        where_clause = ' AND '.join(conditions)

        # Sorting
        sort_map = {
            'date_desc':   'ct.transaction_date DESC, ct.recorded_at DESC',
            'date_asc':    'ct.transaction_date ASC,  ct.recorded_at ASC',
            'amount_desc': 'ct.amount_cents DESC',
            'amount_asc':  'ct.amount_cents ASC',
        }
        order_clause = sort_map.get(sort_param, sort_map['date_desc'])

        # Count for pagination
        cursor.execute(f'''
            SELECT COUNT(*) AS cnt
            FROM cash_transactions ct
            JOIN cash_wallets cw ON ct.wallet_id  = cw.wallet_id
            JOIN businesses  b   ON cw.business_id = b.business_id
            WHERE {where_clause}
        ''', params)
        total_filtered = cursor.fetchone()['cnt']

        # Fetch page
        offset = (page - 1) * per_page
        cursor.execute(f'''
            SELECT
                ct.cash_transaction_id  AS id,
                ct.transaction_type,
                ct.amount_cents,
                ct.payment_method,
                ct.source_destination,
                ct.category,
                ct.transaction_date,
                ct.recorded_at,
                ct.entry_method,
                ct.verified,
                ct.receipt_image_path
            FROM cash_transactions ct
            JOIN cash_wallets cw ON ct.wallet_id  = cw.wallet_id
            JOIN businesses  b   ON cw.business_id = b.business_id
            WHERE {where_clause}
            ORDER BY {order_clause}
            LIMIT %s OFFSET %s
        ''', params + [per_page, offset])
        rows = cursor.fetchall()

        # ── Running balance ───────────────────────────────────────────────
        # For running balance we need all filtered transactions sorted by date ASC
        if sort_param in ('date_asc', 'date_desc'):
            # Fetch ALL filtered transactions in date ASC order for running balance
            cursor.execute(f'''
                SELECT
                    ct.cash_transaction_id AS id,
                    ct.transaction_type,
                    ct.amount_cents
                FROM cash_transactions ct
                JOIN cash_wallets cw ON ct.wallet_id  = cw.wallet_id
                JOIN businesses  b   ON cw.business_id = b.business_id
                WHERE {where_clause}
                ORDER BY ct.transaction_date ASC, ct.recorded_at ASC
            ''', params)
            all_rows_for_balance = cursor.fetchall()

            # Build id -> running_balance dict (keep as int cents for precision)
            running = int(opening_balance_cents)
            balance_map = {}
            for r in all_rows_for_balance:
                if r['transaction_type'] in ('CASH_IN', 'DIGITAL_IN', 'CREDIT_COLLECTED'):
                    running += int(r['amount_cents'])
                else:
                    running -= int(r['amount_cents'])
                balance_map[r['id']] = running
        else:
            balance_map = {}

        # ── Category breakdown ─────────────────────────────────────────────
        cursor.execute('''
            SELECT
                ct.category,
                COALESCE(SUM(CASE WHEN ct.transaction_type IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED')
                                  THEN ct.amount_cents ELSE 0 END), 0) AS income_cents,
                COALESCE(SUM(CASE WHEN ct.transaction_type NOT IN ('CASH_IN','DIGITAL_IN','CREDIT_COLLECTED')
                                  THEN ct.amount_cents ELSE 0 END), 0) AS expense_cents
            FROM cash_transactions ct
            JOIN cash_wallets cw ON ct.wallet_id  = cw.wallet_id
            JOIN businesses  b   ON cw.business_id = b.business_id
            WHERE b.user_id = %s
              AND ct.transaction_date BETWEEN %s AND %s
            GROUP BY ct.category
        ''', (user_id, start_date, end_date))

        category_breakdown = {}
        for row in cursor.fetchall():
            category_breakdown[row['category'] or 'OTHER'] = {
                'income':   round(float(row['income_cents'])  / 100, 2),
                'expenses': round(float(row['expense_cents']) / 100, 2),
            }

        conn.close()

        # ── Build transaction list ─────────────────────────────────────────
        transactions_out = []
        for row in rows:
            is_credit = row['transaction_type'] in ('CASH_IN', 'DIGITAL_IN', 'CREDIT_COLLECTED')
            amount    = float(row['amount_cents']) / 100
            tx_id     = row['id']

            # recorded_at may be a datetime object (psycopg2) or string
            raw_recorded = row['recorded_at']
            if raw_recorded is None:
                recorded_at_str = ''
                tx_time = ''
            elif hasattr(raw_recorded, 'isoformat'):
                recorded_at_str = raw_recorded.isoformat()
                tx_time = raw_recorded.strftime('%H:%M:%S')
            else:
                recorded_at_str = str(raw_recorded)
                tx_time = recorded_at_str.split('T')[1][:8] if 'T' in recorded_at_str else (recorded_at_str.split(' ')[1][:8] if ' ' in recorded_at_str else '')

            # transaction_date may be a date object
            raw_date = row['transaction_date']
            tx_date = raw_date.isoformat() if hasattr(raw_date, 'isoformat') else str(raw_date)

            bal_cents = balance_map.get(tx_id)
            transactions_out.append({
                'id':            tx_id,
                'date':          tx_date,
                'time':          tx_time,
                'description':   row['source_destination'] or '',
                'reference':     f'TXN-{tx_id:06d}',
                'category':      row['category'] or 'OTHER',
                'type':          row['transaction_type'],
                'paymentMethod': row['payment_method'] or 'CASH',
                'debit':         0.0 if is_credit else amount,
                'credit':        amount if is_credit else 0.0,
                'balance':       float(bal_cents) / 100 if bal_cents is not None else None,
                'entryMethod':   row['entry_method'] or 'MANUAL',
                'verified':      bool(row['verified']),
                'receiptImage':  row['receipt_image_path'],
                'recordedAt':    recorded_at_str,
            })

        # Period days
        from datetime import date as date_type
        d_start = datetime.strptime(start_date, '%Y-%m-%d').date()
        d_end   = datetime.strptime(end_date,   '%Y-%m-%d').date()
        period_days = (d_end - d_start).days + 1

        return jsonify({
            'success': True,
            'period': {
                'startDate': start_date,
                'endDate':   end_date,
                'days':      period_days,
            },
            'summary': {
                'openingBalance':    round(float(opening_balance_cents)  / 100, 2),
                'totalIncome':       round(float(total_income_cents)     / 100, 2),
                'totalExpenses':     round(float(total_expense_cents)    / 100, 2),
                'closingBalance':    round(float(closing_balance_cents)  / 100, 2),
                'transactionCount':  int(summary_row['tx_count']),
            },
            'pagination': {
                'page':       page,
                'perPage':    per_page,
                'total':      int(total_filtered),
                'totalPages': max(1, -(-int(total_filtered) // per_page)),  # ceiling div
            },
            'transactions':       transactions_out,
            'categoryBreakdown':  {
                cat: {'income': round(float(v['income']), 2), 'expenses': round(float(v['expenses']), 2)}
                for cat, v in category_breakdown.items()
            },
        }), 200

    except Exception as e:
        print(f"❌ Ledger error: {e}")
        import traceback; traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# CASH WALLET ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

from wallet_manager import WalletManager, InsufficientBalanceError, InvalidPaymentMethodError, NegativeAmountError


def get_wallet_manager():
    return WalletManager(get_db())


@app.route('/api/wallet/<int:user_id>/balance', methods=['GET'])
def get_wallet_balance(user_id):
    """Full wallet balance breakdown for a user"""
    try:
        wm     = get_wallet_manager()
        result = wm.get_wallet_balance(user_id)
        if 'error' in result:
            return jsonify({'success': False, 'error': result['error']}), 404
        return jsonify({'success': True, **result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wallet/<int:wallet_id>/transactions', methods=['GET'])
def get_wallet_transactions(wallet_id):
    """Get transaction history for a wallet with optional filters"""
    try:
        filters = {
            'start_date':     request.args.get('startDate'),
            'end_date':       request.args.get('endDate'),
            'type':           request.args.get('type'),
            'payment_method': request.args.get('paymentMethod'),
            'category':       request.args.get('category'),
            'min_amount':     request.args.get('minAmount'),
            'max_amount':     request.args.get('maxAmount'),
            'limit':          int(request.args.get('limit', 50)),
        }
        filters = {k: v for k, v in filters.items() if v is not None}

        wm   = get_wallet_manager()
        txns = wm.get_transaction_history(wallet_id, filters)
        return jsonify({'success': True, 'transactions': txns, 'count': len(txns)}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wallet/<int:wallet_id>/transactions', methods=['POST'])
def add_wallet_transaction(wallet_id):
    """Add a transaction via WalletManager (validates balance)"""
    try:
        data = request.json
        wm   = get_wallet_manager()
        result = wm.add_transaction(wallet_id, {
            'type':           data.get('type'),
            'amount':         float(data.get('amount', 0)),
            'payment_method': data.get('paymentMethod', 'CASH'),
            'description':    data.get('description', ''),
            'category':       data.get('category', 'OTHER'),
            'date':           data.get('date'),
            'time':           data.get('time'),
        })
        sync_to_obs()
        return jsonify(result), 201
    except InsufficientBalanceError as e:
        return jsonify({'success': False, 'error': str(e), 'code': 'INSUFFICIENT_BALANCE'}), 400
    except (NegativeAmountError, InvalidPaymentMethodError) as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wallet/transactions/<int:transaction_id>', methods=['DELETE'])
def delete_wallet_transaction(transaction_id):
    """Delete a transaction and reverse its balance effect"""
    try:
        wallet_id = request.args.get('walletId')
        if not wallet_id:
            return jsonify({'success': False, 'error': 'walletId query param required'}), 400
        wm     = get_wallet_manager()
        result = wm.delete_transaction(transaction_id, int(wallet_id))
        sync_to_obs()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wallet/<int:wallet_id>/reconcile', methods=['POST'])
def reconcile_wallet_cash(wallet_id):
    """Reconcile physical cash with system records"""
    try:
        data        = request.json
        actual_cash = float(data.get('actualCash', 0))
        wm          = get_wallet_manager()
        result      = wm.reconcile_cash(wallet_id, actual_cash)
        return jsonify({'success': True, **result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wallet/<int:wallet_id>/analytics', methods=['GET'])
def get_wallet_analytics(wallet_id):
    """Wallet analytics for 7days / 30days / 90days / all"""
    try:
        period = request.args.get('period', '30days')
        wm     = get_wallet_manager()
        result = wm.get_analytics(wallet_id, period)
        return jsonify({'success': True, **result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/wallet/<int:wallet_id>/daily-summary', methods=['GET'])
def get_wallet_daily_summary(wallet_id):
    """Income/expense/net for a specific day"""
    try:
        date   = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        wm     = get_wallet_manager()
        result = wm.get_daily_summary(wallet_id, date)
        return jsonify({'success': True, **result}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# BIZ-BANTU CHAT ENDPOINT WITH REAL USER DATA
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Biz-Bantu AI Chat with Real Business Data Access

    PRIVACY: Only accesses data for the logged-in user
    """
    try:
        data = request.json

        if not data.get('message'):
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400

        user_message = data['message']
        user_context = data.get('userContext', {})
        user_id = user_context.get('userId')

        if not user_id:
            return jsonify({
                'success': False,
                'error': 'User ID is required for personalized advice'
            }), 400

        print(f"💬 Chat request from User ID: {user_id}")
        print(f"📝 Message: {user_message}")

        # ═══════════════════════════════════════════════════════════════
        # FETCH REAL BUSINESS DATA (Privacy-protected)
        # ═══════════════════════════════════════════════════════════════
        try:
            business_context = bi_helper.get_user_business_context(user_id)

            if 'error' in business_context:
                return jsonify({
                    'success': False,
                    'error': 'Unable to fetch business data'
                }), 404

            # Preserve the UI-selected language before merging.
            # business_context carries preferred_language from the DB (always 'en'),
            # which would overwrite the language the user selected in Biz-Bantu.
            user_selected_language = user_context.get('language', 'en')

            enhanced_context = {**user_context, **business_context}

            # Restore the UI language — never let the DB value override it.
            enhanced_context['language'] = user_selected_language

            print(f"✅ Fetched real data: R{business_context.get('wallet', {}).get('totalBalance', 0):,.2f} balance")
            print(f"🌍 Language: {user_selected_language}")

        except Exception as e:
            print(f"⚠️  Could not fetch business data: {str(e)}")
            enhanced_context = user_context

        # ═══════════════════════════════════════════════════════════════
        # GET AI RESPONSE (Now with real data!)
        # ═══════════════════════════════════════════════════════════════
        language = enhanced_context.get('language', 'en')

        ai_response = pangu_helper.get_business_advice(
            question=user_message,
            user_context=enhanced_context,
            language=language
        )

        if ai_response['success']:
            print(f"✅ Response generated with real data (intent: {ai_response['intent']})")

            return jsonify({
                'success': True,
                'response': ai_response['response'],
                'suggestions': ai_response['suggestions'],
                'intent': ai_response['intent'],
                'timestamp': ai_response['timestamp'],
                'usedRealData': ai_response.get('usedRealData', False),
                'language': language
            }), 200
        else:
            raise Exception("Failed to generate response")

    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Chat error: {str(e)}'
        }), 500

# ═══════════════════════════════════════════════════════════════════════════
# END: Chat API Endpoint
# ═══════════════════════════════════════════════════════════════════════════

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 MzansiPulse Auth API Server Starting...")
    print("=" * 80)

    print(f"\n📍 Database Mode: {'OBS (smart sync)' if obs_manager else 'Local'}")
    print(f"📍 Database Path: {os.path.abspath(get_db_path())}")
    print(f"🤖 Pangu AI: Initialized")
    print(f"📊 Business Intelligence: Ready")
    print(f"🌐 API URL: http://localhost:5000")
    print(f"📡 Endpoints:")
    print(f"   • GET  /api/health")
    print(f"   • POST /api/signup")
    print(f"   • POST /api/login")
    print(f"   • GET  /api/user/<id>")
    print(f"   • GET  /api/dashboard/<id>")
    print(f"   • POST /api/transactions")
    print(f"   • GET  /api/transactions?userId=<id>")
    print(f"   • POST /api/backup-to-obs")
    print(f"   • POST /api/chat")
    print(f"   • GET  /api/ledger/<id>")
    print(f"\n✅ Ready to accept requests!\n")
    print("=" * 80)

    app.run(debug=True, host='0.0.0.0', port=5000)