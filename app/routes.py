from flask import  render_template, request
from werkzeug.utils import secure_filename
from app import app
import logging
import sys
import os
import pandas as pd
import json
import uuid
import flask_executor
import threading
from app.backend import server_tools, tools

UPLOAD_FOLDER = sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'data_files', 'data'))
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
executor = flask_executor.Executor(app)


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        name = request.form.get('name_data')
        id =  {'id': uuid.uuid1(),
                'status': 'PENDING'}

        if name != '':
            project_name = name
            tools.create_folder(os.path.join('static/', id['id'].__str__()))
            tools.create_folder(os.path.join('static/', id['id'].__str__(), 'data_files'))
            tools.write_DF_to_excel(os.path.join('static/', id['id'].__str__(), 'process_id_status.xlsx'),
                                    id)
        else:
            return json.dumps({ "error": 'cant access the server without a name' }), 403

        if 'patients' in request.files:
            patients = request.files['patients']
        else:
            patients = None
        if 'cytokines' not in request.files:
            return json.dumps({ "error": 'no cytokine file was found' }), 400
        cytokines = request.files['cytokines']
        # if user does not select file
        if cytokines.filename == '':
            return json.dumps({ "error": 'no cytokine file was found' }), 400
        if patients != None:
            if allowed_file(patients.filename):
                filename = secure_filename(patients.filename)
                patients.save(os.path.join(os.path.join(os.getcwd(), 'static',  id['id'].__str__(), 'data_files'), filename))
        if cytokines and allowed_file(cytokines.filename):
            filename = secure_filename(cytokines.filename)
            cytokines.save(os.path.join(os.path.join(os.getcwd(), 'static',  id['id'].__str__(), 'data_files'), filename))
            if patients != None:
                files = pd.DataFrame([secure_filename(cytokines.filename), secure_filename(patients.filename), project_name])
                tools.write_DF_to_excel(os.path.join('static/', id['id'].__str__(), 'data_files_and_project_names.xlsx'), files)
            else:
                files = pd.DataFrame([secure_filename(cytokines.filename), "no file", project_name])
                tools.write_DF_to_excel(os.path.join('static/', id['id'].__str__(), 'data_files_and_project_names.xlsx'), files)
            return {'id': id['id']}
        else:
            return json.dumps({ "error": 'no cytokine file was found' }), 400


# @app.route('/explanation', methods=['POST'])
# def explanation():
#     if request.method == 'POST':
#         return render_template('upload.html')
#     return render_template('explanation.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/status', methods=['POST'])
def method_status():
    id = request.form.get('id')
    statuses = tools.read_excel(os.path.join('static/', id, 'process_id_status.xlsx'))
    status = statuses['value'][1]
    return {'status': status}


@app.route('/generate', methods=['POST'])
def generate():
    logging.info(f'got a request {request.form}')
    name = request.form.get('name_data')
    if name == '':
        return json.dumps({"error": 'please insert your data and project name'}), 400
    id = request.form.get('id')
    if id not in os.listdir('static'):
        logging.warning(f'invalid id {id}, returning error')
        return json.dumps({"error": 'invalid name'}), 400
    id = {'id': id,
         'status': 'PENDING'}
    luminex = request.form.get('luminex') in ['true', '1', 'True', 'TRUE', 'on']
    log_transform = request.form.get('log_transform') in ['true', '1', 'True', 'TRUE', 'on']
    outcomes = request.form.get('outcomes')
    covariates = request.form.get('covariates')  # names of regression covariates to control for
    log_column_names = request.form.get('log_column_names')
    cytokines = request.form.get('cytokines', default='') # if none, will analyze all
    parameters = [name, id, request.form.get('name_compartment', default='Compartment'), luminex, log_transform, request.form.get('max_testing_k', type=int, default=6),
                  False, outcomes.split(", "), covariates.split(", "), log_column_names.split(", ") , cytokines.split(", ")
                  ]
    method = threading.Thread(target=server_tools.run_server, args=(parameters))
    method.daemon = True
    method.start()
    logging.info(f'Tread {method.name} started running and calculating the method')
    return {'id': id}


@app.route('/results' , methods=['POST'])
def results():
    id = request.form.get('id')
    dir = os.listdir('static')
    if id not in dir:
        logging.warning(f'invalid id {id}, not found in {dir} returning error')
        return json.dumps({"error": 'invalid name'}), 400
    # todo: add check for file existence
    results = server_tools.encode_images(id)
    return results.to_json()


# if __name__ == "__main__":
#     app.run(ssl_context=('cert.pem', 'key.pem'))