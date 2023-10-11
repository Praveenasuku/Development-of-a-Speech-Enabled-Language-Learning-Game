from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import speech_recognition as sr
import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key' 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///language_learning.db' #use ur uri
db = SQLAlchemy(app)

class UserExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(200), nullable=False)
    transcription = db.Column(db.String(200), nullable=True)
    score = db.Column(db.Integer, default=0)

db.create_all()

@app.route('/')
def index():
    exercises = UserExercise.query.all()
    return render_template('index.html', exercises=exercises)

@app.route('/add_exercise', methods=['POST'])
def add_exercise():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error='No selected file')

    try:
        recognizer = sr.Recognizer()
        audio_data = recognizer.record(file)
        text = request.form['exercise_text']
        transcription = recognizer.recognize_google(audio_data)

        new_exercise = UserExercise(text=text, transcription=transcription)
        db.session.add(new_exercise)
        db.session.commit()
        flash('Exercise added successfully!', 'success')
        return redirect(url_for('index'))
    except sr.UnknownValueError:
        return render_template('index.html', error='Speech Recognition could not understand the audio')
    except sr.RequestError:
        return render_template('index.html', error='Could not request results from Google Speech Recognition service')

if __name__ == '__main__':
    app.run(debug=True)
