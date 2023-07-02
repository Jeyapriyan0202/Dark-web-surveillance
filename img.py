import os
import cv2
import pandas as pd
import pytesseract
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
sw = stopwords.words('english')
stemmer = PorterStemmer()
"""
page segmentation modes:
0   Orientation and script detection (osd) only .
1   automatic page segmentation with osd.
2  automatic page segmentation , but no osd, or ocr.
3   fully automatic page segmentation, but no osd. default
4   assume a single column of text of vertically aligned text. 
5  assume a single uniform block of vertically aligned text
6   assume a single uniform block of text.
7   treat the image as a single text line.
8  treat the image as a single word.
9   treat thee image as a single word in a circle.
10  treat the image as a single character.
11  sparse text. Find as much text as possible in no particular order. 
12  sparse text with osd.
13  raw line. Treat the image as a single text lene,
                    bypassing hacks that are tesseract-specific."""

"""
OCR engine mode 
0  legacy engine only.
1 Neural nets LSTM engines.
2 Legacy +LSTR engines.
3 Default, based on what is available.
"""

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def grayscale(img):
  img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  return img
def blur(img, param):
  img = cv2.medianBlur(img, param)
  return img
def threshold (img):
  img = cv2.threshold(img, 0, 255,cv2.THRESH_BINARY +cv2.THRESH_OTSU)[1]
  return img


myconfig = r' --psm 12-- oem 3'
def image(img):
    img = cv2.imread(img)
    try:
        img = grayscale(img)
    except:
        pass
    try:
        img = blur(img, 1)
    except:
        pass
    try:
        img = threshold(img)
    except:
        pass

    #cv2.imshow('img', img)
    #cv2.waitKey(0)
    # now feeding image to tesseract

    details = pytesseract.image_to_data(img, config = myconfig,output_type="data.frame", lang = 'eng')
    return details

all_data = []

pathtofolder = ".\images"
for img in os.listdir(pathtofolder):
    url =  f"{pathtofolder}\{img}"
    try:
        datas = image(url)
    except:
        continue
    text = pd.DataFrame.dropna(datas)
    raw_data = text['text']
    print(raw_data)
    texts = []
    for data in raw_data:
        try:
            data = data.lower()
            data = stemmer.stem(data)
        except:
            pass
        if data not in sw:
            texts.append(data)
        else:
            continue
    print(texts)
    img_index = img.removesuffix(".jpg")
    data_dict = {"img_index": img_index,
                 "text_data": texts}
    all_data.append(data_dict)
file = pd.read_csv("data.csv")
indexesofimg = file['image_index']
img_text = []
for indexs in indexesofimg:
    text_data = []
    for index in indexs:
        for data in all_data:
            if index == data['img_index']:
                texts = data['text_data']
                for words in texts:
                    text_data.append(words)
    img_text.append(text_data)


print(img_text)
print(len(img_text))
print(file)
file ['img_text'] = img_text
print(file)
df = pd.DataFrame(file)
df.to_csv('data.csv', index=True, header=True, mode='w' )
