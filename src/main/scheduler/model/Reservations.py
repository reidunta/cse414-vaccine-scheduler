import sys
sys.path.append("../db/*")
from db.ConnectionManager import ConnectionManager
import pymssql

class Reservations:
    def __init__(self, patient_username, caregiver_username, time, vaccine_name, id):
        self.patient_username = patient_username
        self.caregiver_username = caregiver_username
        self.time = time
        self.vaccine_name = vaccine_name
        self.id = id

    #getters
    def get(self):
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        get_reservation = "SELECT PatientUsername, caregiverUsername, Time, VaccineName FROM Availabilities WHERE Id = %s"
        try:
            cursor.execute(get_reservation, self.id)
            for row in cursor:
                self.patient_username = row[1]
                self.caregiver_username = row[2]
                self.time = row[3]
                self.vaccine_name = row[4]
                return self
        except pymssql.Error:
            raise
        finally:
            cm.close_connection()
        return None
    
    def get_patient_username(self):
        return self.patient_username
    
    def get_caregiver_username(self):
        return self.caregiver_username
    
    def get_time(self):
        return self.time
    
    def get_vaccine_name(self):
        return self.vaccine_name
    
    def get_id(self):
        return self.id
    
    def save_to_db(self):
        if self.patient_username is None or self.caregiver_username is None or self.time is None or self.vaccine_name is None or self.id is None:
            raise ValueError("Argument cannot be empty!")

        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor()

        add_reservation = "INSERT INTO Reservations VALUES (%s, %s, %s, %s, %s)"
        try:
            cursor.execute(add_reservation, (self.patient_username, self.caregiver_username, self.time, self.vaccine_name, self.id))
            # you must call commit() to persist your data if you don't set autocommit to True
            conn.commit()
        except pymssql.Error:
            # print("Error occurred when insert Vaccines")
            raise
        finally:
            cm.close_connection()

