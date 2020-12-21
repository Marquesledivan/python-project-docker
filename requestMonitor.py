# #!/usr/local/bin/python3.7
# # -*- coding: utf-8 -*-

import time
import json
import argparse
import requests
import os 
from datetime import datetime
from datetime import timedelta
from influxdb import InfluxDBClient
import uncurl

try: 
    # Definição dos parametros a serem recebidos 
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--request', help='Nome do request a ser executado', required=True)

    # Pega os valores passados como parametro na chamada do script 
    args = parser.parse_args()
    requestname = args.request

except Exception as e: 
    print('Falha nos parâmetros passados ! ' + requestname)
    print(e.args)

try: 
    # Pega os dados do arquivo de configuração (requestMonitor.yaml)
    filename = os.path.realpath(__file__)
    filename = filename.replace('.py','.yaml')
    file = open(filename,'r')
    txtconfig = file.read() 
    file.close() 

    # Busca o código do curl do requestname recebido como parametro
    txtcurl = ''
    pos_request = txtconfig.find(requestname) + len(requestname)
    txtconfig = txtconfig[pos_request + len('curl:'):len(txtconfig)]
    pos_ini = txtconfig.find('curl ')
    pos_end = txtconfig.find('requestname:') - 1 
    if pos_end < 0: 
        pos_end = len(txtconfig)

except Exception as e: 
    print('Falha ao pegar os parametros do request ! ' + requestname)
    print(e.args)

try: 
    # Pega somente o texto do curl
    txtcurl = txtconfig[pos_ini:pos_end]

    # Retira caracteres inválidos
    txtcurl = txtcurl.replace('\n','')
    txtcurl = txtcurl.replace(' \ ','')

    response = None 
    txtrequest = uncurl.parse(txtcurl)
    txtrequest = 'response = ' + txtrequest 

    # Converte o curl em request
    txtrequest = uncurl.parse(txtcurl)
    txtrequest = 'response = ' + txtrequest 

except Exception as e: 
    print('Falha na preparação dos dados para o request !' + requestname)
    print(e.args)

try: 
    # Inicia as variaveis para fazer o request
    status_code = None 
    tempodecorrido = 0.000

    #Inicia o temporizador
    timeini = time.time()

    # Executa o codigo do request
    exec(txtrequest)

    # Encerrao temporizador
    timeend = time.time()

    # Calcula o tempo decorrido
    tempodecorrido = round(timeend - timeini,3) 

except Exception as e: 
    print('Falha ao executar o request ! ' + requestname)
    print(e.args)
    tempodecorrido = 0.000

try: 
    # ----------------------------------------------
    # Envia para o Grafana (via InfluxDB)
    # ----------------------------------------------
    # Conecta ao influxDB
    clientInfluxDB = InfluxDBClient('__IP__', 8086, 'user', 'ping','passwd')
    datacheck = datetime.now() + timedelta(hours=3)
    # Envia os dados
    json_body = [{"measurement": 'requestMonitor',"tags": {"" "requestname": requestname},"time": datacheck,"fields": {"statuscode":status_code,"tempo": tempodecorrido}}]
    clientInfluxDB.write_points(json_body)
    # Encerra a conexao
    clientInfluxDB.close() 

except Exception as e: 
    print('Falha ao enviar para o Grafana ! ' + requestname)
    print(e.args)