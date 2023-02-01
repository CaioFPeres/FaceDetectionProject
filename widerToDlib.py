# this script converts wider annotations to DLIB annotations, as per dlib's annotation example
from xml.dom import minidom
import sys
import os




# This converts wider voc annotations to dlib voc annotations (not used in celebA dataset)



if(len(sys.argv) < 3):
    print("Provide args:program.py maxImages fromFolder Tofilename(without extension)")
    exit()

def createDoc():
    newDocRoot = minidom.Document()

    root = newDocRoot.createElement("dataset")
    newDocRoot.appendChild(root)

    name = newDocRoot.createElement('name')
    newDocRoot.firstChild.appendChild(name)
    nameInnerText = newDocRoot.createTextNode("Training faces")
    name.appendChild(nameInnerText)

    comment = newDocRoot.createElement('comment')
    newDocRoot.firstChild.appendChild(comment)
    commentInnerText = newDocRoot.createTextNode("Annotated faces from WIDER dataset")
    comment.appendChild(commentInnerText)

    images = newDocRoot.createElement('images')
    newDocRoot.firstChild.appendChild(images)
    
    return newDocRoot, images

newDocRoot, images = createDoc()

count = 0

for file in os.listdir("./" + sys.argv[2]):
    DOMTree = minidom.parse("./" + sys.argv[2] + "/" + file)
    collection = DOMTree.documentElement
    path = collection.getElementsByTagName("path")[0].childNodes[0].data
    
    imageWidth = int(collection.getElementsByTagName("size")[0].childNodes[0].childNodes[0].data)
    imageHeight = int(collection.getElementsByTagName("size")[0].childNodes[1].childNodes[0].data)
    
    image = newDocRoot.createElement('image')
    images.appendChild(image)
    image.setAttribute('file', path)
    image.setAttribute('width', str(imageWidth))
    image.setAttribute('height', str(imageHeight))
    
    
    for objects in range(len(collection.getElementsByTagName("object"))):
        xmin = int(collection.getElementsByTagName("object")[objects].childNodes[4].childNodes[0].childNodes[0].data)
        ymin = int(collection.getElementsByTagName("object")[objects].childNodes[4].childNodes[1].childNodes[0].data)
        xmax = int(collection.getElementsByTagName("object")[objects].childNodes[4].childNodes[2].childNodes[0].data)
        ymax = int(collection.getElementsByTagName("object")[objects].childNodes[4].childNodes[3].childNodes[0].data)
        w = xmax - xmin
        h = ymax - ymin
        
        box = newDocRoot.createElement('box')
        image.appendChild(box)
        box.setAttribute('top', str(ymin))
        box.setAttribute('left', str(xmin))
        box.setAttribute('width', str(w))
        box.setAttribute('height', str(h))
            
    count += 1
    if(count == int(sys.argv[1])):
        break

training = newDocRoot.toprettyxml()
with open(sys.argv[3] + ".xml", "w") as f:
    f.write(training)