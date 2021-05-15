import Algorithmia
import pymongo
import pandas as pd
MONGO_CLIENT = 'mongodb+srv://neostark:T19blHfuaefxocwA@sandbox.l4kky.mongodb.net'


# Cargamos los datos de temperatura y humedad desde mongo
client = pymongo.MongoClient(MONGO_CLIENT)
dataset = client.forecast.training_data.find({}, {'_id': 0})
df = pd.DataFrame(dataset)

df = df.dropna()
df_little = df[0:100]

client = Algorithmia.client('simSRYa+NFCPv34fZp/hN0jvbRt1')
algo = client.algo('TimeSeries/Forecast/0.2.1')
algo.set_options(timeout=300)  # optional
input_temp = [list(df_little['TEMP']),
              24, # series (hours)
              1   # maxNumPeriods
              ]

input_hum = [list(df_little['HUM']),
              24, # series (hours)
              1   # maxNumPeriods
              ]

print(algo.pipe(input_temp).result)
print(algo.pipe(input_hum).result)
