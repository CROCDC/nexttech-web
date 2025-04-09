from flask import Flask, render_template, request, jsonify
import os
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['MAIL_SERVER'] = os.getenv('EMAIL_HOST', 'mailu.pantech.solutions')
app.config['MAIL_PORT'] = int(os.getenv('EMAIL_PORT', 587))
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER', 'info@pantech.solutions')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER', 'info@pantech.solutions')

mail = Mail(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        
        msg = Message(
            subject=f'New contact message from {name}',
            recipients=[os.getenv('EMAIL_USER', 'info@pantech.solutions')],
            body=f'''
            Name: {name}
            Email: {email}
            Message: {message}
            '''
        )
        
        mail.send(msg)
        return jsonify({'success': True, 'message': 'Message sent successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 160))) 