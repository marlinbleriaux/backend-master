# importing module

from datetime import date, datetime
from flask import Response, jsonify
import json
import mysql.connector

# from flask import jsonify

# Config
# creating connection Object which will contain MySQL Server Connection
try:
    connection = mysql.connector.connect(
        # host='localhost',
        host='check-stud.cvgq26sewyvb.us-east-2.rds.amazonaws.com',
        port=3306,
        # port=14451,
        # user='root',
        user='admin',
        # password='',
        password='MK3fGitkIG',
        database='recognition',
        # database='sql12713949',
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
cursor = connection.cursor()


# -------------------gestion des presences---------------
def save_attendance(student_id):
    try:
        # Sauvegarder la présence dans la base de données
        sql = "INSERT INTO attendance_lists (student_id, time) VALUES (%s, %s)"
        param_values = (student_id, datetime.now())
        cursor.execute(sql, param_values)
        connection.commit()

        # Récupérer les informations de l'étudiant
        cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
        result = cursor.fetchone()
        content = {
            'id': result[0],
            'name': result[1],
            'email': result[2],
            'sexe': result[3],
            'phoneNumber': result[4],
            'filiere': result[5],
            'level': result[6],
            'matricule': result[7],
            'departement': result[8],
            'faculty': result[9],
            'birthdate': result[10]
        }

        if not result:
            return Response(json.dumps({'message': 'Étudiant non trouvé'}), status=404, mimetype='application/json')

        # Récupérer la liste des présences de l'étudiant
        cursor.execute("SELECT * FROM attendance_lists WHERE student_id = %s", (student_id,))
        attendance_list = cursor.fetchall()
        attendance = {
            'id': result[0],
            'student_id': result[1],
            'time': result[2],

        }

        # Construire la réponse
        response_data = {
            'student': content,
            'attendance_list': attendance
        }

        # Retourner les informations de l'étudiant et la liste des présences
        return response_data
    except mysql.connector.Error as err:
        return Response(json.dumps({'message': str(err)}), status=500, mimetype='application/json')

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

    # Récupérer les informations de l'étudiant
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    result = cursor.fetchone()
    content = {
        'id': result[0],
        'name': result[1],
        'email': result[2],
        'sexe': result[3],
        'phoneNumber': result[4],
        'filiere': result[5],
        'level': result[6],
        'matricule': result[7],
        'departement': result[8],
        'faculty': result[9],
        'birthdate': result[10]
    }

    message = {'message': 'Employee is enrolled with success'}
    # return Response(json.dumps(message), status=200, mimetype='application/json')
    return {
        "user":content,
        "path":picture
    }

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
                'matricule': result[7],
                'departement': result[8],
                'faculty': result[9],
                'birthdate': result[10]
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
                'matricule': result[7],
                'departement': result[8],
                'faculty': result[9],
                'birthdate': result[10]
            }
            return json.dumps(student, default=str)
        else:
            return None
    except Exception as e:
        print("Error fetching student by id:", e)
        return None

def search_students(criteria):
        try:
            # Construction de la requête SQL de base
            sql = "SELECT * FROM students WHERE "
            sql_conditions = []
            sql_params = []

            # Ajout des conditions pour chaque critère
            if 'name' in criteria:
                sql_conditions.append("name LIKE %s")
                sql_params.append(f"%{criteria['name']}%")
            if 'email' in criteria:
                sql_conditions.append("email LIKE %s")
                sql_params.append(f"%{criteria['email']}%")
            if 'sexe' in criteria:
                sql_conditions.append("sexe LIKE %s")
                sql_params.append(f"%{criteria['sexe']}%")
            if 'phoneNumber' in criteria:
                sql_conditions.append("phoneNumber LIKE %s")
                sql_params.append(f"%{criteria['phoneNumber']}%")
            if 'filiere' in criteria:
                sql_conditions.append("filiere LIKE %s")
                sql_params.append(f"%{criteria['filiere']}%")
            if 'level' in criteria:
                sql_conditions.append("level LIKE %s")
                sql_params.append(f"%{criteria['level']}%")
            if 'matricule' in criteria:
                sql_conditions.append("matricule LIKE %s")
                sql_params.append(f"%{criteria['matricule']}%")
            if 'departement' in criteria:
                sql_conditions.append("departement LIKE %s")
                sql_params.append(f"%{criteria['departement']}%")
            if 'faculty' in criteria:
                sql_conditions.append("faculty LIKE %s")
                sql_params.append(f"%{criteria['faculty']}%")
            if 'birthdate' in criteria:
                sql_conditions.append("birthdate LIKE %s")
                sql_params.append(f"%{criteria['birthdate']}%")

            # Joindre les conditions avec 'AND'
            sql += " AND ".join(sql_conditions)

            # Exécuter la requête
            cursor.execute(sql, sql_params)
            results = cursor.fetchall()

            # Construire la liste des étudiants
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
                    'matricule': result[7],
                    'departement': result[8],
                    'faculty': result[9],
                    'birthdate': result[10]
                }
                students.append(content)

            return json.dumps(students, default=str)

        except mysql.connector.Error as err:
            print(f"Error: {err}")
            return Response(json.dumps({'message': str(err)}), status=500, mimetype='application/json')
