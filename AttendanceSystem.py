# -*- coding: utf-8 -*-
import json
import os
from datetime import date, timedelta

import cv2
import face_recognition
import numpy as np
from flask import Flask, request, Response, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash

import databaseScript

# create the Flask app
app = Flask(__name__)
message = {}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Set up the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a random secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file, id):
    file.save(os.path.join(f'Images/', f"{id}-{file.filename}"))


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    hashed_password = generate_password_hash(password)
    result = databaseScript.create_user(username, hashed_password)
    return result


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = databaseScript.get_user(username)
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@app.route('/students', methods=['POST'])
@jwt_required()
def create_student():
    """Crée un nouvel étudiant."""
    data = request.get_json()
    name = data.get('name')
    filiere = data.get('filiere')
    level = data.get('level')
    matricule = data.get('matricule')

    if not name or not filiere or not level or not matricule:
        message = {'message': 'Veuillez fournir toutes les informations de l\'étudiant'}
        return Response(json.dumps(message), status=400, mimetype='application/json')

    result = databaseScript.add_student(name, filiere, level, matricule)
    return result


def findEncodingImg(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:  # Vérifie si la liste d'encodages n'est pas vide
            encode = encodings[0]
            encodeList.append(encode)
    return encodeList


@app.route('/students', methods=['GET'])
@jwt_required()
def getEmployeesdata():
    return databaseScript.getStudents()


@app.route('/enroll/<id>', methods=['POST'])
@jwt_required()
def enrollement(id):
    file = request.files['photo']

    if file.filename == '':
        message = {'message': 'No file selected'}
        return Response(json.dumps(message), status=400, mimetype='application/json')

    if file and allowed_file(file.filename):
        if not os.path.exists(f'Images/'):
            os.makedirs(f'Images/')

        today = date.today()

        path_image = f'Images/{id}-{file.filename}'
        result = databaseScript.enroll_employee(id, path_image)
        save_file(file, id)
        return result


@app.route('/check', methods=['POST'])
@jwt_required()
def check():
    file = request.files['photo']

    if file.filename == '':
        message = {'message': 'No file selected'}
        return Response(json.dumps(message), status=400, mimetype='application/json')

    if file and allowed_file(file.filename):
        path = f'Images'
        if not os.path.exists(path):
            message = {'message': 'Employee isn\'t enrolled'}
            return Response(json.dumps(message), status=400, mimetype='application/json')

        else:
            images = []
            classNames = []
            myList = os.listdir(path)

            for cl in myList:
                curImage = cv2.imread(f'{path}/{cl}')
                images.append(curImage)
                classNames.append(os.path.splitext(cl)[0])
            known_face_encodings = findEncodingImg(images)
            print("Encoding complete.....")

            npImage = np.fromfile(file, np.uint8)

            img = cv2.imdecode(npImage, cv2.COLOR_BGR2RGB)
            faceEncodings = face_recognition.face_encodings(img)
            if (len(faceEncodings)):
                if (len(known_face_encodings)):
                    myEncode = faceEncodings[0]
                    matches = face_recognition.compare_faces(known_face_encodings, myEncode, tolerance=0.5)
                    faceDis = face_recognition.face_distance(known_face_encodings, myEncode)
                    matcheIndexes = np.argmin(faceDis)

                    print("matches")
                    print(matches)

                    print("faceDis")
                    print(faceDis)

                    print("matcheIndexes")
                    print(matcheIndexes)

                    if (matches[matcheIndexes]):
                        today = date.today()
                        path_image = f'{path}/{file.filename}'
                        id = ((classNames[matcheIndexes]).split('-'))[0]
                        result = databaseScript.save_attendance(id)
                        return result

                    else:
                        message = {'message': 'Aucune personne n\'a été trouvé'}
                        return Response(json.dumps(message), status=400, mimetype='application/json')
                else:
                    message = {'message': 'Aucune personne n\'a été trouvé'}
                    return Response(json.dumps(message), status=400, mimetype='application/json')
            else:
                message = {'message': 'Envoyer l\' image d\'une personne'}
                return Response(json.dumps(message), status=400, mimetype='application/json')


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, host='192.168.1.100', port=5000)
