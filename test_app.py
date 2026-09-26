import unittest
import json
import base64
import os
import numpy as np
import cv2
from app import app
from database import init_db, get_db_connection, DB_PATH
from emotion_detector import detect_emotion

class MoodTunesTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        # Clean up existing test database if present
        if os.path.exists(DB_PATH):
            try:
                os.remove(DB_PATH)
            except Exception:
                pass
        init_db()

    def test_database_initialization(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row['name'] for row in cursor.fetchall()]
        conn.close()
        self.assertIn('users', tables)
        self.assertIn('emotion_logs', tables)
        self.assertIn('favourite_songs', tables)

    def test_emotion_detector(self):
        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.circle(dummy_img, (50, 50), 30, (255, 255, 255), -1)
        _, buffer = cv2.imencode('.jpg', dummy_img)
        b64_str = base64.b64encode(buffer).decode('utf-8')

        result = detect_emotion(b64_str)
        self.assertTrue(result['success'])
        self.assertIn('primary_emotion', result)
        self.assertIn('confidence', result)
        self.assertIn('breakdown', result)
        self.assertIn(result['primary_emotion'], ["Happy", "Sad", "Angry", "Fear", "Surprise", "Neutral"])

    def test_auth_registration_and_login(self):
        reg_payload = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        res_reg = self.client.post('/api/register', json=reg_payload)
        self.assertEqual(res_reg.status_code, 200)
        data_reg = json.loads(res_reg.data)
        self.assertTrue(data_reg['success'])

        login_payload = {
            'identifier': 'testuser@example.com',
            'password': 'password123'
        }
        res_login = self.client.post('/api/login', json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        data_login = json.loads(res_login.data)
        self.assertTrue(data_login['success'])

    def test_recommendation_api(self):
        for mood in ["Happy", "Sad", "Angry", "Fear", "Surprise", "Neutral"]:
            res = self.client.get(f'/api/recommendations/{mood}')
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertTrue(data['success'])
            self.assertEqual(data['emotion'], mood)
            self.assertTrue(len(data['tracks']) > 0)

    def test_analytics_api(self):
        res = self.client.get('/api/analytics/summary')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        self.assertIn('distribution', data)

if __name__ == '__main__':
    unittest.main()
