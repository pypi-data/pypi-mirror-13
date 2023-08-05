#coding:utf-8
"""Split different Characters from a single image"""

import os
import sys
from PIL import Image
try:
    from .misc import getNeighbors, getBlackN
except ImportError:
    from misc import getNeighbors, getBlackN


class pixelGroup:
    """一坨像素"""
    def __init__(self):
        self.bound=[32767,32767,-32768,-32768]
                   #   left        up         right       down
        self.pixels=set()
        self.__iter__=self.pixels.__iter__
        self.__len__=self.pixels.__len__
    def __iter__(self, **kwargs):
        return self.pixels.__iter__(**kwargs)
    def __repr__(self):
        return self.__class__.__name__+'(@'+hex(self.__hash__())+') '+str(self.bound)+', '+str(len(self.pixels))+' element(s)'

    def __iadd__(self, pixel):
        try:
            if len(pixel)!=2: raise TypeError('必须是有两个元素x y的组合')
        except: raise TypeError('必须是有两个元素x y的组合')
        self.add(pixel)
    def add(self, x, y):
        self.add((x,y))
    def add(self, pixel):
        """在增加像素的同时标记边界"""
        self.pixels.add(pixel)
        self.bound[0]=min(self.bound[0],pixel[0])
        self.bound[1]=min(self.bound[1],pixel[1])
        self.bound[2]=max(self.bound[2],pixel[0])
        self.bound[3]=max(self.bound[3],pixel[1])

    def toImage(self):
        if (self.bound[2]-self.bound[0]+1) * (self.bound[3]-self.bound[1]+1)>10000000:
            raise MemoryError('无法输出这么大的图像')
        output=Image.new('1',(self.bound[2]-self.bound[0]+1,
                       self.bound[3]-self.bound[1]+1),color=255)
        for p in self.pixels:
            output.putpixel((p[0]-self.bound[0],p[1]-self.bound[1]),0)
        return output


def floodFill(img:Image.Image, waitQueue:list or tuple, visited:pixelGroup=None) -> pixelGroup:
    """
    从waitQueue开始，返回所有与之相连的点。

    waitQueue可以是一个点(tuple)或待检查的点组成的列表(list of tuples)。
    """
    if type(waitQueue) is tuple:
        return floodFill(img,[waitQueue])
    if type(waitQueue) is not list:
        raise TypeError(__doc__)
    if visited is None:
        visited=pixelGroup()
    elif type(visited) is not pixelGroup:
        raise TypeError('只能传None或我特定的类进来')
    while len(waitQueue)!=0:
        currentP=waitQueue.pop(0)
        currentN=getBlackNT(currentP,img)
        for p in currentN:
            if p not in visited:
                visited.add(p)
                waitQueue.append(p)
    return visited

def splitBruteForce(original:pixelGroup,prefer:int,dest:list)->dict:
    """
    暴力把黏在一起的字符分开。

    @参数 original    要分开的一坨东西。
    @参数 prefer      这一坨东西的中心位于原本哪一个字符应该在的区域。 0~4
    @参数 dest(list)  分开后的字符分别放到哪里。e.g. [2,3,4] 或 [2,3] 或 [0,1]
    @返回值(dict)     引索为 dest 里的所有数字，值为分开后的 pixelGroup
    """
    if original is None: return dict()
    returnValue=dict()
    for k in dest:
        returnValue[k]=pixelGroup()
    for p in original:
        dictIndex=(p[0]-4*prefer)//16
        #dictIndex=(p[0]-4*prefer)/16-8
        #dictIndex=min(returnValue.keys(),key=lambda i:abs(i-dictIndex))
        returnValue[dictIndex].add(p)
    return returnValue

def splitImageA(img:Image.Image) -> list: #返回(pixelGroup)数组
    """把图像中的不同部分分开"""
    result1=[]
    visited=set()
    for x in range(img.width):
        for y in range(img.height):
            if img.getpixel((x,y))==255 or (x,y) in visited: continue
            nextGroup=floodFill(img,(x,y))
            result1.append(nextGroup)
            visited|=nextGroup.pixels

    result2=[[] for _ in range(5)] #result2 按照中心x轴方向的值粗略分成5组
    for letter in result1:
        if letter.bound[2]-letter.bound[0]<=3 and letter.bound[3]-letter.bound[1]<=3: continue
        result2[int((letter.bound[0]+letter.bound[2])/2//20)].append(letter) #注意这里 20 是实验得出的，图片中字符虽然随机，但是中线都在0~20,20~40...范围中

    result3=[None for _ in range(5)] #result3 简单的把result2里的东西组合在一起
    for i,g in enumerate(result2):
        if len(g)!=0:
            result3[i]=mergeL(g)

    result4=[x for x in range(5)]
    """
        result4 代表每个字符可能从result3的哪里来。
        这个比较难解释。
        result4==[0,1,2,3,4]表示没有问题，可以直接输出。
        [0,0,2,3,4]表示前两个字符黏在一起。
        [1,1,1,3,4]表示前三个字符黏在一起。
        [0,1,3,3,4]表示[2],[3]两个字符黏在一起。
        .....以此类推
    """
    for i,g in enumerate(result3):
        if g==None:
            if i-1<0:
                nearLeftOne=False
            elif i+1>=5: nearLeftOne=True
            else: nearLeftOne=findNearestConnected(i*20-10,result3[i-1],result3[i+1])
            if nearLeftOne:
                result4[i]=i-1
                #splitedA,splitedB=splitBruteForce(result3[i-1],20*i-3)
            else:
                result4[i]=i+1
                #splitedA,splitedB=splitBruteForce(result3[i+1],20*(i+1)+2)
        #TODO: 将连在一起的分开
    
    result5=[[] for x in range(5)] #result4 的逆命题。 表示result3的要分配到哪里去。
    for i in range(5):
        result5[result4[i]].append(i)
    result6=[None for x in range(5)]
    for i in range(5):
        if len(result5[i])==1:
            result6[i]=result3[i]
        else:
            temp=splitBruteForce(result3[i],i,result5[i])
            for k in temp:
                result6[k]=temp[k]
    return result6

def merge(group1:pixelGroup,group2:pixelGroup)->pixelGroup:
    if group1==None: return group2
    if group2==None: return group1
    merged=pixelGroup()
    merged.pixels=group1.pixels|group2.pixels
    merged.bound[0]=min(group1.bound[0],group2.bound[0])
    merged.bound[1]=min(group1.bound[1],group2.bound[1])
    merged.bound[2]=max(group1.bound[2],group2.bound[2])
    merged.bound[3]=max(group1.bound[3],group2.bound[3])
    return merged

def mergeL(groups:list)->pixelGroup:
     from functools import reduce
     return reduce(merge, groups)
 
def findNearestConnected(standardX:int,possibleT:pixelGroup,possibleF:pixelGroup):
    if possibleT==None: return False
    if possibleF==None: return True
    midT=(possibleT.bound[2]+possibleT.bound[0])/2
    midF=(possibleF.bound[2]+possibleF.bound[0])/2
    return abs(midT-standardX) < abs(midF-standardX)

if __name__=='__main__':
    if len(sys.argv)==1:
        floodFill(None,[])
        print(__doc__)
        exit(-1)
    else:
        path, inputFile = os.path.split(sys.argv[1])
        inputFileName, inputFileExt = os.path.splitext(inputFile)
        def append2FileName(what):
            return path+os.path.sep+inputFileName+what+inputFileExt
        try:
            inputImg=Image.open(sys.argv[1])
        except FileNotFoundError as ex:
            print('找不到文件')
            raise
        inputImg,_=inputImg.convert('1'),inputImg.close()
        result = splitImageA(inputImg) #result1 是分割最初的数据，几组像素
        if type(result) is not list:
            raise Exception('分割失败，', result1, type(result1))
        for i in range(len(result)):
            result[i].toImage().save(append2FileName('_c'+str(i)))

del os
del sys
del Image
