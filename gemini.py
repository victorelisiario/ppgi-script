from dotenv import dotenv_values
import google.generativeai as genai 

from PIL import Image

import json, os, csv

# Obtém a chave de API da variável de ambiente
GOOGLE_API_KEY=dotenv_values(".env").get("GEMINI_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

for m in  genai.list_models():
  print(m.name)

pagesID = ["62b94537dc224a5191294e1f5f279eff",   "f6404f29108e4680a13c84e9530a977d", "5fd0c14972a2459db0c23fb8394eb9a7", "980fbadec6a14323817d4fe1ff0c38c0", "f1e0bc48abd147eba65095a09c57c591", "dd42d48e457d453b81ee778263c64b9e", "dfa4a88fcc654b8cbde894c53e182396", "b7016d74ee264d47a26ece02b23b452e", "68038c682b2740bea225b274d445a02d", "f1be2d3818264412b7e4ef4ab5945140", "efb4b6aa48444dc5a848c8d69dcbf357", "0519733efbad4fdb9e4b4b24055085eb", "4245158c28d5416ca91e008dbae41706", "2e915db3ef1f4adba35c1959c48cbb12", "4b17bae67d484f579dd6adc8d617b620", "bf5dbbcae3e5447fb46485bee9b4ade0", "e01804cc55fa4fa39823511e7896ad05", "9f2c746848fa47e580748e8306ca4f4a", "ecbc8b7f93304a38b4f37e1697e529e2", "96a0d0cd980d49708a0aeb75fea01589"]

descriptions = []

for pageID in pagesID:
  mainImage = os.listdir(f"data/{pageID}/images")
  imageID, imageExtension = mainImage[0].split(".") 

  if (imageExtension == 'webp'):
    im = Image.open(f"data/{pageID}/images/{imageID}.{imageExtension}").convert("RGB")
    im.save(f"data/{pageID}/images/{imageID}.jpg", "jpeg")
    imageExtension = 'jpg'

  sample_file = genai.upload_file(path=f"data/{pageID}/images/{imageID}.{imageExtension}", display_name="Sample image")
  file = genai.get_file(name=sample_file.name)

  model = genai.GenerativeModel('gemini-1.5-pro')

  with open(f'data/{pageID}/{pageID}.VISION.json', 'r') as arquivo:
    vision = json.load(arquivo)

  with open(f'data/{pageID}/{pageID}.CONTENT.json', 'r') as arquivo:
    content = json.load(arquivo)

  prompt = f'''
    Você é um assistente eficiente que descreve imagens para pessoas com deficiência visual, para que elas consigam saber o que existe nas imagens.
    Não especule e nem imagine nada que não esteja na imagem.
    
    Analise os dados a seguir formular sua resposta:

    A imagem foi adicionada a uma noticia na internet.

    O conteudo da noticia é: "{content}"

    Uma API de visão computacional foi utilizada para identificar labels, rostos, textos e objetos na imagem, o resultado obtido foi: "{vision}"

    Faça uma breve descrição da imagem baseando-se na imagem e nas informações acima. Não faça nenhuma referencia aos dados fornecidos, apenas descreva a imagem.
    Não descreva logotipos ou icones. Informe quais são, apenas.
    Limite sua resposta a 25 palavras.
  '''

  response = model.generate_content([sample_file, prompt])
  
  try:
    print(response.text)

    description = {
      "imagem": pageID,
      "descricao": response.text
    }

    descriptions.append(description)

    with open(f'data/description.csv', mode='a', newline='', encoding='utf-8') as arquivo_csv:
      campos = ['imagem', 'descricao']
      escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
      escritor_csv.writerow(description)
  
  except:
    print("Description generation ERROR") 

    description = {
      "imagem": pageID,
      "descricao": "Description generation ERROR"
    }

    descriptions.append(description)

    with open(f'data/descriptions.csv', mode='a', newline='', encoding='utf-8') as arquivo_csv:
      campos = ['imagem', 'descricao']
      escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
      escritor_csv.writerow(description)



#Saves Description @ description folder

