import json
import os
import random
import shutil
import time
from bson import ObjectId
from bson.json_util import dumps
from datetime import datetime
from flask import Flask,jsonify,request,send_from_directory
from flask_cors import CORS, cross_origin
from flask_pymongo import PyMongo
from PIL import Image
from threading import Thread
from werkzeug.utils import secure_filename

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config["MONGO_URI"] = "mongodb://meetmon-test:1testaccount@ds249311.mlab.com:49311/meetmon"
mongo = PyMongo(app)

BASE_COUNTDOWN = 86400
COUNTDOWN =  BASE_COUNTDOWN
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
BASE_URL = 'http://198.199.68.6/'
IMAGE_SIZE = 500

app.config['UPLOAD_FOLDER'] = 'static'
app.config['PLACEHOLDER_FOLDER'] = 'random'

def convert_result(mongo_result):
    mongo_result = list(mongo_result)
    result = []
    for item in mongo_result:
        current_result = {}
        current_result['_id'] = str(item['_id'])
        current_result['title'] = item['title']
        current_result['upvotes'] = item['upvotes']
        current_result['downvotes'] = item['downvotes']
        current_result['image'] = BASE_URL+'image/'+item['filename']
        current_result['timestamp'] = item['timestamp']
        result.append(current_result)
    return jsonify(result)

@app.route("/event",methods=["GET","POST"])
@cross_origin()
def events_method():
    result = None
    if request.method == "GET":
        result = get_all()
    else:
        result = add_new_event()
    return result

def get_all():
    results = mongo.db.event.find({}).sort('upvotes',-1)
    return convert_result(results)

def add_new_event():
    filename = request.form['filename']
    if (filename == 'no_image'):
        filename = random.choice(os.listdir(app.config['PLACEHOLDER_FOLDER']))
    data_input = {'title':request.form['title'],'timestamp':datetime.now(),'filename':filename,'upvotes':1,'downvotes':0}
    result = mongo.db.event.insert_one(data_input)
    return jsonify({'_id':str(result.inserted_id)})


@app.route("/event/<ObjectId:id>",methods=["GET","PUT","DELETE"])
@cross_origin()
def event_method(id):
    result = None
    if request.method=="GET":
        result = get_details(id)
    else:
        result = delete_card(id)
    return result

def get_details(id):
    results = mongo.db.event.find({"_id":id})
    return convert_result(results)

def delete_card(id):
    condition = {'_id':id}
    result = mongo.db.event.delete_one(condition)
    return jsonify({'count':result.deleted_count})

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload',methods=["POST"])
@cross_origin()
def upload_file():
    file = request.files['image']
    filename = 'no_image'
    if(file.filename == 'no_image'):
        return filename
    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        image = Image.open(filepath)
        width, height = image.size
        if (width > IMAGE_SIZE and height > IMAGE_SIZE):
            image.resize((IMAGE_SIZE,IMAGE_SIZE)).save(filepath)
        elif (width <= IMAGE_SIZE and height > IMAGE_SIZE):
            image.resize((width,IMAGE_SIZE)).save(filepath)
        elif (width > IMAGE_SIZE and height <= IMAGE_SIZE):
            image.resize((IMAGE_SIZE,height)).save(filepath)
    return filename

@app.route('/vote/<string:method>/<ObjectId:id>')
@cross_origin()
def vote(method, id):
    if method == 'up':
        mongo.db.event.update_one({"_id":id},{'$inc':{'upvotes':1}})
    elif method == 'down':
        mongo.db.event.update_one({"_id":id},{'$inc':{'downvotes':1}})
    return jsonify({'id':str(id)})

@app.route('/image/<string:filename>')
@cross_origin()
def image_serve(filename):
    if(filename in os.listdir(app.config['PLACEHOLDER_FOLDER'])):
        return send_from_directory(app.config['PLACEHOLDER_FOLDER'],filename)
    return send_from_directory(app.config['UPLOAD_FOLDER'], secure_filename(filename))

@app.route('/explode')
@cross_origin()
def current_time():
    return jsonify({'time':COUNTDOWN})

def periodic_deletion():
    global COUNTDOWN
    while True:
        while COUNTDOWN > 0:
            time.sleep(1)
            COUNTDOWN -= 1
        mongo.db.event.delete_many({})
        shutil.rmtree('static')
        os.makedirs('static')
        COUNTDOWN = BASE_COUNTDOWN

@app.before_first_request
def x():
    print('this is called')
    thread = Thread(target=periodic_deletion)
    thread.start()
