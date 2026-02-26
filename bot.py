import os
import requests
import telebot
import time
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BASE_URL = "https://www.migraciones.gob.ar/accesible/consultaTramitePrecaria/ConsultaUnificada.php"
API_URL = "https://www.migraciones.gob.ar/accesible/consultaTramitePrecaria/api/ajax_consulta_tramite.php"

bot = telebot.TeleBot(TOKEN)
ultimo_status_salvo = ""

def verificar_status():
    global ultimo_status_salvo

    payload = {
        "data": json.dumps({
            "nro_expediente": os.getenv("EXPEDIENTE"),
            "fecha_nac": f"{os.getenv('DIA')}/{os.getenv('MES')}/{os.getenv('ANIO')}"
        })
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Referer": BASE_URL,
        "X-Requested-With": "XMLHttpRequest", # Indica que é uma chamada AJAX
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    
    try:
        response = requests.post(API_URL, data=payload,headers=headers, timeout=15)
        res_json = response.json()

        if response.status_code != 200:
            print(f"Erro no servidor: {response.status_code}")
            return
        
        res_json = response.json()

        # verifica se tem dados na respota
        if "data" in res_json and len(res_json["data"]) > 0:
            
            passo_ativo = next((item for item in res_json["data"] if item["RESUELTO"] == "f"), res_json["data"][-1]) 
            
            status_texto = passo_ativo["DESCRIPCION"]
            print(f"[{time.strftime('%H:%M:%S')}] Status atual: {status_texto}")

            if status_texto != ultimo_status_salvo:
                nome_completo = res_json['datos_persona']['nombres']
                vencimento = res_json['datos_persona']['fecha_vencimiento_precaria']

                mensagem = (
                    f"**ATUALIZAÇÃO NO DNI**\n\n"
                    f"**Nome:** {nome_completo}\n"
                    f"**Status:** {status_texto}\n"
                    f"**Vencimento Precaria:** {vencimento}"
                )
                bot.send_message(CHAT_ID, mensagem, parse_mode="Markdown")
                ultimo_status_salvo = status_texto
        else:
            print("Aviso: Dados ainda não disponíveis ou CPF/Data incorretos.")
            
    except Exception as e:
        print(f"Erro na verificação: {e}")

if __name__ == "__main__":
    print("Monitoramento iniciado via API...")
    verificar_status()