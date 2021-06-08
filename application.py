import os

from werkzeug.security import generate_password_hash
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import datetime
from functions import apology, login_required

# Configure application
app = Flask(__name__)

app.secret_key = b'l\xddD\xc0t\x1d=\xd4&q\xd5.\x14\xef\xb8\xb0'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.debug= True

#Configure uploads for pictures
#class formUploadImage(FlaskForm):
    #pictures = FileField(validators=[FileAllowed(['jpg', 'png'], 'Images only!')])


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#SQLite database
db = SQL("sqlite:///travel.db")



@app.route("/", methods = ["GET"])
@login_required
def index():
    """Show world map"""

    if request.method == "GET":
        Map = db.execute("SELECT * FROM users WHERE user_id=(?)", session['user_id'])
        return render_template("index.html", Plan=Map)


@app.route("/past_trips", methods = ["GET", "POST" , "DELETE"])
@login_required
def past_trips():
    """Show past trips"""
    if request.method == "POST":
        request_data = request.get_json()
        print(request_data)
        db.execute("INSERT INTO Past_trips (latitude, longitude, session_id) VALUES(?,?,?)", request_data['lat'], request_data['lng'], session['user_id'])
        return "ok"



    if request.method == "GET":
        Marker = db.execute("SELECT latitude,longitude FROM Past_trips WHERE session_id=(?)", session['user_id'])
        print("we send the following var:"+ str(Marker))
        print(Marker)
        #print(Marker[0]['latitude'])
        #print(Marker[0]['longitude'])
        if not Marker:
            return render_template("past_trips.html")
        return render_template("past_trips.html", pins=Marker)

    if request.method == "DELETE":
        request_data = request.get_json()
        print(request_data)
        db.execute("DELETE FROM Past_trips WHERE latitude=(?) AND longitude=(?) AND session_id=(?)", request_data['lat'], request_data['lng'], session['user_id'])
        return "ok"


@app.route("/plan", methods = ["GET"])
@login_required
def plan():
    """Plan trips"""

    if request.method == "GET":
        Marker = db.execute("SELECT * FROM users WHERE user_id=(?)", session['user_id'])
        return render_template("plan_trips.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        print(session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        #Ensure field is not empty
        elif not request.form.get("confirmation"):
            return apology("Must confirm password", 400)

        #Ensure password is matching
        elif not (request.form.get("confirmation") == request.form.get("password")):
            return apology("Password is not matching", 400)

        #Ensure there is no duplicate for usename
        existing_user=request.form.get("username")
        password=request.form.get("password")
        old_user = db.execute("SELECT username FROM users WHERE username = ?", existing_user)
        if len(old_user) == 0:
            db.execute("INSERT INTO users (username, hash) VALUES (?,?)", existing_user, generate_password_hash (password, method='pbkdf2:sha256', salt_length=8))
        else:
            return apology("User name not available",400)


        return render_template("registered.html", user_name=existing_user)

    if request.method == "GET":
        return render_template("register.html")






@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """User can change password"""

    if request.method == "POST":
        # Ensure password was submitted
        if not request.form.get("old_password"):
            return apology("must provide password", 403)

        elif not request.form.get("new_password"):
            return apology("must provide password", 403)

        #Ensure field is not empty
        elif not request.form.get("confirm_new_password"):
            return apology("Password is not matching", 403)

        #Ensure password is matching
        if not request.form.get("confirm_new_password") == request.form.get("new_password"):
            return apology("Password is not matching", 403)

        new_password = request.form.get("new_password")

        rows = db.execute("SELECT * FROM users WHERE user_id=(?)", session["user_id"])

        if check_password_hash(rows[0]["hash"], request.form.get("old_password")):
            db.execute("UPDATE users SET hash = (?) WHERE user_id=(?)", generate_password_hash (new_password, method='pbkdf2:sha256', salt_length=8), session["user_id"])
        else:
            return apology("Invalid old password", 403)


        return render_template("pass_changed.html")


    if request.method == "GET":
        return render_template("change_password.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
