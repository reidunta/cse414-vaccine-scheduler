import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql

class Availabilities:
    def __init__(self, time, username):
        self.username = username
        self.time = time

    #getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_availability = "SELECT Username, Time FROM Availabilities WHERE Username = %s AND Time = %s"
        try:
            cursor.execute(get_availability, self.username)
            for row in cursor:
                self.time = row[1]
                return self
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
        return None
    
    def get_username(self):
        return self.username
    
    def get_time(self):
        return self.time
    
    def save_to_db(self):
        if self.username is None or self.time is None:
            raise ValueError("Argument cannot be empty!")

        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s, %s)"
        try:
            cursor.execute(add_availability, (self.username, self.time))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when insert Vaccines")
            raise
        finally:
            cm.close_connection()

    def remove_availability(self, time, username):
        if self.username is None or self.time is None:
            raise ValueError("Argument cannot be empty!")

        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_availability = "INSERT INTO Availabilities VALUES (%s, %s)"
        try:
            cursor.execute(add_availability, (self.username, self.time))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when insert Vaccines")
            raise
        finally:
            cm.close_connection()
