from statsmodels.tsa.arima_model import ARIMA
import pandas as pd
import pmdarima as pm
import pickle
import pymongo
import time

MONGO_CLIENT='mongodb+srv://neostark:T19blHfuaefxocwA@sandbox.l4kky.mongodb.net'

def save_model_db(model, client, db, collection, model_name):
    p_model = pickle.dumps(model)

    # guardando el modelo en mongo
    myclient = pymongo.MongoClient(client)

    mydb = myclient[db]

    mycol = mydb[collection]
    info = mycol.insert_one(
        {model_name: p_model, 'name': model_name, 'created_time': time.time()})
    print(info.inserted_id, ' id saved successfully!')

    details = {
        'inserted_id': info.inserted_id,
        'model_name': model_name,
        'created_time': time.time()
    }

    return details


# Cargamos los datos de temperatura y humedad desde mongo
client = pymongo.MongoClient(MONGO_CLIENT)
dataset = client.forecast.training_data.find({}, {'_id':0})
df = pd.DataFrame(dataset)

df = df.dropna()
df_little = df[0:100]
print(df_little)


model_TEMP = pm.auto_arima(df_little['TEMP'], start_p=1, start_q=1,
                      test='adf',       # use adftest to find optimal 'd'
                      max_p=3, max_q=3, # maximum p and q
                      m=1,              # frequency of series
                      d=None,           # let model determine 'd'
                      seasonal=False,   # No Seasonality
                      start_P=0, 
                      D=0, 
                      trace=True,
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)

model_HUM = pm.auto_arima(df_little['HUM'], start_p=1, start_q=1,
                           test='adf',       # use adftest to find optimal 'd'
                           max_p=3, max_q=3,  # maximum p and q
                           m=1,              # frequency of series
                           d=None,           # let model determine 'd'
                           seasonal=False,   # No Seasonality
                           start_P=0,
                           D=0,
                           trace=True,
                           error_action='ignore',
                           suppress_warnings=True,
                           stepwise=True)



save_model_db(model_HUM, client=MONGO_CLIENT,
              model_name='model_HUM', collection='predictions_models', db='forecast')

save_model_db(model_TEMP, client=MONGO_CLIENT,
              model_name='model_TEMP', collection='predictions_models', db='forecast')

