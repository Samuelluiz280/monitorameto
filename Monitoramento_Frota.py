import time
import os
import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- SUAS CONFIGURAÇÕES ---
URL_MAPA = "https://paineladmin3.azurewebsites.net/mobfy/vermapa"
NOME_GRUPO_WHATSAPP = "Teste"
INTERVALO_MINUTOS = 5

CAMINHO_PERFIL = os.path.join(os.getcwd(), "Bot_WhatsApp_Profile")

def iniciar_driver():
    print("🚀 Iniciando navegador (Modo Multi-Abas)...")
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={CAMINHO_PERFIL}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def job(driver):
    try:
        # --- PASSO 1: FOCAR NA ABA DO MAPA (ABA 0) ---
        driver.switch_to.window(driver.window_handles[0])
        print("📍 Forçando retorno ao Mapa (Aba 1)...")
        
        # --- AQUI ESTÁ A MUDANÇA MÁGICA ---
        # Em vez de apenas atualizar, ele força o navegador a ir para o link certo
        driver.get(URL_MAPA)
        
        # Espera o site carregar e os ícones aparecerem
        time.sleep(15) 

        # Captura os dados
        try:
            vermelhos = driver.find_elements(By.CSS_SELECTOR, "img[src*='pin-vermelho.png']")
            verdes = driver.find_elements(By.CSS_SELECTOR, "img[src*='pin-verde.png']")
            amarelos = driver.find_elements(By.CSS_SELECTOR, "img[src*='pin-amarelo.png']")
            
            qtd_ocupados = len(vermelhos)
            qtd_livres = len(verdes)
            total = qtd_ocupados + qtd_livres + len(amarelos)
        except Exception as e:
            print(f"⚠️ Erro ao ler mapa (talvez o site não carregou): {e}")
            qtd_ocupados = 0
            qtd_livres = 0
            total = 0
        
        mensagem = (
            f"*🚗 Status da Frota - {time.strftime('%H:%M')}*\n"
            f"🟢 *Livres:* {qtd_livres}\n"
            f"🔴 *Em Corrida:* {qtd_ocupados}\n"
            f"⚠️ *Offline:* {len(amarelos)}\n"
            f"📊 *Total:* {total}"
        )
        print(f"CAPTURA: Livres {qtd_livres} | Ocupados {qtd_ocupados}")

        # --- PASSO 2: FOCAR NA ABA DO WHATSAPP (ABA 1) ---
        driver.switch_to.window(driver.window_handles[1])
        print("💬 Mudando para WhatsApp (Aba 2)...")
        
        wait = WebDriverWait(driver, 60)
        
        # Acha o grupo (Lembre-se da dica de FIXAR a conversa no topo!)
        xpath_grupo = f"//span[@title='{NOME_GRUPO_WHATSAPP}']"
        try:
            grupo = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_grupo)))
            grupo.click()
        except:
            print(f"❌ Não achei o grupo na lista visível.")
            return

        # Acha o campo
        xpath_campo = '//footer//div[@contenteditable="true"]'
        campo = wait.until(EC.presence_of_element_located((By.XPATH, xpath_campo)))
        campo.click()
        time.sleep(0.5)
        
        # Cola e envia
        pyperclip.copy(mensagem)
        campo.send_keys(Keys.CONTROL, 'v')
        time.sleep(2) 
        
        # Tenta clicar no botão enviar
        try:
            btn = driver.find_element(By.XPATH, "//span[@data-icon='send']")
            driver.execute_script("arguments[0].click();", btn)
            print("✅ Enviado!")
        except:
            campo.send_keys(Keys.ENTER)
            print("✅ Enviado (via Enter)!")

    except Exception as e:
        print(f"❌ Erro no ciclo: {e}")

if __name__ == "__main__":
    if not os.path.exists(CAMINHO_PERFIL):
        os.makedirs(CAMINHO_PERFIL)
    
    # Mata processos antigos do Chrome se houver (Opcional, mas ajuda a evitar crashes)
    os.system("taskkill /F /IM chrome.exe /T >nul 2>&1")
    os.system("taskkill /F /IM chromedriver.exe /T >nul 2>&1")

    driver = iniciar_driver()
    
    print("🛠️  CONFIGURANDO AS DUAS ABAS...")
    
    # 1. Abre o Mapa na primeira aba
    driver.get(URL_MAPA)
    
    # 2. Abre uma NOVA aba e vai para o WhatsApp
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get("https://web.whatsapp.com")
    
    print("\n" + "="*50)
    print("⏳ PAUSA DE 60 SEGUNDOS PARA LOGIN!")
    print("👉 Não feche nenhuma aba!")
    print("="*50 + "\n")
    
    time.sleep(60) 
    
    print("🤖 INICIANDO MONITORAMENTO AUTOMÁTICO...")
    
    while True:
        job(driver)
        print(f"💤 Aguardando {INTERVALO_MINUTOS} minutos...")
        time.sleep(INTERVALO_MINUTOS * 60)