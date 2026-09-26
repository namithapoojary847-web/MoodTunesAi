import os
import requests
import json
from flask import Blueprint, request, jsonify, session
from database import get_db_connection

recommendation_bp = Blueprint('recommendations', __name__)

# Memory cache for iTunes audio preview URLs
PREVIEW_CACHE = {}

def get_audio_preview_url(artist, title):
    cache_key = f"{artist} - {title}".lower()
    if cache_key in PREVIEW_CACHE:
        return PREVIEW_CACHE[cache_key]

    try:
        query = f"{artist} {title}"
        url = f"https://itunes.apple.com/search?term={requests.utils.quote(query)}&entity=song&limit=1"
        res = requests.get(url, timeout=3).json()
        if res.get('results') and len(res['results']) > 0:
            preview_url = res['results'][0].get('previewUrl')
            PREVIEW_CACHE[cache_key] = preview_url
            return preview_url
    except Exception as e:
        print("iTunes API error for", cache_key, ":", e)

    PREVIEW_CACHE[cache_key] = None
    return None

# Mood to Music Metadata Database
MOOD_MUSIC_MAP = {
    "Happy": {
        "genre": "Upbeat Pop & Dance Hits",
        "description": "High-energy, uplifting tracks to match and boost your cheerful mood!",
        "tempo": "120 - 135 BPM",
        "badge_color": "#ffb703",
        "tracks": [
            {
                "id": "h1",
                "title": "Happy",
                "artist": "Pharrell Williams",
                "album": "Girl",
                "album_art": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
                "youtube_id": "ZbZSe6N_BXs",
                "duration": "3:53"
            },
            {
                "id": "h2",
                "title": "Can't Stop the Feeling!",
                "artist": "Justin Timberlake",
                "album": "Trolls OST",
                "album_art": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
                "youtube_id": "ru0K8uYEZWw",
                "duration": "3:56"
            },
            {
                "id": "h3",
                "title": "Uptown Funk",
                "artist": "Mark Ronson ft. Bruno Mars",
                "album": "Uptown Special",
                "album_art": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300&auto=format&fit=crop",
                "youtube_id": "OPf0YbXqDm0",
                "duration": "4:30"
            },
            {
                "id": "h4",
                "title": "Good as Hell",
                "artist": "Lizzo",
                "album": "Cuz I Love You",
                "album_art": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
                "youtube_id": "VuNIsY6JdUw",
                "duration": "2:39"
            },
            {
                "id": "h5",
                "title": "Levitating",
                "artist": "Dua Lipa",
                "album": "Future Nostalgia",
                "album_art": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=300&auto=format&fit=crop",
                "youtube_id": "TUVcZfQe-Kw",
                "duration": "3:23"
            }
        ]
    },
    "Sad": {
        "genre": "Acoustic, Lo-Fi & Gentle Piano",
        "description": "Soothing, reflective melodies to validate your emotions and bring calm comfort.",
        "tempo": "65 - 85 BPM",
        "badge_color": "#457b9d",
        "tracks": [
            {
                "id": "s1",
                "title": "Someone Like You",
                "artist": "Adele",
                "album": "21",
                "album_art": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=300&auto=format&fit=crop",
                "youtube_id": "hLQl3WQQoQ0",
                "duration": "4:45"
            },
            {
                "id": "s2",
                "title": "Fix You",
                "artist": "Coldplay",
                "album": "X&Y",
                "album_art": "https://images.unsplash.com/photo-1445372736177-6a98fe61557d?w=300&auto=format&fit=crop",
                "youtube_id": "k4V3Mo61fJM",
                "duration": "4:55"
            },
            {
                "id": "s3",
                "title": "All of Me",
                "artist": "John Legend",
                "album": "Love in the Future",
                "album_art": "https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=300&auto=format&fit=crop",
                "youtube_id": "450p7goxZqg",
                "duration": "4:29"
            },
            {
                "id": "s4",
                "title": "Say Something",
                "artist": "A Great Big World ft. Christina Aguilera",
                "album": "Is There Anybody Out There?",
                "album_art": "https://images.unsplash.com/photo-1487180144351-b8472da7d491?w=300&auto=format&fit=crop",
                "youtube_id": "-2U0Ivkn2hY",
                "duration": "3:49"
            },
            {
                "id": "s5",
                "title": "Skinny Love",
                "artist": "Birdy",
                "album": "Birdy",
                "album_art": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=300&auto=format&fit=crop",
                "youtube_id": "aNzCDt2eidg",
                "duration": "3:21"
            }
        ]
    },
    "Calm": {
    "genre": "Peaceful Piano",
    "description": "Gentle melodies to help you relax.",
    "tempo": "60-80 BPM",
    "badge_color": "#6EC6FF",
    "tracks": [
        {
            "id":"c1",
            "title":"River Flows In You",
            "artist":"Yiruma",
            "album":"First Love",
            "album_art":"https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300",
            "youtube_id":"7maJOI3QMu0"
        },
        {
            "id":"c2",
            "title":"Nuvole Bianche",
            "artist":"Ludovico Einaudi",
            "album":"Una Mattina",
            "album_art":"https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=300",
            "youtube_id":"xyY4IZ3JDFE"
        },
        {
            "id":"c3",
            "title":"Comptine d'un autre été",
            "artist":"Yann Tiersen",
            "album":"Amelie",
            "album_art":"https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=300",
            "youtube_id":"znfYwABeSZ0"
        },
        {
            "id":"c4",
            "title":"Weightless",
            "artist":"Marconi Union",
            "album":"Weightless",
            "album_art":"https://images.unsplash.com/photo-1501612780327-45045538702b?w=300",
            "youtube_id":"UfcAVejslrU"
        },
        {
            "id":"c5",
            "title":"Experience",
            "artist":"Ludovico Einaudi",
            "album":"In a Time Lapse",
            "album_art":"https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300",
            "youtube_id":"_VONMkKkdf4"
        }
    ]
},
"Romantic": {
    "genre":"Romantic Love Songs",
    "description":"Beautiful songs for heartfelt moments.",
    "tempo":"70-95 BPM",
    "badge_color":"#ff4d88",
    "tracks":[
        {
            "id":"r1",
            "title":"Perfect",
            "artist":"Ed Sheeran",
            "album":"Divide",
            "album_art":"https://images.unsplash.com/photo-1516280440614-37939bbacd81?w=300",
            "youtube_id":"2Vv-BfVoq4g"
        },
        {
            "id":"r2",
            "title":"All of Me",
            "artist":"John Legend",
            "album":"Love in the Future",
            "album_art":"https://images.unsplash.com/photo-1487180144351-b8472da7d491?w=300",
            "youtube_id":"450p7goxZqg"
        },
        {
            "id":"r3",
            "title":"Until I Found You",
            "artist":"Stephen Sanchez",
            "album":"Easy On My Eyes",
            "album_art":"https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300",
            "youtube_id":"GxldQ9eX2wo"
        },
        {
            "id":"r4",
            "title":"Photograph",
            "artist":"Ed Sheeran",
            "album":"Multiply",
            "album_art":"https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=300",
            "youtube_id":"nSDgHBxUbVQ"
        },
        {
            "id":"r5",
            "title":"A Thousand Years",
            "artist":"Christina Perri",
            "album":"Twilight",
            "album_art":"https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300",
            "youtube_id":"rtOvBOTyX00"
        }
    ]
},
"Energetic":{
    "genre":"Workout Hits",
    "description":"High-energy tracks to keep you moving.",
    "tempo":"130-150 BPM",
    "badge_color":"#ff9800",
    "tracks":[
        {
            "id":"e1",
            "title":"Believer",
            "artist":"Imagine Dragons",
            "album":"Evolve",
            "album_art":"https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300",
            "youtube_id":"7wtfhZwyrcc"
        },
        {
            "id":"e2",
            "title":"Thunder",
            "artist":"Imagine Dragons",
            "album":"Evolve",
            "album_art":"https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300",
            "youtube_id":"fKopy74weus"
        },
        {
            "id":"e3",
            "title":"Stronger",
            "artist":"Kanye West",
            "album":"Graduation",
            "album_art":"https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300",
            "youtube_id":"PsO6ZnUZI0g"
        },
        {
            "id":"e4",
            "title":"Titanium",
            "artist":"David Guetta",
            "album":"Nothing But The Beat",
            "album_art":"https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=300",
            "youtube_id":"JRfuAukYTKg"
        },
        {
            "id":"e5",
            "title":"Hall of Fame",
            "artist":"The Script",
            "album":"#3",
            "album_art":"https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300",
            "youtube_id":"mk48xRzuNvA"
        }
    ]
},
"Relaxed":{
    "genre":"Lo-Fi & Chill",
    "description":"Smooth beats to unwind and recharge.",
    "tempo":"70-90 BPM",
    "badge_color":"#4CAF50",
    "tracks":[
        {
            "id":"re1",
            "title":"Sunflower",
            "artist":"Post Malone",
            "album":"Spider-Verse",
            "album_art":"https://images.unsplash.com/photo-1501612780327-45045538702b?w=300",
            "youtube_id":"ApXoWvfEYVU"
        },
        {
            "id":"re2",
            "title":"Lovely",
            "artist":"Billie Eilish",
            "album":"Single",
            "album_art":"https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300",
            "youtube_id":"V1Pl8CzNzCw"
        },
        {
            "id":"re3",
            "title":"Coffee",
            "artist":"beabadoobee",
            "album":"Patched Up",
            "album_art":"https://images.unsplash.com/photo-1511379938547-c1f69419868d?w=300",
            "youtube_id":"C6CeA6vRtW4"
        },
        {
            "id":"re4",
            "title":"Bloom",
            "artist":"The Paper Kites",
            "album":"States",
            "album_art":"https://images.unsplash.com/photo-1459749411175-04bf5292ceea?w=300",
            "youtube_id":"8inJtTG_DuU"
        },
        {
            "id":"re5",
            "title":"Ocean Eyes",
            "artist":"Billie Eilish",
            "album":"Don't Smile at Me",
            "album_art":"https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300",
            "youtube_id":"viimfQi_pUw"
        }
    ]
},
    "Angry": {
        "genre": "High-Energy Rock, Metal & Heavy Beats",
        "description": "Intense, powerful rhythms to help release frustration and channel energy.",
        "tempo": "130 - 155 BPM",
        "badge_color": "#e63946",
        "tracks": [
            {
                "id": "a1",
                "title": "Numb",
                "artist": "Linkin Park",
                "album": "Meteora",
                "album_art": "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=300&auto=format&fit=crop",
                "youtube_id": "kXYiU_JCYtU",
                "duration": "3:07"
            },
            {
                "id": "a2",
                "title": "In the End",
                "artist": "Linkin Park",
                "album": "Hybrid Theory",
                "album_art": "https://images.unsplash.com/photo-1498038432885-c6f3f1b912ee?w=300&auto=format&fit=crop",
                "youtube_id": "eVTXPUF4Oz4",
                "duration": "3:36"
            },
            {
                "id": "a3",
                "title": "Believer",
                "artist": "Imagine Dragons",
                "album": "Evolve",
                "album_art": "https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?w=300&auto=format&fit=crop",
                "youtube_id": "7wtfhZwyrYY",
                "duration": "3:24"
            },
            {
                "id": "a4",
                "title": "Stronger",
                "artist": "Kanye West",
                "album": "Graduation",
                "album_art": "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=300&auto=format&fit=crop",
                "youtube_id": "PsO6ZnUZI0g",
                "duration": "5:11"
            },
            {
                "id": "a5",
                "title": "Eye of the Tiger",
                "artist": "Survivor",
                "album": "Eye of the Tiger",
                "album_art": "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?w=300&auto=format&fit=crop",
                "youtube_id": "btPJPFnesV4",
                "duration": "4:04"
            }
        ]
    },
    
    "Neutral": {
        "genre": "Lo-Fi Beats, Chill Hop & Study Vibes",
        "description": "Smooth, relaxed background grooves perfect for focus, work, and steady flow.",
        "tempo": "85 - 105 BPM",
        "badge_color": "#2a9d8f",
        "tracks": [
            {
                "id": "n1",
                "title": "Lofi Hip Hop Radio ",
                "artist": "Lofi Girl",
                "album": "Lofi Sessions",
                "album_art": "https://images.unsplash.com/photo-1518609878373-06d740f60d8b?w=300&auto=format&fit=crop",
                "youtube_id": "jfKfPfyJRdk",
                "duration": "Live"
            },
            {
                "id": "n2",
                "title": "Sunflower",
                "artist": "Post Malone & Swae Lee",
                "album": "Spider-Man: Into the Spider-Verse",
                "album_art": "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=300&auto=format&fit=crop",
                "youtube_id": "ApXoWvfEYVU",
                "duration": "2:38"
            },
            {
    "id": "n3",
    "title": "Resonance",
    "artist": "HOME",
    "album": "Odyssey",
    "album_art": "https://images.unsplash.com/photo-1478737270239-2f02b77fc618?w=300&auto=format&fit=crop",
    "youtube_id": "8GW6sLrK40k",
    "duration": "3:32"
},
            {
                "id": "n4",
                "title": "Coffee Break",
                "artist": "Kalaido",
                "album": "Moonlit Tales",
                "album_art": "https://images.unsplash.com/photo-1487180144351-b8472da7d491?w=300&auto=format&fit=crop",
                "youtube_id": "1fueZCTYkpA",
                "duration": "2:45"
            },
            {
                "id": "n5",
                "title": "Comfort Chain",
                "artist": "Instupendo",
                "album": "Friends",
                "album_art": "https://images.unsplash.com/photo-1507838153414-b4b713384a76?w=300&auto=format&fit=crop",
                "youtube_id": "1m0t1-tM4-w",
                "duration": "3:10"
            }
        ]
    }
}

@recommendation_bp.route('/api/recommendations/<emotion>', methods=['GET'])
def get_recommendations(emotion):
    emotion_clean = emotion.capitalize()
    if emotion_clean not in MOOD_MUSIC_MAP:
        emotion_clean = "Neutral"

    data = MOOD_MUSIC_MAP[emotion_clean]
    
    # Check if user has saved any of these songs as favourites
    user_id = session.get('user_id')
    favourite_ids = set()
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT song_id FROM favourite_songs WHERE user_id = ?', (user_id,))
        favourite_ids = {row['song_id'] for row in cursor.fetchall()}
        conn.close()

    tracks_formatted = []
    for track in data['tracks']:
        track_copy = dict(track)
        track_copy['is_favourite'] = track['id'] in favourite_ids
        
        # Attach high-quality direct audio preview stream URL
        preview_url = get_audio_preview_url(track['artist'], track['title'])
        track_copy['preview_url'] = preview_url
        
        tracks_formatted.append(track_copy)

    return jsonify({
        'success': True,
        'emotion': emotion_clean,
        'genre': data['genre'],
        'description': data['description'],
        'tempo': data['tempo'],
        'badge_color': data['badge_color'],
        'tracks': tracks_formatted
    })

@recommendation_bp.route('/api/favourites/toggle', methods=['POST'])
def toggle_favourite():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'error': 'Login required to save favourite songs.'}), 401

    data = request.get_json() or {}
    song_id = data.get('song_id')
    title = data.get('title')
    artist = data.get('artist')
    mood = data.get('mood', 'Neutral')
    youtube_id = data.get('youtube_id')
    album_art = data.get('album_art', '')

    if not song_id or not title:
        return jsonify({'success': False, 'error': 'Missing song parameters.'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM favourite_songs WHERE user_id = ? AND song_id = ?', (user_id, song_id))
    existing = cursor.fetchone()

    if existing:
        cursor.execute('DELETE FROM favourite_songs WHERE id = ?', (existing['id'],))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'is_favourite': False, 'message': 'Removed from favourites.'})
    else:
        cursor.execute(
            'INSERT INTO favourite_songs (user_id, song_id, title, artist, album_art, mood, youtube_id) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (user_id, song_id, title, artist, album_art, mood, youtube_id)
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'is_favourite': True, 'message': 'Saved to favourites!'})

@recommendation_bp.route('/api/favourites', methods=['GET'])
def get_user_favourites():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'favourites': []})

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM favourite_songs WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    rows = cursor.fetchall()
    conn.close()

    favourites = [dict(row) for row in rows]
    return jsonify({'success': True, 'favourites': favourites})
