## IMPORTS ##
from flask import Flask, render_template, json, redirect
from flask_mysqldb import MySQL
from flask import request
import os 
## IMPORTS ##


## DATABASE CONECTION AND CONFIG ##
app = Flask(__name__)
app.config["MYSQL_HOST"] = "classmysql.engr.oregonstate.edu"
app.config["MYSQL_USER"] = "cs340_davisg4"
app.config["MYSQL_PASSWORD"] = "8778"
app.config["MYSQL_DB"] = "cs340_davisg4"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)
## DATABASE CONECTION AND CONFIG ##


#       Table of contents because this is one hefty file     #
#                                                            #
#       Page                                line #           #
#                                                            #
#       Root / Home  .....................  42               #
#       Authors  .........................  56               #
#       Books  ...........................  110              #
#       Employees  .......................  211              #
#       Genres  ..........................  267              #
#       Members  .........................  318              #
#       Orders  ..........................  385              #
#                                                            #
#                                                            #


# INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # INIT # 
###########################################################################################################################################################
# HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # 


@app.route('/')
def root():
    return redirect("/home")
@app.route('/home')
def home():
    return render_template('home.j2')


# HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # HOMEPAGE # 
#############################################################################################################################################################################################################################
# AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # 


# WORKING (CREATE, READ)
@app.route("/authors", methods=["POST", "GET"])
def authors():
    if request.method == "POST":
        if request.form.get("Add_Author"):
            Name = request.form["Name"]
            BirthDate = request.form["BirthDate"]
            Nationality = request.form["Nationality"]
            query = "INSERT INTO Authors (Name, BirthDate, Nationality) VALUES (%s, %s, %s)"
            cur = mysql.connection.cursor()
            cur.execute(query, (Name, BirthDate, Nationality))
            mysql.connection.commit()
            return redirect("/authors")
    if request.method == "GET":
        query = "SELECT AuthorID, Name, BirthDate, Nationality FROM Authors"
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        return render_template("authors.j2", data=data)
# WORKING (UPDATE)
@app.route("/edit_author/<int:AuthorID>", methods=["POST", "GET"])
def edit_author(AuthorID):
    if request.method == "GET":
        query = "SELECT * FROM Authors WHERE AuthorID = %s"
        cur = mysql.connection.cursor()
        cur.execute(query, (AuthorID,))
        data = cur.fetchall()
        return render_template("edit_author.j2", data=data)
    if request.method == "POST":
        if request.form.get("Edit_Author"):
            AuthorID = request.form["AuthorID"]
            Name = request.form["Name"]
            BirthDate = request.form["BirthDate"]
            Nationality = request.form["Nationality"]
            query = "UPDATE Authors SET Name = %s, BirthDate = %s, Nationality = %s WHERE AuthorID = %s"
            cur = mysql.connection.cursor()
            cur.execute(query, (Name, BirthDate, Nationality, AuthorID))
            mysql.connection.commit()
            return redirect("/authors")
# WORKING (DELETE)
@app.route("/delete_author/<int:AuthorID>")
def delete_author(AuthorID):
    query = "DELETE FROM Authors WHERE AuthorID = %s"  # Note for Josh - this runs an error now that the books link table exists - needs to set author to null on books
    cur = mysql.connection.cursor()
    cur.execute(query, (AuthorID,))
    mysql.connection.commit()
    return redirect("/authors")


# AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS # AUTHORS #
#################################################################################################################################################################
# BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # 


# WORKING (CREATE, READ)
@app.route('/books', methods=["GET", "POST"])
def books():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        if request.form.get("Add_Book"):
            title = request.form["title"]
            isbn = request.form["isbn"]
            year_published = request.form["year_published"]
            publisher = request.form["publisher"]
            page_count = request.form["page_count"]
            language = request.form["language"]
            on_hold = bool(request.form.get("on_hold"))
            checked_out = bool(request.form.get("checked_out"))
            authors = request.form.getlist("authors")
            genres = request.form.getlist("genres")
            query = """INSERT INTO Books (Title, ISBN, YearPublished, Publisher, PageCount, Language, OnHold, CheckedOut) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
            cur.execute(query, (title, isbn, year_published, publisher, page_count, language, on_hold, checked_out))
            new_book_id = cur.lastrowid
            for author_id in authors:
                cur.execute('INSERT INTO BooksAuthorsLinked (BookID, AuthorID) VALUES (%s, %s);', (new_book_id, author_id))
            for genre_id in genres:
                cur.execute('INSERT INTO BooksGenresLinked (BookID, GenreID) VALUES (%s, %s);', (new_book_id, genre_id))
            mysql.connection.commit()
            return redirect('/books')
    if request.method == "GET":
        query = """
        SELECT Books.BookID, Title, ISBN, YearPublished, Publisher, PageCount, Language, OnHold, CheckedOut,
            GROUP_CONCAT(DISTINCT Authors.Name) as author_names,
            GROUP_CONCAT(DISTINCT Genres.GenreDescription) as genre_names
        FROM Books
        LEFT JOIN BooksAuthorsLinked ON Books.BookID = BooksAuthorsLinked.BookID
        LEFT JOIN Authors ON BooksAuthorsLinked.AuthorID = Authors.AuthorID
        LEFT JOIN BooksGenresLinked ON Books.BookID = BooksGenresLinked.BookID
        LEFT JOIN Genres ON BooksGenresLinked.GenreID = Genres.GenreID
        GROUP BY Books.BookID;
        """
        cur.execute(query)
        books_data = cur.fetchall()
        cur.execute("SELECT * FROM Authors;")
        authors = cur.fetchall()
        cur.execute("SELECT * FROM Genres;")
        genres = cur.fetchall()
        return render_template("books.j2", data=books_data, authors=authors, genres=genres)
# WORKING (UPDATE)
@app.route('/edit_book/<int:book_id>', methods=["GET", "POST"])
def edit_book(book_id):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        title = request.form["title"]
        isbn = request.form["isbn"]
        year_published = request.form["year_published"]
        publisher = request.form["publisher"]
        page_count = request.form["page_count"]
        language = request.form["language"]
        on_hold = bool(request.form.get("on_hold"))
        checked_out = bool(request.form.get("checked_out"))
        authors = request.form.getlist("authors")
        genres = request.form.getlist("genres")
        query = """UPDATE Books
                   SET Title = %s, ISBN = %s, YearPublished = %s, Publisher = %s, 
                       PageCount = %s, Language = %s, OnHold = %s, CheckedOut = %s
                   WHERE BookID = %s;"""
        cur.execute(query, (title, isbn, year_published, publisher, page_count, language, on_hold, checked_out, book_id))
        cur.execute('DELETE FROM BooksAuthorsLinked WHERE BookID = %s;', (book_id,))
        for author_id in authors:
            cur.execute('INSERT INTO BooksAuthorsLinked (BookID, AuthorID) VALUES (%s, %s);', (book_id, author_id))
        cur.execute('DELETE FROM BooksGenresLinked WHERE BookID = %s;', (book_id,))
        for genre_id in genres:
            cur.execute('INSERT INTO BooksGenresLinked (BookID, GenreID) VALUES (%s, %s);', (book_id, genre_id))
        mysql.connection.commit()
        return redirect('/books')
    if request.method == "GET":
        cur.execute("SELECT * FROM Books WHERE BookID = %s;", (book_id,))
        book_data = cur.fetchone()
        cur.execute("""SELECT AuthorID FROM BooksAuthorsLinked WHERE BookID = %s;""", (book_id,))
        current_authors = [row['AuthorID'] for row in cur.fetchall()]
        cur.execute("""SELECT GenreID FROM BooksGenresLinked WHERE BookID = %s;""", (book_id,))
        current_genres = [row['GenreID'] for row in cur.fetchall()]
        cur.execute("SELECT * FROM Authors;")
        all_authors = cur.fetchall()
        cur.execute("SELECT * FROM Genres;")
        all_genres = cur.fetchall()
        return render_template("edit_book.j2", data=book_data, authors=all_authors, genres=all_genres, current_authors=current_authors, current_genres=current_genres)
# WORKING???? (DELETE)
@app.route('/delete_book/<int:bookID>')
def delete_book(bookID):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM BooksAuthorsLinked WHERE BookID = %s;", (bookID,))
    cur.execute("DELETE FROM BooksGenresLinked WHERE BookID = %s;", (bookID,))
    cur.execute("DELETE FROM Books WHERE BookID = %s;", (bookID,)) # Note for Josh - this seems to work but take a look at it
    mysql.connection.commit()
    return redirect('/books')


# BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS # BOOKS #  
#################################################################################################################################################
# EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES #


# WORKING (CREATE, READ)
@app.route("/employees", methods=["POST", "GET"])
def employees():
    if request.method == "POST":
        if request.form.get("Add_Employee"):
            Name = request.form["Name"]
            Position = request.form["Position"]
            Email = request.form["Email"]
            Phone = request.form["Phone"]
            query = "INSERT INTO Employees (Name, Position, Email, Phone) VALUES (%s, %s, %s, %s)"   
            cur = mysql.connection.cursor()
            cur.execute(query, (Name, Position, Email, Phone))
            mysql.connection.commit()
            return redirect("/employees")
    if request.method == "GET":
        query = "SELECT EmployeeID, Name, Position, Email, Phone FROM Employees"   
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        return render_template("employees.j2", data=data)
# WORKING (UPDATE)
@app.route("/edit_employee/<int:EmployeeID>", methods=["POST", "GET"])
def edit_employee(EmployeeID):
    if request.method == "GET":
        query = "SELECT * FROM Employees WHERE EmployeeID = %s;" % (EmployeeID)
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        return render_template("edit_employee.j2", data=data)
    if request.method == "POST":
        if request.form.get("Edit_Employee"):
            EmployeeID = request.form["EmployeeID"]
            Name = request.form["Name"]
            Position = request.form["Position"]
            Email = request.form["Email"]
            Phone = request.form["Phone"]
            query = "UPDATE Employees SET Name = %s, Position = %s, Email = %s, Phone = %s WHERE EmployeeID = %s;"
            cur = mysql.connection.cursor()
            cur.execute(query, (Name, Position, Email, Phone, EmployeeID))
            mysql.connection.commit()
            return redirect("/employees")
# Working (DELETE)
@app.route("/delete_employee/<int:EmployeeID>")
def delete_employee(EmployeeID):
    query = "DELETE FROM Employees WHERE EmployeeID = %s;"    # Note for Josh - this needs to be fixed to cascade to orders 
    cur = mysql.connection.cursor()
    cur.execute(query, (EmployeeID,))
    mysql.connection.commit()
    return redirect("/employees")


# EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES # EMPLOYEES #
#################################################################################################################################################
# GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # 


#WORKING (CREATE, READ)
@app.route("/genres", methods=["POST", "GET"])
def genres():
    if request.method == "POST":
        if request.form.get("Add_Genre"):
            GenreID = request.form["GenreID"]
            GenreDescription = request.form["GenreDescription"]
            query = "INSERT INTO Genres (GenreID, GenreDescription) VALUES (%s, %s)"   
            cur = mysql.connection.cursor()
            cur.execute(query, (GenreID, GenreDescription))
            mysql.connection.commit()
            return redirect("/genres")
    if request.method == "GET":
        query = "SELECT GenreID, GenreDescription FROM Genres"  
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        return render_template("genres.j2", data=data)
# WORKING (UPDATE)
@app.route("/edit_genre/<string:GenreID>", methods=["POST", "GET"])
def edit_genre(GenreID):
    if request.method == "GET":
        query = "SELECT * FROM Genres WHERE GenreID = %s"  
        cur = mysql.connection.cursor()
        cur.execute(query, (GenreID,))
        data = cur.fetchall()
        return render_template("edit_genre.j2", data=data)
    if request.method == "POST":
        if request.form.get("Edit_Genre"):
            GenreID = request.form["GenreID"]
            GenreDescription = request.form["GenreDescription"]
            query = "UPDATE Genres SET GenreDescription = %s WHERE GenreID = %s"  
            cur = mysql.connection.cursor()
            cur.execute(query, (GenreDescription, GenreID))
            mysql.connection.commit()
            return redirect("/genres")
#WORKING (DELETE)
@app.route("/delete_genre/<GenreID>")
def delete_genre(GenreID):
    query = "DELETE FROM Genres WHERE GenreID = '%s';" % (GenreID)  # Note for Josh - this needs to be fixed to cascade to books
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    return redirect("/genres")


# GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # GENRE # 
#################################################################################################################################################
# MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER #


# WORKING (CREATE, READ)
@app.route("/members", methods=["POST", "GET"])
def members():
    if request.method == "POST":
        if request.form.get("Add_Member"):
            Email = request.form["Email"]	
            Name = request.form["Name"]	
            Phone = request.form["Phone"]	
            Address = request.form["Address"]	
            Standing = "Good"	
            CurrentFines = 0.00
            query = "INSERT INTO Members (Email, Name, Phone, Address, Standing, CurrentFines) VALUES (%s, %s, %s, %s, %s, %s)"   
            cur = mysql.connection.cursor()
            cur.execute(query, (Email, Name, Phone, Address, Standing, CurrentFines))
            mysql.connection.commit()
            return redirect("/members")
    if request.method == "GET":
        query = "SELECT MemberID, Email, Name, Phone, Address, Standing, CurrentFines FROM Members"  
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        return render_template("members.j2", data=data)
# WORKING (UPDATE)
@app.route("/edit_member/<int:MemberID>", methods=["POST", "GET"])
def edit_member(MemberID):
    if request.method == "GET":
        query = "SELECT * FROM Members WHERE MemberID = %s;" % (MemberID)
        cur = mysql.connection.cursor()
        cur.execute(query)
        data = cur.fetchall()
        return render_template("edit_member.j2", data=data)
    if request.method == "POST":
        if request.form.get("Edit_Member"):
            MemberID = request.form["MemberID"]	
            Email = request.form["Email"]	
            Name = request.form["Name"]	
            Phone = request.form["Phone"]	
            Address = request.form["Address"]	
            Standing = request.form["Standing"]	
            CurrentFines = request.form["CurrentFines"]	
            if Address == "" or Address == "None" or Address == None:
                query = "UPDATE Members SET Members.Email = %s, Members.Name = %s, Members.Phone = %s, Members.Address = NULL, Members.Standing = %s, Members.CurrentFines = %s WHERE Members.MemberID = %s;"
                cur = mysql.connection.cursor()
                cur.execute(query, (Email, Name, Phone, Standing, CurrentFines, MemberID))
                mysql.connection.commit()
            else:
                query = "UPDATE Members SET Members.Email = %s, Members.Name = %s, Members.Phone = %s, Members.Address = %s, Members.Standing = %s, Members.CurrentFines = %s WHERE Members.MemberID = %s;"
                cur = mysql.connection.cursor()
                cur.execute(query, (Email, Name, Phone, Address, Standing, CurrentFines, MemberID))
                mysql.connection.commit()
            return redirect("/members")
# Working (DELETE)
@app.route("/delete_member/<int:MemberID>")
def delete_member(MemberID):
    # return redirect("/books")
    query = "DELETE FROM Members WHERE MemberID = %s;"   # Note for Josh - this needs to be fixed to cascade to orders 
    cur = mysql.connection.cursor()
    cur.execute(query, (MemberID,))
    mysql.connection.commit()
    return redirect("/members")


# MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER # MEMBER #
#################################################################################################################################################
# ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS #


# WORKING (CREATE, READ)
@app.route('/orders', methods=["GET", "POST"])
def orders():
    cur = mysql.connection.cursor()
    if request.method == "POST":
        if request.form.get("Add_Order"):
            member_id = request.form["member_id"]
            employee_id = request.form["employee_id"]
            order_date = request.form["order_date"]
            query = """INSERT INTO Orders (MemberID, EmployeeID, OrderDate) 
                       VALUES (%s, %s, %s);"""
            cur.execute(query, (member_id, employee_id, order_date))
            new_order_id = cur.lastrowid
            book_ids = request.form.getlist("book_ids")
            for book_id in book_ids:
                cur.execute('INSERT INTO OrderBooksLinked (OrderID, BookID) VALUES (%s, %s);', (new_order_id, book_id))
            mysql.connection.commit()
            return redirect('/orders')
    if request.method == "GET":
        query = """
        SELECT Orders.OrderID, Orders.OrderDate, Members.Name as MemberName, Employees.Name as EmployeeName,
            GROUP_CONCAT(DISTINCT Books.Title) as BookTitles
        FROM Orders
        LEFT JOIN Members ON Orders.MemberID = Members.MemberID
        LEFT JOIN Employees ON Orders.EmployeeID = Employees.EmployeeID
        LEFT JOIN OrderBooksLinked ON Orders.OrderID = OrderBooksLinked.OrderID
        LEFT JOIN Books ON OrderBooksLinked.BookID = Books.BookID
        GROUP BY Orders.OrderID;
        """
        cur.execute(query)
        orders_data = cur.fetchall()
        cur.execute("SELECT * FROM Members;")
        members = cur.fetchall()
        cur.execute("SELECT * FROM Employees;")
        employees = cur.fetchall()
        cur.execute("SELECT * FROM Books;")
        books = cur.fetchall()
        return render_template("orders.j2", data=orders_data, members=members, employees=employees, books=books)
# Working (UPDATE) - Want to add a "add book" button but don't need it
@app.route('/edit_order/<int:order_id>', methods=["GET", "POST"])
def edit_order(order_id):
    cur = mysql.connection.cursor()
    if request.method == "POST":
        member_id = request.form["member_id"]
        employee_id = request.form["employee_id"]
        order_date = request.form["order_date"]
        query = """UPDATE Orders 
                   SET MemberID = %s, EmployeeID = %s, OrderDate = %s
                   WHERE OrderID = %s;"""
        cur.execute(query, (member_id, employee_id, order_date, order_id))
        mysql.connection.commit()
        cur.execute("DELETE FROM OrderBooksLinked WHERE OrderID = %s;", (order_id,))
        book_ids = request.form.getlist("book_ids")
        for book_id in book_ids:
            cur.execute('INSERT INTO OrderBooksLinked (OrderID, BookID) VALUES (%s, %s);', (order_id, book_id))
        mysql.connection.commit()
        return redirect('/orders')
    if request.method == "GET":
        cur.execute("""
        SELECT Orders.OrderID, Orders.OrderDate, Orders.MemberID, Orders.EmployeeID, 
               Members.Name as MemberName, Employees.Name as EmployeeName,
               GROUP_CONCAT(DISTINCT OrderBooksLinked.BookID) as BookIDs
        FROM Orders
        LEFT JOIN Members ON Orders.MemberID = Members.MemberID
        LEFT JOIN Employees ON Orders.EmployeeID = Employees.EmployeeID
        LEFT JOIN OrderBooksLinked ON Orders.OrderID = OrderBooksLinked.OrderID
        WHERE Orders.OrderID = %s
        GROUP BY Orders.OrderID;
        """, (order_id,))
        order_data = cur.fetchone()
        if order_data['BookIDs']:
            order_data['BookIDs'] = list(map(int, order_data['BookIDs'].split(',')))
        else:
            order_data['BookIDs'] = []
        cur.execute("SELECT * FROM Members;")
        members = cur.fetchall()
        cur.execute("SELECT * FROM Employees;")
        employees = cur.fetchall()
        cur.execute("SELECT * FROM Books;")
        books = cur.fetchall()
        return render_template("edit_order.j2", data=order_data, members=members, employees=employees, books=books)
# WORKING (DELETE)
@app.route('/delete_order/<int:order_id>', methods=["GET"])
def delete_order(order_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM OrderBooksLinked WHERE OrderID = %s;", (order_id,))
    cur.execute("DELETE FROM Orders WHERE OrderID = %s;", (order_id,)) # Note for Josh - this seems to work aswell, but again, take a look and make sure
    mysql.connection.commit()
    return redirect('/orders')


# ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS # ORDERS #
#################################################################################################################################################
# START # START # START # START # START # START # START # START # START # START # START # START # START # START # START # START # START # START # 


if __name__ == "__main__":
    app.run(port=8087, debug=True)