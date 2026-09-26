import os
import sys
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from database import init_db
from emotion_detector import detect_emotion
from auth import auth_bp
from recommendation_engine import recommendation_bp
from analytics import analytics_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'moodtunes_key_987654321_secure')
CORS(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(recommendation_bp)
app.register_blueprint(analytics_bp)

# Initialize Database on Startup
with app.app_context():
    init_db()

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/app')
def index():
    return render_template('index.html')

@app.route('/analytics')
def analytics_page():
    return render_template('analytics.html')

@app.route('/favourites')
def favourites_page():
    return render_template('favourites.html')

@app.route('/auth')
def auth_page():
    return render_template('auth.html')

@app.route('/api/detect_emotion', methods=['POST'])
def api_detect_emotion():
    data = request.get_json() or {}
    image_data = data.get('image')

    if not image_data:
        return jsonify({'success': False, 'error': 'No image data provided.'}), 400

    result = detect_emotion(image_data)
    return jsonify(result)

if __name__ == '__main__':
    print("Starting MoodTunes Server on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
