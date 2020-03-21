import os
import sys
import subprocess
import requests
import ssl
import random
import string
import json

from flask import jsonify
from flask import Flask
from flask import request
from flask import send_file
import traceback

from app_utils import blur
from app_utils import download
from app_utils import generate_random_filename
from app_utils import clean_me
from app_utils import clean_all
from app_utils import create_directory
from app_utils import get_model_bin
from app_utils import get_multi_model_bin


from io import BytesIO
import utils
from models import resnet
import tensorflow as tf
from scipy import misc
import numpy as np


try:  # Python 3.5+
    from http import HTTPStatus
except ImportError:
    try:  # Python 3
        from http import client as HTTPStatus
    except ImportError:  # Python 2
        import httplib as HTTPStatus


app = Flask(__name__)


@app.route("/process", methods=["POST"])
def process():

    input_path = generate_random_filename(upload_directory,"jpg")
    output_path = generate_random_filename(upload_directory,"jpg")

    try:

        url = request.json["url"]
        # phone: iphone, blackberr or sony
        phone = request.json["phone"]
        # resolution: orig,high,medium,small,tiny
        resolution = request.json["resolution"]

        download(url, input_path)
       
        # get the specified image resolution
        IMAGE_HEIGHT, IMAGE_WIDTH, IMAGE_SIZE = utils.get_specified_res(res_sizes, phone, resolution)

        # create placeholders for input images
        x_ = tf.placeholder(tf.float32, [None, IMAGE_SIZE])
        x_image = tf.reshape(x_, [-1, IMAGE_HEIGHT, IMAGE_WIDTH, 3])
            
        # generate enhanced image
        enhanced = resnet(x_image)


        with tf.Session(config=config) as sess:
            saver = tf.train.Saver()
            saver.restore(sess, "models_orig/" + phone + "_orig")
            image = np.float16(misc.imresize(misc.imread(filename), res_sizes[phone])) / 255
            image_crop = utils.extract_crop(image, resolution, phone, res_sizes)
            image_crop_2d = np.reshape(image_crop, [1, IMAGE_SIZE])
            enhanced_2d = sess.run(enhanced, feed_dict={x_: image_crop_2d})
            enhanced_image = np.reshape(enhanced_2d, [IMAGE_HEIGHT, IMAGE_WIDTH, 3])
            misc.imsave(filename, enhanced_image)
    
        callback = send_file(output_path, mimetype='image/jpeg')

        return callback, 200


    except:
        traceback.print_exc()
        return {'message': 'input error'}, 400

    finally:
        clean_all([
            input_path,
            output_path
            ])

if __name__ == '__main__':
    global upload_directory
    global config, res_sizes

    upload_directory = '/src/upload/'
    create_directory(upload_directory)

    config = tf.ConfigProto(device_count={'GPU': 0})

    # get all available image resolutions
    res_sizes = utils.get_resolutions()

    url_prefix = 'http://pretrained-models.auth-18b62333a540498882ff446ab602528b.storage.gra.cloud.ovh.net/image/deep-photo-enhancement/'

    for i in ["blackberry_orig.data-00000-of-00001", "blackberry_orig.index", "iphone_orig.data-00000-of-00001", "iphone_orig.index", "sony_orig.data-00000-of-00001", "sony_orig.index"]:
        get_model_bin(url_prefix + i , "models_orig/" + i)

    get_model_bin(url_prefix + "imagenet-vgg-verydeep-19.mat" , "models/imagenet-vgg-verydeep-19.mat")
    
    port = 5000
    host = '0.0.0.0'

    app.run(host=host, port=port, threaded=True)

