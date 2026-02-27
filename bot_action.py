import os
import requests
import telebot
import json
import hashlib
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

def get_last_hash():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r") as f:
                data = json.load(f)
                return data.get("hash", "")
        except:
            return ""
    return ""

def save_hash(hash_string):
    with open(STATUS_FILE, "w") as f:
        json.dump({"hash": hash_string}, f, indent=4)

def generate_hash(data_dict):
    data_string = json.dumps(data_dict, sort_keys=True).encode('utf-8')
    return hashlib.sha256(data_string).hexdigest()

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
            ultimos_passos = res_json["data"][-3:]
            
            status_atual_data = {
                "nome": res_json['datos_persona']['nombres'],
                "vencimento": res_json['datos_persona']['fecha_vencimiento_precaria'],
                "historico": [p["DESCRIPCION"] for p in ultimos_passos]
            }
            
            current_hash = generate_hash(status_atual_data)
            last_hash = get_last_hash()

            if current_hash == last_hash:
                print("Sem alterações no status (Hash idêntico).")
                return

            historico_texto = ""
            for index, passo in enumerate(ultimos_passos):
                if passo["RESUELTO"] == "t":
                    emoji = "👌🏻"
                else:
                    emoji = "😴" if index == len(ultimos_passos) - 1 else "👨🏻‍💻"
                historico_texto += f"{emoji} {passo['DESCRIPCION']}\n"

            nome_completo = res_json['datos_persona']['nombres']
            vencimento = res_json['datos_persona']['fecha_vencimiento_precaria']

            mensagem = (
                f"**DNI update** 🇦🇷\n\n"
                f"**Histórico Recente:**\n"
                f"{historico_texto}\n\n"
                f"**Nome:** {nome_completo}\n"
                f"**Vencimento Precaria:** {vencimento}"
            )
            
            bot.send_message(int(CHAT_ID), mensagem, parse_mode="Markdown")
            save_hash(current_hash)
            print(f"Atualização detectada! Novo Hash: {current_hash[:10]}...")
        else:
            print("Aviso: Dados ainda não disponíveis ou credenciais incorretas.")
            
    except Exception as e:
        print(f"Erro na verificação: {e}")

if __name__ == "__main__":
    verificar_status()
