from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import time
import requests
import re

import csv

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Opens webpage
url = "https://globo.com"
driver.get(url)
time.sleep(10)

data = []

def savePageHTML(pageID):
  print('SAVING THE HTML')
  
  
  #Salve page HTML
  input_data = driver.page_source

  #Save HTML @ html folder using pageID as a file name
  fileToWrite = open(f"html/{pageID}.html", "w", encoding='utf-8')
  fileToWrite.write(input_data)
  fileToWrite.close()
  

def getImages(pageID, pageURL):
  print('SEARCHING FOR IMG TAG')
  #finds and <img> tag

  # Recuperar todos os elementos <img>
  images = driver.find_elements(By.TAG_NAME, 'img')

  # Processar os elementos <img>
  for index, img in enumerate(images):
 
    print(index + 1)
    # finds alt and aria-label attributes
    print('LOOKING FOR IMG ALT AND ARIA-LABEL')
    alt = img.get_attribute('alt')
    aria = img.get_attribute('aria-label')
    
    #
    print(f"ALT: {alt}")
    print(f"ARIA: {aria}")

    #gets the src attribute of the <img> tag
    src = img.get_attribute('src')
    
    if src != None:
      if src[:4] == 'http':
        # download the image
        print('GETTING IMAGE URL')
        print(src)
        image_data = requests.get(src).content

        # get image extension and save the image using pageID as a file name

        print('GETTING URL EXTENSION')
        padrao = re.compile(r'(\.jpg|\.jpeg|\.svg|\.gif|\.png|\.psd|\.raw|\.tiff|\.bmp|\.pdf|\.webp)')
        resultado = padrao.search(src)
        extensao = resultado.group() if resultado else '.png'


        print('SAVING IMAGE')
        with open(f'images/{pageID}.{index + 1}{extensao}', 'wb') as handler:
          handler.write(image_data)

        # add to data list
        print('ADDING TO DATA LIST')

        imageData = {
          'pageID': pageID,
          'pageURL': pageURL,
          'imageID': f"{pageID}.{index + 1}",
          'imageURL': src,
          'alt': alt,
          'aria-label': aria,
        }

        data.append(imageData)
        
      else:
        print('Image does not have an url')
    else: 
      print('No image found')

def createCSV(data):
  # Lista das chaves do dicionário (campos)
  campos = data[0].keys()

  # Escrevendo os dados no arquivo CSV
  with open('dados.csv', mode='w', newline='', encoding='utf-8') as arquivo_csv:
      campos = ['pageID', 'pageURL', 'imageID', 'imageURL', 'alt', 'aria-label']
      escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
      
      # Escreve os cabeçalhos (nomes dos campos)
      escritor_csv.writeheader()
      
      # Escreve os dados
      for linha in data:
          escritor_csv.writerow(linha)

print("Arquivo CSV criado com sucesso!")


savePageHTML(1)
getImages(1, url)
createCSV(data)


'''
{[ 
  ['site', 'siteID', 'ID', 'URL', 'ALT', 'ARIAL_LABEL', 'descrição'],
  ['google.com', '1', '1.1' 'https://google.com/image.png', 'Google', 'Google', 'Logo do Google' ]
  
]}
'''

driver.quit()