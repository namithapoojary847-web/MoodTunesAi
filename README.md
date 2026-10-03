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
        


🗄️ Database Schema
users — id, username, email, password_hash, created_at
emotion_logs — id, user_id (nullable for guests), emotion, confidence, breakdown_json, created_at
favourite_songs — id, user_id, song_id, title, artist, album_art, mood, youtube_id, preview_url, created_at
playlists — id, user_id, name, mood, songs_json, created_at

Run python database.py on its own anytime to (re)initialize the schema.


