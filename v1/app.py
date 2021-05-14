from flask import Flask

app = Flask(__name__)

@app.route("/servicio/v1/prediccion/24horas/")
def p24_horas():
  return "predicción 24 horas"

@app.route("/servicio/v1/prediccion/48horas/")
def p48_horas():
  return "predicción 48 horas"

@app.route("/servicio/v1/prediccion/72horas/")
def p72_horas():
  return "predicción 72 horas"