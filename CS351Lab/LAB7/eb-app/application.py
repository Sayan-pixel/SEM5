# Name: Sayan Shit
# Roll No: 2401179
# CS351 Lab Assignment 7 - Elastic Beanstalk (Adapted from Lab 6)

from flask import Flask, request, jsonify, send_from_directory
import pymysql
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Elastic Beanstalk expects the application object to be named 'application' by default
application = Flask(__name__, static_folder='website', static_url_path='')

# Configuration for RDS
RDS_ENDPOINT = os.getenv("RDS_ENDPOINT")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

def get_db_connection():
    """
    Establishes and returns a connection to the RDS MySQL database.
    """
    connection = pymysql.connect(
        host=RDS_ENDPOINT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

def create_table_if_not_exists():
    """
    Creates the feedback table if it doesn't already exist in the database.
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            create_table_query = """
            CREATE TABLE IF NOT EXISTS feedbacks (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
        connection.commit()
        connection.close()
        print("Feedback table checked/created successfully.")
    except Exception as e:
        print(f"Error creating table: {e}")

# Serve the static website files
@application.route('/')
def index():
    return send_from_directory('website', 'index.html')

@application.route('/<path:path>')
def static_files(path):
    return send_from_directory('website', path)

# API Endpoint to fetch feedbacks
@application.route('/api/feedback', methods=['GET'])
def get_feedback():
    """
    Retrieves all feedback entries from the database.
    """
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM feedbacks ORDER BY created_at DESC")
            feedbacks = cursor.fetchall()
        connection.close()
        return jsonify(feedbacks), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# API Endpoint to submit feedback
@application.route('/api/feedback', methods=['POST'])
def add_feedback():
    """
    Inserts a new feedback entry into the database.
    """
    data = request.json
    name = data.get('name')
    message = data.get('message')

    if not name or not message:
        return jsonify({'error': 'Name and message are required.'}), 400

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO feedbacks (name, message) VALUES (%s, %s)"
            cursor.execute(sql, (name, message))
        connection.commit()
        connection.close()
        return jsonify({'message': 'Feedback added successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the application when executed directly (Not used by EB, but good for local testing)
if __name__ == '__main__':
    if RDS_ENDPOINT:
        create_table_if_not_exists()
    application.run(host='0.0.0.0', port=80, debug=True)
