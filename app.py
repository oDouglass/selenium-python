from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter


def coletar_resultados(driver):
    """
    Função para coletar dados de exatamente 3 páginas de resultados.
    (página atual + 2 próximas)
    """
    resultados_coleta = []

    for pagina in range(3):  # Página 1 + 2 próximas
        print(f"Coletando dados da página {pagina + 1}...")
        sleep(3)

        produtos = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="product-card"]')
        if not produtos:
            print("Nenhum produto encontrado nesta página.")
            break

        for produto in produtos:
            try:
                descricao = produto.find_element(By.CSS_SELECTOR, 'h2[data-testid="product-card::name"]').text
            except:
                descricao = "Descrição não encontrada"
            try:
                valor = produto.find_element(By.CSS_SELECTOR, 'p[data-testid="product-card::price"]').text
            except:
                valor = "Valor não encontrado"

            resultados_coleta.append({"descricao": descricao, "valor": valor})

        # Só tenta ir para a próxima se ainda não tiver coletado 3 páginas
        if pagina < 2:
            try:
                botao_proximo = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'li[data-testid="page-next"] a'))
                )
                driver.execute_script("arguments[0].scrollIntoView(true);", botao_proximo)
                sleep(1)
                driver.execute_script("arguments[0].click();", botao_proximo)
                sleep(3)
            except NoSuchElementException:
                print("Não há mais páginas para coletar.")
                break
            except Exception as e:
                print(f"Erro ao tentar mudar de página: {e}")
                break

    return resultados_coleta


def coletar_com_filtro(driver, valor_filtro, nome_filtro="Filtro"):
    """
    Função genérica para aplicar um filtro de ordenação, voltar para a página 1,
    e coletar resultados das 3 primeiras páginas.
    """
    resultados = []

    try:
        # Aplica o filtro
        seletor = Select(WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "orderBy"))
        ))
        seletor.select_by_value(valor_filtro)
        print(f"{nome_filtro} aplicado com sucesso!")
        sleep(3)  # espera a página recarregar parcialmente

        # Volta para a página 1
        try:
            botao_pagina1 = driver.find_element(By.CSS_SELECTOR, 'li[data-testid="page-1"] a')
            driver.execute_script("arguments[0].scrollIntoView(true);", botao_pagina1)
            driver.execute_script("arguments[0].click();", botao_pagina1)
            print("Retornou para a página 1 do filtro.")
            sleep(3)
        except NoSuchElementException:
            pass  # Se já estiver na página 1, ignora

        # Coleta os resultados das 3 primeiras páginas
        print(f"\n--- Iniciando coleta com o filtro '{nome_filtro}' ---")
        resultados = coletar_resultados(driver)

    except NoSuchElementException:
        print(f"Não foi possível aplicar o filtro '{nome_filtro}'.")

    return resultados


# --- Início do Script Principal ---

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

# Configurações e inicialização do Chrome
chrome_options = Options()
chrome_options.add_argument("--disable-notifications")
driver = webdriver.Chrome(options=chrome_options)
driver.get("https://www.zoom.com.br/")
sleep(3)

# Realiza a pesquisa inicial
driver.find_element(By.ID, "searchInput").send_keys(termo_pesquisa)
driver.find_element(By.ID, "searchInput").send_keys(Keys.ENTER)
sleep(5)

# --- 1. PRIMEIRA COLETA (ORDEM PADRÃO) ---
print("\n--- Iniciando coleta com a ordenação PADRÃO ('Mais relevantes') ---")
resultados_padrao = coletar_resultados(driver)

# --- 2. FILTRO MELHOR AVALIADO ---
print("\n--- Alterando o filtro para 'MELHOR AVALIADO' ---")
resultados_avaliados = coletar_com_filtro(driver, "rating_desc", "Melhor avaliado")

# --- 3. FILTRO MENOR PREÇO ---
print("\n--- Alterando o filtro para 'MENOR PREÇO' ---")
resultados_menor_preco = coletar_com_filtro(driver, "price_asc", "Menor preço")

# --- 4. FINALIZAÇÃO ---
driver.quit()

# --- Exibição de resultados individuais ---

print("\n\n" + "=" * 50)
print("--- RESULTADOS COM ORDENAÇÃO PADRÃO ('Mais relevantes') ---")
print("=" * 50)
if resultados_padrao:
    for item in resultados_padrao:
        print(item)
else:
    print("Nenhum resultado encontrado.")

print("\n\n" + "=" * 50)
print("--- RESULTADOS COM ORDENAÇÃO 'MELHOR AVALIADO' ---")
print("=" * 50)
if resultados_avaliados:
    for item in resultados_avaliados:
        print(item)
else:
    print("Nenhum resultado encontrado.")

print("\n\n" + "=" * 50)
print("--- RESULTADOS COM FILTRO 'MENOR PREÇO' ---")
print("=" * 50)
if resultados_menor_preco:
    for item in resultados_menor_preco:
        print(item)
else:
    print("Nenhum resultado encontrado.")

# --- 5. ANÁLISE DE FREQUÊNCIA E RANKING ---

# Junta todos os produtos (apenas descrições)
todos_produtos = []
for resultado in [resultados_padrao, resultados_avaliados, resultados_menor_preco]:
    todos_produtos.extend([item["descricao"] for item in resultado])

# Conta a frequência de cada produto
contador = Counter(todos_produtos)
ranking_produtos = contador.most_common()

# Exibe ranking
print("\n\n" + "="*50)
print("--- RANKING DE PRODUTOS MAIS FREQUENTES ---")
print("="*50)
for i, (produto, freq) in enumerate(ranking_produtos, start=1):
    print(f"{i}. {produto} - Aparece {freq} vezes")
