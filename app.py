from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

print("Selecione uma opção de pesquisa:")
print("1. Notebook")
print("2. Smartphone Apple")
print("3. Smartphone Samsung")
opcao = input("Digite o número da opção desejada: ")

if opcao == "1":
    termo_pesquisa = "Notebook"
elif opcao == "2":
    termo_pesquisa = "Smartphone Apple"
elif opcao == "3":
    termo_pesquisa = "Smartphone Samsung"
else:
    print("Opção inválida.")
    exit()

# Adicione estas linhas antes de criar o driver
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")

driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.zoom.com.br/")
sleep(3)
driver.find_element(By.XPATH, '//*[@id="searchInput"]').send_keys(termo_pesquisa)
driver.find_element(By.XPATH, '//*[@id="searchInput"]').send_keys(Keys.ENTER)

def coletar_resultados(driver):
    resultadosGeral = []
    for pagina in range(3):
        sleep(3) 
        produtos = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="product-card"]')
        for produto in produtos:
            try:
                descricao = produto.find_element(By.CSS_SELECTOR, 'h2[data-testid="product-card::name"]').text
            except:
                descricao = "Descrição não encontrada"
            try:
                valor = produto.find_element(By.CSS_SELECTOR, 'p[data-testid="product-card::price"]').text
            except:
                valor = "Valor não encontrado"
            resultadosGeral.append({"descricao": descricao, "valor": valor})
        try:
            #driver.find_element(By.XPATH,'//*[@id="__next"]/main/div[2]/ul/li[9]').click()
            driver.find_element(By.CSS_SELECTOR, 'li[data-testid="page-next"] a').click()
            sleep(3)
        except:
            print("Não foi possível avançar para a próxima página.")
            break
    return resultadosGeral

resultadosGeral = coletar_resultados(driver)
driver.quit()

for item in resultadosGeral:
    print(item)