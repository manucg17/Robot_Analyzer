import os
import shutil
import logging
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from Script_Analyzer import ScriptAnalyzer
from encryption_utils import encrypt_data, generate_key, load_key

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'supersecretkey')  # Use environment variable or default key
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'Uploads')
ALLOWED_EXTENSIONS = {'robot'}

# Load environment variables for sender's email and password
sender_email = os.getenv('SENDER_EMAIL')
sender_password = os.getenv('SENDER_PASSWORD')

if not sender_email or not sender_password:
    raise ValueError('SENDER_EMAIL and SENDER_PASSWORD environment variables must be set.')

# Load or generate encryption key
encryption_key_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'encryption.key')
if os.path.exists(encryption_key_path):
    encryption_key = load_key()
else:
    encryption_key = generate_key()
    with open(encryption_key_path, 'wb') as key_file:
        key_file.write(encryption_key)

# Encrypt sender's email and password
encrypted_sender_email = encrypt_data(sender_email.encode(), encryption_key)
encrypted_sender_password = encrypt_data(sender_password.encode(), encryption_key)

# Setup upload folder
if os.path.exists(UPLOAD_FOLDER):
    shutil.rmtree(UPLOAD_FOLDER)
os.makedirs(UPLOAD_FOLDER, mode=0o777)

@app.route('/')
def index():
    return render_template('index.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'robot'

@app.route('/upload', methods=['POST'])
def upload_file():
    recipient_email = request.form.get('recipient_email')
    if not recipient_email:
        return jsonify({'message': 'Recipient email is required', 'isError': True}), 400

    if 'file' not in request.files:
        return jsonify({'message': 'No file part', 'isError': True}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file', 'isError': True}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        if filename.endswith('.robot'):
            analyzer = ScriptAnalyzer(file_path, recipient_email, encrypted_sender_email, encrypted_sender_password, encryption_key)
            try:
                analyzer.run_analysis()
                logging.info('File successfully uploaded, analyzed, and email sent.')
                return jsonify({'message': 'File successfully uploaded and analyzed. Email sent successfully', 'isError': False}), 200
            except Exception as e:
                logging.error(f'Error analyzing the script and sending email: {str(e)}')
                return jsonify({'message': f'Error analyzing the script and sending email: {str(e)}', 'isError': True}), 500
        else:
            return jsonify({'message': 'Invalid file type. Allowed type is .robot', 'isError': True}), 400
    else:
        return jsonify({'message': 'Allowed file type is .robot', 'isError': True}), 400

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=80, debug=True)
