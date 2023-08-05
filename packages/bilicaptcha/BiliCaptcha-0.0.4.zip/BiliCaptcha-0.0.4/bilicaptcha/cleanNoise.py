#coding:utf-8
"""Erase noises in a captcha"""
import os
import sys
from PIL import Image
try:
    from .misc import getNeighbors, getBlackN
except ImportError:
    from misc import getNeighbors, getBlackN
#from matplotlib import pyplot #for debugging

def erodeI(img:Image.Image, iterations=2, threshold=1):
    img2=img.copy()
    tipPoint=set()
    for _ in range(iterations):
        img=img2.copy()
        for x in range(img.width):
            for y in range(img.height):
                pos=(x,y)
                if img.getpixel(pos)==0: #黑
                    if len(getBlackN(x,y,img))<=threshold:
                        img2.putpixel(pos,255)
                        tipPoint.add(pos)
    prev=None
    while prev!=tipPoint:
        prev=tipPoint.copy()
        for point in tipPoint.copy():
            if len(getBlackN(point[0],point[1],img2))>1:
                img2.putpixel(point,0)
            tipPoint.remove(point)
    return img2

def simplifyI(inputImg:Image.Image):
    colorList=dict()
    for x in range(inputImg.width):
        for y in range(inputImg.height):
            color=inputImg.getpixel((x,y))
            if color not in colorList:
                colorList[color]=0
            colorList[color]+=1

    sortedList=list(colorList)
    sortedList.sort(key=lambda k:colorList[k],reverse=True)
    
    if False: #debug
        for e in sortedList:
            print(e,colorList[e])
        pyplot.bar(tuple(range(len(sortedList))), tuple(colorList[k] for k in sortedList),
                    color=tuple((color[0]/256,color[1]/256,color[2]/256) for color in sortedList), width=0.8, align='center')
        pyplot.axis('tight')
        r=pyplot.axis()
        pyplot.axis((r[0],r[1],0,100))
        pyplot.xticks(tuple(range(len(sortedList))),tuple(str(k) for k in sortedList), rotation=90)
        pyplot.show()

    for x in range(inputImg.width):
        for y in range(inputImg.height):
            color=inputImg.getpixel((x,y))
            if color != sortedList[1]:
                inputImg.putpixel((x,y),(255,255,255))
            else:
                inputImg.putpixel((x,y),(0,0,0))
    inputImg=inputImg.convert('1')
    for x in range(inputImg.width):
        for y in range(inputImg.height):
            ns=getNeighbors(x,y,inputImg)
            blackConnected=False
            for n in ns:
                if inputImg.getpixel(n)==0:
                    blackConnected=True
                    break
            if not blackConnected:
                inputImg.putpixel((x,y),(255,255,255))
    return inputImg
        

if __name__=='__main__':
    if len(sys.argv)==1:
        print(__doc__)
        exit(-1)
    elif len(sys.argv)==2:
        path, inputFile = os.path.split(sys.argv[1])
        inputFileName, inputFileExt = os.path.splitext(inputFile)
        def append2FileName(what):
            return path+os.path.sep+inputFileName+what+inputFileExt
        outputFile=append2FileName('_M')
    else: outputFile=sys.argv[2]
    img=Image.open(sys.argv[1]).convert('RGB')
    simplifyI(img).save(outputFile)
    #erodeI(simplifyI(img))
    
del os
del sys
del Image
