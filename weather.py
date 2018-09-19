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
    
    result = req.get("queryResult")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    name = str(parameters.get("given-name"))
    status = str(parameters.get("Status"))
    home = str(parameters.get("Home"))
    meta = result.get("intent")
    intent = meta.get("displayName")
    if intent == "weather":
        observation = owm.weather_at_place(city)
        w = observation.get_weather()
        latlon_res = observation.get_location()
        lat=str(latlon_res.get_lat())
        lon=str(latlon_res.get_lon())

        sun = w.get_sunset_time('iso')
     
        wind_res = w.get_wind()
        wind_speed = str(wind_res.get('speed'))

        cloud_result = str(w.get_clouds())

        inf_info = str(w.get_status())

        humidity=str(w.get_humidity())

        celsius_result=w.get_temperature('celsius')
        temp_celsius=str(celsius_result.get('temp'))

        fahrenheit_result=w.get_temperature('fahrenheit')
        temp_min_fahrenheit=str(fahrenheit_result.get('temp_min'))
        temp_max_fahrenheit=str(fahrenheit_result.get('temp_max'))

        speech = "In " + city + " we have " + temp_celsius + " °C." + "The sky is " + inf_info

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

    return {
        "fulfillmentText": speech,
        "source": "webhook-micba"
        }
    
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')
