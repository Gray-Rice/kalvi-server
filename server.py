from flask import Flask, request, jsonify, session
from flask_cors import CORS 
from ast import literal_eval
import google.generativeai as genai



# User-defined modules
import modules.dbmanage as dbm
import modules.security as sec
import modules.utilities as util
from modules.utilities import apitools

uobj = dbm.users()


# Configure Gemini API
gem_key = sec.get_gemkey()
genai.configure(api_key=gem_key)  # Replace with your actual API key

app = Flask(__name__)
CORS(app, supports_credentials=True)

print("Getting Secrets....")
secrets = sec.get_secrets()
if secrets is not None:
    app.secret_key = secrets["SECRET_KEY"]
else:
    print("Secrets Missing. Exiting.....")
    exit()

#####################################

@app.route("/api/voice-assistant", methods=["POST"])
def voice_assistant():
    try:
        data = request.json
        user_query = data.get("user_query")
        current_page = data.get("current_page")
        site_structure = data.get("site_structure")

        prompt = f"""
        You are a study assistant for a university website.
        The user is currently on: {current_page}.
        Website structure: {site_structure}
        Provide study-related answers and website navigation help.
        User Query: "{user_query}"
        """

        # Use Gemini model
        model = genai.GenerativeModel("gemini-1.5-pro-latest")  # Try this model
        response = model.generate_content(prompt)

        return jsonify({"reply": response.text})

    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Sorry, there was an issue processing your request."}), 500

#####################################

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

############################################# Courses
@app.route("/get/course",methods=["GET"])
def get_cour():
    subjects = apitools.get_sub()
    if (subjects):
        return jsonify({"Courses": subjects}), 201
    return jsonify({"Error": "No subjects found"}), 204

############################################# Notice
@app.route("/add/notice",methods=["POST"])
def add_notice():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input format"}), 400
    event = [
        data.get('title').strip(),
        data.get('body').strip()
    ]
    if dbm.note_add(event):
        return jsonify({"message": "Notice added"}), 201
    else:
        return jsonify({"error": "Error occured"}), 400
    
@app.route("/get/notice",methods=["GET"])
def get_notice():
    return jsonify(get_notice()), 201

############################################# Course

@app.route("/admin/course", methods=["GET"])
def admin_course():
    """Retrieve all courses (Admin only)."""
    token = request.headers.get("X-API-KEY")
    if sec.check_token(token, "admin") == False:
        return jsonify({"Error": "Unauthorized - Invalid or No API Key Provided"}), 401

    return jsonify({"courses": course.get()}), 200


@app.route("/get/faculty",methods=["GET"])
def avail_fac():
    d = {}
    d["available"] = dbm.get_available_faculties()
    d["assigned"] = dbm.get_course_faculty_details()
    return jsonify(d), 200

############################################################ Course paths

@app.route("/add/course", methods=["POST"])
def add_course():
    """Add a new course (Admin only)."""
    token = request.headers.get("X-API-KEY")
    if sec.check_token(token, "admin") == False:
        return jsonify({"Error": "Unauthorized - Invalid or No API Key Provided"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input format"}), 400

    course_data = [
        data.get("code", "").strip(),
        data.get("course", "").strip(),
        data.get("description", "").strip()
    ]

    if not all(course_data):
        return jsonify({"error": "Missing required fields"}), 400

    if course.add(course_data):
        return jsonify({"message": f"Course '{course_data[1]}' added successfully"}), 201
    else:
        return jsonify({"error": f"Course '{course_data[1]}' already exists"}), 400

@app.route("/edit/course", methods=["POST"])
def edit_course():
    """Edit a course (Admin only)."""
    token = request.headers.get("X-API-KEY")
    if sec.check_token(token, "admin") == False:
        return jsonify({"Error": "Unauthorized - Invalid or No API Key Provided"}), 401

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input format"}), 400

    update_data = [
        data.get("course").strip(),
        data.get("description").strip(),
    ]

    if not all(update_data):
        return jsonify({"error": "Missing required fields"}), 400

    if course.update(update_data):
        return jsonify({"message": "Course updated successfully"}), 200
    else:
        return jsonify({"error": "Error occurred, try again"}), 400

@app.route("/delete/course", methods=["POST"])
def rm_course():
    """Delete a course (Admin only)."""
    token = request.headers.get("X-API-KEY")
    if sec.check_token(token, "admin") == False:
        return jsonify({"Error": "Unauthorized - Invalid or No API Key Provided"}), 401

    data = request.get_json()
    course_id = data.get("course_id")

    if not course_id:
        return jsonify({"error": "Missing course ID"}), 400

    if course.remove(course_id):
        return jsonify({"message": "Course deleted successfully"}), 200
    else:
        return jsonify({"error": "Error occurred, try again"}), 400


############################################# User Management

@app.route('/admin/users', methods=['GET'])
def admin_user():
    token = request.headers.get("X-API-KEY")
    if (sec.check_token(token,"admin") == False):
        return jsonify({"Error": "Unauthorized - Invalid or No API Key Provided"}), 401
    return jsonify({"users": uobj.get()})

@app.route('/add/user/', methods=["POST"])
def add_user():
    token = request.headers.get("X-API-KEY")
    if (sec.check_token(token,"admin") == False):
        return jsonify({"Error": "Unauthorized - Invalid or No API Key Provided"}), 401
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
    
    if uobj.add(user_data):
        usr = uobj.search(user_data[0])
        sec.create_token(usr["id"])
        return jsonify({"message": "User added successfully"}), 201
    else:
        return jsonify({"error": f"Username {user_data[0]} already exists."}), 400

@app.route('/delete/user/', methods=["POST"])
def del_user():
    token = request.headers.get("X-API-KEY")
    if (sec.check_token(token,"admin") == False):
        return jsonify({"Error": "Unauthorized - Invalid or No API Key Provided"}), 401
    data = request.get_json()
    user_id = data.get("user_id")
    
    if uobj.remove(user_id):
        return jsonify({"message": "User removed"})
    else:
        return jsonify({"error": "Error occurred"}), 400

app.route('/add/staff/', methods=["POST"])
def add_staff():
    token = request.headers.get("X-API-KEY")
    if (sec.check_token(token,"admin") == False):
        return jsonify({"Error": "Unauthorized - Invalid or No API Key Provided"}), 401
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
    
    if uobj.add(user_data,"staff"):
        return jsonify({"message": "User added successfully"}), 201
    else:
        return jsonify({"error": f"Username {user_data[0]} already exists."}), 400

@app.route('/delete/staff', methods=["POST"])
def del_staff():
    token = request.headers.get("X-API-KEY")
    if (sec.check_token(token,"admin") == False):
        return jsonify({"Error": "Unauthorized - Invalid or No API Key Provided"}), 401
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
