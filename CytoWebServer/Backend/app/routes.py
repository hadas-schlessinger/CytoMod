from flask import render_template, flash, redirect, request
from CytoWebServer import app
from CytoWebServer import LoginForm


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
    p_value = request.form['p_value']
    k = request.form['k']
    #call calculting return data
    return f"p-value: {p_value}, k: {k}"
