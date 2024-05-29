from flask import Flask, request, jsonify, render_template_string
from cryptography.fernet import Fernet
import base64
import os

app = Flask(__name__)

def generate_key(passphrase):
    return base64.urlsafe_b64encode(passphrase.ljust(32)[:32].encode())

@app.route('/')
def index():
    return render_template_string('''
    <!doctype html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
        <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
        <title>Password Manager</title>
        <style>
          body { background-color: #f7f9fc; }
          .container { margin-top: 50px; }
          .card { margin-bottom: 20px; }
          .btn-primary { background-color: #007bff; border-color: #007bff; }
          .result { margin-top: 20px; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="card">
            <div class="card-header">
              <h2>Password Encryption</h2>
            </div>
            <div class="card-body">
              <form id="encrypt-form">
                <div class="form-group">
                  <label for="password">Password to Encrypt:</label>
                  <input type="text" class="form-control" id="password" name="password" required>
                </div>
                <div class="form-group">
                  <label for="passkey">Passkey:</label>
                  <input type="text" class="form-control" id="passkey" name="passkey" required>
                </div>
                <button type="submit" class="btn btn-primary">Encrypt</button>
              </form>
              <div id="encrypt-result" class="result"></div>
            </div>
          </div>
          <div class="card">
            <div class="card-header">
              <h2>Password Decryption</h2>
            </div>
            <div class="card-body">
              <form id="decrypt-form">
                <div class="form-group">
                  <label for="encrypted_password">Encrypted Password:</label>
                  <input type="text" class="form-control" id="encrypted_password" name="encrypted_password" required>
                </div>
                <div class="form-group">
                  <label for="decrypt_passkey">Passkey:</label>
                  <input type="text" class="form-control" id="decrypt_passkey" name="passkey" required>
                </div>
                <button type="submit" class="btn btn-primary">Decrypt</button>
              </form>
              <div id="decrypt-result" class="result"></div>
            </div>
          </div>
        </div>
        <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.9.2/dist/umd/popper.min.js"></script>
        <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        <script>
          $(document).ready(function() {
            $('#encrypt-form').on('submit', function(e) {
              e.preventDefault();
              $.ajax({
                type: 'POST',
                url: '/encrypt',
                data: $(this).serialize(),
                success: function(response) {
                  $('#encrypt-result').html('<div class="alert alert-success">Encrypted Password: ' + response.encrypted_password + '</div>');
                },
                error: function() {
                  $('#encrypt-result').html('<div class="alert alert-danger">An error occurred while encrypting the password.</div>');
                }
              });
            });
            $('#decrypt-form').on('submit', function(e) {
              e.preventDefault();
              $.ajax({
                type: 'POST',
                url: '/decrypt',
                data: $(this).serialize(),
                success: function(response) {
                  $('#decrypt-result').html('<div class="alert alert-success">Decrypted Password: ' + response.decrypted_password + '</div>');
                },
                error: function() {
                  $('#decrypt-result').html('<div class="alert alert-danger">An error occurred while decrypting the password.</div>');
                }
              });
            });
          });
        </script>
      </body>
    </html>
    ''')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    password = request.form['password']
    passkey = request.form['passkey']
    key = generate_key(passkey)
    fernet = Fernet(key)
    encrypted_password = fernet.encrypt(password.encode()).decode()
    return jsonify({"encrypted_password": encrypted_password})

@app.route('/decrypt', methods=['POST'])
def decrypt():
    encrypted_password = request.form['encrypted_password']
    passkey = request.form['passkey']
    key = generate_key(passkey)
    fernet = Fernet(key)
    try:
        decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
        return jsonify({"decrypted_password": decrypted_password})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
