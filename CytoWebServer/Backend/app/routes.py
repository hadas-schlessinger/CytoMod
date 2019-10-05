from flask import render_template, flash, redirect, request
from CytoWebServer import app
from CytoWebServer import LoginForm
from CytoWebServer import Settings


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))  # for debugging, shows massage to user
        return redirect(url_for('welcome'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/')
@app.route('/welcome')
def welcome():
    user = {'username': 'hadas'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('welcome.html', title='Home', user=user, posts=posts)


@app.route('/generate', methods=['GET', 'POST'])
def generate_plots():
    name_data = request.form['name_data']
    name_compartment = request.form['name_compartment']
    log_transform = request.form['log_transform']
    max_testing_k = request.form['max_testing_k']
    max_final_k = request.form['max_final_k']  # Must be <= max_testing_k
    recalculate_modules = request.form['recalculate_modules']
    outcomes = request.form['outcomes']  # names of binary outcome columns
    covariates = request.form['covariates']  # names of regression covariates to control for
    log_column_names = request.form['log_column_names']  # or empty list: []
    cytokines = request.form['cytokines']  # if none, will analyze all
    get_data()
    return f"p-value: {p_value}, k: {k}"
