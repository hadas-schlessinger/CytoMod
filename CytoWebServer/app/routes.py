from flask import render_template, flash, redirect, request
from . import app
import tools


from .forms import LoginForm
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


@app.route('/', methods=['GET', 'POST'])
@app.route('/welcome', methods=['GET', 'POST'])
def welcome():
    return render_template('upload.html')


@app.route('/generate', methods=['GET', 'POST'])
def generate_plots():
    args = tools.Object()
    args.name_data = request.form['name_data']
    args.name_compartment = request.form['name_compartment']
    args.log_transform = request.form['log_transform']
    args.max_testing_k = request.form['max_testing_k']
    args.max_final_k = request.form['max_final_k']  # Must be <= max_testing_k
    args.recalculate_modules = request.form['recalculate_modules']
    args.outcomes = request.form['outcomes']  # names of binary outcome columns
    args.covariates = request.form['covariates']  # names of regression covariates to control for
    args.log_column_names = request.form['log_column_names']  # or empty list: []
    args.cytokines = request.form['cytokines']  # if none, will analyze all
    args.save_file = request.form['save_file'] #for saving the file

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


