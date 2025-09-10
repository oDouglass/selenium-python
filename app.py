from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter
import requests
from bs4 import BeautifulSoup
import pandas as pd


def coletar_resultados(driver):
    resultados_coleta = []

    for pagina in range(3): 
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

            try:
                link = produto.find_element(By.CSS_SELECTOR, 'a[data-testid="product-card::card"]').get_attribute("href")
            except:
                link = "Link não encontrado"

            resultados_coleta.append({
                "descricao": descricao,
                "valor": valor,
                "link": link
            })

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
            pass  

        # Coleta os resultados das 3 primeiras páginas
        print(f"\n--- Iniciando coleta com o filtro '{nome_filtro}' ---")
        resultados = coletar_resultados(driver)

    except NoSuchElementException:
        print(f"Não foi possível aplicar o filtro '{nome_filtro}'.")

    return resultados


def coletar_detalhes(link):
    detalhes = {}
    try:
        resp = requests.get(link, timeout=10)
        sp = BeautifulSoup(resp.content, "html.parser")
        bloco = sp.find("div", class_="DetailsSection_ContentWrapper__LBFf5")

        if bloco:
            atributos = bloco.find_all("div", class_="DetailsContent_AttributeBlock__lGim_")
            for attr in atributos:
                titulo = attr.find("h3")
                if titulo:
                    titulo = titulo.get_text(strip=True)
                else:
                    continue

                tabela = attr.find_all("tr")
                for linha in tabela:
                    chave = linha.find("th").get_text(strip=True)
                    valor = linha.find("td").get_text(" ", strip=True)
                    detalhes[f"{titulo} - {chave}"] = valor
        else:
            detalhes["Erro"] = "Bloco de especificações não encontrado"
    except Exception as e:
        detalhes["Erro"] = str(e)
    return detalhes

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

print("\n--- Iniciando coleta com a ordenação PADRÃO ('Mais relevantes') ---")
resultados_padrao = coletar_resultados(driver)

print("\n--- Alterando o filtro para 'MELHOR AVALIADO' ---")
resultados_avaliados = coletar_com_filtro(driver, "rating_desc", "Melhor avaliado")

print("\n--- Alterando o filtro para 'MENOR PREÇO' ---")
resultados_menor_preco = coletar_com_filtro(driver, "price_asc", "Menor preço")

driver.quit()

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

todos_produtos = []
for resultado in [resultados_padrao, resultados_avaliados, resultados_menor_preco]:
    todos_produtos.extend(resultado)

contador = Counter([item["descricao"] for item in todos_produtos])
ranking_produtos = contador.most_common()

mapa_links = {}
for item in todos_produtos:
    if item["descricao"] not in mapa_links:
        mapa_links[item["descricao"]] = item["link"]

print("\n\n" + "="*50)
print("--- RANKING DE TODOS OS PRODUTOS MAIS FREQUENTES ---")
print("="*50)
for i, (produto, freq) in enumerate(ranking_produtos, start=1):
    print(f"{i}. {produto} - Aparece {freq} vezes")

print("\n\n" + "="*50)
print("--- TOP 5 PRODUTOS MAIS FREQUENTES (COM LINKS) ---")
print("="*50)
top5 = ranking_produtos[:5]
for i, (produto, freq) in enumerate(top5, start=1):
    link = mapa_links.get(produto, "Link não encontrado")
    print(f"{i}. {produto} - Aparece {freq} vezes")
    print(f"   Link: {link}")

print("\n\n" + "="*50)
print("--- DETALHES DOS 5 PRIMEIROS PRODUTOS ---")
print("="*50)
for produto, _ in top5:
    link = mapa_links.get(produto, None)
    if not link or link == "Link não encontrado":
        print(f"\n--- {produto} ---")
        print("Link não disponível para coletar detalhes.")
        continue

    detalhes = coletar_detalhes(link)
    print(f"\n--- {produto} ---")
    for k, v in detalhes.items():
        print(f"{k}: {v}")

with pd.ExcelWriter("resultados_pesquisa.xlsx", engine="openpyxl") as writer:

    # 1. Resultados padrão
    df_padrao = pd.DataFrame(resultados_padrao)
    df_padrao.to_excel(writer, sheet_name="Padrao", index=False)

    # 2. Melhor avaliado
    df_avaliados = pd.DataFrame(resultados_avaliados)
    df_avaliados.to_excel(writer, sheet_name="Melhor Avaliado", index=False)

    # 3. Menor preço
    df_preco = pd.DataFrame(resultados_menor_preco)
    df_preco.to_excel(writer, sheet_name="Menor Preco", index=False)

    # 4. Ranking completo
    df_ranking = pd.DataFrame(ranking_produtos, columns=["Produto", "Frequência"])
    df_ranking.to_excel(writer, sheet_name="Ranking", index=False)

    # 5. Top 5 com links
    top5_data = []
    for i, (produto, freq) in enumerate(top5, start=1):
        link = mapa_links.get(produto, "Link não encontrado")
        top5_data.append({"Posição": i, "Produto": produto, "Frequência": freq, "Link": link})
    df_top5 = pd.DataFrame(top5_data)
    df_top5.to_excel(writer, sheet_name="Top 5", index=False)

    # 6. Detalhes dos 5 primeiros (Formato Dinâmico com todas as informações)
    detalhes_dinamico_data = []
    for produto, _ in top5:
        link = mapa_links.get(produto, None)
        
        # Dicionário base para a linha do produto
        linha_produto = {"Produto": produto}

        if not link or link == "Link não encontrado":
            linha_produto["Status"] = "Link não disponível para coletar detalhes"
        else:
            detalhes = coletar_detalhes(link)
            if "Erro" in detalhes:
                linha_produto["Status"] = f"Erro ao coletar detalhes: {detalhes['Erro']}"
            else:
                linha_produto.update(detalhes)
        
        detalhes_dinamico_data.append(linha_produto)

    df_detalhes_dinamico = pd.DataFrame(detalhes_dinamico_data)
    
    if 'Produto' in df_detalhes_dinamico.columns:
        cols = df_detalhes_dinamico.columns.tolist()
        cols.insert(0, cols.pop(cols.index('Produto')))
        df_detalhes_dinamico = df_detalhes_dinamico.reindex(columns=cols)

    df_detalhes_dinamico.to_excel(writer, sheet_name="Detalhes Top 5", index=False)


print("Arquivo 'resultados_pesquisa.xlsx' salvo com sucesso!")

