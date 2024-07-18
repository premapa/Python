import os
import cv2 as cv
import requests
from io import BytesIO
from flask import Flask, render_template, Response, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import transform

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'static/images'

net = cv.dnn.readNetFromTensorflow("graph_opt.pb")  # weights

pythonCopy codeimport cv2

cap = cv2.VideoCapture('/dev/video0')if not cap.isOpened():
    raise IOError("Cannot open virtual webcam")
while True:
    ret, frame = cap.read()    if not ret:
        break    cv2.imshow('Virtual Webcam', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()








def process_frame(frame, tx=0, ty=0):
    # Example: Apply some processing to the frame (replace with your processing logic)
    return frame

@app.route('/')
def index():
    local_images = [
        'C:/Users/User/OneDrive/Desktop/images/checks.jpg'
    ]
    return render_template('index2.html', local_images=local_images)

@app.route('/fetch_image')
def fetch_image():
    image_path = request.args.get('path')
    if not image_path:
        return "Path parameter is missing", 400
    
    if is_url(image_path):
        return fetch_external_image(image_path)
    else:
        return fetch_local_image(image_path)

def is_url(path):
    return path.startswith('http://') or path.startswith('https://')

def fetch_local_image(filepath):
    try:
        if os.path.isfile(filepath):
            return send_file(filepath)
        else:
            return "File not found", 404
    except Exception as e:
        return f"Error serving local image: {e}", 500

def fetch_external_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors
        image_content = BytesIO(response.content)
        return send_file(image_content, mimetype=response.headers['Content-Type'])
    except requests.exceptions.RequestException as e:
        return f"Error fetching image: {e}", 500

@app.route('/feed')
def feed_index():
    return render_template('feed.html')

@app.route('/video_feed')
def video_feed():
    tx = int(request.args.get('tx', 0))  # Get translation parameters from the request
    ty = int(request.args.get('ty', 0))

    def gen_frames(tx, ty):
        while True:
            hasFrame, frame = cap.read()
            if not hasFrame:
                break
            frame = process_frame(frame, tx, ty)
            ret, buffer = cv.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(gen_frames(tx, ty), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture_image', methods=['POST'])
def capture_image():
    try:
        tx = int(request.json.get('tx', 0))
        ty = int(request.json.get('ty', 0))
        product = request.json.get('product', 'default')

        hasFrame, frame = cap.read()
        if hasFrame:
            frame = process_frame(frame, tx, ty)
            poseFileName = 'pose.jpg'
            clothName = 'cloth.jpg'
            clothFileName = product
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], poseFileName)
            cv.imwrite(image_path, frame)
            
            # Assuming transform.main(clothFileName, poseFileName) performs image processing
            transform.main(clothFileName, poseFileName)
            transform.deleteImage(clothName)
            transform.deleteImage(poseFileName)

            return jsonify({ "output_path": "/static/images/out_img.jpg"})
        else:
            return jsonify({"error": "Failed to capture frame"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/static/images/<filename>')
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/stop_webcam', methods=['POST'])
def stop_webcam():
    try:
        global cap
        if cap.isOpened():
            cap.release()  # Release the webcam resource
            cap = None
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/hello', methods=['GET'])
def hello():
    print("hello")  # Print to console
    return "Hello, World!"  # Return a response


if __name__ == '__main__':
    app.run(debug=True)
