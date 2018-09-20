# coding=utf-8
from flask import Flask,request,make_response
import os,json
import pyowm
import os

app = Flask(__name__)
owmapikey = os.environ.get('OWMApiKey') #or provide your key here
owm = pyowm.OWM(owmapikey)

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

#processing the request from dialogflow
def processRequest(req):

    # taking data from dialogflow
    result = req.get("queryResult")
    parameters = result.get("parameters")

    # taking parameters data
    city = parameters.get("geo-city")
    date = parameters.get("date")
    time = parameters.get("time")
    date_weather = date[:10]+" "+time[11:-3]
    name = str(parameters.get("given-name"))
    status = str(parameters.get("Status"))
    home = str(parameters.get("Home"))

    # taking intent name
    meta = result.get("intent")
    intent = meta.get("displayName")

    # case for intent "weather"
    if intent == "weather":

        if city != "":

            fc = owm.three_hours_forecast(city)

            observation = owm.weather_at_place(city)

            w = observation.get_weather()
            #f = fc.get_weather_at(date_weather)

            # cordinate of location
            latlon_res = observation.get_location()
            lat = str(latlon_res.get_lat())
            lon = str(latlon_res.get_lon())

            sun = w.get_sunset_time('iso')

            # wind data
            wind_res = w.get_wind()
            wind_speed = str(wind_res.get('speed'))

            # cloud data
            cloud_result = str(w.get_clouds())

            # weather short status
            info_short = str(w.get_status())
            #info_short2 = str(f.get_status())

            # weather detailed status
            info_detail = str(w.get_detailed_status())

            # humidity percentage
            humidity = str(w.get_humidity())

            # Get atmospheric pressure
            pressure_info = w.get_pressure()
            pressure = str(pressure_info.get('press'))
            sea_level = str(pressure_info.get('sea_level'))

            # temperature in Celsius
            celsius_result = w.get_temperature('celsius')
            temp_celsius = str(celsius_result.get('temp'))

            #celsius_result2 = f.get_temperature('celsius')
            #temp_celsius2 = str(celsius_result2.get('temp'))

            temp_min=str(celsius_result.get('temp_min'))
            temp_max=str(celsius_result.get('temp_max'))

            speech = "In " + city + " we have " + temp_celsius + " °C." + "The sky is " + info_short +"TEST: "+date_weather
        else:
            speech = "Please tell me which city you mean, it is necessary for proper work."

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
