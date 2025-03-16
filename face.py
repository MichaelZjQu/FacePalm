import cv2
from deepface import DeepFace
from flask import jsonify
from threading import Event

cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
cam = None

# Global variables
current_emotion = None
stop_stream = Event()

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

def cleanup_resources():
    """Clean up camera and other resources"""
    global cam, stop_stream
    if cam is not None:
        release_camera()
    stop_stream.clear()  # Reset the stop flag
    cv2.destroyAllWindows()

def gen_frames():
    global cam, current_emotion, stop_stream
    stop_stream.clear()  # Reset the stop flag
    
    try:
        while not stop_stream.is_set():
            try:
                if cam is None or not cam.isOpened():
                    print("Initializing camera...")
                    initialize_camera()
                
                ret, frame = cam.read()
                if not ret:
                    print("Failed to read frame")
                    continue
                    
                # Process frame with DeepFace
                result = DeepFace.analyze(img_path=frame, actions=["emotion"], enforce_detection=False)
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = cascade.detectMultiScale(gray, 1.1, 4)

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 3)
                
                emotion = result[0]['dominant_emotion']
                current_emotion = emotion
                cv2.putText(frame, emotion, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 3)

                # Convert frame to JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()

                # Yield frame with proper MIME type headers
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"Error in gen_frames: {str(e)}")
                if cam is not None:
                    release_camera()
                break
    finally:
        cleanup_resources()

def take_picture():
    global cam, current_emotion, stop_stream
    try:
        stop_stream.set()  # Signal video stream to stop
        if cam is None or not cam.isOpened():
            initialize_camera()
        
        ret, frame = cam.read()
        if not ret:
            return jsonify({"success": False})
            
        result = DeepFace.analyze(img_path=frame, actions=["emotion"], enforce_detection=False)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 3)
        
        emotion = result[0]['dominant_emotion']
        current_emotion = emotion
        txt = str(emotion)
        cv2.putText(frame, txt, (50,50), cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),3)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Force cleanup of all camera resources
        cleanup_resources()
        
        return jsonify({
            "success": True,
            "emotion": current_emotion,
            "image": frame_bytes.decode('latin1')
        })
    except Exception as e:
        print(f"Error in take_picture: {str(e)}")
        cleanup_resources()  # Ensure cleanup happens even on error
        return jsonify({"success": False})
