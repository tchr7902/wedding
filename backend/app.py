from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from flask_cors import CORS
import os
import boto3
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv('../../.env')

app = Flask(__name__)
CORS(app)

api_key = os.getenv('API_KEY')
DB_CONFIG = {
    "host": os.getenv('DB_HOST'),
    "user": os.getenv('DB_USER'),
    "password": os.getenv('DB_PASS'),
    "database": os.getenv('DB_NAME'),
}

# Debugging the environment variables to confirm they are loaded correctly
print("AWS Access Key ID:", os.getenv('ACCESS_KEY_ID'))
print("AWS Secret Access Key:", os.getenv('SECRET_ACCESS_KEY'))
print("AWS Region:", os.getenv('AWS_DEFAULT_REGION'))

# Initialize AWS SNS Client
sns_client = boto3.client('sns', 
                          aws_access_key_id=os.getenv('ACCESS_KEY_ID'), 
                          aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'),
                          region_name='us-east-1')

def send_sms_via_aws(phone_number, message_body):
    """
    Send SMS via AWS SNS.
    :param phone_number: Phone number in international format (e.g., +18551234567).
    :param message_body: Message content to send.
    """
    try:
        response = sns_client.publish(
            PhoneNumber=phone_number,
            Message=message_body,
            MessageType='Transactional'  # 'Promotional' is another option.
        )
        print(f"SMS sent! Message ID: {response['MessageId']}")
        return True
    except ClientError as e:
        print(f"Error sending SMS: {e}")
        # Print more error details for debugging
        print(f"Error details: {e.response['Error']}")
        return False

@app.route('/submit', methods=['POST'])
def submit_form():
    """
    Handle form submission and save data to database.
    """
    data = request.json
    name = data.get('name')
    phone_number = data.get('phone')
    email_address = data.get('email')
    address = data.get('address')

    try:
        print(f'Received: {data}')

        #connection = mysql.connector.connect(**DB_CONFIG)
        # cursor = connection.cursor()
        # Uncomment to insert into your database
        # cursor.execute(
        #     "INSERT INTO contacts (name, phone_number, address, email_address) VALUES (%s, %s, %s, %s)",
        #     (name, phone_number, address, email_address)
        # )
        # connection.commit()

        sms_message = f"Hello {name}! Thank you for your submission."
        
        # Send SMS via AWS SNS
        if send_sms_via_aws(phone_number, sms_message):
            print(f"SMS sent to {phone_number}")
        else:
            print(f"Failed to send SMS to {phone_number}")

        return jsonify({"message": "Success!"}), 200
    except Error as e:
        return jsonify({"message": f"Database Error: {e}"}), 500
    except Exception as ex:
        return jsonify({"message": f"Unexpected Error: {ex}"}), 500
    finally:
 #       if 'connection' in locals() and connection.is_connected():
 #           cursor.close()
 #           connection.close()
        print('worked')

if __name__ == '__main__':
    app.run(debug=True)
