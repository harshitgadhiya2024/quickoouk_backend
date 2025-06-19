from operations.mongo_operation import mongoOperation
from operations.common_operations import commonOperation
from utils.constant import constant_dict
import os, json
from flask import (Flask, render_template, request, flash, session, send_file, jsonify, send_from_directory)
from flask_cors import CORS
from datetime import datetime, date
from utils.html_format import htmlOperation
from operations.mail_sending import emailOperation
import uuid
from werkzeug.utils import secure_filename, redirect

app = Flask(__name__)
CORS(app)

app.config["SECRET_KEY"] = constant_dict.get("secreat_key")
UPLOAD_FOLDER = 'static/uploads/'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Utility to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


client = mongoOperation().mongo_connect(get_mongourl=constant_dict.get("mongo_url"))

################################# user app api creation ##################################

#User creation in quickoo
@app.route("/quickoo/register-user", methods=["POST"])
def register_user():
    try:
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        phone_number = request.form.get("phone_number", "")
        company_name = request.form.get("company_name", "")
        gender = request.form.get("gender", "")
        password = request.form.get("password", "")

        get_all_user_data = mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "user_data")
        all_emails = [user_data["email"] for user_data in get_all_user_data]
        if email in all_emails:
            return commonOperation().get_error_msg("Email already registered...")

        get_all_user_data = mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "login_mapping")
        all_userids = [user_data["id"] for user_data in get_all_user_data]

        flag = True
        user_id = ""
        while flag:
            user_id = str(uuid.uuid4())
            if user_id not in all_userids:
                flag = False

        mapping_dict = {
            "user_id": user_id,
            "name": name,
            "email": email,
            "gender": gender,
            "phone_number": phone_number,
            "password": password,
            "company_name": company_name,
            "user_type": "user",
            "type": "email",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        login_mapping = {
            "user_id": user_id,
            "email": email,
            "password": password,
            "user_type": "user",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "user_data", mapping_dict)
        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "login_mapping", login_mapping)
        response_data_msg = commonOperation().get_success_response(200, {"user_id": user_id, "email": email})
        return response_data_msg

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in register user data route: {str(e)}")
        return response_data

# login process for user data
@app.route("/quickoo/login", methods=["POST"])
def login_user():
    try:
        email = request.form.get("email", "")
        password = request.form.get("password", "")

        get_all_user_data = mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "login_mapping", {"email": email, "password": password})
        if get_all_user_data:
            if get_all_user_data[0]["is_active"]:
                response_data_msg = commonOperation().get_success_response(200, {"user_id": get_all_user_data[0]["user_id"], "email": email})
            else:
                response_data_msg = commonOperation().get_error_msg("Your account disabled.. Please contact administration")
        else:
            response_data_msg = commonOperation().get_error_msg("Enter correct credentials")

        return response_data_msg

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in login user data route: {str(e)}")
        return response_data

@app.route("/quickoo/otp-email-verification", methods=["POST"])
def user_otp_email_verification():
    try:
        otp = request.form.get("otp", "")
        email = request.form.get("email", "")
        process = request.form.get("process", "")
        if process=="register":
            get_all_user_data = mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "user_data")
            all_emails = [user_data["email"] for user_data in get_all_user_data]
            if email in all_emails:
                return commonOperation().get_error_msg("Email already registered...")

        html_format = htmlOperation().otp_verification_process(otp)
        emailOperation().send_email(email, "Quickoo: Your Account Verification Code", html_format)
        response_data = commonOperation().get_success_response(200, {"message": "Mail sent successfully..."})
        return response_data

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again...")
        print(f"{datetime.now()}: Error in otp email verification: {str(e)}")
        return response_data

@app.route("/quickoo/forgot-password", methods=["POST"])
def user_forgot_password():
    try:
        email = request.form.get("email", "")
        otp = request.form.get("otp", "")
        email_condition_dict = {"email": email}
        email_data = mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "user_data", email_condition_dict)
        if email_data:
            if email_data[0]["is_active"]:
                html_format = htmlOperation().otp_verification_process(otp)
                emailOperation().send_email(email, "Quickoo: Your Account Verification Code", html_format)
                return commonOperation().get_success_response(200, {"message": "Otp sent successfully", "user_id": email_data[0]["user_id"]})
            else:
                return commonOperation().get_error_msg("Your account was disabled, Contact administration")
        else:
            response_data = commonOperation().get_error_msg("Account not exits..")
        return response_data

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again...")
        print(f"{datetime.now()}: Error in forgot password route: {str(e)}")
        return response_data

@app.route("/quickoo/change-password", methods=["POST"])
def change_password():
    try:
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        user_id = request.form.get("user_id")
        if password==confirm_password:
            mongoOperation().update_mongo_data(client, "quickoo_uk", "user_data", {"user_id":user_id}, {"password": password})
            mongoOperation().update_mongo_data(client, "quickoo_uk", "login_mapping", {"user_id":user_id}, {"password": password})
            return commonOperation().get_success_response(200, {"message": "Password updated"})
        else:
            return commonOperation().get_error_msg("Password doesn't match...")

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again...")
        print(f"{datetime.now()}: Error in change password route: {str(e)}")
        return response_data

@app.route("/quickoo/get-user-data", methods=["GET"])
def get_user_data():
    try:
        user_id = request.args.get("user_id", "")
        get_all_user_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "user_data", {"user_id": user_id}))
        response_data = get_all_user_data[0]
        del response_data["_id"]
        del response_data["created_at"]
        del response_data["updated_at"]
        response_data_msg = commonOperation().get_success_response(200, response_data)
        return response_data_msg

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in get user data route: {str(e)}")
        return response_data

@app.route("/quickoo/update-user-data", methods=["POST"])
def update_user_data():
    try:
        name = request.form.get("name")
        email = request.form.get("email", "")
        phone_number = request.form.get("phone_number", "")
        user_id = request.form.get("user_id", "")

        if name:
            mongoOperation().update_mongo_data(client, "quickoo_uk", "user_data", {"user_id":user_id}, {"name": name})
            return commonOperation().get_success_response(200, {"message": "Name updated successfully..."})
        elif email:
            get_all_user_data = mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "user_data")
            all_emails = [user_data["email"] for user_data in get_all_user_data]
            if email in all_emails:
                return commonOperation().get_error_msg("Email already registered...")
            mongoOperation().update_mongo_data(client, "quickoo_uk", "user_data", {"user_id":user_id}, {"email": email})
            mongoOperation().update_mongo_data(client, "quickoo_uk", "login_mapping", {"user_id":user_id}, {"email": email})
            return commonOperation().get_success_response(200, {"message": "Email updated successfully..."})
        elif phone_number:
            mongoOperation().update_mongo_data(client, "quickoo_uk", "user_data", {"user_id":user_id}, {"phone_number": phone_number, "is_phone": True})
            return commonOperation().get_success_response(200, {"message": "Phone number updated successfully..."})
        else:
            return commonOperation().get_error_msg("Something won't wrong!")

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again...")
        print(f"{datetime.now()}: Error in update user data route: {str(e)}")
        return response_data

@app.route("/quickoo/request-ride", methods=["POST"])
def request_ride():
    try:
        user_id = request.form.get("user_id", "")
        from_location = request.form.get("from", "")
        to_location = request.form.get("to", "")
        pickup_date = request.form.get("pickup_date", "")
        pickup_time = request.form.get("pickup_time", "")
        drop_points = request.form.get("drop_points", [])
        drop_points = json.loads(drop_points)
        person = request.form.get("person", "")
        vehicle_type = request.form.get("vehicle_type", "")
        if from_location.lower() == to_location.lower():
            response_data = commonOperation().get_error_msg("Pickup & Drop Point are same...")
        else:
            all_rides_data = list(mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "rides_data"))
            all_rideids = [ride_data["ride_id"] for ride_data in all_rides_data]

            flag = True
            ride_id = ""
            while flag:
                ride_id = str(uuid.uuid4())
                if ride_id not in all_rideids:
                    flag = False

            mapping_dict = {
                "user_id": user_id,
                "ride_id": ride_id,
                "driver_id": "",
                "vehicle_id": "",
                "from_location": from_location,
                "to_location": to_location,
                "pickup_date": pickup_date,
                "pickup_time": pickup_time,
                "drop_points": drop_points,
                "person": person,
                "vehicle_type": vehicle_type,
                "ride_status": "pending",
                "driver_status": "not_started",
                "is_completed": False,
                "created_on": datetime.utcnow(),
                "updated_on": datetime.utcnow()
            }

            mongoOperation().insert_data_from_coll(client, "quickoo_uk", "rides_data", mapping_dict)
            response_data = commonOperation().get_success_response(200, {"message": "Ride created successfully..."})

        return response_data
    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again...")
        print(f"{datetime.now()}: Error in create ride route: {str(e)}")
        return response_data

@app.route('/quickoo/get_past_rides', methods=['GET'])
def get_past_rides():
    try:
        user_id = request.args.get("user_id", "")
        ride_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "rides_data", {"user_id": user_id}))[::-1]
        rides_data = []
        for ride in ride_data:
            del ride["_id"]
            del ride["created_on"]
            del ride["updated_on"]
            rides_data.append(ride)
        return commonOperation().get_success_response(200, rides_data)

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in check get past rides for user: {str(e)}")
        return response_data

@app.route('/quickoo/get_spec_past_ride', methods=['GET'])
def get_spec_past_ride():
    try:
        ride_id = request.args.get("ride_id", "")
        user_id = request.args.get("user_id", "")
        ride_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "rides_data", {"ride_id": ride_id, "user_id": user_id}))
        ride_dict = ride_data[0]
        driver_id = ride_dict.get("driver_id")
        vehicle_id = ride_dict.get("vehicle_id")
        if driver_id:
            driver_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "driver_data", {"driver_id": driver_id}))
            driver_dict = driver_data[0]
            del driver_dict["_id"]
            del driver_dict["created_at"]
            del driver_dict["updated_at"]
        else:
            driver_dict = {}

        if vehicle_id:
            vehicle_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "vehicle_data", {"vehicle_id": vehicle_id}))
            vehicle_dict = vehicle_data[0]
            del vehicle_dict["_id"]
            del vehicle_dict["created_at"]
            del vehicle_dict["updated_at"]
        else:
            vehicle_dict = {}

        del ride_dict["_id"]
        del ride_dict["created_on"]
        del ride_dict["updated_on"]
        ride_dict["vehicle_data"] = vehicle_dict
        ride_dict["driver_data"] = driver_dict
        return commonOperation().get_success_response(200, ride_dict)

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in check get specific ride data for user: {str(e)}")
        return response_data

@app.route('/quickoo/user-dashboard', methods=['GET'])
def api_user_dashboard():
    try:
        user_id = request.args.get("user_id", "")
        past_rides = []
        ride_count = 0
        ride_data = list(mongoOperation().get_spec_data_from_coll(client, "quickoo_uk", "rides_data", {"user_id": user_id}))[::-1]
        for ride in ride_data[:3]:
            del ride["_id"]
            del ride["created_on"]
            del ride["updated_on"]
            past_rides.append(ride)
            ride_count+=1

        ride_dict = {
            "user_id": user_id,
            "ride_count": len(ride_data),
            "past_rides": past_rides
        }

        return commonOperation().get_success_response(200, ride_dict)

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in check get dashboard data for user: {str(e)}")
        return response_data

@app.route('/quickoo/create-complaint', methods=['POST'])
def create_complaint():
    try:
        user_id = request.form.get("user_id", "")
        driver_id = request.form.get("driver_id", "")
        ride_id = request.form.get("ride_id", "")
        complaint_text = request.form.get("complaint_text", "")
        type = request.form.get("type", "user")

        get_all_complaint_data = mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "complaint_data")
        all_complaintids = [complaint_data["complaint_id"] for complaint_data in get_all_complaint_data]

        flag = True
        complaint_id = ""
        while flag:
            complaint_id = str(uuid.uuid4())
            if complaint_id not in all_complaintids:
                flag = False

        mapping_dict = {
            "complaint_id": complaint_id,
            "user_id": user_id,
            "driver_id": driver_id,
            "ride_id": ride_id,
            "complaint_text": complaint_text,
            "who_complaint": type,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "complaint_data", mapping_dict=mapping_dict)
        return commonOperation().get_success_response(200, {"message": "Complaint created successfully"})

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in check create complaint: {str(e)}")
        return response_data

@app.route('/quickoo/create-ticket', methods=['POST'])
def create_ticket():
    try:
        user_id = request.form.get("user_id", "")
        ticket_text = request.form.get("ticket_text", "")

        get_all_ticket_data = mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "ticket_data")
        all_ticketids = [ticket_data["ticket_id"] for ticket_data in get_all_ticket_data]

        flag = True
        ticket_id = ""
        while flag:
            ticket_id = str(uuid.uuid4())
            if ticket_id not in all_ticketids:
                flag = False

        mapping_dict = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "ticket_text": ticket_text,
            "type": "user",
            "status": "activate",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "ticket_data", mapping_dict=mapping_dict)
        return commonOperation().get_success_response(200, {"message": "Ticket created successfully"})

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in check create ticket: {str(e)}")
        return response_data

@app.route('/quickoo/delete-account', methods=['POST'])
def delete_account():
    try:
        user_id = request.args.get("user_id", "")
        mongoOperation().delete_data_from_coll(client, "quickoo_uk", "user_data", {"user_id": user_id})
        mongoOperation().delete_data_from_coll(client, "quickoo_uk", "rides_data", {"user_id": user_id})
        mongoOperation().delete_data_from_coll(client, "quickoo_uk", "login_mapping", {"user_id": user_id})
        mongoOperation().delete_data_from_coll(client, "quickoo_uk", "complaint_data", {"user_id": user_id})
        mongoOperation().delete_data_from_coll(client, "quickoo_uk", "ticket_data", {"user_id": user_id})
        return commonOperation().get_success_response(200, {"message": "Account delete successfully"})

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in delete account: {str(e)}")
        return response_data


################################## driver application backend #####################################
@app.route("/quickoo/register-driver", methods=["POST"])
def register_driver():
    try:
        name = request.form["name"]
        email = request.form["email"]
        phone_number = request.form["phone_number"]
        gender = request.form["gender"]
        password = request.form["password"]

        get_all_driver_data = mongoOperation().get_all_data_from_coll(client, "quickoo_uk", "login_mapping")
        all_ids = [driver_data["id"] for driver_data in get_all_driver_data]

        flag = True
        user_id = ""
        while flag:
            user_id = str(uuid.uuid4())
            if user_id not in all_ids:
                flag = False

        mapping_dict = {
            "id": user_id,
            "name": name,
            "gender": gender,
            "email": email,
            "phone_number": phone_number,
            "password": password,
            "vehicle_details": {},
            "payment_details": {},
            "user_type": "driver",
            "type": "email",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        login_mapping = {
            "id": user_id,
            "email": email,
            "password": password,
            "user_type": "driver",
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "driver_data", mapping_dict)
        mongoOperation().insert_data_from_coll(client, "quickoo_uk", "login_mapping", login_mapping)
        response_data_msg = commonOperation().get_success_response(200, {"user_id": user_id, "name": name, "email": email})
        return response_data_msg

    except Exception as e:
        response_data = commonOperation().get_error_msg("Please try again..")
        print(f"{datetime.utcnow()}: Error in register driver data route: {str(e)}")
        return response_data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7040)
