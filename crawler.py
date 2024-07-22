from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import requests, imghdr, csv, json, time, os, uuid

pages, pagesID = [
  "https://www.netshoes.com.br/p/bicicleta-aro-29-gti-aluminio-21-velocidades-freio-a-disco-original-mtb-kw-suspensao-com-garantia-verde+agua-AEE-0252-218",
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