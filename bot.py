from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Configuração da API do WhatsApp
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/618470544675414/messages"
ACCESS_TOKEN = "EAAJZAaaQbvioBO9GSOTAg3IyoZCrTXw0xC3XJQDZAMgUyQiHfD608P9kJ9EjN9HQwm3WsG6DtVzF7e7rK940hCZBbzoXjvBQTPd94S8ZCbglZARNrZBL9ybsHMnAVX1BfIjcbgjnUF33o3qM7zyLz22UGKBSN0v9JIEYWFyXwHkFkrZCn1KnMEW1HZCHW2lytX1YyoWx5Rk6s8KZAKdrqCO2M0EZBp0llhhNAbqcHgNcLJ6IscZD"
GOOGLE_SAFE_BROWSING_API_KEY = "YOUR_GOOGLE_API_KEY"

# Função para enviar mensagem no WhatsApp
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
    requests.post(WHATSAPP_API_URL, headers=headers, json=payload)

# Função para verificar se um link é seguro
def check_url_safety(url):
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_SAFE_BROWSING_API_KEY}"
    payload = {
        "client": {"clientId": "yourcompany", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    response = requests.post(api_url, json=payload)
    result = response.json()
    return "Este link pode ser perigoso!" if "matches" in result else "O link parece seguro."

# Rota do Webhook do WhatsApp
@app.route("/webhook", methods=["POST"])
def whatsapp_webhook():
    data = request.get_json()
    if "messages" in data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}):
        message = data["entry"][0]["changes"][0]["value"]["messages"][0]
        sender = message["from"]
        text = message.get("text", {}).get("body", "")

        # Se for um link, verificar a segurança dele
        if "http" in text:
            response_message = check_url_safety(text)
        else:
            response_message = "Desculpe, ainda não entendo essa solicitação."
        
        send_whatsapp_message(sender, response_message)
    return jsonify({"status": "received"})

# Rota para validação do Webhook
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    print("Recebida uma solicitação de verificação do Meta!")  # Debug

    mode = request.args.get("hub.mode")
    challenge = request.args.get("hub.challenge")
    token = request.args.get("hub.verify_token")

    print(f"Modo: {mode}, Token Recebido: {token}, Challenge: {challenge}")  # Debug

    if mode == "subscribe" and token == "meubottoken":  # Certifique-se de que o token está idêntico ao Meta
        print("Token verificado com sucesso!")
        return challenge, 200  # O Meta precisa que o desafio seja retornado diretamente
    else:
        print("Token inválido ou erro na verificação!")
        return "Token inválido", 403

if __name__ == "__main__":
    app.run(port=5000, debug=True)