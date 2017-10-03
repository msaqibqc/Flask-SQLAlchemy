"""
File for creating a new user depending on the data required
"""


class Users:
    def __init__(self, id, username, session, password):
        """
        Constructor to initialize the user data
        :param str id: user_id
        :param str username: user name
        :param bool session: true or false
        :param str password: user's password
        """
        self.id = id
        self.session = session
        self.username = username
        self.password = password

    def get_data(self):
        """
        Returns the users's data
        :return: dictionary
        """
        return {
            "username": self.username,
            "session": self.session,
            "id": self.id
        }
