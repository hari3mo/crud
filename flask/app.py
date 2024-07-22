from flask import Flask, render_template, redirect, url_for, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://erpcrm:Erpcrmpass1!@aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com:3306/erpcrmdb'
app.secret_key = 'key'
app.permanent_session_lifetime = timedelta(minutes=60)

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))



@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST': 
        session.permanent = True
        user = request.form['nm']
        session['user'] = user
        
        flash('Login succesful.', 'info')
        return redirect(url_for('index'))
    else:
        if 'user' in session:
            return redirect(url_for('index'))
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    
    session.pop('email', None) # Test
    flash('Successfully logged out.', "info")
    return redirect(url_for('login'))


@app.route('/user')
def user():
    if 'user' in session:
        usr = session['user']
        return render_template('user.html', user=usr)
    else:
        return redirect(url_for('login'))



# @app.route('/test', methods=['POST', 'GET'])
# def input():
#     eml = None
#     if 'user' in session:
#         usr = session['user']
        
#         if request.method == 'POST':
#             eml = request.form['email']
#             session['email'] = eml
#             flash('Email saved.')
#         else:
#             if 'email' in session:
#                 eml = session['email']
#     return render_template('input.html', email=eml)

# @app.route('/out')
# def out():
#     eml = session['email'] 
#     return f"<h1>{eml}</h1>"

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
    
