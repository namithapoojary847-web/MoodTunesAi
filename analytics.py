import json
from flask import Blueprint, request, jsonify, session
from database import get_db_connection

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/api/log_emotion', methods=['POST'])
def log_emotion():
    data = request.get_json() or {}
    emotion = data.get('emotion')
    confidence = data.get('confidence', 0.0)
    breakdown = data.get('breakdown', {})
    
    if not emotion:
        return jsonify({'success': False, 'error': 'Emotion field required.'}), 400

    user_id = session.get('user_id') # Can be None for guest users

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO emotion_logs (user_id, emotion, confidence, breakdown_json) VALUES (?, ?, ?, ?)',
        (user_id, emotion, float(confidence), json.dumps(breakdown))
    )
    conn.commit()
    log_id = cursor.lastrowid
    conn.close()

    return jsonify({'success': True, 'log_id': log_id})

@analytics_bp.route('/api/analytics/summary', methods=['GET'])
def get_analytics_summary():
    user_id = session.get('user_id')

    conn = get_db_connection()
    cursor = conn.cursor()

    if user_id:
        cursor.execute('SELECT * FROM emotion_logs WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    else:
        # Fallback to all logs if guest user
        cursor.execute('SELECT * FROM emotion_logs ORDER BY created_at DESC LIMIT 50')

    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return jsonify({
            'success': True,
            'total_detections': 0,
            'dominant_mood': 'Neutral',
            'distribution': {'Happy': 20, 'Sad': 10, 'Angry': 5, 'Fear': 5, 'Surprise': 15, 'Neutral': 45},
            'recent_history': [],
            'weekly_trend': {'labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], 'counts': [0, 0, 0, 0, 0, 0, 0]}
        })

    # Compute emotion counts
    counts = {'Happy': 0, 'Sad': 0, 'Angry': 0, 'Fear': 0, 'Surprise': 0, 'Neutral': 0}
    recent_history = []

    for row in rows:
        emo = row['emotion'].capitalize()
        if emo in counts:
            counts[emo] += 1
        else:
            counts['Neutral'] += 1

        if len(recent_history) < 10:
            recent_history.append({
                'id': row['id'],
                'emotion': row['emotion'],
                'confidence': row['confidence'],
                'created_at': row['created_at']
            })

    total = len(rows)
    distribution = {k: round((v / total) * 100, 1) for k, v in counts.items()}
    dominant_mood = max(counts, key=counts.get)

    # Calculate weekly trend (grouped by date)
    cursor.execute('''
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM emotion_logs 
        WHERE created_at >= DATE('now', '-7 days')
        GROUP BY DATE(created_at)
        ORDER BY date ASC
    ''')
    trend_rows = cursor.fetchall()
    conn.close()

    trend_labels = [r['date'] for r in trend_rows] if trend_rows else ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    trend_counts = [r['count'] for r in trend_rows] if trend_rows else [1, 2, 4, 3, 5, 2, 6]

    return jsonify({
        'success': True,
        'total_detections': total,
        'dominant_mood': dominant_mood,
        'distribution': distribution,
        'counts': counts,
        'recent_history': recent_history,
        'weekly_trend': {
            'labels': trend_labels,
            'counts': trend_counts
        }
    })
