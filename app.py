from flask import Flask, render_template, request, session, redirect, url_for, g
import sqlite3
import random

app = Flask(__name__)
app.secret_key = 'cannot_be_hacked' #secret key for security of our app


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('database.db')
    return db

# 'g' stores temporary data during a request.

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

#it is a way to specify some cleanup code that
#needs to be executed after a request has been processed.


@app.route('/gameon', methods=['GET', 'POST'])
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        number = random.randint(1, 10)

        guess = int(request.form['guess'])
        session['number'] = number
        if guess == number:
            session['points'] += 100
            return render_template('win.html', number=number,points=session['points'])
        else:
            session['points'] -= 25
            return render_template('lose.html', number=number,points=session['points'])

    return render_template('index.html',points=session['points'])

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user and password == user[2]:
            session['username'] = username
            session['points'] = user[3]
            return redirect(url_for('index'))
        else:
            error = 'Invalid username or password.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            error = 'Passwords do not match.'
            return render_template('signup.html', error=error)
        else:
            db = get_db()
            cursor = db.cursor()
            try:
                cursor.execute('INSERT INTO users (username, password, points) VALUES (?, ?, ?)', (username, password, 0))
                db.commit()
                return redirect(url_for('login'))
            except:
                error = 'Username already exists.'
                return render_template('signup.html', error=error)

    return render_template('signup.html')

@app.route('/reset', methods=['POST'])
def reset():
    if 'username' not in session:
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE users SET points = 0 WHERE username = ?', (session['username'],))
    db.commit()
    session['points'] = 0
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('points', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
