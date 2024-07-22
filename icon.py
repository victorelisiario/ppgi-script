from dotenv import dotenv_values
import google.generativeai as genai 

from PIL import Image

import json, os, csv

# Obtém a chave de API da variável de ambiente
GOOGLE_API_KEY=dotenv_values(".env").get("GEMINI_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

for m in  genai.list_models():
  print(m.name)

pages = [
          ["https://www.netshoes.com.br/p/bicicleta-aro-29-gti-aluminio-21-velocidades-freio-a-disco-original-mtb-kw-suspensao-com-garantia-verde+agua-AEE-0252-218", 24], 
          ["https://www.instagram.com/instagram/", 17], 
          ["https://www.instagram.com/p/C9nDNQUJm-K/", 9],
          ["https://www.nytimes.com/games/wordle/index.html", 5]
        ]

descriptions = []

pageID = 0

for page in pages:
  pageID = pageID + 1

  index = 0

  for image in range(page[1]):

    index = index + 1

    sample_file = genai.upload_file(path=f"data/images/{pageID}/png/{pageID}.{index}.png", display_name="Sample image")
    file = genai.get_file(name=sample_file.name)

    print(f'data/images/{pageID}/png/{pageID}.{image + 1}.png')
    print(sample_file)

    model = genai.GenerativeModel('gemini-1.5-pro')

    prompt = f'''
      Você é um assistente eficiente que descreve icones para pessoas com deficiência visual.   

      O icone foi retirado da página {page[0]}

      Analise a imagem anexada e fornceça uma possivel funcionalidade do icone para ser inserido dentro de um aria-label. 
      Não faça nenhuma referencia aos dados fornecidos.
      Retorne apenas o conteúdo do aria-label. Seja direto e claro. Limite sua resposta a 10 palavras.
    '''

    response = model.generate_content([sample_file, prompt])
    
    try:
      print(response.text)

      description = {
        "imagem": f'{pageID}.{image + 1}',
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
        "imagem": f'{pageID}.{image + 1}',
        "descricao": "Description generation ERROR"
      }

      descriptions.append(description)

      with open(f'data/descriptions.csv', mode='a', newline='', encoding='utf-8') as arquivo_csv:
        campos = ['imagem', 'descricao']
        escritor_csv = csv.DictWriter(arquivo_csv, fieldnames=campos)
        escritor_csv.writerow(description)



#Saves Description @ description folder

