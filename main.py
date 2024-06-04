from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from dotenv import dotenv_values

from google.cloud import vision
import google.generativeai as genai 


import requests, imghdr, csv, json, time, os, uuid


url = input("Insira o link da página: ")
pageID = uuid.uuid4().hex

#GOOGLE VISION API KEY
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vison-key.json'

#GOOGLE GEMINI KEY
GOOGLE_API_KEY=dotenv_values(".env").get("GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)


# Instantiates a client
client = vision.ImageAnnotatorClient()

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
            'imagePath': f"data/{pageID}/images/{index + 1}.{extension}",
            'imageURL': src,
          }

          print(imageData)

          #Creates vision data for current image
          getVisionData(imageData)

          #Generate description using Gemini
          description = getGeminiDescription(imageData)
          
          #Save image data @ global data variable
          imageData['descricao'] = description

          print(imageData)
      
          # Escreve os dados
          with open(f'data/{pageID}/{pageID}.csv', mode='a', newline='', encoding='utf-8') as arquivo_csv:
            campos = ['pageID', 'imageID', 'alt', 'aria-label', 'descricao','pageURL', 'imageURL', 'imagePath']
            escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
            escritor_csv.writerow(imageData)
        except:
          print('Error')

      else:
        print('URL not accessible')   
    else:
      print('Image does not have an url')

def getVisionData(imageData):
  url = imageData['imageURL']
  print(url)

  image = vision.Image()
  image.source.image_uri = url

  vision_data = []

  #### LABEL DETECTION ######
  response = client.label_detection(image=image)

  labels = []

  for label in response.label_annotations:
    print({'label': label.description, 'score': label.score})
    labels.append({'label': label.description, 'score': label.score})

  vision_data.append({'labels': labels})
    
  #### FACE DETECTION ######
  response = client.face_detection(image=image)

  faces = []

  for face_detection in response.face_annotations:
    face = {
        'confidence': face_detection.detection_confidence,
        'joy': face_detection.joy_likelihood,
        'sorrow': face_detection.sorrow_likelihood,
        'surprise': face_detection.surprise_likelihood,
        'anger': face_detection.anger_likelihood
    }
      
    faces.append(face)
    print(face)
  
  vision_data.append({'face': faces})  

  #### TEXT DETECTION ######
  response = client.text_detection(image=image)
  texts = []

  for response in response.text_annotations:
      text = {
          'text': response.description
      }

      texts.append(text)
      print(text)
  
  vision_data.append({'texts': texts})

  #### OBJECTS DETECTION ######
  response = client.object_localization(image=image).localized_object_annotations
  objects = []

  for object_ in response:
    objects.append({'name': object_.name, 'confidence': object_.score})
    print({'name': object_.name, 'confidence': object_.score})
  
  vision_data.append({'objects': objects})

  #Check and create vision folder
  if not os.path.exists(f'data/{imageData["pageID"]}/vision/'):
    os.makedirs(f'data/{imageData["pageID"]}/vision/')

  #Saves vision data as ImageID.PageID.json inside vision folder
  with open(f'data/{imageData["pageID"]}/vision/{imageData["imageID"]}.json', 'w') as f:
    json.dump(vision_data, f)

def getGeminiDescription(imageData):

  sample_file = genai.upload_file(path=imageData["imagePath"], display_name="Sample image")
  file = genai.get_file(name=sample_file.name)

  safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

  model = genai.GenerativeModel('gemini-1.5-pro',safety_settings=safety_settings)

  with open(f'data/{imageData["pageID"]}/vision/{imageData["imageID"]}.json', 'r') as arquivo:
    vision = json.load(arquivo)


  prompt = f'''
    Você é um assistente eficiente que descreve imagens para pessoas com deficiência visual, para que elas consigam saber o que existe nas imagens.
    Não especule e nem imagine nada que não esteja na imagem.
    
    Analise os dados a seguir formular sua resposta:

    O alt da imagem possui o texto: {imageData["alt"]}"
    O aria-label da imagem possui o texto: {imageData["aria-label"]}"
    A imagem foi tirada da página: {imageData["pageURL"]}
    A seguinte arquivo json foi retornado de uma API de Visão computacional:
    {vision}

    Faça uma breve descrição da imagem, baseando-se na imagem e nas informações acima. Não faça nenhuma referencia aos dados fornecidos, apenas descreva a imagem.
    Não descreva logotipos ou icones. Informe quais são, apenas.
  '''

  response = model.generate_content([sample_file, prompt])
  
  try:
    print(response.text)

    description = {
      imageData["imageID"]: response.text
    }

    #Saves Description @ description folder
    if not os.path.exists(f'data/{pageID}/descriptions/'):
        os.makedirs(f'data/{pageID}/descriptions/')

    with open(f'data/{imageData["pageID"]}/descriptions/{imageData["imageID"]}.json', 'w') as f:
      json.dump(description, f)

    return response.text
  
  except:
    print("Description generation ERROR") 

    description = {
      imageData["imageID"]: 'Description generation ERROR'
    }

    #Saves Description @ description folder
    if not os.path.exists(f'data/{pageID}/descriptions/'):
        os.makedirs(f'data/{pageID}/descriptions/')

    with open(f'data/{imageData["pageID"]}/descriptions/{imageData["imageID"]}.json', 'w') as f:
      json.dump(description, f)

    return 'Description generation ERROR'



def createCSV(data,pageId):
  # Lista das chaves do dicionário (campos)
  campos = data[0].keys()

  # Escrevendo os dados no arquivo CSV
  with open(f'data/{pageId}.{pageId}.csv', mode='w', newline='', encoding='utf-8') as arquivo_csv:
    campos = ['pageID', 'imageID', 'alt', 'aria-label', 'descrição','pageURL', 'imageURL']
    escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
    
    # Escreve os cabeçalhos (nomes dos campos)
    escritor_csv.writeheader()
    
    # Escreve os dados
    for linha in data:
        escritor_csv.writerow(linha)  
  
  print("Arquivo CSV criado com sucesso!")


savePageHTML(url, pageID)

with open(f'data/{pageID}/{pageID}.csv', mode='w', newline='', encoding='utf-8') as arquivo_csv:
  campos = ['pageID', 'imageID', 'alt', 'aria-label', 'descricao','pageURL', 'imageURL', 'imagePath']
  escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
  # Escreve os cabeçalhos (nomes dos campos)
  escritor_csv.writeheader()

getImages(pageID, url)
#createCSV(data, pageID)


driver.quit()