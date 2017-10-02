# """
#
# """
#
# from flask import request
# from flask_jwt_extended import  get_jwt_identity,jwt_required
#
# from flask_restful import  Resource
# from flask_mysql_app.settings import mysql
#
#
# class User(Resource):
#     def send_response(self, data, status_code):
#         return data, status_code
#
#     @jwt_required
#     def delete(self):
#         """
#         Authenticates the username in the database and if username is available in db then
#         deletes that user from database.
#         :return: response message to user
#         """
#         data = get_jwt_identity()
#         if not data['user']['session']:
#             data = {"Message": "Session expired"}
#             return self.send_response(data, 400)
#
#         data = request.json
#         user_id = data['id']
#         user_id = user_id.strip()
#         if user_id:
#             conn = mysql.get_db()
#             cursor = conn.cursor()
#             cursor.execute("SELECT * FROM User WHERE userId='" + user_id + "'")
#             data = cursor.fetchone()
#             if data is None:
#                 cursor.close()
#                 data = {'message: ': "User is not available in database with this id"}
#                 return self.send_response(data, 400)
#             else:
#                 cursor.execute("DELETE FROM User WHERE userId = '" + user_id + "'")
#                 conn.commit()
#                 cursor.close()
#                 data = {'message: ': "User removed successfully"}
#                 return self.send_response(data, 200)
#
#         data = {'message: ': "Only spaces are entered"}
#         return self.send_response(data, 400)
#
#     @jwt_required
#     def post(self):
#         """
#         Method to add the new user in the DB.
#         Fetches data from the form and then enters it in to DB  after connecting with DB.
#         :return: response to user accordingly
#         """
#         data = get_jwt_identity()
#         if not data['user']['session']:
#             data = {"Message": "Session expired"}
#             return self.send_response(data, 400)
#
#         if not request.json['username'] or not request.json['password'] or not request.json['email']:
#             data = {'message: ': "Some fields are missing"}
#             return self.send_response(data, 400)
#         else:
#             data = request.json
#             username = data['username']
#             password = data['password']
#             email = data['email']
#
#             conn = mysql.get_db()
#             cursor = conn.cursor()
#             cursor.execute("SELECT * from User WHERE username='%s" % username + "' OR email='%s" % email + "'")
#             data = cursor.fetchall()
#
#             if not data:
#                 cursor.execute("SELECT * from User")
#                 data = cursor.fetchall()
#                 id = data[-1][0] + 1
#                 query = "INSERT INTO User VALUES ( {id}, {username}, {password}, {email} )"
#                 query = query.format(id=str(id), username="'" + username + "'", password="'" + password
#                                                                                          + "'",
#                                      email="'" + email + "'")
#                 cursor.execute(query)
#                 conn.commit()
#                 cursor.close()
#                 data = {'id': id}
#                 return self.send_response(data, 201)
#             else:
#                 cursor.close()
#                 data = {'message: ': "Username or email already exist"}
#                 return self.send_response(data, 401)
#
#     @jwt_required
#     def get(self):
#         """
#         Gets all the user from the database and then display them in response
#         :return: response having all the user or invalid session message
#         """
#         data = get_jwt_identity()
#         if not data['user']['session']:
#             data = {"Message": "Session expired"}
#             return self.send_response(data, 400)
#
#         cursor = mysql.connect().cursor()
#         cursor.execute("SELECT * from User")
#         data = cursor.fetchall()
#         payload = []
#         for result in data:
#             content = {'id': result[0], 'username': result[1], 'password': result[2]}
#             payload.append(content)
#         cursor.close()
#         data = (payload)
#         return self.send_response(data, 200)
#
#     @jwt_required
#     def put(self):
#         """
#         Changes the password of the user and responds accordingly
#         :return: response msg to user
#         """
#         user_data = get_jwt_identity()
#         if not user_data['user']['session']:
#             data = {"Message": "Session expired"}
#             return self.send_response(data, 400)
#
#         data = request.json
#         old_password = data['old_password']
#         new_password = data['new_password']
#         user_id = user_data['user']['id']
#         old_password = old_password.strip()
#         new_password = new_password.strip()
#         if old_password and new_password:
#             conn = mysql.get_db()
#             cursor = conn.cursor()
#             cursor.execute("SELECT * FROM User WHERE userId='%d" % user_id + "' and password='%s" % old_password + "'")
#             data = cursor.fetchone()
#             if data is None:
#                 cursor.close()
#                 data = {'message: ': "Old password is not correct"}
#                 return self.send_response(data, 400)
#             else:
#                 cursor.execute("UPDATE User SET password='%s" % new_password + "' WHERE userId ='%d" % user_id + "'")
#                 conn.commit()
#                 cursor.execute(
#                     "UPDATE session SET is_active=%s" % 0 + ", token='%s" % 0 + "' WHERE userId ='%d" % user_id + "'")
#                 conn.commit()
#                 cursor.close()
#                 data = {'msg': "Password updated successfully"}
#                 return self.send_response(data, 200)
#         data = {'message: ': "Only spaces are entered"}
#         return self.send_response(data, 400)
