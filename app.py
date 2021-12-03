import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# to use flash, you need a secret key
app.config['SECRET_KEY'] = 'thisisasecret'

db = SQLAlchemy(app)


class City(db.Model):
    # create columns for db
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)


def get_weather_data(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={ city }&units=metric&appid=c132d77d92936f71976280314983c16b'
    res = requests.get(url).json()
    return res


@app.route('/')
def index_get():

    # gives all cities in db-table
    cities = City.query.all()

    weather_data = []

    # loop all cities
    for city in cities:

        res = get_weather_data(city.name)
        # show json in console
        print(res)

        weather = {
            'city': city.name,
            'temperature': res['main']['temp'],
            'description': res['weather'][0]['description'],
            'icon': res['weather'][0]['icon'],
        }

        # after every loop, each city's weather data will append in the weather_data array
        weather_data.append(weather)

    return render_template('weather.html', weather_data=reversed(weather_data))


@app.route('/', methods=['POST'])
def index_post():
    err_msg = ''
    new_city = request.form.get('city')

    if new_city:
        # check if posted city is already in db
        existing_city = City.query.filter_by(name=new_city).first()

        if not existing_city:
            new_city_data = get_weather_data(new_city)

            # check if posted city exists in API, code 200 = successful
            if new_city_data['cod'] == 200:

                # create new city
                new_city_obj = City(name=new_city)

                # save new city to db
                db.session.add(new_city_obj)
                db.session.commit()

            else:
                err_msg = 'City does not exist!'
        else:
            err_msg = 'City already exists in the list!'

    # shows 'alert' after post
    if err_msg:
        flash(err_msg, 'error')
    else:
        flash('City added to the list')

    return redirect(url_for('index_get'))


@app.route('/delete/<name>')
def delete(name):
    # delete city from db
    city = City.query.filter_by(name=name).first()
    db.session.delete(city)
    db.session.commit()

    flash(f'Succesfully deleted { city.name }.', 'success')
    return redirect(url_for('index_get'))
