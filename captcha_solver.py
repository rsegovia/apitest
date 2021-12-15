import torch
import cv2 as cv
import numpy as np
import os
from os import listdir

class CaptchaSolver:
    def __init__(self) -> None:
        self.boxes = []
        self.js = {}
    
    def toText(self, cords):
        solved = ""
        
        for cord in cords:
            for x in range(0, len(self.boxes)):
                if list(self.boxes[x].values())[0]['y1'] == cord:
                    solved += str(list(self.boxes[x].keys())[0])
        
        self.text = solved
    
    def solveSecond(self, img_bytes, percent_required):
        model = torch.hub.load('.', 'custom', 'bomb_captcha.pt', source='local')
        
        nparr = np.fromstring(img_bytes, np.uint8)
        img = cv.imdecode(nparr, cv.IMREAD_COLOR) 
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        
        results = model(img, size=416)

        if results.xyxy[0].shape[0] >= 1:
            for box in range(0, results.xyxy[0].shape[0]):
                y1, x1, y2, x2, percent, pred = results.xyxy[0][box]
                if percent >= percent_required:
                    self.boxes.append({str(int(pred.item())):{"x1":round(x1.item(), 2), "y1":round(y1.item(), 2), "x2":round(x2.item(), 2), "y2":round(y2.item(), 2), "per":round(percent.item(), 2)}})
            
            xCord = sorted([self.boxes[x][list(self.boxes[x].keys())[0]]['y1'] for x in range(0, len(self.boxes))])
            
            self.toText(xCord)
            
            self.js["captcha"] = str(self.text)
            self.js["coordinates"] = self.boxes
                                    
        return self.js
    
    def remove_suffix(self, input_string, suffix):
        if suffix and input_string.endswith(suffix):
            return input_string[:-len(suffix)]
        return input_string

    def load_images(self):
        dir_name = './images/'
        file_names = listdir(dir_name)
        
        targets = {}
        
        for file in file_names:
            path = dir_name + file
            targets[self.remove_suffix(file, '.png')] = cv.imread(path)

        return targets

    def positions(self, target, threshold=0.85,img = None):
        result = cv.matchTemplate(img,target, cv.TM_CCOEFF_NORMED)
        w = target.shape[1]
        h = target.shape[0]

        yloc, xloc = np.where(result >= threshold)


        rectangles = []
        for (x, y) in zip(xloc, yloc):
            rectangles.append([int(x), int(y), int(w), int(h)])
            rectangles.append([int(x), int(y), int(w), int(h)])

        rectangles, weights = cv.groupRectangles(rectangles, 1, 0.2)
        return rectangles

    def getDigits(self, img):
        digits = []
        d = self.load_images()
        
        for i in range(10):
            p = self.positions(d[str(i)],img=img,threshold=0.95)
            if len (p) > 0:
                digits.append({'digit':str(i),'x':p[0][0]})

        def getX(e):
            return e['x']

        digits.sort(key=getX)
        r = list(map(lambda x : x['digit'],digits))
        
        return ''.join(r)
    
    def solveFirst(self, img_bytes):
        nparr = np.fromstring(img_bytes, np.uint8)
        result = cv.imdecode(nparr, cv.IMREAD_COLOR)        
        
        return {"captcha": self.getDigits(result)}