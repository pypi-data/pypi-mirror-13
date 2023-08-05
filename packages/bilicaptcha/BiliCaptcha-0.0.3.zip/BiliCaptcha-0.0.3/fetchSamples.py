#coding:utf-8
"""
Fetch captcha samples from bilibili.com

Usage:
    Pass in the amount of samples to fetch as the first argument.
    If not, the amount will be *1000*.
"""
DEFAULTAMOUNT=1000

import sys
import time
import threading
import shutil
import requests
try:
    from . import misc
except ImportError:
    import misc

def fetchSample(filename):
    response=requests.get('https://account.bilibili.com/captcha',headers={'Connection':'close'})
    try:
        response.raise_for_status()
    except:
        print('Fetch error!')
        return
    with open(filename,'wb') as f:
        f.write(response.content)

if __name__=='__main__':
    if len(sys.argv)==1:
        amount=DEFAULTAMOUNT
    else:
        try:
            amount=int(sys.argv[1])
        except:
            print(__doc__)
            exit()

    misc.mdncd('data')
    misc.mdncd('original')

    for _ in range(amount):
        threading.Thread(target=fetchSample,args=(str(time.time())+'.png',)).start()
