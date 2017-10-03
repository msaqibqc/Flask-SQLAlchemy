#
#
# from flask_jwt_extended import get_jwt_identity, jwt_required
# from flask_restful import Resource
# from flask_mysql_app.settings import mysql
#
#
# class UserLogout(Resource):
#     def send_response(self, data, status_code):
#         return data, status_code
#
#     @jwt_required
#     def delete(self):
#         """
#         Logout the user and expired the session and update the session in DB
#         :return: response msg to user
#         """
#         data = get_jwt_identity()
#         if not data['user']['session']:
#             data = {"Message": "Session expired"}
#             return self.send_response(data, 400)
#
#         get_jwt_identity()['user']['session'] = False
#         user_id = data['user']['id']
#         session_id = data['session_id']
#         device = data['device']
#         conn = mysql.get_db()
#         cursor = conn.cursor()
#
#         cursor.execute("UPDATE session SET is_active=%s" % 0 + " WHERE userId = '%d" % user_id +
#                        "' AND sessionId='%d" % session_id + "' AND device='%s" % device + "'")
#         conn.commit()
#         cursor.close()
#         data = {"msg": "Successfully logged out"}
#         return self.send_response(data, 200)
#
