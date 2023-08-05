#coding:utf-8

from PIL import Image, ImageDraw
import unittest
try:
    from .splitImage import floodFill, splitImageA
    from .misc import randomRGBT, mdncd
except ImportError:
    from splitImage import floodFill, splitImageA
    from misc import randomRGBT, mdncd

class imageOpTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        mdncd('test')

    @staticmethod
    def test_FloodFill():
        """把与(0,0)相连的线条染色"""
        testImage=Image.open('floodfill.png').convert('RGB')
        binary_copy=testImage.convert('1')
        #####################################>
        color=randomRGBT()
        for p in floodFill(binary_copy, (0,0)):
            testImage.putpixel(p, color)
        color=randomRGBT()
        for p in floodFill(binary_copy, (0,binary_copy.height-1)):
            testImage.putpixel(p, color)
        color=randomRGBT()
        for p in floodFill(binary_copy, (binary_copy.width-1,0)):
            testImage.putpixel(p, color)
        color=randomRGBT()
        for p in floodFill(binary_copy, (binary_copy.width-1,binary_copy.height-1)):
            testImage.putpixel(p, color)
        #####################################>
        testImage.save('floodfill_o.png')

    @staticmethod
    def test_splitImageA():
        """把图片中的不同部分分开"""

        testImage=Image.open('split1.png')
        testImage,_=testImage.convert('RGB'),testImage.close()
        draw=ImageDraw.Draw(testImage.convert('RGB'))
        for c in splitImageA(testImage.convert('1')):
            print(c)
            outlineColor=randomRGBT()
            draw.rectangle(((c.bound[0]-1,c.bound[1]-1),
                            (c.bound[2]+1,c.bound[3]+1)),
                           outline=outlineColor)
        testImage.save('split1_o.png')

        testImage=Image.open('split2.png')
        testImage,_=testImage.convert('RGB'),testImage.close()
        draw=ImageDraw.Draw(testImage)
        for c in splitImageA(testImage.convert('1')):
            print(c)
            outlineColor=randomRGBT()
            draw.rectangle(((c.bound[0]-1,c.bound[1]-1),
                            (c.bound[2]+1,c.bound[3]+1)),
                           outline=outlineColor)
        testImage.save('split2_o.png')

        testImage=Image.open('split3.png')
        testImage,_=testImage.convert('RGB'),testImage.close()
        draw=ImageDraw.Draw(testImage)
        for c in splitImageA(testImage.convert('1')):
            print(c)
            outlineColor=randomRGBT()
            draw.rectangle(((c.bound[0]-1,c.bound[1]-1),
                            (c.bound[2]+1,c.bound[3]+1)),
                           outline=outlineColor)
        testImage.save('split3_o.png')

if __name__=='__main__':
    unittest.main()
