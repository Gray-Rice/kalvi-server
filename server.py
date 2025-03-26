from flask import Flask, request, jsonify, session
from ast import literal_eval

# User-defined modules
import modules.dbmanage as dbm
import modules.security as sec
import modules.utilities as util
from modules.utilities import apitools

uobj = dbm.users()

app = Flask(__name__)
print("Getting Secrets....")
secrets = sec.get_secrets()
if secrets is not None:
    app.secret_key = secrets["SECRET_KEY"]
else:
    print("Secrets Missing. Exiting.....")
    exit()

def validate_api_key(required_role):
    api_key = request.headers.get("X-API-KEY")
    if not api_key:
        return jsonify({"error": "Missing API Key"}), 401
    
    user_role = sec.check_token(api_key)
    if not user_role or user_role != required_role:
        return jsonify({"error": "Unauthorized"}), 403
    
    return user_role

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the API"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input format"}), 400
    
    username = data.get('username').strip()
    password = data.get('password').strip()
    valid = sec.verify_login(username, password)
    
    if valid[0]:
        user = valid[1]
        return jsonify({"role": user["role"], "token" : sec.get_token(user["id"]) })
    else:
        error = "Username does not exist" if valid[1] == "usr" else "Wrong password"
        return jsonify({"error": error}), 401


@app.route('/admin/users', methods=['GET'])
def admin_user():
    user_role = validate_api_key("admin")
    if isinstance(user_role, tuple):
        return user_role
    
    return jsonify({"users": uobj.get()})

@app.route('/add/user/', methods=["POST"])
def add_user():
    user_role = validate_api_key("admin")
    if isinstance(user_role, tuple):
        return user_role
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input format"}), 400
    
    user_data = [
        data.get('username').strip(),
        data.get('password').strip(),
        data.get('fullname').strip(),
        data.get('qualification').strip(),
        data.get('dob')
    ]
    
    if not util.valid_mail(user_data[0]):
        return jsonify({"error": "Username Error: Not a valid email"}), 400
    
    if any(i == "" for i in user_data):
        return jsonify({"error": "Input Error: Check if values entered are correct"}), 400
    
    if uobj.add(user_data):
        return jsonify({"message": "User added successfully"}), 201
    else:
        return jsonify({"error": f"Username {user_data[0]} already exists."}), 400

@app.route('/delete/user/', methods=["POST"])
def del_user():
    user_role = validate_api_key("admin")
    if isinstance(user_role, tuple):
        return user_role
    
    data = request.get_json()
    user_id = data.get("user_id")
    
    if uobj.remove(user_id):
        return jsonify({"message": "User removed"})
    else:
        return jsonify({"error": "Error occurred"}), 400

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"message": "Logout successful"})

if __name__ == '__main__':
    sec.start_checkup()
    app.run(host="0.0.0.0", debug=True)
