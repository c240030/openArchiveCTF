from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib

# --- Thông tin từ đề bài ---
PASSPHRASE = b'VIRELIA-WATER-FAC'
IV = b'\x00' * 16 # IV cố định 16 byte toàn số 0
KEY_LENGTH_BYTES = 32 # Thử với AES-256 (32 bytes key)
ENCRYPTED_FILE = 'log.enc' # Tên file log đã tải về

def derive_key(password: bytes, key_len: int) -> bytes:
    """
    Tạo ra khóa từ passphrase.
    PHIÊN BẢN MỚI: Dùng SHA-256.
    """
    derived_bytes = b''
    prev_hash_block = b''
    while len(derived_bytes) < key_len:
        # THAY ĐỔI QUAN TRỌNG Ở ĐÂY
        m = hashlib.sha256()
        m.update(prev_hash_block + password)
        prev_hash_block = m.digest()
        derived_bytes += prev_hash_block
    return derived_bytes[:key_len]

def main():
    """
    Hàm chính để đọc file, tạo khóa, giải mã và in kết quả.
    """
    print("--- Bắt đầu quá trình giải mã ---")

    # 1. Đọc file log mã hóa
    try:
        with open(ENCRYPTED_FILE, 'rb') as f:
            encrypted_data = f.read()
        print(f"[+] Đã đọc thành công file '{ENCRYPTED_FILE}'.")
    except FileNotFoundError:
        print(f"[!] LỖI: Không tìm thấy file '{ENCRYPTED_FILE}'.")
        print("    Hãy chắc chắn bạn đã tải file và đặt nó vào cùng thư mục với script này.")
        return

    # 2. Tạo khóa từ passphrase
    key = derive_key(PASSPHRASE, KEY_LENGTH_BYTES)
    print(f"[+] Đã tạo khóa AES-256: {key.hex()}")
    print(f"[+] Sử dụng IV cố định: {IV.hex()}")

    # 3. Giải mã dữ liệu
    try:
        cipher = AES.new(key, AES.MODE_CBC, IV)
        decrypted_padded_data = cipher.decrypt(encrypted_data)
        
        # 4. Loại bỏ padding (PKCS#7)
        plaintext = unpad(decrypted_padded_data, AES.block_size)
        print("[+] Giải mã và loại bỏ padding thành công!")
        
        # 5. In kết quả và tìm flag
        print("\n--- NỘI DUNG LOG ĐÃ GIẢI MÃ ---\n")
        # In kết quả dưới dạng text, bỏ qua các lỗi ký tự nếu có
        decrypted_text = plaintext.decode('utf-8', errors='ignore')
        print(decrypted_text)
        print("\n--- KẾT THÚC LOG ---\n")
        print("Hãy tìm flag trong nội dung log ở trên.")
        
        # Lưu kết quả vào file để dễ xem
        with open('decrypted_log.txt', 'w', encoding='utf-8') as f:
            f.write(decrypted_text)
        print(f"[+] Đã lưu nội dung giải mã vào file 'decrypted_log.txt'")

    except (ValueError, KeyError) as e:
        print(f"[!] LỖI KHI GIẢI MÃ: {e}")
        print("    Nguyên nhân có thể là do khóa hoặc IV không đúng, hoặc file đã bị hỏng.")

if __name__ == '__main__':
    main()