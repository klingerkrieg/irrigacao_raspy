from flask import Flask
import json
import datetime, time
import threading
import requests
import logging
import traceback

HISTORY_LOG = 'history.log'
logging.basicConfig(filename=HISTORY_LOG, 
            format='%(asctime)s %(levelname)-8s %(message)s',
            level=logging.INFO,
            datefmt='%Y-%m-%d %H:%M:%S')


with open('config.json', 'r') as f:
    config = json.load(f)

def write_json():
    with open('config.json', 'w') as f:
        logging.info("Configurações modificadas:"+ str(config))
        json.dump(config,f)




app = Flask(__name__)

@app.route('/')
def get_conf():
    return config.__str__()

@app.route('/get_precipitation')
def get_next_precipitation():
    token = "25cd15646b405897ea8f2276bf4b5c00"
    response = requests.get("http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/5871/hours/72?token="+token)
    try:
        data = json.loads(response.content)
        hours = 12
        total = 0.0
        for values in data["data"]:
            total += values["rain"]["precipitation"]
            hours -= 1
            if hours == 0:
                break
        config["next_precipitation"] = "%.2f" % (float(total)/12)
        write_json()
        return config["next_precipitation"]
    except Exception:
        logging.error("Erro ao capturar previsao do tempo")
        logging.error(traceback.format_exc())
        print("Erro ao capturar previsao do tempo")
        return "false"



@app.route('/scheduled_time/<string:hour>', methods=['PUT'])
def set_scheduled_time(hour):
    time_obj = datetime.datetime.strptime(hour,"%H:%M:%S")
    config["scheduled_time"] = time_obj.strftime("%H:%M:%S")
    write_json()
    return "true"


@app.route('/set_duration/<int:valve_id>/<string:hour>', methods=['PUT'])
def set_duration(valve_id,hour):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    time_obj = datetime.datetime.strptime(hour,"%H:%M:%S")
    valve["duration"] = time_obj.strftime("%H:%M:%S")
    write_json()
    return "true"
    
@app.route('/set_name/<int:valve_id>/<string:name>', methods=['PUT'])
def set_name(valve_id,name):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    try:
        valve["name"] = name
        write_json()
        return "true"
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
        write_json()
        return "true"
    except:
        return "false"


@app.route('/irrigate/<int:valve_id>/<string:hour>', methods=['PUT'])
def irrigate(valve_id,hour):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    time_obj = datetime.datetime.strptime(hour,"%H:%M:%S")
    valve["remains"] = time_obj.strftime("%H:%M:%S")
    write_json()
    return "true"

def threadFunc():
    last_minute = None
    delay_sec = 5
    while True:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        if last_minute != now:
            last_minute = now
            logging.info("Verificando hora programada" + config["scheduled_time"])
            #compara o horario atual com o da irrigacao
            now_t = datetime.datetime.strptime(now,"%H:%M:%S")
            scheduled_t = datetime.datetime.strptime(config["scheduled_time"],"%H:%M:%S")
            
            if (now_t.strftime("%H:%M") == scheduled_t.strftime("%H:%M")):
                #verifica a chuva nas proximas horas
                get_next_precipitation()
                #se for abaixo do minimo necessario para nao irrigar
                logging.info("Previsão de precipitação: " + config["next_precipitation"]
                            + " mínimo para cancelar irrigação:" + config["precipitation_limit"])
                if float(config["next_precipitation"]) < float(config["precipitation_limit"]):
                    #irriga normalmente
                    for valve in config["valves"]:
                        valve["remains"] = valve["duration"]
                    write_json()
                
        time.sleep(delay_sec)
        for valve in config["valves"]:
            if valve["remains"] != "00:00:00":
                logging.info("Irrigando "+valve["name"]+" "+valve["remains"])
                remains = datetime.datetime.strptime(valve["remains"],"%H:%M:%S")
                remains = remains - datetime.timedelta(seconds=delay_sec)
                #se tiver ido abaixo de 00:00:00
                if remains.day == 31:
                    remains = datetime.time(0,0)
                valve["remains"] = remains.strftime("%H:%M:%S")
                if valve["remains"] == "00:00:00":
                    logging.info(valve["name"]+" finalizado.")
                    print("Finalizado")
                write_json()
                break


if __name__ == '__main__':    
    th = threading.Thread(target=threadFunc,daemon=True)
    logging.info("Thread started")
    th.start()
    logging.info("Flask started")
    app.run(host='localhost', port=8080)