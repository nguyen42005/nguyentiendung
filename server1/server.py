from flask import Flask, request, send_from_directory, render_template
import socket
import hashlib
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def calculate_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest()

def send_file_over_socket(file_path, file_hash):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(("localhost", 9999))  # Receiver address
        with open(file_path, "rb") as f:
            file_data = f.read()
        filename = os.path.basename(file_path)
        message = f"{filename}::{file_hash}::".encode() + file_data
        s.sendall(message)

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file.filename == "":
            return "No file selected!"
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
        uploaded_file.save(save_path)

        file_hash = calculate_sha256(save_path)
        send_file_over_socket(save_path, file_hash)

        return f"File '{uploaded_file.filename}' đã được gửi đi với SHA-256: {file_hash}"

    return render_template("index.html")

@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory("received", filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

