import sqlite3
from datetime import date
import hashlib

def hashpwd(password): 
    return hashlib.sha256(password.encode()).hexdigest()

def get_role(username):
    with sqlite3.connect("data/instance.db") as con:
        cur = con.cursor()
        cur.execute("SELECT role FROM Users WHERE username = ?",(username,))
        user = cur.fetchone()
        if(user != None):
            return user[0]


import sqlite3

def get_available_faculties():
    with sqlite3.connect("data/instance.db") as conn:
        query = """
        SELECT id, username, fullname, qualification, dob
        FROM Users
        WHERE role = 'staff' 
        AND id NOT IN (SELECT fac_id FROM Coursefac);
        """
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return [{"id": row[0], "username": row[1], "fullname": row[2], "qualification": row[3], "dob": row[4]} for row in result]

def get_course_faculty_details():
    with sqlite3.connect("data/instance.db") as conn:
        query = """
        SELECT c.course_id, c.fac_id, u.username, u.fullname, c.slot
        FROM Coursefac c
        JOIN Users u ON c.fac_id = u.id;
        """
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        return [{"course_id": row[0], "fac_id": row[1], "username": row[2], "fullname": row[3], "slot": row[4]} for row in result]



class users():
    def add(self,user,role="student"):
        with sqlite3.connect("data/instance.db") as con:
            try:
                user[0] = user[0].strip()
                user[1] = hashpwd(user[1].strip())
                cur = con.cursor()
                cur.execute(f'''INSERT INTO Users (username, password, fullname, qualification, dob, role) VALUES (?,?,?,?,?,?)''',user+[role])
                con.commit()
                print("Added User: "+user[0])
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

    def get(self,username=None):
        with sqlite3.connect("data/instance.db") as con:
                cur = con.cursor()
                if(username == None):
                    cur.execute(f'''SELECT id,username,fullname,qualification,dob from Users''')
                    users = cur.fetchall()
                    users.pop(0)
                else:
                    cur.execute(f"SELECT id,username,fullname,qualification,dob from Users WHERE username = ?",(username,))
                    users = cur.fetchone()
                return users
    def username(self,user_id):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT username from Users WHERE id = ?''',(user_id,))
            user = cur.fetchone()
            return user[0]

    @staticmethod
    def search(username=None,id=None):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            if(username not in (None,"")):
                cur.execute("SELECT id, username, password, fullname, qualification, dob, role FROM Users WHERE username = ?",(username,))
            elif(id != None):
                cur.execute("SELECT id, username, password, fullname, qualification, dob, role FROM Users WHERE id = ?",(id,))
            user = cur.fetchone()
            if user:
                print(f"User found: ID={user[0]}, Username={user[1]}")
                return {"id": user[0],"username": user[1],"pwd":user[2],"fname":user[3],"qual":user[4],"dob":user[5],"role": user[6] }
            else:
                print("User not found.")
                return None

    def remove(self,user_id):
        if user_id == 0:
                print("Cannot delete the admin user!")
                return
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute("DELETE FROM Users WHERE id = ?", (user_id,))
                con.commit()
                print(f"User deleted successfully.")
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

class course:
    def add(self,sub_data):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute(f'''INSERT INTO Courses (code,name, description) VALUES (?,?,?)''',sub_data)
                con.commit()
                print("Added Subject: "+sub_data[1])
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

    def get(self):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT * from Courses''')
            subjects = cur.fetchall()
            return subjects

    def name(self,id):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            cur.execute(f'''SELECT name from Courses WHERE id = ?''',(id,))
            subject = cur.fetchone()
            return subject[0]

    def remove(self,cur_id):
        with sqlite3.connect("data/instance.db") as con:
            try:
                cur = con.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")
                cur.execute("DELETE FROM Courses WHERE id = ?", (cur_id,))
                con.commit()
                print(f"Subject '{cur_id}' deleted successfully.")
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False
    
    def update(self,up_data):
        with sqlite3.connect("data/instance.db") as con:
            cur = con.cursor()
            try:
                con.execute("UPDATE Courses SET name = ?, description = ? WHERE id = ?",up_data)
                con.commit()
                return True
            except Exception as e:
                print("Exception : "+str(e))
                return False

def add_notice(data):
    with sqlite3.connect("data/instance.db") as con:
        try:
            cur = con.cursor()
            cur.execute(f'''INSERT INTO Notice (title,body) VALUES (?,?)''',data)
            con.commit()
            print("Added Notice: "+sub_data[1])
            return True
        except Exception as e:
            print("Exception : "+str(e))
            return False

def get_notice():
    with sqlite3.connect("data/instance.db") as con:
        cur = con.cursor()
        cur.execute(f'''SELECT * from Notice''')
        subjects = cur.fetchall()
        return notices