# coding=utf-8
from flask import Flask,request,make_response
import datetime
import os,json
import pyowm
import os

app = Flask(__name__)
owmapikey = os.environ.get('OWMApiKey') #or provide your key here
owm = pyowm.OWM(owmapikey)

pressure = None
sunrise = None
sunset = None

#geting and sending response to dialogflow
@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print("Request:")
    print(json.dumps(req, indent=4))
    res = processRequest(req)
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def getPressure(o):
    # Get atmospheric pressure
    pressure_info = o.get_pressure()
    pressure = str(pressure_info.get('press'))
    sea_level = str(pressure_info.get('sea_level'))
    return pressure, sea_level

def getTemperature(o):
    # temperature in Celsius
    celsius_result = o.get_temperature('celsius')
    temp_celsius = str(celsius_result.get('temp'))
    temp_min = str(celsius_result.get('temp_min'))
    temp_max = str(celsius_result.get('temp_max'))
    return temp_celsius, temp_min, temp_max

def getSunInfo(o):
    sunset = o.get_sunset_time('iso')
    sunrise = o.get_sunrise_time('iso')
    return sunrise, sunset

def getWeatherInfo(o):
    # weather short status
    info_short = str(o.get_status())
    # weather detailed status
    info_detail = str(o.get_detailed_status())
    return info_short, info_detail

# processing the request from dialogflow
def processRequest(req):

    global pressure
    global sunrise, sunset

    # taking data from dialogflow
    result = req.get("queryResult")
    parameters = result.get("parameters")

    # taking parameters data
    city = parameters.get("geo-city")
    date = parameters.get("date")
    time = parameters.get("time")
    date_pariod = parameters.get('date-period')

    name = str(parameters.get("given-name"))
    status = str(parameters.get("Status"))
    home = str(parameters.get("Home"))

    # taking intent name
    meta = result.get("intent")
    intent = meta.get("displayName")

    # case for intent "weather"
    if intent == "weather":
        if city != "":
            # converting to ISO standard
            future_time_weather = time[:10] + " " + time[11:-5] + "00"
            future_date_weather = date[:10] + " " + date[11:-5] + "00"
            future_date_time_weather = date[:10] + " " + time[11:-5] + "00"

            now = datetime.datetime.now()
            # difference_date = date[:10] - now[:10]

            if date == "" and time == "" and date_pariod == "":
                observation = owm.weather_at_place(city)
                w = observation.get_weather()
                # cordinate of location
                latlon_res = observation.get_location()
                lat = str(latlon_res.get_lat())
                lon = str(latlon_res.get_lon())

                # wind data
                wind_res = w.get_wind()
                test = str(w.get_wind())
                wind_speed = str(wind_res.get('speed'))

                rain_info = w.get_rain()
                rain = str(rain_info.get('3h'))
                # cloud data
                cloud_result = str(w.get_clouds())

                # humidity percentage
                humidity = str(w.get_humidity())

                sunrise, sunset = getSunInfo(w)
                info_short, info_detail = getWeatherInfo(w)
                pressure, sea_leavel = getPressure(w)
                temp_celsius, temp_min, temp_max = getTemperature(w)

                speech = "In " + city + " we have " + temp_celsius + " °C." + "The weather is " + info_detail+" TEST  "+rain

            elif (date != "" or time != "") and date_pariod == "":
                fc = owm.three_hours_forecast(city)
                if date != "" and time == "":
                    f = fc.get_weather_at(future_date_weather)
                elif date == "" and time != "":
                    f = fc.get_weather_at(future_time_weather)
                else:
                    f = fc.get_weather_at(future_date_time_weather)

                sunrise, sunset = getSunInfo(f)
                info_short, info_detail = getWeatherInfo(f)
                pressure, sea_leavel = getPressure(f)
                temp_celsius, temp_min, temp_max = getTemperature(f)

                speech = "We will have " + temp_celsius + " °C." + "The weather will be " + info_detail

            else:
                #fc = owm.three_hours_forecast(city, 2)
                #f = fc.get_forecast()

                speech = "Sorry, period weather is not ready yet"
        else:
            speech = "Please tell me which city you mean, it is necessary for proper work."

    if intent == "WeatherPressure":
        speech = "The pressure will be "+pressure+" hPa"

    if intent == "WeatherSunrise":
        sunrise_hour = sunrise[11:16]
        speech = "The sun will rise at "+sunrise_hour+" o'clock"

    if intent == "WeatherSunset":
        sunset_hour = sunset[11:16]
        speech = "The sun will set at "+sunset_hour+" o'clock"

    if intent == "WeatherRain":
        speech = ""
        #speech = rain
    # case for intent "name"
    if intent == "name":
        if name == "Michael":
            speech = "Hello Michael, today we will talk about sience!"

        elif name in ("Filip", "Philip"):
            speech = "Hello " + name +", did you miss me??"

        elif name in ("Markus","Marcus"):
            speech = "Hello my owner! Yes these is me, your robot Pepper!"
        else :
            namedropping = name
            speech = "Nice to meet you "+namedropping

    # case for intent "LightHome"
    #if intent == "LightsHome":
             #if name == "Michael":
            #     speech = "Hello Michael, today we will talk about sience!"
            #
            # elif name in ("Filip", "Philip"):
            #     speech = "Hello " + name +", did you miss me??"
            #
            # elif name in ("Markus","Marcus"):
            #     speech = "Hello my owner! Yes these is me, your robot Pepper!"
            # else :
            #     namedropping = name
            #     speech = "Nice to meet you "+namedropping

    return {
        "fulfillmentText": speech,
        "source": "webhook-micba"
        }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')

