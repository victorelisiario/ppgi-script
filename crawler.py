from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

import time
import requests, imghdr
import re

import csv
import uuid

url = input("Insira o link da página: ")
pageID = uuid.uuid4().hex

service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Opens webpage
driver.get(url)
time.sleep(10)

data = []

def savePageHTML(url, pageID):
  print('SAVING THE HTML')
  
  print(url)
  print(url[:30])
  
  #Salve page HTML
  input_data = driver.page_source

  #Save HTML @ html folder using pageID as a file name
  fileToWrite = open(f"html/{pageID}.html", "w", encoding='utf-8')
  fileToWrite.write(input_data)
  fileToWrite.close()
  

def getImages(pageID, pageURL):
  print(pageURL)
  print('SEARCHING FOR IMG TAG')
  #finds and <img> tag

  # Recuperar todos os elementos <img>
  images = driver.find_elements(By.TAG_NAME, 'img')

  # Processar os elementos <img>
  for index, img in enumerate(images):
 
    print(index + 1)
    # finds alt and aria-label attributes
    print('LOOKING FOR IMG ALT AND ARIA-LABEL')
    alt = img.get_dom_attribute("alt")
    aria = img.get_dom_attribute("aria-label")  
    #

    #If image alt is empty, the image is not goint to be saved bc author doesnt want it to be read
    if (alt == ''):
      print ('ALT: Vazio')
      alt = 'SCRIPT: Vazio'
      continue
    
    if (alt == None):
      print ('SCRIPT: Não Existe')

    if (aria == ''):
      print ('SCRIPT: Vazio')
    
    if (aria == None):
      print ('SCRIPT: Não Existe')

    print(f'ALT: {alt}')

    #gets the src attribute of the <img> tag
    src = img.get_attribute('src')
    
    if src != None:
      if (src[:4] != "data" ):
        # download the image
        print('GETTING IMAGE URL')
        print(src)

        
        image_data = requests.get(src)
        print(image_data.headers.get("Content-Disposition"))

        # get image extension and save the image using pageID as a file name
        extension = imghdr.what(file=None, h=image_data.content)
        print(extension)

        print('SAVING IMAGE')
        with open(f'images/{pageID}.{index + 1}.{extension}', 'wb') as handler:
          handler.write(image_data.content)

        # add to data list
        print('ADDING TO DATA LIST')

        imageData = {
          'pageID': pageID,
          'imageID': f"{index + 1}",
          'alt': alt,
          'aria-label': aria,
          'pageURL': pageURL,
          'imageURL': src,
        }

        data.append(imageData)  
      else:
        print('coundnt download the image')   
    else:
      print('Image does not have an url')


def createCSV(data,pageId):
  # Lista das chaves do dicionário (campos)
  campos = data[0].keys()

  # Escrevendo os dados no arquivo CSV
  with open(f'data/{pageId}.csv', mode='w', newline='', encoding='utf-8') as arquivo_csv:
      campos = ['pageID', 'imageID', 'alt', 'aria-label','pageURL', 'imageURL']
      escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
      
      # Escreve os cabeçalhos (nomes dos campos)
      escritor_csv.writeheader()
      
      # Escreve os dados
      for linha in data:
          escritor_csv.writerow(linha)

print("Arquivo CSV criado com sucesso!")


savePageHTML(url, pageID)
getImages(pageID, url)
createCSV(data, pageID)


driver.quit()