import socket
import hashlib
import os

RECEIVE_FOLDER = "received"
os.makedirs(RECEIVE_FOLDER, exist_ok=True)

def verify_sha256(file_path, expected_hash):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(4096):
            sha256.update(chunk)
    return sha256.hexdigest() == expected_hash

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(("localhost", 9999))
    s.listen()
    print("🟢 Receiver đang chờ kết nối...")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"📡 Kết nối từ {addr}")
            data = b""
            while chunk := conn.recv(4096):
                data += chunk
                if len(chunk) < 4096:
                    break

            try:
                header, file_data = data.split(b"::", 2)[:2], data.split(b"::", 2)[2]
                filename, file_hash = header[0].decode(), header[1].decode()
                save_path = os.path.join(RECEIVE_FOLDER, filename)

                with open(save_path, "wb") as f:
                    f.write(file_data)

                if verify_sha256(save_path, file_hash):
                    print(f"✅ {filename} hợp lệ! SHA-256 đúng.")
                else:
                    print(f"❌ {filename} lỗi! SHA-256 không khớp.")
            except Exception as e:
                print("❌ Lỗi xử lý dữ liệu:", e)


