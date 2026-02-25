"""
MzansiPulse Authentication API
Flask server with OBS database integration
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
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

def get_db_path():
    """
    Get database path
    Uses OBS if configured, otherwise uses local file
    """
    if obs_manager:
        return obs_manager.get_database_path()
    else:
        return LOCAL_DB_PATH

def get_db():
    """Get database connection"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def sync_to_obs():
    """Upload database changes to OBS (after write operations)"""
    if obs_manager:
        try:
            obs_manager.upload_to_obs()
            print("✅ Database synced to OBS")
        except Exception as e:
            print(f"⚠️  Failed to sync to OBS: {e}")

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
        cursor.execute('SELECT user_id FROM users WHERE email = ?', (data['email'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': 'Email already registered'
            }), 409
        
        # Check if phone already exists
        cursor.execute('SELECT user_id FROM users WHERE phone_number = ?', (data['phone'],))
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        
        user_id = cursor.lastrowid
        
        # Insert business
        cursor.execute('''
            INSERT INTO businesses (
                user_id, business_name, business_type, province,
                township, verification_status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['businessName'],
            data['businessType'],
            data['location'].split(',')[-1].strip() if ',' in data['location'] else data['location'],
            data['location'].split(',')[0].strip() if ',' in data['location'] else data['location'],
            'PENDING',
            datetime.now().isoformat()
        ))
        
        business_id = cursor.lastrowid
        
        # Create cash wallet for the business
        cursor.execute('''
            INSERT INTO cash_wallets (
                business_id, virtual_balance_cents, cash_on_hand_cents,
                wallet_status, last_updated
            ) VALUES (?, 0, 0, 'ACTIVE', ?)
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
            WHERE u.user_id = ?
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
        
        # Fetch user by email
        cursor.execute('''
            SELECT 
                u.user_id, u.first_name, u.last_name, u.email, u.phone_number,
                u.password_hash, u.is_active,
                b.business_id, b.business_name, b.business_type, b.township, b.province
            FROM users u
            LEFT JOIN businesses b ON u.user_id = b.user_id
            WHERE u.email = ?
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
            SET last_login = ?
            WHERE user_id = ?
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
            WHERE u.user_id = ?
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

# ═══════════════════════════════════════════════════════════════════════════
# PART 2: BIZ-BANTU CHAT API ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════

# Import Pangu helper at the top of the file (after other imports)
from pangu_helper import PanguAIHelper

# Initialize Pangu helper (add after obs_manager initialization)
PANGU_PROJECT_ID = os.environ.get('PANGU_PROJECT_ID', 'demo-project')
PANGU_AK = os.environ.get('PANGU_ACCESS_KEY', OBS_AK)  # Can reuse OBS keys
PANGU_SK = os.environ.get('PANGU_SECRET_KEY', OBS_SK)

pangu_helper = PanguAIHelper(
    project_id=PANGU_PROJECT_ID,
    access_key=PANGU_AK,
    secret_key=PANGU_SK
)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Biz-Bantu AI Chat Endpoint
    
    Expected JSON body:
    {
        "message": "How can I get funding?",
        "userContext": {
            "userId": 1,
            "firstName": "Thandi",
            "businessName": "Mama Thandi's Spaza",
            "businessType": "SPAZA_SHOP",
            "location": "Soweto, Gauteng",
            "empowerScore": 542,
            "language": "en"
        },
        "chatHistory": [
            {"role": "user", "content": "previous message"},
            {"role": "assistant", "content": "previous response"}
        ]
    }
    
    Returns:
    {
        "success": true,
        "response": "AI response text",
        "suggestions": ["follow up 1", "follow up 2"],
        "intent": "FUNDING_INQUIRY",
        "timestamp": "2026-02-24T21:30:00"
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('message'):
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        user_message = data['message']
        user_context = data.get('userContext', {})
        chat_history = data.get('chatHistory', [])
        language = user_context.get('language', 'en')
        
        print(f"💬 Chat request from: {user_context.get('firstName', 'Unknown')}")
        print(f"📝 Message: {user_message}")
        
        # Get AI response from Pangu
        ai_response = pangu_helper.get_business_advice(
            question=user_message,
            user_context=user_context,
            language=language
        )
        
        if ai_response['success']:
            print(f"✅ Response generated (intent: {ai_response['intent']})")
            
            return jsonify({
                'success': True,
                'response': ai_response['response'],
                'suggestions': ai_response['suggestions'],
                'intent': ai_response['intent'],
                'timestamp': ai_response['timestamp']
            }), 200
        else:
            raise Exception("Failed to generate response")
        
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")
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
    # Upload local database to OBS on startup (if using OBS mode)
    if obs_manager and os.path.exists(LOCAL_DB_PATH):
        print("\n🔄 Syncing local database to OBS...")
        try:
            obs_manager.obs_client.putFile(
                bucketName=OBS_BUCKET,
                objectKey='mzansipulse.db',
                file_path=LOCAL_DB_PATH
            )
            print("✅ Local database synced to OBS")
        except Exception as e:
            print(f"⚠️  Sync failed: {e}")
    
    print(f"\n📍 Database Mode: {'OBS' if obs_manager else 'Local'}")
    print(f"\n📍 Database Mode: {'OBS' if obs_manager else 'Local'}")
    print(f"📍 Database Path: {os.path.abspath(get_db_path())}")
    print(f"🤖 Pangu AI: Initialized")
    print(f"🌐 API URL: http://localhost:5000")
    print(f"📡 Endpoints:")
    print(f"   • GET  /api/health")
    print(f"   • POST /api/signup")
    print(f"   • POST /api/login")
    print(f"   • GET  /api/user/<id>")
    print(f"   • POST /api/chat") 
    print(f"\n✅ Ready to accept requests!\n")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)