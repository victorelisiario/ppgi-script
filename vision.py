import os
import json

from google.cloud import vision

#ENVIRONMENT KEY
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vison-key.json'

# Instantiates a client
client = vision.ImageAnnotatorClient()


file_uri = 'https://f.i.uol.com.br/fotografia/2024/05/30/17170776426658868ab2031_1717077642_3x2_lg.jpg'

image = vision.Image()
image.source.image_uri = file_uri


#### LABEL DETECTION ######
def labelDetection():
  response = client.label_detection(image=image)

  labels = []

  for label in response.label_annotations:
    print({'label': label.description, 'score': label.score})
    labels.append({'label': label.description, 'score': label.score})

  with open('vision-data/labels.json', 'w') as f:
    json.dump(labels, f)
  

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
  
  with open('vision-data/faces.json', 'w') as f:
    json.dump(faces, f)
   

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
  
  with open('vision-data/texts.json', 'w') as f:
    json.dump(texts, f)


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
  
  with open('vision-data/objects.json', 'w') as f:
    json.dump(objects, f)


labelDetection()