from flask import Flask, render_template, Response, jsonify, request, redirect, url_for
from face import gen_frames, cleanup_resources, take_picture
from ai import prompt



app = Flask(__name__)

responses = []

@app.route('/', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        favSubject = request.form.get('favSubject')
        notFavSubject = request.form.get('notFavSubject')
        funThing = request.form.get('funThing')
        freeTime = request.form.get('freeTime')
        frustration = request.form.get('frustration')
        fear = request.form.get('fear')

        responses.append({
            'favSubject': favSubject,
            'notFavSubject': notFavSubject,
            'funThing': funThing,
            'freeTime': freeTime,
            'frustration': frustration,
            'fear': fear
        })
        
        # Return the template with a success flag
        return render_template('index.html', submitted=True)

    return render_template('index.html', submitted=False)

@app.route('/video')
def video():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/take_picture')
def handle_picture():
    response = take_picture()
    data = response.get_json()
    
    # if data['success'] and data['emotion']:
    #     prompt_text = f"Given that someone is feeling {data['emotion']}, provide a short supportive response (max 2 sentences)."
    #     ai_response = prompt(prompt_text)
    #     data['ai_response'] = ai_response.text
    
    return jsonify(data)

@app.route('/cleanup', methods=['POST'])
def cleanup():
    cleanup_resources()
    return jsonify({"status": "success"})

@app.route('/reinitialize_camera', methods=['POST'])
def reinitialize():
    cleanup_resources()  # Clean up existing resources
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_ai_response', methods=['POST'])
def get_ai_response():
    data = request.get_json()
    emotion = data.get('emotion')
    responses = data.get('responses')
    
    prompts = {
        'happy': f"Give me the base google images url, just the url, for images of 'pictures of {responses['fear']}'.",
        'sad': f"Give me a url, just the url, to a site to learn about {responses['notFavSubject']}. Make sure the site is able to be embedded in a web page. DONT GIVE MOZILLA, KHAN ACADEMY, or MATHPLAYGROUND",
        'fear': f"Give me the base google images url, just the url, for images of 'pictures of {responses['fear']}'.",
        'angry': f"Give me a url, just the url, to a site to learn about {responses['notFavSubject']}. Make sure the site is able to be embedded in a web page. DONT GIVE MOZILLA, KHAN ACADEMY, or MATHPLAYGROUND",
        'disgust': f"Give me a url, just the url, to a site to learn about {responses['notFavSubject']}. Make sure the site is able to be embedded in a web page. DONT GIVE MOZILLA, KHAN ACADEMY, or MATHPLAYGROUND",
        'surprise': f"Give me a url, just the url, to a site to learn about {responses['notFavSubject']}. Make sure the site is able to be embedded in a web page. DONT GIVE MOZILLA, KHAN ACADEMY, or MATHPLAYGROUND",
        'neutral': f"Give me the base google images url, just the url, for images of 'pictures of {responses['fear']}'.",
    }
    
    prompt_text = prompts.get(emotion)
    
    response = prompt(prompt_text)
    
    message = prompt(f"Give me on very short sentence of: roast me on how I am feel {emotion}, and use the fact that my favorite subject is {responses['favSubject']}, or my least favorite subject is {responses['notFavSubject']}, or I like to do {responses['funThing']} in my free time, or I am afraid of {responses['fear']}, or I get frustrated when {responses['frustration']}. Only use one of those facts, make it a very short sentence.")

    response_text = response.text.strip()
    if(emotion in ['fear', 'happy']):
        response_text += '&igu=1'
    
    return jsonify({"searchterm": response_text, "message": f"Detected: {emotion}.\n" + message.text.strip()})

if __name__ == '__main__':
    app.run(debug=True)