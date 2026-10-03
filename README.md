🎵 MoodTunes AI

Music that understands your emotions.

MoodTunes AI is a Flask-based web app that detects a user's mood — either via live webcam facial emotion detection or manual selection — and recommends a curated set of songs to match it. It logs every detection for mood-history analytics and lets users save favourite tracks to their account.

✨ Features
Live webcam mood detection using OpenCV Haar cascades — no external ML API required.
Six recognized emotions: Happy, Sad, Angry, Fear, Surprise, Neutral.
Mood-based music recommendations with genre, tempo, and a curated track list per emotion.
In-browser audio previews (30-second clips) plus a direct link to the full track on YouTube.
User accounts — register/login with hashed passwords, session-based auth.
Favourites — save tracks per user, view them later on a dedicated page.
Mood analytics dashboard — pie chart of mood distribution, weekly trend chart, and a history table, powered by Chart.js.
Guest mode — mood detection and recommendations work without an account; favourites require login.

🛠️ Tech Stack
Layer	Tech
Backend	Python, Flask, Flask-CORS
Emotion detection	OpenCV (cv2), NumPy, Haar cascade classifiers
Auth	Werkzeug password hashing, Flask sessions
Database	SQLite (moodtunes.db)
Frontend	HTML5, CSS3, vanilla JavaScript
Charts	Chart.js
Fonts / Icons	Google Fonts, Font Awesome

📁 Project Structure
Project/
├── app.py                   # App entry point, routes, blueprint registration
├── auth.py                  # /api/register, /api/login, /api/logout, /api/user
├── database.py               # SQLite connection + schema (init_db)
├── emotion_detector.py       # Webcam frame → emotion breakdown (OpenCV)
├── recommendation_engine.py  # Emotion → genre / tempo / track list
├── analytics.py               # /api/log_emotion, /api/analytics/summary
├── test_app.py                # Unit tests (unittest)
├── moodtunes.db                # SQLite database (auto-created on first run)
│
├── templates/
│   ├── welcome.html          # Public landing page
│   ├── index.html            # Main dashboard (mood detector + recommendations)
│   ├── analytics.html        # Mood insights / charts page
│   └── favourites.html       # Saved tracks page
│
└── static/
    ├── css/
    │   ├── style.css          # Dashboard, analytics & favourites styling
    │   └── welcome.css        # Landing page styling
    └── js/
        ├── auth.js
        ├── player.js
        ├── webcam.js
        ├── script.js
        ├── mood.js
        ├── analytics.js
        └── welcome.js
        
🚀 Getting Started
1. Clone / open the project folder

Make sure app.py sits at the project root, with templates/ and static/ as direct subfolders — Flask's url_for('static', ...) and render_template() depend on that exact layout.

2. Create a virtual environment (recommended)
bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
3. Install dependencies
bash
pip install flask flask-cors opencv-python numpy werkzeug

(If you keep a requirements.txt, run pip install -r requirements.txt instead. Generate one anytime with pip freeze > requirements.txt.)

4. Run the app
bash
python app.py

You should see:

Starting MoodTunes Server on http://127.0.0.1:5000
5. Open it in your browser — through the server, not the file

Go to:

http://127.0.0.1:5000/ → landing page (welcome.html)
http://127.0.0.1:5000/app → main dashboard (index.html)
http://127.0.0.1:5000/analytics → mood insights
http://127.0.0.1:5000/favourites → saved tracks

⚠️ Don't double-click index.html in File Explorer. The templates use Jinja ({{ url_for(...) }}) for CSS/JS paths, which only resolves when Flask actually renders the page. Opening the raw file shows unstyled HTML with broken links.

🔌 API Reference
Method	Endpoint	Description
POST	/api/register	Create an account (username, email, password)
POST	/api/login	Log in (identifier, password)
POST	/api/logout	Clear the session
GET	/api/user	Get the current logged-in user
POST	/api/detect_emotion	Send a base64 image, get back the detected emotion + confidence breakdown
GET	/api/recommendations/<emotion>	Get genre, tempo, description, and tracks for an emotion
POST	/api/log_emotion	Log a detected/selected emotion for analytics
GET	/api/analytics/summary	Mood distribution, weekly trend, and recent history
GET / POST	/api/favourites	Get / toggle saved favourite tracks (login required to persist)

Supported emotions throughout the app: Happy, Sad, Angry, Fear, Surprise, Neutral.

🗄️ Database Schema
users — id, username, email, password_hash, created_at
emotion_logs — id, user_id (nullable for guests), emotion, confidence, breakdown_json, created_at
favourite_songs — id, user_id, song_id, title, artist, album_art, mood, youtube_id, preview_url, created_at
playlists — id, user_id, name, mood, songs_json, created_at

Run python database.py on its own anytime to (re)initialize the schema.

🧪 Running Tests
bash
python -m unittest test_app.py

Covers database initialization, emotion detection on a synthetic image, registration/login, the recommendations API, and the analytics API.

🌐 Sharing a Live Demo

For a quick live demo without a full deployment, run the app locally as usual and tunnel it with ngrok:

bash
ngrok http 5000

This gives you a temporary public https:// URL that forwards straight to your local server — no code changes, and everything (SQLite, OpenCV) behaves exactly as it does on your machine. The link only stays live while your laptop and python app.py are both running.

For something more permanent, deploy to a host that supports a persistent Python process and disk — Render, PythonAnywhere, or Railway/Fly.io are good fits. Netlify is not, since it's built for static sites/serverless functions and can't support OpenCV or a writable SQLite file.

🔮 Planned Enhancements
Facial emotion detection accuracy improvements (current model uses handcrafted feature heuristics, not a trained CNN)
Voice-based emotion recognition
AI-generated custom playlists
Spotify / YouTube Music API integration for full-length playback
Persistent, cross-device recently-played history
