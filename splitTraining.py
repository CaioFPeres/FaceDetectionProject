from xml.dom import minidom
import sys


# This script will split a xml file containing a huge training into several xml files containing a fixed number of images per training file.
# You can pass the third parameter as being the number of images per training file.
# The last file obviously will contain less files than the number you chose; it will contain the remaining files from the original xml.

if(len(sys.argv) < 3):
    print("Provide args:program.py file.xml numberOfImagesPerTraining")
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
    commentInnerText = newDocRoot.createTextNode("Annotated faces from CelebFaceA dataset")
    comment.appendChild(commentInnerText)

    images = newDocRoot.createElement('images')
    newDocRoot.firstChild.appendChild(images)
    
    return newDocRoot, images


if __name__ == "__main__":

    DOMTree = minidom.parse("./" + sys.argv[1])
    collection = DOMTree.documentElement
    imageElements = collection.getElementsByTagName("images")[0].childNodes

    newDocRoot, images = createDoc()
    
    imageCount = 0
    fileCount = 0
    
    for imageElem in collection.getElementsByTagName("images")[0].childNodes:
        if(imageElem.nodeType != imageElem.TEXT_NODE):
            images.appendChild(imageElem)
            imageCount += 1
            
            if(imageCount % int(sys.argv[2]) == 0):
                training = newDocRoot.toprettyxml()
                
                with open("training" + str(fileCount) + ".xml", "w") as f:
                    f.write(training)
                
                newDocRoot, images = createDoc()
                fileCount += 1
                
            
    training = newDocRoot.toprettyxml()
    
    with open("training" + str(fileCount) + ".xml", "w") as f:
        f.write(training)
    
    newDocRoot, images = createDoc()
    fileCount += 1