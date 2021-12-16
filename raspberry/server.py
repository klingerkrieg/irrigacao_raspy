from flask import Flask
import datetime, time
import threading
import flask
import requests
import logging
import traceback
from config import *
from history import *
from constants import *
import os

PRODUCTION = False

#use o seguinte comando no serv de producao
# export FLASK_ENV=production
if os.environ.get("FLASK_ENV") == "production":
    PRODUCTION = True

if PRODUCTION:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    print("GPIO active.")


INFO_LOG = 'info.log'
logging.basicConfig(filename=INFO_LOG, 
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')



        
#start
initialize_json()
config = read_json()

#cadastrar e deletar valvulas

app = Flask(__name__)

@app.route('/')
def get_conf():
    #set headers json
    response = flask.Response()
    response.content_type = "application/json"
    response.data = config.__str__()
    config["current_time"] = datetime.datetime.now().strftime("%H:%M:%S")
    return response

@app.route('/history')
def history():
    with open(HISTORY_JSON, 'r') as f:
        hist = json.load(f)
        f.close()
    return hist

@app.route('/get_precipitation')
def get_precipitation():
    token = "25cd15646b405897ea8f2276bf4b5c00"
    response = requests.get("http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/5871/hours/72?token="+token)
    try:
        data = json.loads(response.content)
        next_hours = 12
        past_hours = 0
        past_precipt = 0.0
        next_precipt = 0.0
        for values in data["data"]:
            date = datetime.datetime.strptime(values["date"],"%Y-%m-%d %H:%M:%S")

            if date.hour < datetime.datetime.now().hour:
                past_hours += 1
                past_precipt += values["rain"]["precipitation"]
            else:
                next_hours -= 1
                next_precipt += values["rain"]["precipitation"]
            
            if next_hours == 0:
                break

        config["precipitation_today"] = "%.2f" % (float(past_precipt)/past_hours)    
        config["next_precipitation"] = "%.2f" % (float(next_precipt)/12)
        write_json(config)
        return {"next_precipitation":config["next_precipitation"],
                "precipitation_today":config["precipitation_today"]}
    except Exception:
        logging.error("Erro ao capturar previsao do tempo")
        logging.error(traceback.format_exc())
        print("Erro ao capturar previsao do tempo")
        return "false"

@app.route('/schedule_time_all/<string:hour>', methods=['PUT'])
def schedule_time_all(hour):
    for valve in config["valves"]:
        time_obj = datetime.datetime.strptime(hour,"%H:%M:%S")
        valve["scheduled_time"] = time_obj.strftime("%H:%M:%S")
    write_json(config)
    resp = {}
    for valve in config["valves"]:
        resp[valve["name"]] = valve["scheduled_time"]
    return resp

@app.route('/schedule_time/<int:valve_id>/<string:hour>', methods=['PUT'])
def set_schedule_time(valve_id,hour):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    time_obj = datetime.datetime.strptime(hour,"%H:%M:%S")
    valve["scheduled_time"] = time_obj.strftime("%H:%M:%S")
    write_json(config)
    return {valve["name"]:valve["scheduled_time"]}



@app.route('/cancel_all/<string:value>', methods=['PUT'])
def cancel_all(value):
    for valve in config["valves"]:
        if value == "1":
            valve["irrigation"] = IRR_CANCELED
        else:
            valve["irrigation"] = IRR_WAITING
    write_json(config)
    resp = {}
    for valve in config["valves"]:
        resp[valve["name"]] = valve["irrigation"]
    return resp

@app.route('/cancel/<int:valve_id>/<int:value>', methods=['PUT'])
def cancel(valve_id,value):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    if value == 1:
        valve["irrigation"] = IRR_CANCELED
    else:
        valve["irrigation"] = IRR_WAITING
    write_json(config)
    return {valve["name"]:valve["irrigation"]}

@app.route('/set_duration/<int:valve_id>/<string:hour>', methods=['PUT'])
def set_duration(valve_id,hour):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    time_obj = datetime.datetime.strptime(hour,"%H:%M:%S")
    valve["duration"] = time_obj.strftime("%H:%M:%S")
    write_json(config)
    return {valve["name"]:valve["duration"]}
    
@app.route('/set_name/<int:valve_id>/<string:name>', methods=['PUT'])
def set_name(valve_id,name):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    try:
        valve["name"] = name
        write_json(config)
        return {"id":valve_id, "name":valve["name"]}
    except:
        return "false"


@app.route('/set_gpio/<int:valve_id>/<int:gpio>', methods=['PUT'])
def set_gpio(valve_id,gpio):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    try:
        valve["gpio"] = gpio
        write_json(config)
        return {valve["name"]:valve["gpio"]}
    except:
        return "false"



@app.route('/set_irrigate/<int:valve_id>/<string:mode>', methods=['PUT'])
def set_irrigate(valve_id,mode):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    if mode == "1":
        valve["irrigation"] = IRR_WAITING
    elif mode == "2":
        valve["irrigation"] = IRR_CANCELED
    elif mode == "3":
        valve["irrigation"] = IRR_FINIHSED
    elif mode == "4":
        valve["irrigation"] = IRR_INTERRUPT
    
    write_json(config)
    return {valve["name"]:valve["irrigation"]}

@app.route('/irrigate/<int:valve_id>/<string:hour>', methods=['PUT'])
def irrigate(valve_id,hour):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    time_obj = datetime.datetime.strptime(hour,"%H:%M:%S")
    valve["remains"] = time_obj.strftime("%H:%M:%S")
    valve["irrigation"] = IRR_WAITING
    get_precipitation()
    write_json(config)
    return {valve["name"]:valve["remains"],"irrigation":valve["irrigation"]}

def start_valve(gpio):
    print ("starting:",gpio)
    if PRODUCTION: 
        logging.info("GPIO"+str(gpio)+"=OUT")
        #to work with 5v
        GPIO.setup(gpio, GPIO.OUT)
        #GPIO.output(gpio, 0)

def stop_valve(gpio):
    print ("stop:",gpio)
    if PRODUCTION:
        logging.info("GPIO"+str(gpio)+"=IN")
        GPIO.setup(gpio, GPIO.IN)
        #GPIO.output(gpio, 1)


def threadFunc():
    last_minute = None
    delay_sec = 1
    while True:

        #quando mudar de dia
        if config["last_day"] != datetime.datetime.now().strftime("%d/%m/%Y"):
            config["last_day"] = datetime.datetime.now().strftime("%d/%m/%Y")
            #reativa tudo
            for valve in config["valves"]:
                #if valve["irrigation"] in [IRR_CANCELED,IRR_FINIHSED,IRR_FINIHSED]:
                valve["irrigation"] = IRR_WAITING
            write_json(config)


        now = datetime.datetime.now().strftime("%H:%M:%S")
        if last_minute != now:
            last_minute = now

            #verifica se alguma valvula tem agendamento no horário atual
            for valve in config["valves"]:

                #se o status da irrigacao for diferente de rodando ou cancelado
                if valve["irrigation"] == IRR_WAITING:
                    logging.debug("Verificando válvula:"+valve["name"]+" hora programada:" + valve["scheduled_time"])
                    #compara o horario atual com o da irrigacao
                    now_t = datetime.datetime.strptime(now,"%H:%M:%S")
                    scheduled_t = datetime.datetime.strptime(valve["scheduled_time"],"%H:%M:%S")

                    if (now_t.strftime("%H:%M") == scheduled_t.strftime("%H:%M")):
                        #verifica a chuva nas proximas horas
                        get_precipitation()
                        #se for abaixo do minimo necessario para nao irrigar
                        if (float(config["next_precipitation"]) < float(config["precipitation_limit"]) 
                            and float(config["precipitation_today"]) < float(config["precipitation_limit"])):
                            logging.info("Válvula:"+valve["name"]+" iniciando, precipitação:"+config["next_precipitation"]+" limite:"+config["precipitation_limit"])
                            #irriga normalmente
                            valve["remains"]   = valve["duration"]
                            valve["irrigated"] = "00:00:00"
                        else:
                            logging.info("Válvula:"+valve["name"]+" cancelada por motivo de chuva.")
                            valve["irrigation"] = IRR_CANCELED
                        write_json(config)
                
        time.sleep(delay_sec)
        for valve in config["valves"]:
            if valve["remains"] != "00:00:00":
                #inicia a irrigacao
                if valve["irrigation"] not in([IRR_RUNNING, IRR_INTERRUPT]):
                    #iniciar na GPIO
                    start_valve(valve["gpio"])
                    add_history("Start irrigation",config,valve)
                    valve["irrigation"] = IRR_RUNNING
                
                #atualiza o tempo que falta
                logging.info("Irrigando "+valve["name"]+" "+valve["remains"])
                remains = datetime.datetime.strptime(valve["remains"],"%H:%M:%S")
                remains = remains - datetime.timedelta(seconds=delay_sec)

                #atualiza o tempo que ja irrigou
                irrigated = datetime.datetime.strptime(valve["irrigated"],"%H:%M:%S") + datetime.timedelta(seconds=delay_sec)
                valve["irrigated"] = irrigated.strftime("%H:%M:%S")

                #se tiver ido abaixo de 00:00:00
                if remains.day == 31:
                    remains = datetime.time(0,0)
                valve["remains"] = remains.strftime("%H:%M:%S")

                #parar a irrigacao
                if valve["irrigation"] == IRR_INTERRUPT:
                    add_history("Interrupted irrigation",config,valve)
                    #interromper na GPIO
                    stop_valve(valve["gpio"])
                    valve["remains"] = "00:00:00"
                    valve["irrigated"] = "00:00:00"
                    valve["irrigation"] = IRR_FINIHSED

                elif valve["remains"] == "00:00:00":
                    #interromper na GPIO
                    stop_valve(valve["gpio"])
                    logging.info(valve["name"]+" finalizado.")
                    add_history("Stop irrigation",config,valve)
                    print("Stop irrigation")
                    valve["irrigation"] = IRR_FINIHSED
                    valve["irrigated"] = "00:00:00"
                write_json(config)
                break


if __name__ == '__main__':
    try:
        th = threading.Thread(target=threadFunc,daemon=True)
        logging.info("Thread started")
        th.start()
        add_history("Turn on",config)
        logging.info("Flask started")

        while True:
            try:
                if PRODUCTION:
                    print('Running on 192.168.0.28')
                    app.run(host='192.168.0.28', port=8080)
                else:
                    print('Running on localhost')
                    app.run(host='localhost', port=8080)
            except:
                logging.info("Wait network connection")
                time.sleep(5)

    except (KeyboardInterrupt):
        if PRODUCTION:
            print("Limpando GPIO")
            GPIO.cleanup()
