/**
 * MoodTunes - AI Webcam & Real-time Emotion Detection Engine
 */

let videoElement = null;
let canvasElement = null;
let canvasCtx = null;
let isWebcamActive = false;
let isLiveScanning = false;
let scanInterval = null;
let currentEmotion = "Neutral";

const EMOTION_COLORS = {
    "Happy": "#E85234",
    "Sad": "#00408C",
    "Angry": "#b91c1c",
    "Fear": "#F2D7D3",
    "Surprise": "#F9B8A7",
    "Neutral": "#96ADD6"
};

const EMOTION_EMOJIS = {
    "Happy": "😊",
    "Sad": "😢",
    "Angry": "😠",
    "Fear": "😨",
    "Surprise": "😲",
    "Neutral": "😐"
};

document.addEventListener('DOMContentLoaded', () => {
    videoElement = document.getElementById('webcamFeed');
    canvasElement = document.getElementById('overlayCanvas');
    if (canvasElement) {
        canvasCtx = canvasElement.getContext('2d');
    }

    const btnStart = document.getElementById('btnStartWebcam');
    const btnScan = document.getElementById('btnScanEmotion');
    const btnToggleLive = document.getElementById('btnToggleLive');

    if (btnStart) btnStart.addEventListener('click', startWebcam);
    if (btnScan) btnScan.addEventListener('click', captureAndDetect);
    if (btnToggleLive) btnToggleLive.addEventListener('click', toggleLiveScan);

    // Image Upload fallback
    const fileUpload = document.getElementById('fileUpload');
    if (fileUpload) {
        fileUpload.addEventListener('change', handleImageUpload);
    }
});

async function startWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
        });
        
        videoElement.srcObject = stream;
        await videoElement.play();

        isWebcamActive = true;
        document.getElementById('webcamPlaceholder').style.display = 'none';
        document.getElementById('scannerBadge').style.display = 'flex';
        
        canvasElement.width = videoElement.videoWidth || 640;
        canvasElement.height = videoElement.videoHeight || 480;

        setTimeout(captureAndDetect, 1000);
    } catch (err) {
        console.error("Webcam access error:", err);
        alert("Unable to access webcam. Please ensure camera permissions are granted or upload an image instead.");
    }
}

async function captureAndDetect() {
    if (!videoElement || (!isWebcamActive && !videoElement.src)) return;

    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = videoElement.videoWidth || 640;
    tempCanvas.height = videoElement.videoHeight || 480;
    const ctx = tempCanvas.getContext('2d');
    ctx.drawImage(videoElement, 0, 0, tempCanvas.width, tempCanvas.height);

    const base64Image = tempCanvas.toDataURL('image/jpeg', 0.85);
    await processDetectionPayload(base64Image);
}

async function processDetectionPayload(base64Image) {
    try {
        const response = await fetch('/api/detect_emotion', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: base64Image })
        });

        const data = await response.json();
        if (data.success) {
            currentEmotion = data.primary_emotion;
            renderDetectionResults(data);
            
            fetch('/api/log_emotion', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    emotion: data.primary_emotion,
                    confidence: data.confidence,
                    breakdown: data.breakdown
                })
            });

            if (window.loadRecommendationsForMood) {
                window.loadRecommendationsForMood(data.primary_emotion);
            }
        }
    } catch (err) {
        console.error("Emotion detection error:", err);
    }
}

function renderDetectionResults(data) {
    const emotionEmoji = document.getElementById('moodEmoji');
    const moodTitle = document.getElementById('moodTitle');
    const moodConfidence = document.getElementById('moodConfidence');
    const barsContainer = document.getElementById('barsContainer');

    if (emotionEmoji) emotionEmoji.textContent = EMOTION_EMOJIS[data.primary_emotion] || '😐';
    if (moodTitle) moodTitle.textContent = data.primary_emotion;
    if (moodConfidence) moodConfidence.textContent = `${data.confidence}% Confidence`;

    if (canvasCtx && data.faces) {
        canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
        
        data.faces.forEach(face => {
            canvasCtx.strokeStyle = EMOTION_COLORS[data.primary_emotion] || '#E85234';
            canvasCtx.lineWidth = 3;
            canvasCtx.strokeRect(face.x, face.y, face.w, face.h);

            canvasCtx.fillStyle = EMOTION_COLORS[data.primary_emotion] || '#E85234';
            canvasCtx.fillRect(face.x, face.y - 24, face.w, 24);
            canvasCtx.fillStyle = '#ffffff';
            canvasCtx.font = 'bold 12px Outfit, sans-serif';
            canvasCtx.fillText(`${data.primary_emotion} (${data.confidence}%)`, face.x + 6, face.y - 7);
        });
    }

    if (barsContainer && data.breakdown) {
        barsContainer.innerHTML = '';
        Object.entries(data.breakdown).forEach(([emotion, percent]) => {
            const row = document.createElement('div');
            row.className = 'bar-row';
            row.innerHTML = `
                <div class="bar-label">
                    <span>${EMOTION_EMOJIS[emotion] || ''} ${emotion}</span>
                    <span>${percent}%</span>
                </div>
                <div class="bar-bg">
                    <div class="bar-fill" style="width: ${percent}%; background: ${EMOTION_COLORS[emotion] || '#E85234'}"></div>
                </div>
            `;
            barsContainer.appendChild(row);
        });
    }
}

function toggleLiveScan() {
    const btnToggle = document.getElementById('btnToggleLive');
    if (!isLiveScanning) {
        if (!isWebcamActive) {
            startWebcam().then(() => {
                isLiveScanning = true;
                if (btnToggle) btnToggle.innerHTML = '⏹ Stop Live Scan';
                scanInterval = setInterval(captureAndDetect, 2500);
            });
        } else {
            isLiveScanning = true;
            if (btnToggle) btnToggle.innerHTML = '⏹ Stop Live Scan';
            scanInterval = setInterval(captureAndDetect, 2500);
        }
    } else {
        isLiveScanning = false;
        if (btnToggle) btnToggle.innerHTML = '🔄 Live Continuous Scan';
        if (scanInterval) clearInterval(scanInterval);
    }
}

function handleImageUpload(e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (event) => {
        const base64Img = event.target.result;
        
        const imgDisplay = new Image();
        imgDisplay.src = base64Img;
        imgDisplay.onload = () => {
            canvasElement.width = imgDisplay.width;
            canvasElement.height = imgDisplay.height;
            canvasCtx.drawImage(imgDisplay, 0, 0);
            document.getElementById('webcamPlaceholder').style.display = 'none';
        };

        processDetectionPayload(base64Img);
    };
    reader.readAsDataURL(file);
}
