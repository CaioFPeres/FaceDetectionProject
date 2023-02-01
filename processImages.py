from xml.dom import minidom
from PIL import Image
import os
import sys
import math


# This script will process the images. Basically resizing the bounding box and cropping them into 250x250.
# You need to pass which image index to start from, and which image index to end.


if(len(sys.argv) < 3):
    print("Provide args: program.py countFrom countTo")
    exit()
    
    
# This function pastes an image into the newSize parameter. It basically crops an image.
# But, if one of the sides of the image are smaller than 250, it will automatically insert a black padding.
# It will also center the image based on the bounding box position (will only work for single object images)
def pasteNewImage(img, left, top, width, height, newSize):
    # creating a new image with black padding 
    # centering paste location with the face in the exact center (close as possible)

    middleX = left + (width / 2)
    middleY = top + (height / 2)

    pasteAt = ( int((newSize[0] / 2) - middleX), int((newSize[1] / 2) - middleY))
    
    #creating new total black image
    newImg = Image.new('RGB', newSize, color = 'black')
    newImg.paste(img, pasteAt)
    
    # update bounding boxes after centering
    top = top + pasteAt[1]
    left = left + pasteAt[0]
    
    return newImg, left, top
    
    
# This function was once used for cropping a bigger area that contains the area of the bounding box. Can still be useful for cropping images with more than one object. 
# The side argument (s) will be understood as being the side of a square. So the crop will happen considering a square with side s.
# Which means, you need to make sure the area to be cut out comprehends the bounding box within it. Theres a commented example in main function.
def cropSquareArea(im, x1, y1, width, height, s):
    
    top = 0
    left = 0
    right = 0
    bottom = 0
    totalWidth, totalHeight = im.size
    
    # crop is based on the middle of the segments of the bounding boxes:
    middleX = x1 + (width / 2)
    middleY = y1 + (height / 2)
    
    x2 = middleX - (s/2)
    y2 = middleY - (s/2)
        
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
    if((x2 + s) < totalWidth):
        right = int(x2 + s)
    else:
        right = totalWidth
    
    if((y2 + s) < totalHeight):
        bottom = int(y2 + s)
    else:
        bottom = totalHeight
    
    # cropping
    cropImg = im.crop((left, top, right, bottom))
    
    # update bounding boxes after crop
    top = int(y1 - top)
    left = int(x1 - left)
    
    return cropImg, left, top


# resize based on bounding box
def resize(im, left, top, width, height, size):
    
    ratio = 0
    totalWidth, totalHeight = im.size
    
    if(width > height):
        ratio = size/width
    else:
        ratio = size/height
        
    im = im.resize((int(totalWidth*ratio), int(totalHeight*ratio)), Image.ANTIALIAS)
    
    # update bounding boxes after resizing
    left = left*ratio
    top = top*ratio
    width = width*ratio
    height = height*ratio
    
    return im, left, top, width, height


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
                left = int(x1)
                top = int(y1)
                width = int(width)
                height = int(height)

                im = Image.open("img_celeba/" + fileName)
                
                
                newSize = (250, 250)
                
                # skip bad images
                if(height < 40):
                    continue
                
                
                # error in some image
                if(im.width == 0):
                    print("Error: " + str(count) + "\n")
                    count += 1
                    continue
                
                
                # Resize is done based on bounding box size
                # In this way, all the faces will have the same dimensions. Which makes the model train better.
                im, left, top, width, height = resize(im, left, top, width, height, 100)
                
                
                # In this case, i chose to just crop and at the same time apply the black padding, using pasteNewImage function.
                # But you can also crop the images choosing a multiplier for a bigger area based on the existing bounding box area.
                # its just another way of cropping based on the bounding box dimensions.
                
                # this is an example for calculating a square area that contains the original bounding box area
                #s = math.sqrt(width * height * 3) # last multiplier is how larger our new area will be
                
                # here i just pick a size if the side of the square is smaller than the size we want
                # i would do this because if we proceeding with a smaller area than the size, we would need to put black paddings anyway, so its better to just
                # get more image area (Since its not black, it helps to train a little better the not-face class. But i think in the end doesn't really matter)
                #if(s < newSize[0]):
                #s = 500

                #im, left, top = cropSquareArea(im, left, top, width, height, s)
                
                
                # if cropImg is either bigger or smaller than newSize, we create a black padding, but the padding will only be visible when the cropImg is smaller
                # or if after the resize, one of the dimensions is still smaller
                
                newImg, left, top = pasteNewImage(im, left, top, width, height, newSize)
                
                
                # Always use PNG images for better accuracy
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
                image.setAttribute('width', str(newImg.size[0]))
                image.setAttribute('height', str(newImg.size[1]))
                
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