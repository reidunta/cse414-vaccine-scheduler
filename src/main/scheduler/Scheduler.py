from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from model.Reservations import Reservations
from model.Availabilities import Availabilities
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import random


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None
current_caregiver = None

def create_patient(tokens):
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Create patient failed")
        return
    
    # idk if this is needed
    if current_caregiver != None or current_patient != None:
        print("Please sign out before creating a new user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again.")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Create patient failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Create patient failed")
        print(e)
        return
    print("Created user ", username)

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False


def login_patient(tokens):
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient, current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in, try again")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login patient failed")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login patient failed")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login patient failed")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login patient failed")
    else:
        print("Logged in as " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    if current_caregiver is None and current_patient is None:
        print("Please login first")
        return

    if len(tokens) != 2:
        print("Please try again")
        return

    date = tokens[1]

    try:
        date_tokens = date.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
        try:
            d = datetime.date(year, month, day)
        except ValueError:
            print("Please try again")
    except:
        print("Invalid date. Please try again")

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    get_availabilities = "SELECT * FROM Availabilities WHERE Time = %s ORDER BY Username"
    try:
        cursor.execute(get_availabilities, d)
        for row in cursor:
            print(row[1])
    except pymssql.Error:
        print("Please try again")
        cm.close_connection()
        return
    
    get_vaccines = "SELECT * FROM Vaccines"
    try:
        cursor.execute(get_vaccines)
        for row in cursor:
            print(f"{row[0]} {row[1]}")
    except pymssql.Error:
        print("Please try again")
    finally:
        cm.close_connection()


def reserve(tokens):
    if current_patient is None:
        print("Please login first")
        return
    
    if current_caregiver is not None:
        print("Please login as a patient")
    
    if len(tokens) != 3:
        print("Please try again")
        return
    
    date = tokens[1]
    vaccine = tokens[2]

    # assume input is hyphenated in the format mm-dd-yyyy
    try:
        date_tokens = date.split("-")
        month = int(date_tokens[0])
        day = int(date_tokens[1])
        year = int(date_tokens[2])
        try:
            d = datetime.date(year, month, day)
        except ValueError:
            print("Please try again")
    except:
        print("Invalid date. Please try again")

    caregiver = None
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    doses = -1;

    get_vaccines = "SELECT Doses FROM Vaccines WHERE Name = %s"
    try:
        cursor.execute(get_vaccines, vaccine)
        cursor_list = list(cursor)
        if len(cursor_list) == 0:
            print("Not enough available doses")
        doses_tuple = cursor_list[0]
        doses = doses_tuple[0]
    except pymssql.Error:
            print("Please try again")
            return
    except pymssql.Error:
        print("Please try again")
        cm.close_connection()
        return

    get_caregivers = "SELECT Username FROM Availabilities WHERE Time = %s ORDER BY Username"
    try:
        cursor.execute(get_caregivers, d)
        cursor_list = list(cursor)
        if len(cursor_list) == 0:
            print("No caregiver is available")
            return
        else:
            caregiver_tuple = cursor_list[0]
            caregiver = caregiver_tuple[0]
    except pymssql.Error:
        print("Please try again")
        cm.close_connection()
        return
    finally:
        cm.close_connection()

    random_id = random.randint(0,999)  # Add a random id, just in case
    appointment_id = f"{caregiver}-{date}-{random_id}"

    # create the reservation
    reservation = Reservations(current_patient.get_username(), caregiver, d, vaccine, appointment_id)

    # save reservation information to our database
    try:
        reservation.save_to_db()
    except pymssql.Error as e:
        print("Please try again")
        return
    except Exception as e:
        print(e)
        print("Please try again")
        return
    print(f"Appointment ID {appointment_id}, Caregiver username {caregiver}")

    #remove availability
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()
    remove_availability = "DELETE FROM Availabilities WHERE Time = %d AND Username = %s"
    try:
        cursor.execute(remove_availability, (d, caregiver))
        conn.commit()
    except pymssql.Error:
        print("Please try again")
        cm.close_connection()
        return

    #remove vaccine dose
    vaccine = Vaccine(vaccine, doses)
    vaccine.decrease_available_doses(1)


def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.date(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):

    if len(tokens) != 2:
        print("Please try again")
        return
    appointment_id = tokens[1]

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    if current_patient is not None or current_caregiver is not None:
         remove_reservation = "DELETE FROM Reservations WHERE Id = %s"
         try:
            cursor.execute(remove_reservation, appointment_id)
            conn.commit()
            print("Your appointment has been cancelled")
         except pymssql.Error:
            print("Please try again")
            cm.close_connection()
            return
         finally:
            cm.close_connection()
    else:
        print("Please login first")




def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):

    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor()

    if current_caregiver is not None:

        appointment_id = None
        vaccine_name = None
        date = None
        patient = None

        get_appointments = "SELECT Id, VaccineName, Time, PatientUsername FROM Reservations WHERE CaregiverUsername = %s"
        try:
            cursor.execute(get_appointments, current_caregiver.get_username())
            cursor_list = list(cursor)
            if len(cursor_list) == 0:
                print("No current appointments!")
            else:
                for appointment_id, vaccine_name, date, patient in cursor_list:
                    print(f"{appointment_id} {vaccine_name} {date} {patient}")
        except pymssql.Error:
            print("Please try again")
            cm.close_connection()
            return
        finally:
            cm.close_connection()

    elif current_patient is not None:

        appointment_id = None
        vaccine_name = None
        date = None
        caregiver = None

        get_appointments = "SELECT Id, VaccineName, Time, CaregiverUsername FROM Reservations WHERE PatientUsername = %s"
        try:
            cursor.execute(get_appointments, current_patient.get_username())
            cursor_list = list(cursor)
            if len(cursor_list) == 0:
                print("No current appointments!")
            else:
                for appointment_id, vaccine_name, date, caregiver in cursor_list:
                    print(f"{appointment_id} {vaccine_name} {date} {caregiver}")
        except pymssql.Error:
            print("Please try again")
            cm.close_connection()
            return
        finally:
            cm.close_connection()

    else:
        print("Please login first")
        return




def logout(tokens):
    global current_caregiver, current_patient
    if current_caregiver is not None:
        print("Successfully logged out")
        current_caregiver = None
    elif current_patient is not None:
        print("Successfully logged out")
        current_patient = None
    elif current_patient is None and current_caregiver is None:
        print("Nobody is logged in!")
    else:
        print("Please try again")


def start():
    stop = False
    while not stop:
        print()
        print(" *** Please enter one of the following commands *** ")
        print("> create_patient <username> <password>")  
        print("> create_caregiver <username> <password>")
        print("> login_patient <username> <password>") 
        print("> login_caregiver <username> <password>")
        print("> search_caregiver_schedule <date>")  
        print("> reserve <date> <vaccine>")  
        print("> upload_availability <date>")
        print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
        print("> add_doses <vaccine> <number>")
        print("> show_appointments") 
        print("> logout")
        print("> Quit")
        print()
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break

        response = response.lower()
        tokens = response.split(" ")
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
