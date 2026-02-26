import os
import requests
import telebot
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
EXPEDIENTE = os.getenv("EXPEDIENTE")
DIA = os.getenv("DIA")
MES = os.getenv("MES")
ANIO = os.getenv("ANIO")

API_URL = "https://www.migraciones.gob.ar/accesible/consultaTramitePrecaria/api/ajax_consulta_tramite.php"
BASE_URL = "https://www.migraciones.gob.ar/accesible/consultaTramitePrecaria/ConsultaUnificada.php"

bot = telebot.TeleBot(TOKEN)

def verificar_status():
    payload = {
        "data": json.dumps({
            "nro_expediente": EXPEDIENTE,
            "fecha_nac": f"{DIA}/{MES}/{ANIO}"
        })
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": BASE_URL,
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    
    try:
        response = requests.post(API_URL, data=payload, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"Erro no servidor: {response.status_code}")
            return
        
        res_json = response.json()

        if "data" in res_json and len(res_json["data"]) > 0:
            passo_ativo = next((item for item in res_json["data"] if item["RESUELTO"] == "f"), res_json["data"][-1]) 
            
            status_texto = passo_ativo["DESCRIPCION"]
            print(f"Status detectado: {status_texto}")
            
            nome_completo = res_json['datos_persona']['nombres']
            vencimento = res_json['datos_persona']['fecha_vencimiento_precaria']

            mensagem = (
                f"**RASTREADOR DNI**\n\n"
                f"**Nome:** {nome_completo}\n"
                f"**Status Atual:** {status_texto}\n"
                f"**Vencimento Precaria:** {vencimento}"
            )
            
            bot.send_message(int(CHAT_ID), mensagem, parse_mode="Markdown")
            print("Mensagem enviada com sucesso!")
        else:
            print("Aviso: Dados ainda não disponíveis ou credenciais incorretas.")
            
    except Exception as e:
        print(f"Erro na verificação: {e}")

if __name__ == "__main__":
    verificar_status()