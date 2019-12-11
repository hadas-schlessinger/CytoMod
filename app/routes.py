from flask import render_template, flash, redirect, request
from app import app
import tools
from app.Backend import DataManipulation as dm
from app.Backend import Visualization
from app.Backend import server_tools
import logging

# from .forms import LoginForm
# import os
# from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = set(['csv'])


# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         flash('Login requested for user {}, remember_me={}'.format(
#             form.username.data, form.remember_me.data))  # for debugging, shows massage to user
#         return redirect('welcome.html')
#     return render_template('login.html', title='Sign In', form=form)


@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    return render_template('upload.html')


@app.route('/set')
def set():
    return render_template('set.html')


@app.route('/generate', methods=['GET', 'POST'])
def generate():
    parameters = tools.Object()
    parameters.name_compartment = request.form.get('name_compartment')
    parameters.name_data = request.form.get('name_data')
    parameters.log_transform = request.form.get('log_transform') in ['true', '1', 'True', 'TRUE'] #change to bool
    parameters.max_testing_k = request.form.get('max_testing_k', type=int)
    parameters.max_final_k = request.form.get('max_final_k', type=int)  # Must be <= max_testing_k
    parameters.recalculate_modules = request.form.get('recalculate_modules') in ['true', '1', 'True', 'TRUE'] # change to bool
    parameters.outcomes = request.args.getlist('outcomes')  # names of binary outcome columns
    parameters.covariates = request.args.getlist('covariates')  # names of regression covariates to control for
    parameters.log_column_names = request.args.getlist('log_column_names')  # or empty list: []
    parameters.cytokines = request.args.getlist('cytokines') # if none, will analyze all
    parameters.save_file = request.form.get('save_file') in ['true', '1', 'True', 'TRUE']  # for saving the file in the server
    print(parameters.save_file)
    parameters = dm.settings.set_data(parameters)
    parameters = dm.cytocine_adjustments.adjust_cytokine(parameters)
    Visualization.figures.calc_abs_figures(parameters)
    #Visualization.figures.calc_adj_figures(args)
    # logging.warning('finished')
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


if __name__ == "__main__":
  app.run(debug=True)

