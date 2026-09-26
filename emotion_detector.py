import cv2
import numpy as np
import base64
import os

EMOTIONS = ["Happy", "Sad", "Angry", "Fear", "Surprise", "Neutral"]

# Attempt loading OpenCV CascadeClassifiers safely
face_cascade = None
eye_cascade = None

try:
    if hasattr(cv2, 'CascadeClassifier'):
        cascade_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        eye_file = cv2.data.haarcascades + 'haarcascade_eye.xml'
        
        if os.path.exists(cascade_file):
            face_cascade = cv2.CascadeClassifier(cascade_file)
        if os.path.exists(eye_file):
            eye_cascade = cv2.CascadeClassifier(eye_file)
except Exception as err:
    print("Warning initializing Haar Cascades:", err)

def base64_to_cv2_img(base64_string):
    """Converts a base64 encoded image string to an OpenCV BGR image."""
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print("Error decoding base64 image:", e)
        return None

def analyze_facial_features(face_gray, face_bgr=None):
    """
    Analyzes spatial, intensity, smile curvature, brow furrow, and color warmth features
    to classify confidence scores across 6 emotions: Happy, Sad, Angry, Fear, Surprise, Neutral.
    """
    h, w = face_gray.shape
    if h < 10 or w < 10:
        return {e: 16.66 for e in EMOTIONS}

    # Normalize face image for spatial analysis
    if hasattr(cv2, 'equalizeHist'):
        face_norm = cv2.equalizeHist(face_gray)
    else:
        face_norm = face_gray

    # 1. Lower face (Mouth & Smile area) analysis - bottom 38%
    mouth_roi = face_norm[int(h * 0.60):h, int(w * 0.15):int(w * 0.85)]
    mouth_h, mouth_w = mouth_roi.shape
    
    # Mouth edge density (lips, teeth, smile lines)
    if hasattr(cv2, 'Canny') and mouth_h > 2 and mouth_w > 2:
        mouth_edges = cv2.Canny(mouth_roi, 30, 100)
        edge_density = float(np.sum(mouth_edges > 0)) / float(mouth_h * mouth_w + 1e-5)
    else:
        edge_density = float(np.std(mouth_roi)) / 100.0
    
    # Smile Curvature & Teeth Brightness:
    # A smiling mouth has bright teeth/lips in center and distinct cheek/corner contours
    if mouth_w > 6 and mouth_h > 4:
        center_strip = mouth_roi[:, int(mouth_w * 0.25):int(mouth_w * 0.75)]
        outer_strips = np.hstack((mouth_roi[:, :int(mouth_w * 0.25)], mouth_roi[:, int(mouth_w * 0.75):]))
        center_mean = float(np.mean(center_strip))
        outer_mean = float(np.mean(outer_strips))
        smile_contrast = center_mean - outer_mean
    else:
        smile_contrast = 0.0

    # 2. Upper face (Eyes and Eyebrows area) analysis
    eyes_roi = face_norm[int(h * 0.12):int(h * 0.48), int(w * 0.12):int(w * 0.88)]
    if hasattr(cv2, 'Sobel') and eyes_roi.shape[0] > 2 and eyes_roi.shape[1] > 2:
        eyes_sobel_y = cv2.Sobel(eyes_roi, cv2.CV_64F, 0, 1, ksize=3)
        brow_furrow = float(np.mean(np.abs(eyes_sobel_y)))
    else:
        brow_furrow = float(np.std(eyes_roi))

    # Color warmth check if BGR image is provided
    warmth_boost = 0.0
    if face_bgr is not None and face_bgr.shape[0] > 0:
        b, g, r = cv2.split(face_bgr)
        r_mean = float(np.mean(r))
        b_mean = float(np.mean(b))
        warmth_boost = max(0.0, (r_mean - b_mean) * 0.05)

    # Calibrated raw score weights (prevents high contrast from dominating Fear)
    raw_scores = {}

    # Happy: Strong smile contrast, high mouth edge density, teeth highlights
    smile_indicator = max(0.0, smile_contrast) + (edge_density * 40.0)
    happy_score = 10.0 + (smile_indicator * 0.6) + warmth_boost
    if smile_contrast > 2.0 or edge_density > 0.08:
        happy_score += 15.0 # Strong boost for detected smile/teeth
    raw_scores["Happy"] = happy_score

    # Neutral / Calm: Moderate brow furrow, gentle facial contrast
    calm_neutral_score = 14.0 - (brow_furrow * 0.05)
    if abs(smile_contrast) < 5.0 and edge_density < 0.08:
        calm_neutral_score += 4.0
    raw_scores["Neutral"] = max(2.0, calm_neutral_score)

    # Surprise: Wide mouth opening + brow elevation
    surprise_score = (edge_density * 25.0) + (brow_furrow * 0.1)
    raw_scores["Surprise"] = max(1.0, surprise_score)

    # Angry: Sharp brow furrow + negative smile contrast
    angry_score = (brow_furrow * 0.2) - (smile_contrast * 0.05)
    raw_scores["Angry"] = max(0.5, angry_score)

    # Sad: Negative smile curve (outer corners lower/darker)
    sad_score = max(0.5, (-smile_contrast * 0.2) + 4.0 - (edge_density * 10.0))
    raw_scores["Sad"] = sad_score

    # Fear: Strictly requires high brow furrow AND absence of a smile
    fear_score = max(0.2, (brow_furrow * 0.1) - (happy_score * 0.4))
    raw_scores["Fear"] = fear_score

    # Softmax conversion to robust percentage distribution
    exp_scores = {k: np.exp(v / 5.0) for k, v in raw_scores.items()}
    sum_exp = sum(exp_scores.values())

    breakdown = {k: round((v / sum_exp) * 100.0, 1) for k, v in exp_scores.items()}
    
    # Ensure percentages total exactly 100%
    diff = round(100.0 - sum(breakdown.values()), 1)
    primary_key = max(breakdown, key=breakdown.get)
    breakdown[primary_key] = round(breakdown[primary_key] + diff, 1)

    return breakdown

def detect_emotion(base64_image):
    """
    Main detection pipeline. Normalizes image size, performs multi-scale face detection,
    and returns emotion confidence breakdown and bounding boxes.
    """
    img = base64_to_cv2_img(base64_image)
    if img is None:
        return {
            "success": False,
            "error": "Failed to decode image.",
            "face_detected": False,
            "primary_emotion": "Neutral",
            "confidence": 50.0,
            "breakdown": {e: 16.6 for e in EMOTIONS},
            "faces": []
        }

    h, w = img.shape[:2]

    # Resize large uploaded images to ~640px max width for high face detection accuracy
    scale_ratio = 1.0
    if w > 1000 or h > 1000:
        scale_ratio = 640.0 / max(w, h)
        img_resized = cv2.resize(img, (int(w * scale_ratio), int(h * scale_ratio)), interpolation=cv2.INTER_AREA)
    else:
        img_resized = img

    gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
    faces = []
    
    if face_cascade and not face_cascade.empty():
        try:
            # Multi-scale detection passes for high recall on different face sizes
            rects = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.08,
                minNeighbors=4,
                minSize=(30, 30)
            )
            if len(rects) == 0:
                rects = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.15,
                    minNeighbors=3,
                    minSize=(25, 25)
                )
            faces = rects
        except Exception as e:
            print("Face cascade detect error:", e)

    detected_faces_list = []

    if len(faces) > 0:
        primary_face = max(faces, key=lambda rect: rect[2] * rect[3])
        fx, fy, fw, fh = primary_face
        face_gray = gray[fy:fy+fh, fx:fx+fw]
        face_bgr = img_resized[fy:fy+fh, fx:fx+fw]
        
        breakdown = analyze_facial_features(face_gray, face_bgr)
        primary_emotion = max(breakdown, key=breakdown.get)
        confidence = breakdown[primary_emotion]

        inv_scale = 1.0 / scale_ratio
        for (rx, ry, rw, rh) in faces:
            detected_faces_list.append({
                "x": int(rx * inv_scale),
                "y": int(ry * inv_scale),
                "w": int(rw * inv_scale),
                "h": int(rh * inv_scale)
            })

        return {
            "success": True,
            "face_detected": True,
            "primary_emotion": primary_emotion,
            "confidence": confidence,
            "breakdown": breakdown,
            "faces": detected_faces_list,
            "image_size": {"width": w, "height": h}
        }
    else:
        # Fallback ROI analysis when face cascade misses
        center_gray = gray[int(gray.shape[0]*0.15):int(gray.shape[0]*0.85), int(gray.shape[1]*0.15):int(gray.shape[1]*0.85)]
        center_bgr = img_resized[int(gray.shape[0]*0.15):int(gray.shape[0]*0.85), int(gray.shape[1]*0.15):int(gray.shape[1]*0.85)]
        breakdown = analyze_facial_features(center_gray, center_bgr)
        primary_emotion = max(breakdown, key=breakdown.get)
        confidence = breakdown[primary_emotion]

        return {
            "success": True,
            "face_detected": False,
            "primary_emotion": primary_emotion,
            "confidence": confidence,
            "breakdown": breakdown,
            "faces": [],
            "image_size": {"width": w, "height": h}
        }
