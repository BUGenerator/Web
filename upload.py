# encoding:utf8

from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, send_file, send_from_directory, url_for, redirect, jsonify, abort
import os
import predict
import tempfile
import json
from shutil import copyfile

app = Flask(__name__)
application = app
basedir = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(basedir, 'static', 'upload')
DEMO_FOLDER = os.path.join(basedir, 'static', 'image', 'demo')
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg'])


# allowed file type (
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def get_index():
    return render_template('index.html')


@app.route('/model')
def get_model():
    return render_template('model.html')


@app.route('/upload', methods=['GET'], strict_slashes=False)
def get_upload():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'], strict_slashes=False)
def post_upload():
    # file_dir = os.path.join(basedir, 'static', app.config['UPLOAD_FOLDER'])
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    try:
        file = request.files['file']
    except KeyError:
        return render_template('upload_error.html')
        # return jsonify({"error": 1001, "errmsg": u"failed"})
    if file and allowed_file(file.filename):
        # basepath = os.path.dirname(__file__)  # the path of current file
        # upload_path = os.path.join(file_dir, secure_filename(file.filename))
        filename = secure_filename(file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        seg, _ = predict.predict_by_path(path)
        temp_path = os.path.join(UPLOAD_FOLDER, 'result', filename)
        predict.save_by_path(seg, temp_path)

        output_data = json.dumps(predict.extract_seg(seg))
        with open(os.path.join(UPLOAD_FOLDER, 'result', filename+'.json'), 'w') as file_handle:
            file_handle.write(output_data)

        return redirect(url_for('get_show', filename=filename))
    else:
        return render_template('upload_error.html')


@app.route('/show/<filename>')
def get_show(filename):
    if not os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
        abort(404)
    # filename = 'http://127.0.0.1:5000/upload/' + filename

    output_text = "{}"
    output_path = os.path.join(UPLOAD_FOLDER, 'result', filename+'.json')
    if os.path.isfile(output_path):
        with open(output_path, 'r') as file_handle:
            output_text = file_handle.read()

    return render_template('upload.html', filename=filename, output_text="", output_json=output_text)


@app.route('/uploaded/<filename>')
def get_img_uploaded(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route('/predict/<filename>')
def get_img_predict(filename):
    return send_from_directory(os.path.join(UPLOAD_FOLDER, 'result'), filename)


@app.route('/demo-provision/<filename>')
def get_demo_provision(filename):
    """
    One thing here: if there is error, pretend there is no error
    """
    if os.path.isfile(os.path.join(DEMO_FOLDER, filename)):
        if os.path.isfile(os.path.join(UPLOAD_FOLDER, filename)):
            # Already provisioned
            return redirect(url_for('get_show', filename=filename))
        else:
            try:
                path = os.path.join(UPLOAD_FOLDER, filename)
                copyfile(os.path.join(DEMO_FOLDER, filename), path)
                # Then do the prediction
                seg, _ = predict.predict_by_path(path)
                temp_path = os.path.join(UPLOAD_FOLDER, 'result', filename)
                predict.save_by_path(seg, temp_path)

                output_data = json.dumps(predict.extract_seg(seg))
                with open(os.path.join(UPLOAD_FOLDER, 'result', filename+'.json'), 'w') as file_handle:
                    file_handle.write(output_data)

            except Exception:
                return redirect(url_for('get_upload'))
            else:
                return redirect(url_for('get_show', filename=filename))
    else:
        return redirect(url_for('get_upload'))

@app.route('/BUGenerator_delete_all')
def get_delete_all(filename):
    # Clean upload
    os.system("rm -rf ./static/upload/*")
    return "OK"

def prepare_env():
    # Clean upload
    # os.system("rm -rf ./static/upload/*")
    #import subprocess
    #subprocess.Popen(['curl -s https://api.github.com/repos/BUGenerator/Model/releases/latest | grep "browser_download_url.*model_fullres_keras.h5" | cut -d \'"\' -f 4 | wget -qi -'], shell=True)
    #if os.environ.get('AWS_PATH'):
    #    os.system("chmod 644 model_fullres_keras.h5")
    #    os.system("chown wsgi:wsgi model_fullres_keras.h5")
    pass

if __name__ == '__main__':
    prepare_env()
    app.run()
