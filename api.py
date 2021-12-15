from flask import Flask, request, redirect
import numpy as np
from captcha_solver import CaptchaSolver
import cv2 as cv
import pytesseract
import json
import os

app = Flask(__name__)

@app.route("/second", methods=["POST"])
def second():
    if not "file" in request.files.keys():
        return redirect(request.url)
    
    file = request.files["file"].read()
    captcha = CaptchaSolver()

    return json.dumps(captcha.solveSecond(file, 0.7))

@app.route("/first", methods=["POST"])
def first():
    if not "file" in request.files.keys():
        return redirect(request.url)
    
    file = request.files["file"].read()
    captcha = CaptchaSolver()

    return json.dumps(captcha.solveFirst(file))

#app.run('0.0.0.0', port=5000)