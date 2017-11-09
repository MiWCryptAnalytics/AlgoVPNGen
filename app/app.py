from flask import Flask, flash, redirect, request, render_template
from flask_bootstrap import Bootstrap
from wtforms import Form, BooleanField, StringField, SelectField, SubmitField, validators
from flask_wtf import FlaskForm
import os

WTF_CSRF_SECRET_KEY = os.urandom(32)

class DigitalOceanForm(FlaskForm):
    do_access_token = StringField('Digital Ocean API Token', [
        validators.InputRequired(),
        validators.Length(min=64, max=64, message="Must be 64 Characters"),
        validators.Regexp("^[a-zA-Z0-9]*$", flags=0, message="Must be Alphanumeric")
    ])
    do_region = SelectField(
        'Digital Ocean Region',
        choices=[('ams1', 'Amsterdam 1'), ('ams2', 'Amsterdam 2'), ('ams3', 'Amsterdam 3')]
    )
    do_server_name = StringField("Server Name", [
        validators.InputRequired(),
        validators.Regexp("^[a-zA-Z0-9][a-zA-Z0-9-]*$", flags=0, message="Must be Alphanumeric and not start with -")

    ])
    submitbutton = SubmitField(label='Go')


app = Flask(__name__)
Bootstrap(app)
app.secret_key = os.urandom(32)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return 'The app appears to be working correctly.'

@app.route('/digitalocean', methods=['GET', 'POST'])
def digitalocean():
    form = DigitalOceanForm(request.form)
    
    if form.validate_on_submit():
        string = "Will run: %s" % build_do_cmd_string(form.do_access_token.data, form.do_region.data, form.do_server_name.data)
        print(string)
        return render_template('confirm.html', status=string)

    if form.errors:
        for error_message in form.errors:
            flash("error : {error}".format(error=error_message))
    
    return render_template('digitalocean.html', form=form)


def build_do_cmd_string(token, region, name):
    return "heroku run -a algovpngen --type worker worker -e \"DO_ACCESS_TOKEN=%s;DO_REGION=%s;DO_SERVER_NAME=%s\"" % (token, region, name)