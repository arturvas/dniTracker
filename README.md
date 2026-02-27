## DNI Tracker 
Bot simples em python pra monitorar o status do tramite de residencia na Argentina (migraciones) e enviar notificações via Telegram.

### O script consome a API interna da Migraciones:
Faz um POST com os dados do expediente e data de nascimento

Identifica o passo atual

Notifica via bot do Telegram

 ### Setup local
Instale as dependencias `pip install -r requirements.txt`

Crie um .env baseado nas suas credenciais (Numero Expediente, Data de nascimento, bot token, e chat id)

rode `python bot.py`