from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_cors import CORS
import os

# Initialize Flask app
app = Flask(__name__)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('EMAIL') 
app.config['MAIL_PASSWORD'] = os.getenv('PASSWORD') 
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

CORS(app, origins=["https://wedding-32ve.onrender.com/", "https://www.meekswedding.com"])

mail = Mail(app)

@app.route('/submit', methods=['POST', 'OPTIONS'])
def submit():
    form_data = request.get_json()

    if not all(key in form_data for key in ('name', 'phone', 'email', 'address')):
        return jsonify(message="Missing required field(s)"), 400

    print('Request received with the following data:')
    print(form_data)

    recipient_email = form_data['email']
    msg_to_recipient = Message(
        "Meeks Wedding - Save the Date",
        sender=app.config['MAIL_USERNAME'],
        recipients=[recipient_email]
    )

    msg_to_recipient.html = """
    <!DOCTYPE html>
    <html>
        <head>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    font-size: 14px;
                    line-height: 1.5;
                    color: black;
                }
                .bold {
                    font-weight: bold;
                }
                .section-title {
                    font-size: 20px;
                    font-weight: bold;
                    margin-top: 10px;
                }
                .date {
                    font-size: 20px;
                    margin-bottom: 15px;
                    font-weight: bold;
                }
                .address {
                    font-size: 14px;
                }

                p {
                    margin: 0;
                }
            </style>
        </head>
        <body>
            <p class="date">Madison and Bradley - May 1st, 2025</p>

            <p class="section-title"><span class="bold">Venue:</span></p>
            <p class="address"><span class="bold">Millennial Falls Event Center -</span> 12375 S 1300 E, Draper, UT 84020</p>

            <p class="section-title"><span class="bold">Hotels:</span></p>
            
            <p class="address"><span class="bold">Hampton Inn -</span> 13711 S 200 W, Draper, UT 84020</p>
            <p class="address"><span class="bold">HomeWood Suites by Hilton -</span> 437 W 13490 S, Draper, UT 84020</p>
            <p class="address"><span class="bold">Quality Inn -</span> 12033 S State Street, Draper, UT 84020</p>
        </body>
    </html>
    """

    admin_email = app.config['MAIL_USERNAME']
    msg_to_self = Message(
        "Meeks Wedding - Save the Date",
        sender=app.config['MAIL_USERNAME'],
        recipients=[admin_email]
    )
    msg_to_self.body = f"""
    New Save the Date Request:

    Name: {form_data['name']}
    Phone: {form_data['phone']}
    Email: {form_data['email']}
    Address: {form_data['address']}
    """

    try:
        mail.send(msg_to_recipient)

        mail.send(msg_to_self)

        return jsonify(message="Form submitted successfully! Emails have been sent."), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify(message=f"Error sending emails: {str(e)}"), 500

if __name__ == '__main__':
    app.run(debug=False)
