import os
import requests
import telebot
import json
from hashlib import md5
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
EXPEDIENTE = os.getenv("EXPEDIENTE")
DIA = os.getenv("DIA")
MES = os.getenv("MES")
ANIO = os.getenv("ANIO")
STATUS_FILE = "last_status.json"

API_URL = "https://www.migraciones.gob.ar/accesible/consultaTramitePrecaria/api/ajax_consulta_tramite.php"
BASE_URL = "https://www.migraciones.gob.ar/accesible/consultaTramitePrecaria/ConsultaUnificada.php"

bot = telebot.TeleBot(TOKEN)

def get_last_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_status(status_data):
    with open(STATUS_FILE, "w") as f:
        json.dump(status_data, f, indent=4)

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
            ultimos_passos = res_json["data"][-4:]
            
            # Criar um hash ou string única baseada nos dados importantes
            status_atual = {
                "nome": res_json['datos_persona']['nombres'],
                "vencimento": res_json['datos_persona']['fecha_vencimiento_precaria'],
                "historico": [p["DESCRIPCION"] for p in ultimos_passos]
            }
            
            last_status = get_last_status()

            # Compara o status atual com o último salvo
            if status_atual == last_status:
                print("Sem alterações no status. Notificação não enviada.")
                return

            historico_texto = ""
            for index, passo in enumerate(ultimos_passos):
                if passo["RESUELTO"] == "t":
                    emoji = "👌🏻"
                else:
                    emoji = "😴" if index == len(ultimos_passos) - 1 else "👨🏻‍💻"
                historico_texto += f"{emoji} {passo['DESCRIPCION']}\n"

            mensagem = (
                f"**ATUALIZAÇÃO RASTREADOR DNI**\n\n"
                f"**Nome:** {status_atual['nome']}\n"
                f"**Histórico Recente:**\n"
                f"{historico_texto}\n\n"
                f"**Vencimento Precaria:** {status_atual['vencimento']}"
            )
            
            bot.send_message(int(CHAT_ID), mensagem, parse_mode="Markdown")
            save_status(status_atual)
            print("Update!")
        else:
            print("Aviso: Dados ainda não disponíveis ou credenciais incorretas.")
            
    except Exception as e:
        print(f"Erro na verificação: {e}")

if __name__ == "__main__":
    verificar_status()