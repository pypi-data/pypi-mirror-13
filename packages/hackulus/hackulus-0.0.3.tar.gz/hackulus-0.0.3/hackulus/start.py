import mongoengine as mongo
from flask import Flask, request, jsonify
from flask.templating import render_template
from hackulus.config import *
from hackulus.utils import Interpreter
from hackulus.models import Hacker

app_db = mongo.connect('hackulus')
app = Flask(__name__)

app_shell = Interpreter()

@app.route("/")
def home():
    hackers = Hacker.objects.all()
    return render_template('home.html', hackers=hackers)

@app.route('/shell/<language>', methods=['GET','POST'])
def shell(language):
    """ Takes in 'querystring' from POST request and then
        passes it as an argument into a function of form f(querystring)
        that returns a string """
    if request.method == 'POST':
#         print request.form['querystring']
#         print app_shell.input(request.form['querystring'])
        retval = app_shell.input(request.form['querystring'])
        print(retval)
        return jsonify(retval)
    else:
        app_shell.set_language(language)
        return render_template('shell.html', language=language, APP_CONFIG=APP_CONFIG)

@app.route("/login")
def login():
    return "Yolo"

@app.route('/logout')
def logout():
    return "Byebye"

if __name__ == "__main__":
    app.run(host='localhost', port=8000)