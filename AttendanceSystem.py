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
from flask_cors import CORS


import databaseScript

# create the Flask app
app = Flask(__name__)
CORS(app)
message = {}
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Set up the Flask-JWT-Extended extension
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # Change this to a random secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_file(file, id):
    file.save(os.path.join(f'Images/', f"{id}-{file.filename}"))


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400

    hashed_password = generate_password_hash(password)
    result = databaseScript.create_user(username, hashed_password)
    return result


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # print(data)

    user = databaseScript.get_user(username)
    if user and check_password_hash(user['password'], password):
        access_token = create_access_token(identity=username)
        return jsonify(
            user=user,
            access_token=access_token
                       ), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@app.route('/api/students', methods=['POST'])
@jwt_required()
def create_student():
    """Crée un nouvel étudiant."""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    sexe = data.get('sexe')
    phoneNumber = data.get('phoneNumber')
    filiere = data.get('filiere')
    level = data.get('level')
    matricule = data.get('matricule')
    departement = data.get('departement')
    faculty = data.get('faculty')
    birthdate = data.get('birthdate')

    if not all([name, email, sexe, phoneNumber, filiere, level, matricule, departement, faculty, birthdate]):
        message = {'message': 'Veuillez fournir toutes les informations de l\'étudiant'}
        return Response(json.dumps(message), status=400, mimetype='application/json')

    result = databaseScript.add_student(name, email, sexe, phoneNumber, filiere, level, matricule, departement, faculty, birthdate)
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


@app.route('/api/students', methods=['GET'])
@jwt_required()
def getEmployeesdata():
    try:
        data = databaseScript.getStudents()

        # Si les données sont une chaîne JSON, les convertir en liste de dictionnaires
        if isinstance(data, str):
            data = json.loads(data)

        return jsonify(data=data), 200
    except Exception as e:
        # Log l'exception si nécessaire
        print(f"An error occurred: {e}")
        # Retourne un message d'erreur avec le code de statut 500 (Internal Server Error)
        return jsonify(error="An error occurred while fetching the employees data .", details=str(e)), 500

# Route pour mettre à jour un étudiant
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.json
    try:
        if databaseScript.updateStudent(id, data):
            # Si la mise à jour réussit, renvoyer les informations mises à jour de l'étudiant
            updated_student = {
                'id': id,
                'name': data['name'],
                'email': data['email'],
                'sexe': data['sexe'],
                'phoneNumber': data['phoneNumber'],
                'filiere': data['filiere'],
                'level': data['level'],
                'matricule': data['matricule']
            }
            return jsonify(student=updated_student), 200
        else:
            return jsonify(error="Failed to update student"), 500
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/api/enroll/<id>', methods=['POST'])
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
        print(result)
        save_file(file, id)
        return result


@app.route('/api/check', methods=['POST'])
@jwt_required()
def check():
    file = request.files['photo']
    print(file)

    if file.filename == '':
        message = {'message': 'No file selected'}
        return Response(json.dumps(message), status=400, mimetype='application/json')
    # print(file)
    if file and allowed_file(file.filename):
        # print(file)
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

                        if isinstance(result, str):  # Si result est une chaîne de caractères JSON
                            result = json.loads(result)

                        faceDis_list = faceDis.tolist()
                        data = {
                         'result' : result,
                        'faceDis' : faceDis_list,
                        'matcheIndexes' : int(matcheIndexes)
                        }
                        return jsonify(data)

                    else:
                        message = {'message': 'Aucune personne n\'a été trouvé'}
                        return Response(json.dumps(message), status=400, mimetype='application/json')
                else:
                    message = {'message': 'Aucune personne n\'a été trouvé'}
                    return Response(json.dumps(message), status=400, mimetype='application/json')
            else:
                message = {'message': 'Envoyer une image conforme'}
                return Response(json.dumps(message), status=400, mimetype='application/json')

# Route pour récupérer un étudiant spécifique
@app.route('/api/students/<int:id>', methods=['GET'])
def get_student(id):
    try:
        student = databaseScript.getStudentById(id)
        print(student)
        if student:
            return jsonify(student=json.loads(student)), 200
        else:
            return jsonify(error="Student not found"), 404
    except Exception as e:
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    # run app in debug mode on port 5000
    app.run(debug=True, host='192.168.1.100', port=5000)
