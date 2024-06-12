from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import requests, imghdr, csv, json, time, os, uuid

pages, pagesID = [
  "https://oglobo.globo.com/fotogalerias/noticia/2023/10/09/guerra-entre-hamas-e-israel-veja-fotos-do-conflito.ghtml",
  "https://www.terra.com.br/noticias/mundo/guerra-israel-x-hamas-veja-os-principais-acontecimentos-dos-ultimos-dias,b0a05859054b298f111e6d65a37d9b195byqn5pf.html",
  "https://noticias.uol.com.br/internacional/ultimas-noticias/2023/11/01/guerra-em-israel-hoje-111-veja-novas-noticias-e-videos.htm",
  "https://agenciabrasil.ebc.com.br/internacional/noticia/2023-10/mais-de-6-mil-pessoas-morreram-na-guerra-entre-israel-e-hamas",
  "https://agenciabrasil.ebc.com.br/internacional/noticia/2023-10/israel-bombardeia-gaza-e-numero-de-mortos-em-nova-guerra-passa-de-900#",
  "https://g1.globo.com/jornal-nacional/noticia/2024/05/31/onda-de-calor-extremo-provoca-ao-menos-50-mortes-na-india.ghtml",
  "https://www.cnnbrasil.com.br/internacional/onda-de-calor-na-india-mata-pelo-menos-33-pessoas/",
  "https://noticias.uol.com.br/ultimas-noticias/ansa/2024/06/01/calor-extremo-na-india-mata-85-em-24-horas.htm",
  "https://www.bbc.com/portuguese/articles/cp05gz25r9po",
  "https://www.uol.com.br/ecoa/noticias/rfi/2024/05/29/calor-extremo-india-registra-recorde-de-523c-e-governo-raciona-agua.htm",
  "https://sbtnews.sbt.com.br/noticia/brasil/rio-grande-do-sul-chega-a-15-mortes-por-leptospirose-apos-enchentes",
  "https://veja.abril.com.br/brasil/enchentes-castigam-populacao-no-sul-do-pais-neste-final-de-semana",
  "https://g1.globo.com/sp/vale-do-paraiba-regiao/noticia/2024/06/05/sao-luiz-do-paraitinga-sera-a-primeira-cidade-de-sp-a-receber-novo-sistema-de-alerta-de-enchentes.ghtml",
  "https://g1.globo.com/rs/rio-grande-do-sul/noticia/2024/06/08/entenda-como-funcionarao-cidades-provisorias-no-rs-apos-enchentes-especialistas-criticam-proposta-por-falta-de-dialogo.ghtml",
  "https://www.cnnbrasil.com.br/nacional/enchentes-no-rs-compare-imagens-do-google-maps-de-antes-e-depois-das-chuvas/",
  "https://www.correiobraziliense.com.br/euestudante/educacao-basica/2024/05/6864043-a-gente-vai-radicalizar-diz-sindicatos-sobre-ultimato-do-governo.html",
  "https://gcmais.com.br/noticias/2024/05/17/professores-das-universidades-federais-do-ce-rejeitam-nova-proposta-do-governo-e-seguem-em-greve/",
  "https://www.correiobraziliense.com.br/euestudante/ensino-superior/2024/06/6872565-professores-se-organizam-apos-reabertura-das-negociacoes-com-o-governo.html",
  "https://oglobo.globo.com/opiniao/editorial/coluna/2024/06/greve-nas-federais-passou-do-limite.ghtml",
  "https://iclnoticias.com.br/governo-greve-da-educacao-federal/"
], []


for page in pages:
  try:
    url = page
    pageID = uuid.uuid4().hex
    pagesID.append(pageID)

    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)

    # Opens webpage
    driver.get(url)
    #time.sleep(10)

    data = []

    def savePageHTML(url, pageID):
      print('SAVING THE HTML')
      
      print(url)
      print(url[:30])
      
      #Salve page HTML
      input_data = driver.page_source

      #Check and create data folder
      if not os.path.exists(f'data'):
        os.makedirs(f'data')

      if not os.path.exists(f'data/{pageID}'):
        os.makedirs(f'data/{pageID}')

      #Save HTML @ html folder using pageID as a file name
      fileToWrite = open(f"data/{pageID}/{pageID}.html", "w", encoding='utf-8')
      fileToWrite.write(input_data)
      fileToWrite.close()
      
    def getImages(pageID, pageURL):  
      print('SEARCHING FOR IMG TAG')

      # Finds all <img> elements
      images = driver.find_elements(By.TAG_NAME, 'img')

      # Processar os elementos <img>
      for index, img in enumerate(images):
    
        print(index + 1)
        # finds alt and aria-label attributes
        alt = img.get_dom_attribute("alt")
        aria = img.get_dom_attribute("aria-label")  

        #If image alt is empty, the image is not going to be saved bc author doesnt want it to be read
        if (alt == ''):
          print ('Empty Alt')
          continue
        
        if (alt == None):
          print ('O autor não fornceu texto alternativo para a tag alt')

        if (aria == ''):
          print ('O aria-label está vazio')
        
        if (aria == None):
          print ('O autor não forneceu um texto para o aria-label n')

        print(f'ALT: {alt}')

        #gets the src attribute of the <img> tag
        src = img.get_attribute('src')
        print(src)
        
        #IF scr link exists:
        if src != None:

          #If scr link is not on base64:
          if (src[:4] != "data" ):

            # download the image 
            try:      
              image_data = requests.get(src)

              # get image extension and save the image using pageID as a file name
              extension = imghdr.what(file=None, h=image_data.content)

              if extension == None:
                extension = 'svg'

              if extension == 'svg':
                print(".svg not supported - image will not be downloaded")
                continue

              if extension == 'gif':
                print(".gif not supported - image will not be downloaded")
                continue

              print('SAVING IMAGE')

              if not os.path.exists(f'data/{pageID}/images/'):
                os.makedirs(f'data/{pageID}/images/')

              with open(f'data/{pageID}/images/{index + 1}.{extension}', 'wb') as handler:
                handler.write(image_data.content)

              # add to data list
              print('ADDING DATA TO LIST')

              imageData = {
                'pageID': pageID,
                'imageID': f"{index + 1}",
                'alt': alt,
                'aria-label': aria,
                'pageURL': pageURL,
                'imageURL': src,
                'imagePath': f"data/{pageID}/images/{index + 1}.{extension}",
              }

              print(imageData)
          
              # Escreve os dados
              with open(f'data/{pageID}/{pageID}.csv', mode='a', newline='', encoding='utf-8') as arquivo_csv:
                campos = ['pageID', 'imageID', 'alt', 'aria-label','pageURL', 'imageURL', 'imagePath']
                escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
                escritor_csv.writerow(imageData)
            except:
              print('Error')

          else:
            print('URL not accessible')   
        else:
          print('Image does not have an url')

    def getInfo(pageID):
      try:
        main_element = driver.find_element(By.TAG_NAME, 'main')

        # Recupera todos os elementos dentro da tag <main>
        all_elements_in_main = main_element.find_elements(By.XPATH, './/*')

        pageData = []

        # Exibe informações sobre os elementos encontrados
        for element in all_elements_in_main:
          
          if element.tag_name == 'h1' or element.tag_name == 'h2' or element.tag_name == 'p':
            if element.text != "":
              pageData.append({element.tag_name : element.text})
              print(f'Tag: {element.tag_name}, Text: {element.text}')

              #Check and create vision folder
              if not os.path.exists(f'data/{pageID}'):
                os.makedirs(f'data/{pageID}')

              #Saves vision data as ImageID.PageID.json inside vision folder
              with open(f'data/{pageID}/{pageID}.CONTENT.json', 'w') as f:
                json.dump(pageData, f)

      except:
        main_element = driver.find_element(By.TAG_NAME, 'article')

        # Recupera todos os elementos dentro da tag <main>
        all_elements_in_main = main_element.find_elements(By.XPATH, './/*')

        pageData = []

        # Exibe informações sobre os elementos encontrados
        for element in all_elements_in_main:
          
          if element.tag_name == 'h1' or element.tag_name == 'h2' or element.tag_name == 'p':
            if element.text != "":
              pageData.append({element.tag_name : element.text})
              print(f'Tag: {element.tag_name}, Text: {element.text}')

              #Check and create vision folder
              if not os.path.exists(f'data/{pageID}'):
                os.makedirs(f'data/{pageID}')

              #Saves vision data as ImageID.PageID.json inside vision folder
              with open(f'data/{pageID}/{pageID}.CONTENT.json', 'w') as f:
                json.dump(pageData, f)
    
    savePageHTML(url, pageID)

    with open(f'data/{pageID}/{pageID}.csv', mode='w', newline='', encoding='utf-8') as arquivo_csv:
      campos = ['pageID', 'imageID', 'alt', 'aria-label', 'pageURL', 'imageURL', 'imagePath']
      escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
      # Escreve os cabeçalhos (nomes dos campos)
      escritor_csv.writeheader()

    getInfo(pageID)
    getImages(pageID, url)

    driver.quit()
  except:
    print("Não foi possivel completar a tarefa")

with open(f'data/pagesID.json', 'w') as f:
  json.dump(pagesID, f)