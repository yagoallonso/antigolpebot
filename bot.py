from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/618470544675414/messages"
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # Token do WhatsApp API
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Função para enviar mensagens de resposta no WhatsApp
def send_whatsapp_message(to, message):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "text": {"body": message}
    }

    print(f"📤 Tentando enviar mensagem para {to}: {message}")  # Log antes do envio
    response = requests.post(WHATSAPP_API_URL, headers=headers, json=payload)

    print(f"🔄 Código de status da resposta: {response.status_code}")  # Código HTTP
    print(f"📩 Resposta da API do WhatsApp: {response.json()}")  # Log da resposta JSON

    if response.status_code != 200:
        print(f"⚠️ ERRO ao enviar mensagem: {response.text}")  # Log do erro completo
    
    return response.json()

# Rota para receber mensagens do WhatsApp
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.get_json()
    print("📥 Mensagem Recebida:", data)

    if "entry" in data:
        for entry in data["entry"]:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                messages = value.get("messages", [])
                for message in messages:
                    sender = message["from"]
                    text = message.get("text", {}).get("body", "")

                    print(f"📨 Mensagem recebida de {sender}: {text}")  # Log da mensagem
                    response_message = f"📩 Você enviou: {text}"
                    
                    print("🚀 Chamando send_whatsapp_message()...")  # NOVO LOG
                    send_whatsapp_message(sender, response_message)  # Envia a resposta

    return jsonify({"status": "received"}), 200

# Rota para verificação do webhook
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Erro de verificação", 403

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)