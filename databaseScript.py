# importing module
import pypyodbc
from dotenv import dotenv_values
from collections import OrderedDict
from datetime import date, datetime
from flask import Response
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


def getStudents():
    sql = "SELECT * FROM students"
    cursor.execute(sql)
    results = cursor.fetchall()
    students = []

    for result in results:
        content = {
            'id': result[0],
            'name': result[1],
            'filiere': result[2],
            'level': result[3],
            'matricule': result[4]
        }
        students.append(content)

    return json.dumps(students, default=str)


def enroll_employee(student_id, picture):
    date_enrolment = datetime.now()
    sql = "INSERT INTO attendance_enrolments (student_id, date_enrolment, picture) values(%s, %s, %s)"
    param_values = (student_id, date_enrolment, picture)
    cursor.execute(sql, param_values)
    connection.commit()

    message = {'message': 'Employee is enrolled with success'}
    return Response(json.dumps(message), status=200, mimetype='application/json')


def save_attendance(student_id):
    sql = "INSERT INTO attendance_lists (student_id , time) values(%s, %s)"
    param_values = (student_id, datetime.now())
    cursor.execute(sql, param_values)
    connection.commit()

    message = {'message': 'La présence a été enregistrée'}
    return Response(json.dumps(message), status=200, mimetype='application/json')


def add_student(name, filiere, level, matricule):
    """Ajoute un nouvel étudiant à la base de données."""
    sql = "INSERT INTO students (name, filiere, level, matricule) VALUES (%s, %s, %s, %s)"
    param_values = (name, filiere, level, matricule)

    cursor.execute(sql, param_values)
    connection.commit()

    message = {'message': 'Student has been added successfully'}
    return Response(json.dumps(message), status=200, mimetype='application/json')
