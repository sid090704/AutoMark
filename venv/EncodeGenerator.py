import cv2
import face_recognition
import pickle
import os

# importing student images:
folderPath= 'Images'
pathList = os.listdir(folderPath)
imgList= []
studentRoll=[]
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    studentRoll.append(os.path.splitext(path)[0]) #removes .png from image name
#print(studentRoll) : ['170', '175']



def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodes = face_recognition.face_encodings(img)
        if encodes:
            encodeList.append(encodes[0])
        else:
            print("Warning: No face detected in one of the images.")
    return encodeList

print("encoding started...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithId= [encodeListKnown,studentRoll]
print("encoding complete.")

with open("EncodeFile.p",'wb') as file:
    pickle.dump(encodeListKnownWithId,file)
