from google.cloud import vision

import os, json

#KEY
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'vison-key.json'

# Instantiates a client
client = vision.ImageAnnotatorClient()

pagesID = ["62b94537dc224a5191294e1f5f279eff",   "f6404f29108e4680a13c84e9530a977d", "5fd0c14972a2459db0c23fb8394eb9a7", "980fbadec6a14323817d4fe1ff0c38c0", "f1e0bc48abd147eba65095a09c57c591", "dd42d48e457d453b81ee778263c64b9e", "dfa4a88fcc654b8cbde894c53e182396", "b7016d74ee264d47a26ece02b23b452e", "68038c682b2740bea225b274d445a02d", "f1be2d3818264412b7e4ef4ab5945140", "efb4b6aa48444dc5a848c8d69dcbf357", "0519733efbad4fdb9e4b4b24055085eb", "4245158c28d5416ca91e008dbae41706", "2e915db3ef1f4adba35c1959c48cbb12", "4b17bae67d484f579dd6adc8d617b620", "bf5dbbcae3e5447fb46485bee9b4ade0", "e01804cc55fa4fa39823511e7896ad05", "9f2c746848fa47e580748e8306ca4f4a", "ecbc8b7f93304a38b4f37e1697e529e2", "96a0d0cd980d49708a0aeb75fea01589"]

for pageID in pagesID:
  mainImage = os.listdir(f"data/{pageID}/images")
  imageID, imageExtension = mainImage[0].split(".") 

  print(imageID,imageExtension)

  with open(f"data/{pageID}/images/{imageID}.{imageExtension}", "rb") as image_file:
    content = image_file.read()
  
  image = vision.Image(content=content)

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
  if not os.path.exists(f'data/{pageID}'):
    os.makedirs(f'data/{pageID}')

  #Saves vision data as ImageID.PageID.json inside vision folder
  with open(f'data/{pageID}/{pageID}.VISION.json', 'w') as f:
    json.dump(vision_data, f)