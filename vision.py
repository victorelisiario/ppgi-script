import os
import json

from google.cloud import vision

import uuid

#KEY
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vison-key.json'

# Instantiates a client
client = vision.ImageAnnotatorClient()

url = input("Insira o link da imagem: ")
imageID = uuid.uuid4().hex

image = vision.Image()
image.source.image_uri = url

vision_data = []

#### LABEL DETECTION ######
def labelDetection():
  response = client.label_detection(image=image)

  labels = []

  for label in response.label_annotations:
    print({'label': label.description, 'score': label.score})
    labels.append({'label': label.description, 'score': label.score})

  vision_data.append({'labels': labels})
  
#### FACE DETECTION ######
def faceDetection():
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
  
  vision_data.append({'face': face})  

#### TEXT DETECTION ######
def textDetection():
  response = client.text_detection(image=image)

  print("Printing response")
  print(response)
  print("Creating json file")

  texts = []

  for response in response.text_annotations:
      text = {
          'text': response.description
      }

      texts.append(text)
      print(text)
  
  vision_data.append({'texts': texts})

#### OBJECTS DETECTION ######
def objectDetection():
  response = client.object_localization(image=image).localized_object_annotations
  
  print("Printing response")
  print(response)
  print("Creating json file")

  objects = []

  for object_ in response:
    objects.append({'name': object_.name, 'confidence': object_.score})
    print({'name': object_.name, 'confidence': object_.score})
  
  vision_data.append({'objects': objects})


labelDetection()
objectDetection()
textDetection()
faceDetection()


with open(f'vision-data/{imageID}.json', 'w') as f:
  json.dump(vision_data, f)