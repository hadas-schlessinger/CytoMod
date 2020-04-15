from flask import  render_template, flash, redirect, request, url_for, send_file
from werkzeug.utils import secure_filename
from app import app
import tools
from app.backend import data_manipulation as dm
from app.backend import visualization
from app.backend import server_tools
import logging
import sys
import os
import pandas as pd
import json

# from .forms import LoginForm
UPLOAD_FOLDER = sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'data_files', 'data'))
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         flash('Login requested for user {}, remember_me={}'.format(
#             form.username.data, form.remember_me.data))  # for debugging, shows massage to user
#         return redirect('welcome.html')
#     return render_template('login.html', title='Sign In', form=form)



# @app.route('/time')
# def get_current_time():
#     return {'time': time.time()}


@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        name = request.form.get('name_data', default='data')
        project_name = name if name != '' else ('Unknown project')
        tools.create_folder(os.path.join('app/static/', project_name))
        tools.create_folder(os.path.join('app/static/', project_name, 'data_files'))
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
                patients.save(os.path.join(os.path.join(os.getcwd(), 'app', 'static', project_name, 'data_files'), filename))
        if cytokines and allowed_file(cytokines.filename):
            filename = secure_filename(cytokines.filename)
            cytokines.save(os.path.join(os.path.join(os.getcwd(), 'app', 'static', project_name, 'data_files'), filename))
            if patients != None:
                files = pd.DataFrame([secure_filename(cytokines.filename), secure_filename(patients.filename), project_name])
                tools.write_DF_to_excel(os.path.join('app/static/', project_name, 'data_files_names.xlsx'), files)
            else:
                files = pd.DataFrame([secure_filename(cytokines.filename), "", project_name])
                tools.write_DF_to_excel(os.path.join('app/static/', project_name, 'data_files_names.xlsx'), files)
            return {'project': project_name}
        else:
            return json.dumps({ "error": 'no cytokine file was found' }), 400


@app.route('/explanation', methods=['POST'])
def explanation():
    if request.method == 'POST':
        return render_template('upload.html')
    return render_template('explanation.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/generate', methods=['POST'])
def generate():
    logging.info('got a request')
    parameters = tools.Object()
    parameters.images = []
    parameters.name_data = request.form.get('name_data', default='data')
    if parameters.name_data == '':
        parameters.name_data = 'Unknown project'
    parameters.name_compartment = request.form.get('name_compartment', default='Compartment')
    parameters.luminex = request.form.get('luminex') in ['true', '1', 'True', 'TRUE', 'on']
    parameters.log_transform = request.form.get('log_transform') in ['true', '1', 'True', 'TRUE', 'on']
    parameters.max_testing_k = request.form.get('max_testing_k', type=int, default=6)  # Must be <= max_testing_k
    parameters.recalculate_modules = True
    parameters.outcomes = request.form.get('outcomes')  # names of binary outcome columns
    parameters.outcomes = parameters.outcomes.split(", ")
    parameters.covariates = request.form.get('covariates') # names of regression covariates to control for
    parameters.covariates = parameters.covariates.split(", ")
    parameters.log_column_names = request.form.get('log_column_names')
    parameters.log_column_names = parameters.log_column_names.split(", ")   # or empty list: []
    parameters.cytokines = request.form.get('cytokines', default='') # if none, will analyze all
    parameters.cytokines = parameters.cytokines.split(", ")
    # parameters.save_file = request.form.get('save_file') in ['true', '1', 'True', 'TRUE', 'on']  # for saving the file in the server
    # print(parameters.save_file)
    parameters = dm.settings.set_data(parameters)
    parameters = dm.cytocine_adjustments.adjust_cytokine(parameters)
    parameters = visualization.figures.calc_clustering(parameters)
    parameters = visualization.figures.calc_abs_figures(parameters)
    parameters = visualization.figures.calc_adj_figures(parameters)
    ans = server_tools.make_ans(parameters)
    logging.info('finished to calc the method')
    return send_file(ans[0]['path'], mimetype='image/png')
    # server_tools.clean_static(parameters)
    # server_tools.clean_data(parameters)
    # tools.write_DF_to_excel(os.path.join(parameters.paths['data'], 'abs_modules.xlsx'), parameters.modules[0])
    # tools.write_DF_to_excel(os.path.join(parameters.paths['data'], 'adj_modules.xlsx'), parameters.modules[1])
    return render_template(
        'results.html', results=ans, abs_modules=parameters.modules[0], adj_modules=parameters.modules[1],
        abs_len= range(1,len(parameters.cyto_mod_abs.modDf.columns)+1), adj_len=range(1,len(parameters.cyto_mod_adj.modDf.columns)+1))


