"""
MzansiPulse Authentication API
Local Flask server for signup/login with SQLite
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Allow requests from Vue frontend

# Database path
DB_PATH = os.path.join('..', 'database', 'mzansipulse.db')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

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
        'message': 'MzansiPulse Auth API is running!'
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

# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 MzansiPulse Auth API Server Starting...")
    print("=" * 80)
    print(f"\n📍 Database: {os.path.abspath(DB_PATH)}")
    print(f"🌐 API URL: http://localhost:5000")
    print(f"📡 Endpoints:")
    print(f"   • GET  /api/health")
    print(f"   • POST /api/signup")
    print(f"   • POST /api/login")
    print(f"   • GET  /api/user/<id>")
    print(f"\n✅ Ready to accept requests!\n")
    print("=" * 80)
    
    app.run(debug=True, host='0.0.0.0', port=5000)