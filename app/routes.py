from flask import Flask, render_template, flash, redirect, request, url_for
from werkzeug.utils import secure_filename
from app import app
import tools
from app.Backend import DataManipulation as dm
from app.Backend import Visualization
from app.Backend import server_tools
import logging
import sys
import os

# from .forms import LoginForm


UPLOAD_FOLDER = sys.path.append(os.path.join(os.getcwd(), 'cytomod', 'data_files', 'data'))
ALLOWED_EXTENSIONS = {'xlsx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.debug = True


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         flash('Login requested for user {}, remember_me={}'.format(
#             form.username.data, form.remember_me.data))  # for debugging, shows massage to user
#         return redirect('welcome.html')
#     return render_template('login.html', title='Sign In', form=form)

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(os.path.join(os.getcwd(), 'app', 'static', 'data_files', 'data'), filename))
            return render_template('set.html')
        else:
            flash('please upload an excel file')
            return redirect(request.url)
    return render_template('upload.html')


@app.route('/')
def welcome():
    if request.method == 'POST':
        return render_template('upload.html')
    return render_template('welcome.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    parameters = tools.Object()
    parameters.images = []
    parameters.name_compartment = request.form.get('name_compartment')
    print(parameters.name_compartment)
    print(request.form.get('name_compartment', default='data'))
    parameters.name_data = request.form.get('name_data')
    print(request.form.get('name_data'))
    parameters.log_transform = request.form.get('log_transform') in ['true', '1', 'True', 'TRUE', 'on']
    print(parameters.log_transform)
    parameters.max_testing_k = request.form.get('max_testing_k', type=int, default=8)
    print(parameters.max_testing_k)
    parameters.max_final_k = request.form.get('max_final_k', type=int, default=6)  # Must be <= max_testing_k
    print(parameters.max_final_k)
    parameters.recalculate_modules = False
    parameters.outcomes = request.form.get('outcomes')  # names of binary outcome columns
    parameters.outcomes = parameters.outcomes.split(", ")
    print(parameters.outcomes)
    parameters.covariates = request.form.get('covariates') # names of regression covariates to control for
    parameters.covariates = parameters.covariates.split(", ")
    print(parameters.covariates)
    parameters.log_column_names = request.form.get('log_column_names')
    parameters.log_column_names = parameters.log_column_names.split(", ")   # or empty list: []
    print(parameters.log_column_names)
    parameters.cytokines = request.form.get('cytokines', default='') # if none, will analyze all
    parameters.cytokines = parameters.cytokines.split(", ")
    print(parameters.cytokines)
    # parameters.save_file = request.form.get('save_file') in ['true', '1', 'True', 'TRUE', 'on']  # for saving the file in the server
    # print(parameters.save_file)
    parameters = dm.settings.set_data(parameters)
    parameters = dm.cytocine_adjustments.adjust_cytokine(parameters)
    Visualization.figures.calc_abs_figures(parameters)
    Visualization.figures.calc_adj_figures(parameters)
    logging.warning('finished')
    ans = server_tools.make_ans(parameters)
    # server_tools.clean_static()
    server_tools.clean_data()
    return render_template(
        'results.html', results=ans)







