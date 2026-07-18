from flask import Flask, request
import os
import requests

app = Flask(__name__)

@app.route('/api/webhook', methods=['GET', 'POST'])
def webhook():
    # 1. VERIFIKASI WEBHOOK DARI META (Method GET)
    if request.method == 'GET':
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        # Ambil Verify Token dari Environment Variables Vercel
        verify_token = os.environ.get('VERIFY_TOKEN')

        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                print("Webhook berhasil diverifikasi!")
                return challenge, 200
            else:
                return 'Verifikasi Gagal: Token tidak cocok', 403
        return 'Bad Request', 400

    # 2. MENERIMA & MEMBALAS PESAN MASUK (Method POST)
    elif request.method == 'POST':
        body = request.json

        if body and body.get('object'):
            try:
                # Menelusuri struktur JSON dari WhatsApp
                entry = body['entry'][0]
                changes = entry['changes'][0]
                value = changes['value']
                
                if 'messages' in value:
                    msg = value['messages'][0]
                    phone_number_id = value['metadata']['phone_number_id']
                    from_number = msg['from']
                    msg_body = msg['text']['body']
                    
                    print(f"Pesan masuk dari {from_number}: {msg_body}")

                    # LOGIKA MEMBALAS PESAN
                    access_token = os.environ.get('WA_ACCESS_TOKEN')
                    url = f"https://graph.facebook.com/v17.0/{phone_number_id}/messages"
                    headers = {
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json"
                    }
                    data = {
                        "messaging_product": "whatsapp",
                        "to": from_number,
                        "text": {"body": f"Halo! Pesan kamu: \"{msg_body}\". Bot Python sudah aktif!"}
                    }
                    
                    requests.post(url, headers=headers, json=data)
            except Exception as e:
                print("Terjadi kesalahan:", e)
                
        return 'EVENT_RECEIVED', 200