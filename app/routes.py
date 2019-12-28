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
#app = Flask(__name__)
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

@app.route('/', methods=['GET', 'POST'])
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
            file.save(os.path.join(os.path.join(os.getcwd(), 'data_files', 'data'), filename))
            return render_template('set.html')
        else:
            flash('please upload an excel file')
            return redirect(request.url)
    return render_template('upload.html')


@app.route('/', methods=['GET', 'POST'])
def welcome():
    return render_template('upload.html')


@app.route('/set')
def set():
    return render_template('set.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    parameters = tools.Object()
    parameters.name_compartment = request.form.get('name_compartment')
    parameters.name_data = request.form.get('name_data')
    parameters.log_transform = request.form.get('log_transform') in ['true', '1', 'True', 'TRUE']
    parameters.max_testing_k = request.form.get('max_testing_k', type=int)
    parameters.max_final_k = request.form.get('max_final_k', type=int)  # Must be <= max_testing_k
    parameters.recalculate_modules = True
    parameters.outcomes = request.args.getlist('outcomes[]')  # names of binary outcome columns
    print(request.args.getlist('outcomes'))
    parameters.covariates = request.args.getlist('covariates[]')  # names of regression covariates to control for
    parameters.log_column_names = request.args.getlist('log_column_names')  # or empty list: []
    parameters.cytokines = request.args.getlist('cytokines') # if none, will analyze all
    parameters.save_file = request.form.get('save_file') in ['true', '1', 'True', 'TRUE']  # for saving the file in the server
    parameters = dm.settings.set_data(parameters)
    parameters = dm.cytocine_adjustments.adjust_cytokine(parameters)
    Visualization.figures.calc_abs_figures(parameters)
    Visualization.figures.calc_adj_figures(parameters)
    logging.warning('finished')
    # ans = server_tools.make_ans()
    # pdf_path = server_tools.make_pdf()
    # return ans
    return "hayyyyy"
    # upload data for later
    # data = request.files['file']
    # if not data:
    #     return 'Upload a CSV file'
    # if data.filename == '':
    #     flash('No selected file')
    #     return redirect(request.url)
    # if data and allowed_file(data.filename):
    #     filename = secure_filename(data.filename)
    #     data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    #     #make calculations
# another option
    # stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
    # # csv_input = csv.reader(stream)
    #
    # print(csv_input)
    # for row in csv_input:
    #     print(row)
    #
    # stream.seek(0)
    # result = transform(stream.read())
    #
    # response = make_response(result)
    # response.headers["Content-Disposition"] = "attachment; filename=result.csv"
    # return ""


# def allowed_file(filename):
#     return '.' in filename and \
#            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# if __name__ == "__main__":
#     app.debug = True
#     app.run(debug=True)

