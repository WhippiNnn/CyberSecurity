import threading
import time
import random
import requests
import sys
import os
from stem import Signal
from stem.control import Controller
from datetime import datetime
from colorama import init, Fore, Style

# Başlangıç ayarları
init(autoreset=True)  # Colorama için
proxies = {
    'http': 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}
log_file = 'tor_bot_log.txt'
target_file = 'targets.txt'
retry_limit = 5

def load_targets():
    with open(target_file, 'r') as f:
        targets = [line.strip() for line in f if line.strip()]
    return targets

def renew_tor_ip():
    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()  
            controller.signal(Signal.NEWNYM)
            print(Fore.YELLOW + "[*] IP değişikliği istendi.")
    except Exception as e:
        print(Fore.RED + f"[!] IP değiştirilemedi: {e}")

def get_current_ip():
    try:
        ip = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10).json()['origin']
        print(Fore.CYAN + f"[*] Şu anki IP: {ip}")
        return ip
    except Exception as e:
        print(Fore.RED + f"[!] IP alınamadı: {e}")
        return None

def send_request(target_url):
    try:
        response = requests.get(target_url, proxies=proxies, timeout=10)
        if response.status_code == 200:
            print(Fore.GREEN + f"[*] {target_url} -> Başarılı!")
            return True
        else:
            print(Fore.RED + f"[!] {target_url} -> Hata Kodu: {response.status_code}")
            return False
    except Exception as e:
        print(Fore.RED + f"[!] {target_url} -> İstek hatası: {e}")
        return False

def log_event(ip, target, status):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"[{now}] IP: {ip} | Hedef: {target} | Durum: {'Başarılı' if status else 'Başarısız'}\n")

def tor_bot():
    targets = load_targets()
    last_ip = None
    retries = 0

    while True:
        renew_tor_ip()
        time.sleep(5)
        current_ip = get_current_ip()

        if current_ip and current_ip != last_ip:
            last_ip = current_ip
            retries = 0
            target = random.choice(targets)
            status = send_request(target)
            log_event(current_ip, target, status)
            time.sleep(10)
        else:
            print(Fore.RED + "[!] IP değişmedi! Tekrar deneniyor...")
            retries += 1
            if retries >= retry_limit:
                print(Fore.RED + "[X] Çok fazla başarısız IP değişimi. Bot durduruluyor.")
                break
            time.sleep(5)

def loading_animation(text):
    for i in range(3):
        sys.stdout.write(Fore.YELLOW + f"\r{text}{'.' * i}   ")
        sys.stdout.flush()
        time.sleep(0.5)
    print("\r", end="")  # Satırı temizle

def main_menu():
    while True:
        os.system('clear')
        print(Fore.CYAN + Style.BRIGHT + """
    ================================
          TOR BOT ANA MENÜ
    ================================
        1) Botu Başlat
        2) Logları Gör
        3) Çıkış
    """)
        choice = input(Fore.GREEN + "[?] Seçiminiz: ")

        if choice == '1':
            print(Fore.YELLOW + "[*] Bot başlatılıyor...")
            loading_animation("Yükleniyor")
            bot_thread = threading.Thread(target=tor_bot)
            bot_thread.start()
            bot_thread.join()
        elif choice == '2':
            print(Fore.YELLOW + "\n[*] Log Dosyası İçeriği:\n")
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    print(Fore.WHITE + f.read())
            else:
                print(Fore.RED + "[!] Log dosyası bulunamadı.")
            input(Fore.GREEN + "\n[ENTER] Ana menüye dönmek için...")
        elif choice == '3':
            print(Fore.CYAN + "[*] Çıkılıyor, görüşürüz!")
            sys.exit()
        else:
            print(Fore.RED + "[!] Geçersiz seçim!")
            time.sleep(1)

if __name__ == "__main__":
    main_menu()
