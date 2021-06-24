import requests
from flask import Flask, render_template, request, redirect
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

db = SQLAlchemy(app)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(255), unique=False, nullable=True, primary_key=False)
    forecast = db.Column(db.String(255), unique=False, nullable=True, primary_key=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return "<City/Forecast: {}/{}>".format(self.city, self.forecast)


@app.route("/", methods=["GET", "POST"])
def home():
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=0fbd5ebbc7f18bbc23508a54bdbba174'
    city = request.form.get('city')
    r = requests.get(url.format(city)).json()
    if request.method != 'POST':
        weather = ''
    elif r['cod'] != 200:
        weather = 'Not found'
    elif city == '':
        weather = ''
    else:
        weather = {
            'city': r['name'],
            'temperature': round((5 / 9) * (r['main']['temp'] - 32)),
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
            'unit': '°C'
        }
        result = Result(city=weather['city'], forecast=(str(weather['temperature']) + weather['unit']))
        db.session.add(result)
        db.session.commit()
    return render_template('celsius.html', weather=weather, r=r)

@app.route('/fahrenheit', methods=['GET', 'POST'])
def fahrenheit():
    url = 'http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid=0fbd5ebbc7f18bbc23508a54bdbba174'
    city = request.form.get('city')
    r = requests.get(url.format(city)).json()
    if request.method != 'POST':
        weather = ''
    elif r['cod'] != 200:
        weather = 'Not found'
    elif city == '':
         weather = ''
    else:
        weather = {
            'city': r['name'],
            'temperature': r['main']['temp'],
            'description': r['weather'][0]['description'],
            'icon': r['weather'][0]['icon'],
            'unit': '°F'
        }
        result = Result(city=weather['city'], forecast=(str(weather['temperature']) + weather['unit']))
        db.session.add(result)
        db.session.commit()
    return render_template('fahrenheit.html', weather=weather, r=r)

@app.route("/history", methods=['GET', 'POST'])
def history():
    results = Result.query.all()
    return render_template("history.html", results=results)

@app.route("/search")
def search():
    city = request.args.get("city")
    city = "%{}%".format(city)
    results = Result.query.filter(Result.city.like(city)).all()
    return render_template("history.html", results=results)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == "__main__":
    app.run()