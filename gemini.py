from dotenv import dotenv_values
import json

import google.generativeai as genai 

# Obtém a chave de API da variável de ambiente
GOOGLE_API_KEY=dotenv_values(".env").get("GEMINI_API_KEY")

genai.configure(api_key=GOOGLE_API_KEY)


for m in  genai.list_models():
  print(m.name)


image = input('Insira nome da imagem: ')
vision_data = input("Insira vision data name: ")

sample_file = genai.upload_file(path=f"images/{image}", display_name="Sample image")
file = genai.get_file(name=sample_file.name)

model = genai.GenerativeModel('gemini-1.5-flash-latest')

with open(f'vision-data/{vision_data}', 'r') as arquivo:
  vision = json.load(arquivo)


prompt = f'''
  Você é um assistente eficiente que descreve imagens para pessoas com deficiência visual, para que elas consigam saber o que existe nas imagens.
  Não especule e nem imagine nada que não esteja na imagem.
  
  O alt da imagem possui o texto "{'Foto: Lionsgate Television / Adoro Cinema'}"

  Analise os dados em json a seguir para formular sua resposta

  {vision}

  Faça uma breve descrição da imagem, baseando-se na imagem e nas informações acima. Não faça nenhuma referencia aos dados fornecidos, apenas descreva a imagem

'''

response = model.generate_content([sample_file, prompt])

print(response)
print(response.text)

