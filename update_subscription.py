import urllib.request
import base64
import urllib.parse
import json
import os
import subprocess

SUB_URL = "https://get.dealup.online/userkeys/v3f9mi0wnmwitmrhqmy31pf4yaqweukd_1773683821"
CONFIG_PATH = "/root/expense-tracker-bot/xray_config.json"

def fetch_links():
    try:
        req = urllib.request.Request(
            SUB_URL, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8').strip()
        
        # Try base64 decoding (standard for V2Ray/Xray subscriptions)
        try:
            padded = content + '=' * (-len(content) % 4)
            decoded = base64.b64decode(padded).decode('utf-8')
            links = [line.strip() for line in decoded.split('\n') if line.strip()]
        except Exception:
            # Fallback to plain text links
            links = [line.strip() for line in content.split('\n') if line.strip()]
            
        return links
    except Exception as e:
        print(f"Error fetching subscription: {e}")
        return []

def parse_vless(url):
    try:
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != 'vless':
            return None
            
        uuid = parsed.username
        address = parsed.hostname
        port = parsed.port
        
        query = urllib.parse.parse_qs(parsed.query)
        network = query.get('type', ['ws'])[0]
        path = query.get('path', ['/'])[0]
        host = query.get('host', [address])[0]
        security = query.get('security', ['tls'])[0]
        sni = query.get('sni', [host])[0]
        fp = query.get('fp', ['firefox'])[0]
        
        return {
            "uuid": uuid,
            "address": address,
            "port": int(port) if port else 443,
            "network": network,
            "path": path,
            "host": host,
            "security": security,
            "sni": sni,
            "fp": fp
        }
    except Exception as e:
        print(f"Error parsing VLESS URL: {e}")
        return None

def update_xray():
    links = fetch_links()
    vless_links = [l for l in links if l.startswith('vless://')]
    
    if not vless_links:
        print("No VLESS links found in subscription.")
        return
        
    vless_data = parse_vless(vless_links[0])
    if not vless_data:
        print("Failed to parse the VLESS link.")
        return
        
    config = {
      "log": {
        "loglevel": "warning"
      },
      "inbounds": [
        {
          "port": 8080,
          "protocol": "http",
          "settings": {
            "timeout": 360
          }
        }
      ],
      "outbounds": [
        {
          "protocol": "vless",
          "settings": {
            "vnext": [
              {
                "address": vless_data["address"],
                "port": vless_data["port"],
                "users": [
                  {
                    "id": vless_data["uuid"],
                    "encryption": "none",
                    "level": 0
                  }
                ]
              }
            ]
          },
          "streamSettings": {
            "network": vless_data["network"],
            "security": vless_data["security"],
            "tlsSettings": {
              "serverName": vless_data["sni"],
              "fingerprint": vless_data["fp"]
            },
            "wsSettings": {
              "path": vless_data["path"],
              "headers": {
                "Host": vless_data["host"]
              }
            }
          }
        }
      ]
    }
    
    new_config_str = json.dumps(config, indent=2)
    
    # Check if config changed
    old_config_str = ""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r') as f:
            old_config_str = f.read()
            
    try:
        changed = json.loads(new_config_str) != json.loads(old_config_str)
    except Exception:
        changed = True
        
    if changed:
        print("Config changed! Updating xray_config.json...")
        with open(CONFIG_PATH, 'w') as f:
            f.write(new_config_str)
            
        print("Restarting xray container...")
        subprocess.run(
            ["docker", "compose", "restart", "xray"],
            cwd="/root/expense-tracker-bot"
        )
        print("Xray restarted successfully.")
    else:
        print("Config is up-to-date. No restart needed.")

if __name__ == "__main__":
    update_xray()
