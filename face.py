import cv2
from deepface import DeepFace
from flask import jsonify

cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
cam = None

# Global variables to control freezing
is_frozen = False
frozen_frame = None
current_emotion = None

def initialize_camera():
    global cam
    if cam is None or not cam.isOpened():
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            raise RuntimeError("Could not initialize camera")
    return cam

def release_camera():
    global cam
    if cam is not None and cam.isOpened():
        cam.release()
        cam = None

def toggle_freeze():
    global is_frozen, cam, current_emotion
    is_frozen = not is_frozen
    if is_frozen:
        release_camera()
    else:
        # Force camera reinitialization
        if cam is not None:
            release_camera()
        initialize_camera()
    return jsonify({"frozen": is_frozen, "emotion": current_emotion})

def cleanup_resources():
    """Clean up camera and other resources"""
    global cam, is_frozen, frozen_frame
    if cam is not None:
        release_camera()
    is_frozen = False
    frozen_frame = None
    cv2.destroyAllWindows()

def gen_frames():
    global is_frozen, frozen_frame, cam, current_emotion
    
    try:
        while True:
            if not is_frozen:
                try:
                    if cam is None or not cam.isOpened():
                        initialize_camera()
                    
                    ret, frame = cam.read()
                    if not ret:
                        continue
                        
                    result = DeepFace.analyze(img_path=frame, actions=["emotion"], enforce_detection=False)
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = cascade.detectMultiScale(gray, 1.1, 4)

                    for (x, y, w, h) in faces:
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 3)
                    
                    emotion = result[0]['dominant_emotion']
                    current_emotion = emotion  # Store the current emotion
                    txt = str(emotion)
                    cv2.putText(frame, txt, (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)

                    ret, buffer = cv2.imencode('.jpg', frame)
                    frame_bytes = buffer.tobytes()
                    frozen_frame = frame_bytes
                except Exception as e:
                    print(f"Error capturing frame: {str(e)}")
                    if cam is not None:
                        release_camera()
                    continue
            else:
                frame_bytes = frozen_frame

            if frame_bytes is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    finally:
        cleanup_resources()

    if cam is not None:
        release_camera()
    cv2.destroyAllWindows()
