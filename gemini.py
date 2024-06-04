from dotenv import dotenv_values
import json

import google.generativeai as genai 

# Obtém a chave de API da variável de ambiente
GOOGLE_API_KEY=dotenv_values(".env").get("GEMINI_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)

'''
for m in  genai.list_models():
  print(m.name)
'''

sample_file = genai.upload_file(path="images/1.9.jpg", display_name="Sample image")
file = genai.get_file(name=sample_file.name)

model = genai.GenerativeModel('gemini-1.5-flash-latest')

with open('vision-data/labels.json', 'r') as arquivo:
  labels = json.load(arquivo)

with open('vision-data/objects.json', 'r') as arquivo:
  objects = json.load(arquivo)

with open('vision-data/texts.json', 'r') as arquivo:
  texts = json.load(arquivo)

with open('vision-data/faces.json', 'r') as arquivo:
  faces = json.load(arquivo)

prompt = f'''
  Você é um assistente eficiente que descreve imagens para pessoas com deficiência visual, para que elas consigam saber o que existe nas imagens.
  Não especule e nem imagine nada que não esteja na imagem.
  
  O alt da imagem possui o texto "{'Taxistas que atuam no Aeroporto Afonso Pena, em São José dos Pinhais, fazem greve'}"

  Analise os dados em json a seguir para formular sua resposta

  {faces}

  {labels}

  {objects}

  {texts}

  Faça uma breve descrição da image, baseando-se na image e nas informações acima. Não faça nenhuma referencia aos dados forncidos, apenas descreva a imagem

'''

response = model.generate_content([sample_file, prompt])

print(response)
print(response.text)

