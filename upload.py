# encoding:utf8

from werkzeug.utils import secure_filename
from flask import Flask, render_template, jsonify, request, send_from_directory
import time
import os
import base64

app = Flask(__name__)
UPLOAD_FOLDER = 'upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'JPG', 'PNG'])


# file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'], strict_slashes=False)
def indexpage():
    return render_template('upload.html')


# upload
@app.route('/', methods=['POST'], strict_slashes=False)
def api_upload():
    file_dir = os.path.join(basedir, app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f = request.files['file']

    if f and allowed_file(f.filename): # if type is allowed
        fname = secure_filename(f.filename)
        print(fname)
        f.save(os.path.join(file_dir, fname))
        # token = base64.b64encode(fname)
        # print(token)

        return jsonify({"error": 0, "msg": "succeed"})
    else:
        return jsonify({"error": 1001, "errmsg": u"failed"})


if __name__ == '__main__':
    app.run()
