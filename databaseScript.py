# importing module
import pypyodbc
from dotenv import dotenv_values
from collections import OrderedDict
from datetime import date, datetime
from flask import Response, jsonify
import json
import mysql.connector

# from flask import jsonify

# Config
config = dotenv_values(".env")
# creating connection Object which will contain MySQL Server Connection
try:
    connection = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        database='recognition',
        # port=int(config['DB_PORT']),
        # user=config['DB_USERNAME'],
        # password=config['DB_PASSWORD'],
        # host=config['DB_HOST'],
        # database=config['DB_DATABASE']
    )

    if connection.is_connected():
        print('Connecté à la base de données MySQL')
except mysql.connector.Error as e:
    print(f"Erreur lors de la connexion à la base de données MySQL: {e}")
# connection = pypyodbc.connect(f"Driver={config['DB_DRIVER']};Server={config['DB_HOST']};Database={config['DB_DATABASE']};uid={config['DB_USERNAME']};pwd={config['DB_PASSWORD']}", autocommit=True)
cursor = connection.cursor()


def create_user(username, password):
    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    param_values = (username, password)
    try:
        cursor.execute(sql, param_values)
        connection.commit()
        return jsonify({"message": "User created successfully"}), 201
    except mysql.connector.Error as err:
        return jsonify({"message": str(err)}), 400


def get_user(username):
    sql = """
    SELECT users.id, users.username, users.password, roles.id AS id, roles.name
    FROM users
    JOIN roles ON users.id = roles.id
    WHERE users.username = %s
    """
    param_values = (username,)
    cursor.execute(sql, param_values)
    result = cursor.fetchone()
    if result:
        user = {
            'id': result[0],
            'username': result[1],
            'password': result[2],
            'role': {
                'id': result[0],
                'name': result[1]
            }
        }
        return user
    return None




def enroll_employee(student_id, picture):
    date_enrolment = datetime.now()
    sql = "INSERT INTO attendance_enrolments (student_id, date_enrolment, picture) values(%s, %s, %s)"
    param_values = (student_id, date_enrolment, picture)
    cursor.execute(sql, param_values)
    connection.commit()

    message = {'message': 'Employee is enrolled with success'}
    return Response(json.dumps(message), status=200, mimetype='application/json')

# -------------------gestion des presences---------------
def save_attendance(student_id):
    sql = "INSERT INTO attendance_lists (student_id , time) values(%s, %s)"
    param_values = (student_id, datetime.now())
    cursor.execute(sql, param_values)
    connection.commit()

    message = {'message': 'La présence a été enregistrée'}
    return Response(json.dumps(message), status=200, mimetype='application/json')

# // student requete--------

# -----------------ajout student--------------
def add_student(name, email, sexe, phoneNumber, filiere, level, matricule, departement, faculty, birthdate):
    """Ajoute un nouvel étudiant à la base de données."""
    sql = """
    INSERT INTO students (name, email, sexe, phoneNumber, filiere, level, matricule, departement, faculty, birthdate)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    param_values = (name, email, sexe, phoneNumber, filiere, level, matricule, departement, faculty, birthdate)

    cursor.execute(sql, param_values)
    connection.commit()

    message = {'message': 'Student has been added successfully'}
    return Response(json.dumps(message), status=200, mimetype='application/json')


# --------------------------------Mettre à jour un étudiant
def updateStudent(id, data):
    try:
        sql_update = """
        UPDATE students
        SET name = %s, email = %s, sexe = %s, phoneNumber = %s, filiere = %s, level = %s, matricule = %s
        WHERE id = %s
        """
        values_update = (
            data['name'],
            data['email'],
            data['sexe'],
            data['phoneNumber'],
            data['filiere'],
            data['level'],
            data['matricule'],
            id
        )
        cursor.execute(sql_update, values_update)
        connection.commit()
        return True
    except Exception as e:
        connection.rollback()
        print("Error updating student:", e)
        return False

# -----------------------recuper les etudiants ----------------------------------------------
def getStudents():
        sql = "SELECT * FROM students"
        cursor.execute(sql)
        results = cursor.fetchall()
        students = []

        for result in results:
            content = {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'sexe': result[3],
                'phoneNumber': result[4],
                'filiere': result[5],
                'level': result[6],
                'matricule': result[7]
            }
            students.append(content)

        return json.dumps(students, default=str)


# ----------------Récupérer un étudiant spécifique
def getStudentById(id):
    try:
        sql = "SELECT * FROM students WHERE id = %s"
        cursor.execute(sql, (id,))
        result = cursor.fetchone()
        if result:
            student = {
                'id': result[0],
                'name': result[1],
                'email': result[2],
                'sexe': result[3],
                'phoneNumber': result[4],
                'filiere': result[5],
                'level': result[6],
                'matricule': result[7]
            }
            return json.dumps(student, default=str)
        else:
            return None
    except Exception as e:
        print("Error fetching student by id:", e)
        return None