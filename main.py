
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/send_message', methods=['POST'])
def handle_message():
    user_message = request.json.get('message')
    print(f"Received: {user_message}")
    
    bot_reply = f"'{user_message}' 잘 받았습니다!"
    return jsonify({'reply': bot_reply})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
