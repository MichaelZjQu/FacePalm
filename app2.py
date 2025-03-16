from flask import Flask, render_template, request, redirect, url_for

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


    return render_template('form.html')

@app.route('/edit', methods=['GET', 'POST'])

def edit_responses():
    if request.method == 'POST':
        responses['favSubject'] = request.form.get('favSubject')
        responses['notFavSubject'] = request.form.get('notFavSubject')
        responses['funThing'] = request.form.get('funThing')
        responses['freeTime'] = request.form.get('freeTime')
        responses['frustration'] = request.form.get('frustration')
        responses['fear'] = request.form.get('fear')

        return redirect(url_for('edit_responses'))  # Refresh edit page

    return render_template('edit.html', data=responses)
if __name__ == '__main__':
    app.run(debug=True)
