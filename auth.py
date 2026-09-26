from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from database import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'success': False, 'error': 'Please fill in all fields.'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'error': 'Password must be at least 6 characters.'}), 400

    password_hash = generate_password_hash(password)

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        session['user_id'] = user_id
        session['username'] = username
        session['email'] = email

        return jsonify({
            'success': True,
            'message': 'Registration successful!',
            'user': {'id': user_id, 'username': username, 'email': email}
        })
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'error': 'Username or Email already exists.'}), 409
    finally:
        conn.close()

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email_or_username = data.get('identifier', '').strip().lower()
    password = data.get('password', '')

    if not email_or_username or not password:
        return jsonify({'success': False, 'error': 'Please provide email/username and password.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM users WHERE LOWER(email) = ? OR LOWER(username) = ?',
        (email_or_username, email_or_username)
    )
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'error': 'Invalid credentials.'}), 401

    session['user_id'] = user['id']
    session['username'] = user['username']
    session['email'] = user['email']

    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {'id': user['id'], 'username': user['username'], 'email': user['email']}
    })

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully.'})

@auth_bp.route('/api/user', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        return jsonify({
            'logged_in': True,
            'user': {
                'id': session['user_id'],
                'username': session['username'],
                'email': session['email']
            }
        })
    return jsonify({'logged_in': False, 'user': None})
