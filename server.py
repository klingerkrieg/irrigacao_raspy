from flask import Flask
import json
import datetime, time
import threading
import requests
import logging
import traceback

HISTORY_LOG = 'history.log'
INFO_LOG = 'info.log'

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


info_log    = setup_logger("info_log", INFO_LOG)
history_log = setup_logger("history_log", HISTORY_LOG)


IRR_RUNNING  = "irrigando"
IRR_CANCELED = "cancelado"
IRR_FINIHSED = "finalizado por hoje"
IRR_WAITING  = "esperando"

with open('config.json', 'r') as f:
    config = json.load(f)

def write_json():
    with open('config.json', 'w') as f:
        info_log.debug("Configurações modificadas:"+ str(config))
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
        info_log.error("Erro ao capturar previsao do tempo")
        info_log.error(traceback.format_exc())
        print("Erro ao capturar previsao do tempo")
        return "false"

@app.route('/schedule_time_all/<string:hour>', methods=['PUT'])
def schedule_time_all(hour):
    for valve in config["valves"]:
        time_obj = datetime.datetime.strptime(hour,"%H:%M:%S")
        valve["scheduled_time"] = time_obj.strftime("%H:%M:%S")
    write_json()
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
    write_json()
    return {valve["name"]:valve["scheduled_time"]}



@app.route('/cancel_all/<string:value>', methods=['PUT'])
def cancel_all(value):
    for valve in config["valves"]:
        if value == "1":
            valve["irrigation"] = IRR_CANCELED
        else:
            valve["irrigation"] = IRR_FINIHSED
    write_json()
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
        valve["irrigation"] = IRR_FINIHSED
    write_json()
    return {valve["name"]:valve["irrigation"]}

@app.route('/set_duration/<int:valve_id>/<string:hour>', methods=['PUT'])
def set_duration(valve_id,hour):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    time_obj = datetime.datetime.strptime(hour,"%H:%M:%S")
    valve["duration"] = time_obj.strftime("%H:%M:%S")
    write_json()
    return {valve["name"]:valve["duration"]}
    
@app.route('/set_name/<int:valve_id>/<string:name>', methods=['PUT'])
def set_name(valve_id,name):
    if valve_id < len(config["valves"]):
        valve = config["valves"][valve_id]
    else:
        return "false"
    try:
        valve["name"] = name
        write_json()
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
        write_json()
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
    
    write_json()
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
    history_log.info("Válvula:"+valve["name"]+" irrigando por:"+valve["remains"])
    write_json()
    return {valve["name"]:valve["remains"],"irrigation":valve["irrigation"]}

def threadFunc():
    last_minute = None
    delay_sec = 5
    while True:

        #quando mudar de dia
        if config["last_day"] != datetime.datetime.now().strftime("%d/%m/%Y"):
            config["last_day"] = datetime.datetime.now().strftime("%d/%m/%Y")
            #reativa tudo que foi cancelado ou finalizado
            for valve in config["valves"]:
                if valve["irrigation"] in [IRR_CANCELED,IRR_FINIHSED]:
                    valve["irrigation"] = IRR_WAITING
            write_json()


        now = datetime.datetime.now().strftime("%H:%M:%S")
        if last_minute != now:
            last_minute = now

            #verifica se alguma valvula tem agendamento no horário atual
            for valve in config["valves"]:

                #se o status da irrigacao for diferente de rodando ou cancelado
                if valve["irrigation"] not in ([IRR_RUNNING, IRR_CANCELED, IRR_FINIHSED]):
                    info_log.debug("Verificando válvula:"+valve["name"]+" hora programada:" + valve["scheduled_time"])
                    #compara o horario atual com o da irrigacao
                    now_t = datetime.datetime.strptime(now,"%H:%M:%S")
                    scheduled_t = datetime.datetime.strptime(valve["scheduled_time"],"%H:%M:%S")

                    if (now_t.strftime("%H:%M") == scheduled_t.strftime("%H:%M")):
                        valve["irrigation"] = IRR_RUNNING
                        #verifica a chuva nas proximas horas
                        get_next_precipitation()
                        #se for abaixo do minimo necessario para nao irrigar
                        if float(config["next_precipitation"]) < float(config["precipitation_limit"]):
                            info_log.info("Válvula:"+valve["name"]+" iniciando, precipitação:"+config["next_precipitation"]+" limite:"+config["precipitation_limit"])
                            #irriga normalmente
                            valve["remains"] = valve["duration"]
                            history_log.info("Válvula:"+valve["name"]+" irrigando por:"+valve["remains"])
                        else:
                            info_log.info("Válvula:"+valve["name"]+" cancelada por motivo de chuva.")
                            history_log.info("Válvula:"+valve["name"]+" cancelada por motivo de chuva.")
                            valve["irrigation"] = IRR_CANCELED
                        write_json()
                
        time.sleep(delay_sec)
        for valve in config["valves"]:
            if valve["remains"] != "00:00:00":
                valve["irrigation"] = IRR_RUNNING
                info_log.info("Irrigando "+valve["name"]+" "+valve["remains"])
                remains = datetime.datetime.strptime(valve["remains"],"%H:%M:%S")
                remains = remains - datetime.timedelta(seconds=delay_sec)
                #se tiver ido abaixo de 00:00:00
                if remains.day == 31:
                    remains = datetime.time(0,0)
                valve["remains"] = remains.strftime("%H:%M:%S")
                if valve["remains"] == "00:00:00":
                    info_log.info(valve["name"]+" finalizado.")
                    valve["irrigation"] = IRR_FINIHSED
                    print("Finalizado")
                write_json()
                break


if __name__ == '__main__':    
    th = threading.Thread(target=threadFunc,daemon=True)
    info_log.info("Thread started")
    th.start()
    info_log.info("Flask started")
    app.run(host='localhost', port=8080)