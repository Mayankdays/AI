from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from pdf_linker import get_pdf_link
from backend import ai
from helpers import apology, login_required
import sqlite3
import markdown

app = Flask(__name__)



def connect_db():
    conn = sqlite3.connect('database.db')
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        if 'delete_id' in request.form:
            row_id = request.form['delete_id']
            cursor.execute("DELETE FROM combined_cbse_data WHERE id=?", (row_id,))
            conn.commit()

    # Fetch data from the database
    cursor.execute("SELECT * FROM combined_cbse_data")
    rows = cursor.fetchall()

    # Close the database connection
    conn.close()

    return render_template('admin.html', rows=rows)

@app.route('/add_data', methods=['GET', 'POST'])
def add_data():
    if request.method == 'POST':
        # Database Connection
        conn = connect_db()
        c = conn.cursor()

        # Data from the form
        board = request.form['field1']
        grade = request.form['field2']
        subject = request.form['field3']
        chapter = request.form['field4']
        link = request.form['field5']

        # Inserting Data
        c.execute("INSERT INTO combined_cbse_data (board_name, grade_name, subject_name, chapter_name, chapter_link) VALUES (?, ?, ?, ?, ?)", (board, grade, subject, chapter, link))

        # Close the connection
        conn.commit()
        conn.close()

        return redirect(url_for('admin'))
    return render_template('add_data.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'GET':
        return render_template('chat.html')
    else:
        try:
            message = request.form['message']
        except KeyError:
            return jsonify({'error': 'Missing message'}), 400

        # Temp Storage for messages.
        chapter = ['Motion in a Straight Line']
        questions = []

        questions.append(message)
        response = ai(questions, chapter)
        response = response['output_text']
        html_response = markdown.markdown(response)
        
        questions.clear()
        return jsonify({
            'messages': questions,
            'response': html_response
        })


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
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
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    conn = connect_db()
    cursor = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        # Add the user to the database
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()

    # Close the database connection
    conn.close()

    return render_template('add_user.html')

if __name__ == '__main__':
    app.run(debug=True)