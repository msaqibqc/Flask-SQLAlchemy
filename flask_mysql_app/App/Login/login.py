#
#
# import datetime
# from flask import request
# from flask_jwt_extended import create_access_token
#
# from flask_restful import Resource
# from flask_mysql_app.users_data.Users import Users
# from flask_mysql_app.settings import mysql
#
# class UserLogin(Resource):
#     def send_response(self, data, status_code):
#         return data, status_code
#
#     def post(self):
#         """
#         Gets the credentials from the user and authenticates that the user is available in the DB.
#         And on availability of user in DB, logins the user.
#         :return: token and login status
#         """
#         data = request.json
#         username_or_email = data['username_or_email']
#         password = data['password']
#
#         cursor = mysql.connect().cursor()
#         query = "SELECT * from User WHERE  (email={username_or_email} " \
#                 "OR Username={username_or_email}) AND Password={password} "
#         query = query.format(username_or_email="'" + username_or_email + "'", password="'" + password + "'")
#         cursor.execute(query=query)
#         data = cursor.fetchone()
#         if data is not None:
#             expires = datetime.timedelta(days=365)
#             user = Users(data[0], username_or_email + "'", True, password)
#             conn = mysql.get_db()
#             cursor = conn.cursor()
#             device = "mobile"
#             cursor.execute("SELECT * from session where userId='%d" % user.id + "' and device ='%s" % device + "'")
#             response = cursor.fetchall()
#             if not response:
#                 cursor.execute("SELECT * from session")
#                 response = cursor.fetchall()
#                 id = response[-1][0] + 1
#                 access_token = create_access_token(identity={'user': user.get_data(),
#                                                              'session_id': id, 'device': device}, expires_delta=expires)
#                 query = "INSERT INTO Session VALUES ( {id}, {userId}, {device}, {token}, {is_active} )"
#                 query = query.format(id=str(id), userId="'" + str(user.id) + "'", device="'" + "mobile" + "'",
#                                      token="'" + access_token + "'", is_active=1)
#                 cursor.execute(query)
#                 conn.commit()
#                 cursor.close()
#                 data = {'access_token': access_token, 'status': 'User logged in'}
#                 return self.send_response(data, 200)
#             else:
#                 id = response[0][0]
#                 access_token = create_access_token(
#                     identity={'user': user.get_data(), 'session_id': id, 'device': device},
#                     expires_delta=expires)
#
#                 cursor.execute("UPDATE session SET is_active ='%d" % 1 + "', token='%s" % access_token +
#                                "' WHERE userId = %d;" % user.id)
#             conn.commit()
#             cursor.close()
#             data = {'access_token': access_token, 'status': 'User logged in'}
#             return self.send_response(data, 200)
#         else:
#             cursor.close()
#
#             data = {'message': 'Credentials are not correct'}
#             return self.send_response(data, 401)
#
