import json
import pickle
import time
from datetime import datetime, timedelta

import Algorithmia
import pandas as pd
import pymongo
from flask import Flask

app = Flask(__name__)

mongo_client='mongodb+srv://neostark:T19blHfuaefxocwA@sandbox.l4kky.mongodb.net'

def load_model_db(model_name, client, db, collection):
    json_data = {}
    myclient = pymongo.MongoClient(client)

    mydb = myclient[db]

    mycol = mydb[collection]
    data = mycol.find({'name': model_name})

    for i in data:
        json_data = i

    p_model = json_data[model_name]

    return pickle.loads(p_model)

def zip_result(rango_fechas, prediction_temp, prediction_hum):
  result = []
  for tiempo, temp, hum in zip(rango_fechas, prediction_temp, prediction_hum):
      tiempo_unix = time.mktime(tiempo.timetuple())
      result.append(
          {'hour': datetime.utcfromtimestamp(tiempo_unix).strftime('%d-%m %H:%M'),
          'temp': temp,  
            'hum': hum
          })
  return result

def make_prediction_v1(hours):
  model_TEMP = load_model_db('model_TEMP', mongo_client, 'forecast', 'predictions_models')
  model_HUM = load_model_db('model_HUM', mongo_client, 'forecast', 'predictions_models')

  prediction_temp, confint = model_TEMP.predict(n_periods=hours, return_conf_int=True)
  prediction_hum, confint = model_HUM.predict(n_periods=hours, return_conf_int=True)

  primera_fecha = datetime.now() + timedelta(hours=3)
  rango_fechas = pd.date_range(primera_fecha.replace(second=0, microsecond=0), periods=hours, freq='H')

  return zip_result(rango_fechas, prediction_temp, prediction_hum)

def make_prediction_v2(hours):
  # Cargamos los datos de temperatura y humedad desde mongo
  client = pymongo.MongoClient(mongo_client)
  dataset = client.forecast.training_data.find({}, {'_id': 0})
  df = pd.DataFrame(dataset)

  df = df.dropna()
  df_little = df[0:100]

  client = Algorithmia.client('simSRYa+NFCPv34fZp/hN0jvbRt1')
  algo = client.algo('TimeSeries/Forecast/0.2.1')
  algo.set_options(timeout=300)  # optional
  input_temp = [list(df_little['TEMP']),
                hours, # series (hours)
                1   # maxNumPeriods
                ]

  input_hum = [list(df_little['HUM']),
                hours, # series (hours)
                1   # maxNumPeriods
                ]

  primera_fecha = datetime.now() + timedelta(hours=3)
  rango_fechas = pd.date_range(primera_fecha.replace(second=0, microsecond=0), periods=hours, freq='H')
  prediction_temp = algo.pipe(input_temp).result
  prediction_hum = algo.pipe(input_hum).result

  return zip_result(rango_fechas, prediction_temp, prediction_hum)

@app.route("/servicio/v1/prediccion/24horas")
def p24_horas_v1():
  return  json.dumps(make_prediction_v1(24))

@app.route("/servicio/v1/prediccion/48horas")
def p48_horas_v1():
  return json.dumps(make_prediction_v1(48))

@app.route("/servicio/v1/prediccion/72horas")
def p72_horas_v1():
  return json.dumps(make_prediction_v1(72))

# Version 2
@app.route("/servicio/v2/prediccion/24horas")
def p24_horas_v2():
  return json.dumps(make_prediction_v2(24))

@app.route("/servicio/v2/prediccion/48horas")
def p48_horas_v2():
  return json.dumps(make_prediction_v1(48))

@app.route("/servicio/v2/prediccion/72horas")
def p72_horas_v2():
  return json.dumps(make_prediction_v1(72))

if __name__ == '__main__':
  app.run(host="0.0.0.0")
