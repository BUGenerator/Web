# encoding:utf8

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_from_directory, url_for, redirect, jsonify
import os

app = Flask(__name__)
application = app
basedir = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'upload')
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg'])


@app.route('/', methods=['GET'], strict_slashes=False)
def index():
    return render_template('upload.html')


# allowed file type (
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'], strict_slashes=False)
def upload_file():
    # file_dir = os.path.join(basedir, 'static', app.config['UPLOAD_FOLDER'])
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    if request.method == 'POST':
        try:
            file = request.files['file']
        except KeyError:
            return render_template('upload_error.html')
            # return jsonify({"error": 1001, "errmsg": u"failed"})
        if file and allowed_file(file.filename):
            # basepath = os.path.dirname(__file__)  # the path of current file
            # upload_path = os.path.join(file_dir, secure_filename(file.filename))
            filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return redirect(url_for('uploaded_file', filename=filename))
        else:
            return render_template('upload_error.html')
            # return jsonify({"error": 1001, "errmsg": u"failed"})
        # return render_template('index.html')


@app.route('/show/<filename>')
def uploaded_file(filename):
    # filename = 'http://127.0.0.1:5000/upload/' + filename
    return render_template('upload.html', filename=filename)


@app.route('/upload/<filename>')
def send_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    app.run()
