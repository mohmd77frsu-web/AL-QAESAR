#!/usr/bin/env python3
import subprocess
import time
import sys

def create_public_tunnel(port=5000):
    print(f"[*] جاري إنشاء النفق الآمن لتوليد الرابط العام على المنفذ {port}...")
    time.sleep(1)
    
    tunnels = [
        ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{port}", "serveo.net"],
        ["ssh", "-o", "StrictHostKeyChecking=no", "-R", f"80:localhost:{port}", "localhost.run"]
    ]
    
    for cmd in tunnels:
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    if "https://" in output:
                        for word in output.split():
                            if word.startswith("https://"):
                                print(f"\n[+] تم توليد الرابط العام بنجاح: {word}\n")
                                return word
        except Exception as e:
            continue
            
    print("[-] تعذر إنشاء النفق، تأكد من تثبيت عميل SSH والاتصال بالإنترنت.")
    return None

if __name__ == "__main__":
    create_public_tunnel()
