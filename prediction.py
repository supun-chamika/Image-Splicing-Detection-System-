from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from keras.preprocessing.image import ImageDataGenerator
import tensorflow as tf
import numpy as np
import os
from cv2 import cv2

from PIL import Image
import os
from pylab import *
import re
from PIL import Image, ImageChops, ImageEnhance

import matplotlib.pyplot as plt
import flask
from flask import jsonify
from flask_cors import CORS, cross_origin

imageModel = tf.keras.models.load_model('correct_model.h5')


app = Flask(__name__)
CORS(app)


def imagePrediction(image, target):

    npimg = np.fromstring(image, np.uint8)
    npimg = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    image = cv2.imwrite('prediction.jpg',npimg)

    resaved_filename = 'test.jpg'
    
    im = Image.open('prediction.jpg').convert('RGB')
    im.save(resaved_filename, 'JPEG', quality=90)
    resaved_im = Image.open(resaved_filename)
    
    ela_im = ImageChops.difference(im, resaved_im)
    
    extrema = ela_im.getextrema()
    max_diff = max([ex[1] for ex in extrema])
    if max_diff == 0:
        max_diff = 1
    scale = 255.0 / max_diff
    
    X = []
    X.append(array(ImageEnhance.Brightness(ela_im).enhance(scale).resize((128, 128))).flatten() / 255.0)
    X = np.array(X)
    X = X.reshape(-1, 128, 128, 3)

    result = imageModel.predict(X)
    result = np.argmax(result,axis = 1)


    if(result > 0.5):
        predict = 'Spliced'
    else:
        predict = 'Authentic'

    data = {
        
        
            "title": "Prediction Result",
            "description": predict
        
       
    }
    response = flask.jsonify(data)

    response.headers.add('Access-Control-Allow-Origin', '*')
    print(data)

    return response


@app.route('/prediction', methods=['GET', 'POST'])
def predict():
    # initialize the data dictionary that will be returned from the
    # view
    data = {"data": [{
        "title": 'Operation',
        "description": 'Internal Server Error'
    }]}
    try:
        if request.method == 'POST':
            if flask.request.files.get("image"):
                result = ''
                image = request.files['image'].read()
                result = imagePrediction(image, target=(224, 224))

                return (result)

            return ({"status": false})
    except Exception as e:

        print(e)
        return flask.jsonify(e)


if __name__ == '__main__':
    app.run(port=3000)
