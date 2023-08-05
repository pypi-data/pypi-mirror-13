#coding:utf-8
"""Misc for this project"""


from PIL import Image
from random import randint

def mdncd(dirname):
    import os
    try: os.mkdir(dirname)
    except FileExistsError: pass
    os.chdir(dirname)

def getNeighbors(x, y, img:Image.Image) -> list:
    n=[]
    if img is not None:
        w=img.width
        h=img.height
        if (x<0 or y<0 or x>=w or y>=h): return 0
    n.append((x-1, y-1))
    n.append((x-1, y))
    n.append((x-1, y+1))
    n.append((x, y-1))
    n.append((x, y+1))
    n.append((x+1, y-1))
    n.append((x+1, y))
    n.append((x+1, y+1))
    if not img is None:
        n2=[]
        for e in n:
            x=e[0]
            y=e[1]
            if x<0 or y<0 or x>=w or y>=h:
                continue
            n2.append(e)
    return n2

def getNeighborsT(point, img:Image.Image = None) -> list:
    return getNeighbors(point[0], point[1], img)

def getBlackN(x, y, img:Image.Image) -> list:
    n=[]
    for e in getNeighbors(x,y,img):
        x=e[0]
        y=e[1]
        if img.getpixel((x,y))!=0:
            continue
        n.append(e)
    return n

def getBlackNT(point, img:Image) -> list:
    return getBlackN(point[0], point[1], img)

def randomRGBT() -> tuple:
    return (randint(0,255),randint(0,255),randint(0,255))

def randomRGBI() -> int:
    return randint(0,255) + randint(0,255)*256 + randint(0,255)*256*256

del Image
