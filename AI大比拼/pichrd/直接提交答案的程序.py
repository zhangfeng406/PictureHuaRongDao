import sys
import base64
import json
import cv2
import requests
import numpy as np
import time
import copy
from tkinter import _flatten
from enum import IntEnum
from PIL import Image
from PIL import ImageChops

def post(url, data_json):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3941.4 Safari/537.36',
        'Content-Type': 'application/json'
    }
    r = requests.post(url, headers=headers, data=data_json)
    return r.text


uuid ="55db0891-ac50-4ccf-9c5a-c7d5e6d15a31"
operation="wasddwassawwdsdsw"
myswap=[2,3]

url1 = 'http://47.102.118.1:8089/api/challenge/start/'+str(uuid)
inputdata = {
    "teamid":9,
    "token":"46d12dca-2c6b-4a0a-9fdd-92b1404e23a9"
}
data_json = json.dumps(inputdata)
ret = json.loads(post(url1, data_json))
uuid2 = ret["uuid"]
chanceleft=ret["chanceleft"]

url2 = 'http://47.102.118.1:8089/api/challenge/submit'
datas = {
    "uuid": uuid2,
    "teamid": 9,
    "token": "46d12dca-2c6b-4a0a-9fdd-92b1404e23a9",
    "answer": {
        "operations": operation,
        "swap": myswap
    }
}
data_json = json.dumps(datas)
ret = json.loads(post(url2, data_json))
for key in ret.keys():
    print(key + " : ", ret[key])

print("chanceleft",chanceleft)