from xml.dom import minidom
from PIL import Image
import os
import sys
import math



# This script is a scratch for processImages.py. Prefer to use processImages.py.




if(len(sys.argv) < 4):
    print("Provide args: program.py countFrom countTo currentIndex")
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

newDocRoot, images = createDoc()

fileName = 0
x1 = 0
y1 = 0
width = 0
height = 0

count = 0

if(not os.path.exists("splittedTraining/img_celeba/cropped")):
    os.mkdir("splittedTraining/img_celeba/cropped")

with open("list_bbox_celeba.csv", "r") as fbbox:
    for line in fbbox:
        if(count == 0):
            count += 1
            continue
        
        if(count >= int(sys.argv[1])):
        
            fileName, x1, y1, width, height = line.split(",")
            x1 = int(x1)
            y1 = int(y1)
            width = int(width)
            height = int(height)

            im = Image.open("img_celeba/" + fileName)
            totalWidth, totalHeight = im.size
            
            newSize = (250, 250)
            
            
            if(totalHeight < newSize[1] or height < 70):
               continue
            
            l = math.sqrt(width * height * 2) # last multiplier is how larger our new area will be
            
            if(l < newSize[0]):
                l = newSize[0]
            
            # crop is based on the middle of the segments of the bounding boxes:
            meioX = x1 + (width / 2)
            meioY = y1 + (height / 2)
            
            x2 = meioX - (l/2)
            y2 = meioY - (l/2)
            
            # if starting point for new crop area is starting out of bounds (less than 0)
            if(x2 > 0):
                left = int(x2)
            else:
                left = 0
            
            if(y2 > 0):
                top = int(y2)
            else:
                top = 0
            
            # if new crop area is going beyond bounds (more than totalWidth or totalHeight)
            if((x2 + l) < totalWidth):
                right = int(x2 + l)
            else:
                right = totalWidth
            
            if((y2 + l) < totalHeight):
                bottom = int(y2 + l)
            else:
                bottom = totalHeight
            
            # cropping
            cropImg = im.crop((left, top, right, bottom))
            totalWidth, totalHeight = cropImg.size
            
            # error in some image
            if(totalWidth == 0):
                print("Error: " + str(count) + "\n")
                count += 1
                continue
            
            # update bounding boxes after crop
            top = int(y1 - top)
            left = int(x1 - left)
            
            
            # if size is bigger than newSize, resize cropImg
            #if(totalWidth > newSize[0] or totalHeight > newSize[1]):
            ratio = 0
            
            if(totalWidth > totalHeight):
                ratio = newSize[0]/totalWidth
            else:
                ratio = newSize[1]/totalHeight
                
            cropImg = cropImg.resize((int(totalWidth*ratio), int(totalHeight*ratio)), Image.ANTIALIAS)
            
            # update bounding boxes after resizing
            left = left*ratio
            top = top*ratio
            width = width*ratio
            height = height*ratio

            totalWidth, totalHeight = cropImg.size
                
            
            # if cropImg is either bigger or smaller than newSize, we create a black padding, but the padding will only be visible when the cropImg is smaller
            # or if after the resize, one of the dimensions is still smaller
            
            # creating a new image with black padding 
            # centering paste location with the face in the exact center (close as possible)
            meioX = left + (width / 2)
            meioY = top + (height / 2)
        
            pasteAt = ( int((newSize[0] / 2) - meioX), int((newSize[1] / 2) - meioY))
            
            #creating new total black image
            newImg = Image.new('RGB', newSize, color = 'black')
            newImg.paste(cropImg, pasteAt)
            
            # update bounding boxes after padding
            top = top + pasteAt[1]
            left = left + pasteAt[0]
            
            # update size
            totalWidth, totalHeight = newImg.size
            
            newName, ex = fileName.split(".")
            
            try:
                newImg.save("splittedTraining/img_celeba/cropped/" + newName + ".png")
            except:
                print("Error: " + str(count) + "\n")
                count += 1
                continue
            
            # building xml training file with new bounding boxes
            image = newDocRoot.createElement('image')
            images.appendChild(image)
            image.setAttribute('file', "img_celeba/cropped/" + newName + ".png")
            image.setAttribute('width', str(totalWidth))
            image.setAttribute('height', str(totalHeight))
            
            # new coordinates for bounding box
            box = newDocRoot.createElement('box')
            image.appendChild(box)
            box.setAttribute('top', str(int(top)))
            box.setAttribute('left', str(int(left)))
            box.setAttribute('width', str(int(width)))
            box.setAttribute('height', str(int(height)))

        if(count >= int(sys.argv[2])):
            break
        
        count += 1


training = newDocRoot.toprettyxml()
with open("splittedTraining/training" + sys.argv[3] + ".xml", "w") as f:
    f.write(training)