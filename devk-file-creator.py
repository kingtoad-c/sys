import tkinter as tk
from tkinter import filedialog, messagebox
import base64
import struct
import os
import sys
import ast
import importlib.util
import sysconfig

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

def is_std_lib(module):
    if module in sys.builtin_module_names:
        return True
    try:
        spec = importlib.util.find_spec(module)
        if spec and spec.origin:
            stdlib_path = sysconfig.get_paths()["stdlib"]
            return spec.origin.startswith(stdlib_path)
    except Exception:
        pass
    return False

def get_imports_and_python_version(code):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return [], "Invalid Python file"

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])

    third_party = sorted([imp for imp in imports if not is_std_lib(imp)])
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    return third_party, version

def generate_devk(input_path, output_dir):
    with open(input_path, "r", encoding="utf-8") as f:
        code = f.read()

    imports, py_version = get_imports_and_python_version(code)

    key = "Mjg0NzM4NjM="
    mult = 7417
    original_key = base64.b64decode(key).decode("utf-8")
    shift = int(int(original_key) / mult)

    encrypted = encrypt(code, shift)
    encoded = base64.b64encode(encrypted.encode("utf-8")).decode("utf-8")
    compressed = compress(encoded)

    base_name = os.path.splitext(os.path.basename(input_path))[0]
    devk_path = os.path.join(output_dir, f"{base_name}.devk")
    reqs_path = os.path.join(output_dir, f"{base_name}-requirements.txt")

    with open(devk_path, "wb") as f:
        f.write(compressed)

    with open(reqs_path, "w", encoding="utf-8") as f:
        f.write(f"python>={py_version}\n")
        for imp in imports:
            f.write(f"{imp}\n")

    return devk_path, reqs_path, imports, py_version

def select_file():
    filepath = filedialog.askopenfilename(filetypes=[("Python Files", "*.py")])
    if not filepath:
        return

    entry_path_var.set(filepath)

    base_name = os.path.splitext(os.path.basename(filepath))[0]
    output_dir = os.path.join(os.path.dirname(filepath), f"{base_name}-devk")

    try:
        os.makedirs(output_dir, exist_ok=True)
        devk_path, reqs_path, imports, version = generate_devk(filepath, output_dir)

        status_var.set(f"✅ Success: Files saved to {output_dir}")
        details = f"\nPython >= {version}\nImports: {', '.join(imports) if imports else 'None'}"
        messagebox.showinfo("Finished", f".devk and requirements.txt created.\n{details}")
    except Exception as e:
        status_var.set("❌ Failed.")
        messagebox.showerror("Error", f"Conversion failed:\n{e}")

# === GUI Setup ===

root = tk.Tk()
root.title("Python to .devk Converter")
root.geometry("550x280")
root.resizable(False, False)

tk.Label(root, text="📦 Python to .devk File Converter", font=("Segoe UI", 16, "bold")).pack(pady=10)

frame = tk.Frame(root)
frame.pack(pady=5)

tk.Label(frame, text="Selected Python File:", font=("Segoe UI", 11)).pack(anchor="w")

entry_path_var = tk.StringVar()
entry = tk.Entry(frame, textvariable=entry_path_var, width=70, font=("Segoe UI", 10))
entry.pack(padx=10, pady=5)

btn = tk.Button(root, text="📂 Choose File", font=("Segoe UI", 11), command=select_file, width=20)
btn.pack(pady=10)

status_var = tk.StringVar()
status_label = tk.Label(root, textvariable=status_var, fg="green", font=("Segoe UI", 10))
status_label.pack()

footer = tk.Label(root, text="By Windows Inc.", fg="gray", font=("Segoe UI", 9))
footer.pack(side="bottom", pady=8)

root.mainloop()
