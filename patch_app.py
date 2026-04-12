import re
import os

app_path = "c:/Users/ASUS/Downloads/Gastric-Cancer-Risk-Estimation---main/Gastric-Cancer-Risk-Estimation---main/app.py"

with open(app_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    '''import sqlite3
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify, render_template, make_response''',
    '''import datetime
import os
from flask import Flask, request, jsonify, render_template, make_response, send_from_directory, redirect, url_for'''
)

# 2. Remove init_db
content = re.sub(r'def init_db\(\):.*?init_db\(\)', '', content, flags=re.DOTALL)

# 3. Remove migrate_db
content = re.sub(r'def migrate_db\(\):.*?migrate_db\(\)', '', content, flags=re.DOTALL)

# 4. Remove /api/auth/signup and /api/auth/login routes entirely
content = re.sub(r'@app\.route\(\'/api/auth/signup\'.*?@app\.route\(\'/\'\)', "@app.route('/')", content, flags=re.DOTALL)

# 5. Update /risk to redirect nicely
old_risk = '''@app.route('/risk')
def risk():
    """Risk assessment page."""
    name = request.cookies.get('username')
    return render_template('index.html', name=name)'''

new_risk = '''@app.route('/risk')
def risk():
    """Risk assessment page."""
    name = request.cookies.get('username')
    if not name:
        return redirect('/login')
    return render_template('index.html', name=name)'''

content = content.replace(old_risk, new_risk)

# 6. Update /login and /signup
old_login_signup = '''@app.route('/login')
def login():
    """Login page - redirects to React app."""
    return render_template('login.html')

@app.route('/signup')
def signup():
    """Signup page - redirects to React app."""
    return render_template('signup.html')'''

new_login_signup = '''@app.route('/login')
@app.route('/signup')
def serve_react():
    """Serve React frontend build directory."""
    return send_from_directory('frontend/dist', 'index.html')

@app.route('/assets/<path:path>')
def serve_react_assets(path):
    """Serve React frontend assets."""
    return send_from_directory('frontend/dist/assets', path)
    
@app.route('/logout')
def logout():
    resp = redirect('/login')
    resp.set_cookie('username', '', expires=0)
    return resp'''

content = content.replace(old_login_signup, new_login_signup)

with open(app_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app.py successfully!")
