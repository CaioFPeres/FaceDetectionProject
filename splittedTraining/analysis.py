from xml.dom import minidom
from PIL import Image
import sys
import numpy as np


# This tool will just print a list as follows:
# [("height"), numberOfImagesThatHasThatHeight]
# [("width"), numberOfImagesThatHasThatWidth]


if(len(sys.argv) < 2):
    print("Provide args:program.py fromFile")
    exit()
    
heightDict = {}
widthDict = {}

with open(sys.argv[1], "r") as file:
    DOMTree = minidom.parse(file)
    collection = DOMTree.documentElement
    
    for imageElem in collection.getElementsByTagName("images")[0].childNodes:
        if(imageElem.nodeType != imageElem.TEXT_NODE):
            
            for boxElem in imageElem.childNodes:
                if(boxElem.nodeType != boxElem.TEXT_NODE):
                    height = boxElem.getAttribute("height")
                    width = boxElem.getAttribute("width")
                    
                    if(height in heightDict):
                        heightDict[height] += 1
                    else:
                        heightDict[height] = 1
                        
                    if(width in widthDict):
                        widthDict[width] += 1
                    else:
                        widthDict[width] = 1
                        

sortedHeightDict = sorted(heightDict.items(), key=lambda x:x[1], reverse=True)
sortedWidthDict = sorted(widthDict.items(), key=lambda x:x[1], reverse=True)

print(sortedHeightDict)
print()
print(sortedWidthDict)