from flask import Flask, render_template, request, session, flash, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flaskext.mysql import MySQL
import yaml

app = Flask(__name__)

cred = yaml.load(open('cred.yaml'), Loader=yaml.Loader)
mysql = MySQL()
app.secret_key = cred['secret_key']
app.config['MYSQL_DATABASE_USER'] = cred['mysql_user']
app.config['MYSQL_DATABASE_PASSWORD'] = cred['mysql_password']
app.config['MYSQL_DATABASE_DB'] = cred['mysql_db']
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

@app.route("/")
def index():
    cur = mysql.get_db().cursor()
    queryStatement = (
        f"SELECT e.first_name, e.last_name, l.leave_date FROM leaves AS l JOIN employees e on e.employee_id = l.employee_id;"
    )
    check_request = cur.execute(queryStatement)

    if check_request > 0:
        requested_leave = cur.fetchall()
        return render_template("index.html", requested_leave=requested_leave)
    
    else:
        return render_template("index.html", requested_leave=None)


@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    elif request.method == 'POST':
        loginForm = request.form
        username = loginForm['username']
        cur = mysql.get_db().cursor()
        queryStatement = f"SELECT * FROM employees WHERE username = '{username}'"
        numRow = cur.execute(queryStatement)

        if numRow > 0:
            user = cur.fetchone()

            if check_password_hash(user[4], loginForm['password']):
                session['login'] = True
                session['username'] = user[3]
                session['firstName'] = user[1]
                session['lastName'] = user[2]

                print(session['username'])
                flash('Welcome ' + session['firstName'], 'success')
                return redirect('/')
            
            else:
                cur.close()
                flash('Password is incorrect!', 'danger')
                
        else:
            cur.close()
            flash('User not found!', 'danger')
            return render_template('login.html')
        
        cur.close()
        return render_template('login.html')
    
    return render_template('login.html')



@app.route("/register/", methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    
    elif request.method == 'POST':
        employeeDetails = request.form
        queryStatement = f"SELECT * FROM employees WHERE username = '{employeeDetails['username']}'"
        cur = mysql.get_db().cursor()
        numRow = cur.execute(queryStatement)
        print(numRow)

        if numRow > 0:
            employee = cur.fetchone()
            if employeeDetails['username'] in employee[3]:
                flash('This username isn\'t available. Please try another.', 'danger')
                return render_template("register.html")
            
        if employeeDetails['password'] != employeeDetails['confirm_password']:
            flash('Passwords do not match!', 'danger')
            return render_template("register.html")
        
        p1 = employeeDetails['first_name']
        p2 = employeeDetails['last_name']
        p3 = employeeDetails['username']
        p4 = employeeDetails['password']

        hashed_pw = generate_password_hash(p4)
        print(p1 + "," + p2 + "," + p3 + "," + p4 + "," + hashed_pw)

        queryStatement = (
            f"INSERT INTO employees(first_name, last_name, username, password) "
            f"VALUES('{p1}', '{p2}', '{p3}', '{hashed_pw}')"
        )
        print(check_password_hash(hashed_pw, p4))

        cur = mysql.get_db().cursor()
        cur.execute(queryStatement)
        mysql.get_db().commit()
        cur.close()
        flash("Form Submitted Successfully.", "success")
        return redirect("/")
    
    return render_template("register.html")


@app.route('/request_leave', methods=['GET', 'POST'])
def request_leave():
    try:
        username = session['username']
    except:
        flash('Please sign in first.', 'danger')
        return redirect('/')

    cur = mysql.get_db().cursor()
    queryStatement = f"SELECT employee_id FROM employees WHERE username = '{username}'"
    cur.execute(queryStatement)
    user = cur.fetchone()

    if request.method == 'POST':
        requestForm = request.form
        date = requestForm['datepicker']
        reason = requestForm['body']
        print(date)

        cur1 = mysql.get_db().cursor()
        queryStatement1 = (
            f"INSERT INTO leaves(employee_id, leave_reason, leave_date) "
            f"VALUES('{user[0]}', '{reason}', '{date}')"
        )
        print(queryStatement1)
        cur1.execute(queryStatement1)
        mysql.get_db().commit()
        cur1.close()

        flash('Successfully requested leave.', 'success')
        return redirect('/')
    return render_template('request_leave.html')


@app.route('/logout')
def logout():
    try:
        session['username']
        session.clear()
        flash("You have been logged out", 'info')
        return redirect('/')

    except:
        flash('Please sign in first.', 'danger')
        return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)