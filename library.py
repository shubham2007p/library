import datetime

import mysql.connector as m
import datetime as dt
import random


db = m.connect(user="root", host="localhost", password="system@2007", database="library")
db_cursor = db.cursor()

members = {
    "M1": ["Aryan", "aryan123"],
    "M2": ["Neha", "neha456"],
    "M3": ["Rahul", "rahul789"],
    "M4": ["Priya", "priya012"],
    "M5": ["Rohan", "rohan345"],
    "M6": ["Aisha", "aisha678"],
    "M7": ["Nikhil", "nikhil901"],
    "M8": ["Riya", "riya234"],
    "M9": ["Siddharth", "siddharth567"],
    "M10": ["Ananya", "ananya890"]
}


empty = () # why tuple not some other
def search():
    book_name = input("Enter the book name")
    try:
        if True:
            db_cursor.execute("select * from book_inventory where lower(book_name) = lower(%s) ;",(book_name, )) #%s ( ,) lower()
            i = db_cursor.fetchall() #why fetch all
            if i :
                db_cursor.execute("select * from book_inventory where lower(book_name) = lower(%s) and availability = TRUE ;",(book_name,))
                j = db_cursor.fetchone()  # why fetch all
                if j != empty:
                    print("book is available ")
                    choice = input(f"Want to Issue {book_name} ? ")
                    if choice in "yY":
                        issue_book()
                    else:
                        menu()
                else:
                    print("Book is issued by someone else for now")
            else:
                print("Book isn't in library")
            choice= input(f"Want to add this book :  {book_name} to Library ? ")
            if choice in "yY":
                add_book(book_name)
            else:
                menu()
    except Exception as err:
        print(err)

def issue_book():
    book_name = input("Enter the book name")
    try:
        db_cursor.execute("select * from book_inventory where lower(book_name) = lower(%s) and availability = TRUE ;",(book_name, ))
        book_details = db_cursor.fetchone()

        # Check if book_details is not None before accessing elements
        if book_details:
            try:
                member_id = input("enter your member_id : ")
                pass_key = input("enter your password : ")
                if member_id in members.keys() :
                    if  members[member_id][1] == pass_key :

                        issued_date = dt.datetime.now()
                        returning_date = issued_date + dt.timedelta(days=7)
                        db_cursor.execute(
                            "update book_inventory set availability = FALSE , issued_date = %s  , return_date = %s where book_ID = %s ;",
                            (str(issued_date), str(returning_date), book_details[0],))
                        db.commit()
                        print("BOOK ISSUED SUCCESSFULY")
                        print(f"Your {book_name} book_ID is {book_details[0]} and returning_date {returning_date}")
                        db_cursor.execute(
                            "INSERT INTO issued_books_records VALUES (%s, %s, %s, %s, %s)",
                            (book_details[0], member_id, members[member_id][0] , str(issued_date), str(returning_date))
                        )
                        db.commit()
                else:
                    print("Your member_id or password is incorrect")
            except Exception as err:
                print(err)
        else:
            print("Book is not available or issued by someone else")

    except Exception as err:
        print(err)

def return_book():
    book_ID = input("Enter the book_ID : ")

    # Query the database to get the issued time
    db_cursor.execute("SELECT issued_date FROM book_inventory WHERE book_ID = %s", (book_ID,))
    issued_date = db_cursor.fetchone()[0]  # Get the issued_date value

    if issued_date:
        # Convert issued_date to datetime if it's a date (assuming issued_date is stored as date in the database)
        if isinstance(issued_date, dt.date):
            issued_time = dt.datetime.combine(issued_date, dt.time.min)  # Combine with minimum time
        else:
            issued_time = issued_date  # Already a datetime

        returning_time = dt.datetime.now()
        book_period = returning_time - issued_time

        # Check for overdue considering only days (assuming no fine for hours)
        overdue_days = max(book_period.days, 0)  # Ensure non-negative overdue days
        total_bill = overdue_days * 10

        if overdue_days > 0:
            print(f"You have overdue your book by {overdue_days} day(s) and owe a fine of ₹ {total_bill}")
        else:
            print("Thank you for returning book on time , we appreciate your effort")

        # Update book_inventory regardless of overdue status
        db_cursor.execute("update book_inventory set availability = TRUE , issued_date = null  , return_date = %s where book_ID = %s ;", (returning_time, book_ID,))
        db.commit()
    else:
        print("Book not found in issued records")



def add_book():
    book_name = input("Enter the book name")
    book_ID = book_name[0] + random.randint(10000, 99999)
    db_cursor.execute("INSERT INTO book_inventory (book_name  , book_ID , availability ) VALUES (%s,%s,1);",(book_name, book_ID))
    print("Added successfuly")
    db.commit()

def view_records():
    db_cursor.execute("describe issued_books_records")
    columns = []
    for row in db_cursor.fetchall():
        columns.append(row[0])  # list form headings
    # Fetch the table data
    db_cursor.execute("SELECT * FROM issued_books_records")
    rows = db_cursor.fetchall()  # list-tuple form data


    print("-" * 23 * len(columns))
    # printing headers
    for c in columns:
        print(f"{c :^20}", end=" | ")
    print(" ")

    print("-" * 23 * len(columns))

    # printing rows
    for row in rows:
        for data in row:
            if isinstance(data, datetime.date):  # Check if 'data' is a date object
                # Format date as 'YYYY-MM-DD'
                print(f"{data.strftime('%Y-%m-%d'):^20}", end=" | ")
            else:
                # Handle non-date data normally
                print(f"{str(data):^20}", end=" | ")
        print(" ")

    print("-" * 23 * len(columns))

def book_status():
    db_cursor.execute("describe book_inventory")
    columns = []
    for row in db_cursor.fetchall():
        columns.append(row[0])  # list form headings
    # Fetch the table data
    db_cursor.execute("SELECT * FROM book_inventory")
    rows = db_cursor.fetchall()  # list-tuple form data

    print("-" * 43 * len(columns))
    # printing headers
    for c in columns:
        print(f"{c :^40}", end=" | ")
    print(" ")

    print("-" * 43 * len(columns))

    # printing rows
    for row in rows:
        for data in row:
            if isinstance(data, datetime.date):  # Check if 'data' is a date object
                # Format date as 'YYYY-MM-DD'
                print(f"{data.strftime('%Y-%m-%d'):^40}", end=" | ")
            else:
                # Handle non-date data normally
                print(f"{str(data):^40}", end=" | ")
        print(" ")

    print("-" * 43 * len(columns))
def add_member ():
    member_id = input("make a member_id : ")
    member_name = input("name of member : ")
    member_pass = input("set a password : ")
    members[member_id] = [member_name , member_pass]
    print("member added")
    print(f"hello {member_name} , i hpoe u would like to read from this library . A most heartly welcome to this library")

def remove_member ():
    member_id = input("give member_id : ")
    sure = input("are u sure u wan to remove (yY) : ")
    if sure in "yY":
        del members[member_id]
        print("member removed")

def view_members ():
    print("MEMBER NAME")
    for i in members.values() :
        print(i[0])

    print("cant print member_id or pass for security reasons")

def update_member():
    member_id = input("enter your member id  : ")
    change = input("what u want to change (name) or (password) : ")
    if change == "name":
        name = input("enter the new name : ")
        members[member_id][0] = name
    elif change == "password":
        password = input("enter new password")
        members[member_id][1] = password
    else :
        print("wrong option , enter (name) or (password)")

def menu():
    while True:
        try:
            print("1. Search for a book\n"
                  "2. Issue a book\n"
                  "3. Return a book \n"
                  "4. Add a book\n"
                  "5. View all issued book records \n"
                  "6. View all library book status \n"
                  "7. Add a member \n"
                  "8. Remove a member \n"
                  "9. Update a Member \n"
                  "10. View all members \n"
                  "11. Exit")

            func_list = [search, issue_book, return_book, add_book ,view_records , book_status , add_member , remove_member ,update_member, view_members , exit]
            choice = int(input("Enter your choice : ")) - 1
            func_list[choice]()
        except Exception as err:
            print(err)
menu()
