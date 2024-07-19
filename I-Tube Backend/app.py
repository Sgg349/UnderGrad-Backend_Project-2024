from flask import Flask, render_template, request, redirect, url_for, Response
from pymongo import MongoClient
from gridfs import GridFS
from werkzeug.utils import secure_filename
import os
import certifi
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient("mongodb+srv://itubedevs:enterpass@cluster0.cbncjeu.mongodb.net/", tlsCAFile=certifi.where())
db = client["itubedb"]
collection = db["uservid"]
fs = GridFS(db)

UPLOAD_FOLDER = 'temp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploadvideo')
def uploadvid():
    return render_template('uploadvideo.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), 'rb') as f:
            fs.put(f, filename=filename, content_type=file.content_type)
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('view_uploaded_videos'))

@app.route('/videos')
def view_uploaded_videos():
    uploaded_videos = [file for file in fs.find()]
    return render_template('index.html', uploaded_videos=uploaded_videos)

@app.route('/video/<filename>')
def serve_video(filename):
    video_file = fs.find_one({'filename': filename})
    if not video_file:
        return "Video not found", 404
    response = Response(video_file.read(), mimetype=video_file.content_type)
    response.headers['Content-Disposition'] = f'inline; filename={video_file.filename}'
    return response

@app.route('/signin')
def signin():
    return render_template('Sign in page.html')

@app.route('/signuppage', methods=['GET', 'POST'])
def signup():
    return render_template('sign-up.html')

@app.route('/submit_signup', methods=['POST'])
def submitsignupform():
    if request.method == 'POST':
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        password = request.form['password']
        dob = request.form['dob']

        user_data = {
            'firstname': firstname,
            'lastname': lastname,
            'email': email,
            'password': password,
            'dob': dob
        }

        collection.insert_one(user_data)
        return render_template('homepage.html')

@app.route('/video/<video_id>')
def video(video_id):
    video_file = fs.find_one({"_id": ObjectId(video_id)})
    if video_file is None:
        return 'Video not found', 404
    response = Response(video_file.read(), mimetype=video_file.content_type)
    response.headers['Content-Disposition'] = f'inline; filename={video_file.filename}'
    return response

if __name__ == '__main__':
    app.run(debug=True)
