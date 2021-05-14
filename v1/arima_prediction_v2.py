# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
from statsmodels.tsa.arima_model import ARIMA
import pandas as pd
import pmdarima as pm
import pickle
import pymongo
import time

DATASET = './temperature.csv'


# %%
df = pd.read_csv(DATASET, header=0)


# %%
df = df.dropna()


# %%
df_little = df[0:100]


# %%
model_TEMP = pm.auto_arima(df_little['San Francisco'], start_p=1, start_q=1,
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


# %%
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


# %%
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


# %%
save_model_db(model_TEMP, client='mongodb+srv://neostark:T19blHfuaefxocwA@sandbox.l4kky.mongodb.net',
              model_name='model_TEMP', collection='predictions_models', db='forecast')


# %%
model_TEMP_LOADED = load_model_db(client='mongodb+srv://neostark:T19blHfuaefxocwA@sandbox.l4kky.mongodb.net',
                                  model_name='model_TEMP', collection='predictions_models', db='forecast')

prediction, confint = model_TEMP_LOADED.predict(
    n_periods=24, return_conf_int=True)


# %%
prediction


# %%
