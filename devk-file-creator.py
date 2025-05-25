import tkinter as tk
from tkinter import filedialog, messagebox
import base64
import struct
import os
import re
import sys
import ast

def encrypt(text, shift):
    encrypted = ""
    for char in text:
        if char.isalpha():
            start = 65 if char.isupper() else 97
            encrypted += chr((ord(char) - start + shift) % 26 + start)
        else:
            encrypted += char
    return encrypted

def compress(text):
    output = bytearray()
    i = 0
    while i < len(text):
        match_offset = 0
        match_length = 0
        for j in range(max(0, i - 255), i):
            length = 0
            while (length < 255 and i + length < len(text) and
                   text[j + length] == text[i + length]):
                length += 1
            if length > match_length:
                match_length = length
                match_offset = i - j
        if match_length >= 3:
            char = text[i + match_length].encode("latin1") if i + match_length < len(text) else b'\x00'
            output.extend(struct.pack('>HBc', match_offset, match_length, char))
            i += match_length + 1
        else:
            output.extend(struct.pack('>HBc', 0, 0, text[i].encode("latin1")))
            i += 1
    return bytes(output)

def get_imports_and_python_version(code):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [], "Invalid Python file"

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return sorted(imports), version

def generate_devk(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        code = f.read()

    imports, py_version = get_imports_and_python_version(code)

    # === Encryption setup ===
    key = "Mjg0NzM4NjM="  # base64-encoded string of int key
    mult = 7417
    original_key = base64.b64decode(key).decode("utf-8")
    shift = int(int(original_key) / mult)

    # Encrypt, base64, compress
    encrypted = encrypt(code, shift)
    encoded = base64.b64encode(encrypted.encode("utf-8")).decode("utf-8")
    compressed = compress(encoded)

    # Write .devk
    with open(output_path, "wb") as f:
        f.write(compressed)

    return imports, py_version

def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if not filepath:
        return

    output_path = os.path.splitext(filepath)[0] + ".devk"
    try:
        imports, version = generate_devk(filepath, output_path)
        msg = f"✅ .devk file created:\n{output_path}\n\n"
        msg += f"📦 Imports: {', '.join(imports) if imports else 'None'}\n"
        msg += f"🐍 Python version: {version}"
        messagebox.showinfo("Success", msg)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create .devk file:\n{e}")

# === GUI Setup ===

root = tk.Tk()
root.title("Python to .devk Converter")
root.geometry("400x200")

label = tk.Label(root, text="Select a Python file to convert to .devk format.", font=("Arial", 12))
label.pack(pady=20)

btn = tk.Button(root, text="Choose Python File", font=("Arial", 12), command=select_file)
btn.pack(pady=10)

footer = tk.Label(root, text="By Windows Inc.", fg="gray", font=("Arial", 9))
footer.pack(side="bottom", pady=5)

root.mainloop()
