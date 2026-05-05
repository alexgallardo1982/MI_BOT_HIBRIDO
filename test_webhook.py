from flask import Flask, request
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    print("\n" + "="*50)
    print("🔔 PETICIÓN RECIBIDA")
    print("="*50)
    print(f"Método: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {request.get_data(as_text=True)}")
    print("="*50 + "\n")
    return 'OK', 200

if __name__ == '__main__':
    print("🧪 TEST WEBHOOK EN PUERTO 5000")
    app.run(debug=True, port=5000)
