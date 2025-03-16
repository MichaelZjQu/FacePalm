from flask import Flask, render_template, Response, jsonify
from face import gen_frames, toggle_freeze, cleanup_resources
from ai import prompt

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/toggle_freeze')
def handle_freeze():
    response = toggle_freeze()
    data = response.get_json()
    
    if data['frozen'] and data['emotion']:
        prompt_text = f"Given that someone is feeling {data['emotion']}, provide a short supportive response (max 2 sentences)."
        ai_response = prompt(prompt_text)
        data['ai_response'] = ai_response.text
    
    return jsonify(data)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    cleanup_resources()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True)