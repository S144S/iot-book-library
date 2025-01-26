from app import app
from flask import render_template

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/mission')
def mission():
    return render_template('mission.html')

@app.route('/planet')
def planet():
    return render_template('planet.html')
