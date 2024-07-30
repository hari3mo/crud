from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_migrate import Migrate
from wtforms import StringField, SubmitField, PasswordField, EmailField, IntegerField, FileField, BooleanField, ValidationError
from flask_wtf.file import FileRequired
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.validators import DataRequired, Email, EqualTo, Length
import datetime
from datetime import timedelta
import mysql.connector
import os

from sqlalchemy import create_engine, desc, insert, text

import pandas as pd
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'key'

# MySQL Database Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://erpcrm:Erpcrmpass1!@aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com:3306/erpcrmdb' 

app.config['UPLOAD_FOLDER'] = 'static/files'

engine = create_engine('mysql+pymysql://erpcrm:Erpcrmpass1!@aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com:3306/erpcrmdb')

# Sets session timeout duration
app.permanent_session_lifetime = timedelta(minutes=30) 

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
mydb = mysql.connector.connect(
    host = 'aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com',
    user = 'erpcrm', 
    passwd = 'Erpcrmpass1!',
    database = 'erpcrmdb'
)
    
########################################################################################################################################################################################

# Accounts model
class Accounts(db.Model):
    __tablename__ = 'Accounts'
    AccountID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    CompanyName = db.Column(db.String(100), nullable=False)
    CompanyRevenue = db.Column(db.Integer, nullable=False)
    EmployeeHeadCount = db.Column(db.Integer, nullable=False)
    CompanyIndustry = db.Column(db.String(100))
    CompanySpecialties = db.Column(db.Text)
    CompanyType = db.Column(db.String(50))
    Country = db.Column(db.String(50), nullable=False)
    City = db.Column(db.String(50))
    Timezone = db.Column(db.String(50))
    
    def __repr__(self):
        return '<Name %r>' % self.name
    
# Users model (for login)
class Users(db.Model):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Username = db.Column(db.String(50), nullable=False)
    PasswordHash = db.Column(db.String(128), nullable=False)
    ClientID = db.Column(db.String(20), nullable=False)
    ValidFrom = db.Column(db.Date, nullable=False) # Add option on form to set current date as ValidFrom date
    ValidTo = db.Column(db.Date, nullable=False)
    
    # date_added = db.Column(db.Date, default=datetime.datetime.now(datetime.timezone.utc))
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        self.PasswordHash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.PasswordHash, password)
    
    def __repr__(self):
        return '<Name %r>' % self.name

    
    
# Account form
class AccountForm(FlaskForm):
    company_name = StringField('Company Name:*', validators=[DataRequired()])
    company_revenue = IntegerField('Revenue:*', validators=[DataRequired()])
    employee_head_count = IntegerField('Head Count:*', validators=[DataRequired()])
    company_specialties = StringField('Company Specialties:')
    company_industry = StringField('Company Industry:')
    company_type = StringField('Company Type:')
    country = StringField('Country:*', validators=[DataRequired()])
    city = StringField('City:')
    timezone = StringField('Timezone:')
    submit = SubmitField('Submit')
    
    # email = EmailField('Email:', validators=[DataRequired(), Email()])
    
# User form
class UserForm(FlaskForm):
    username = StringField('User:', validators=[DataRequired()])
    client_id = StringField('ClientID:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password:', validators=[DataRequired(), EqualTo('password', message='Passwords do not match.')])
    submit = SubmitField('Submit')
    

class FileForm(FlaskForm):
    file = FileField('File', validators=[FileRequired()])
    submit = SubmitField('Submit')
 
    
    
    
##############################################################################
    
@app.route('/new_user/', methods=['GET', 'POST'])
def new_user():
    user = None
    form = UserForm()
    if form.validate_on_submit():
        # user = Users.query.filter_by(UserID=form.user.data).first()
        # if user is None:
        # Hash password
        hashed_password = generate_password_hash(form.password.data, 'scrypt')
        new_user = Users(Username=form.username.data,
                        PasswordHash=hashed_password,
                        ClientID=form.client_id.data, 
                        ValidFrom=datetime.datetime.now(datetime.timezone.utc),
                        ValidTo=datetime.datetime.now(datetime.timezone.utc))
            
        db.session.add(new_user)
        db.session.commit()
        flash('User added successfully.')
        return redirect(url_for('new_user'))
            
        # else:
        #     flash('User already exists.')
        #     return redirect(url_for('new_user'))
    return render_template('new_user.html', form=form)



# Test add
# @app.route('/test/', methods=['GET', 'POST'])
# def test():
#     name = None
#     password = None
#     email = None
#     form = ImportForm()
#     # Validate form
#     if form.validate_on_submit():
#         user = Test.query.filter_by(email=form.email.data).first()
#         if user is None:     
#             user = Test(name=form.name.data, email=form.email.data, 
#                         password=form.password.data)
#             db.session.add(user)
#             db.session.commit()
            
#         name = form.name.data
#         password = form.password.data
#         email = form.email.data
#         form.name.data = ''
#         form.email.data = ''
#         form.password.data = ''
#         flash('User added successfully.')
#     users = Test.query.order_by(Test.date_added)
#     return render_template('test.html', form=form, name=name, 
#                            password=password, email=email, users=users)



# Accounts import
@app.route('/accounts_import/', methods=['GET', 'POST'])
def accounts_import():
    form = FileForm()
    filename = None
    if form.validate_on_submit():        
        file = form.file.data
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            if filename.split('.')[-1] != 'csv':
                flash('Import failed. Please upload a .csv file.')
                return redirect(url_for('accounts_import'))
            
            while os.path.exists(filepath):
                filename = filename.split('.')[0] + ' copy.csv'
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
            file.save(filepath)
            
            df = pd.read_csv('static/files/{filename}'.format(filename=filename))
            df = df.where(pd.notnull(df), None)
            
            ids = pd.read_sql("SELECT AccountID FROM Accounts", con=engine)

            if ids['AccountID'].empty:
                id = 1000
            else:
                id = ids['AccountID'].max() + 10
            
            for index, row in df.iterrows():
                dct = row.to_dict()
                dct.update({'AccountID': id})
                id += 10
                account = Accounts(**dct)
                db.session.add(account)
                
            db.session.commit()
            flash('Import successful.')
            return redirect(url_for('accounts_list'))    
                
        except:
            db.session.rollback()
            flash('Import failed. Please ensure .csv file is ordered as \
                follows: Company Name, Company Revenue, Employee Head Count, \
                Company Industry, Company Specialties, Company Type, Country, \
                City, Timezone.')
            return redirect(url_for('accounts_import'))
        
    return render_template('accounts_import.html', form=form)
    
@app.route('/clear/')
def clear():
    Accounts.query.delete()
    db.session.commit()
    
    flash('Accounts list cleared.')
    return redirect(url_for('accounts_list'))

# Accounts list    
@app.route('/accounts_list/')
def accounts_list():
    try:
        accounts = Accounts.query.order_by(desc(Accounts.AccountID))
        return render_template('accounts_list.html', accounts=accounts)
    except:
        flash('Error loading database.')
        return redirect(url_for('accounts'))


# Update record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = AccountForm()
    account = Accounts.query.get_or_404(id)
    if form.validate_on_submit():

        account.CompanyName = request.form['company_name']
        account.CompanyRevenue = request.form['company_revenue']
        account.EmployeeHeadCount = request.form['employee_head_count']
        account.CompanySpecialties = request.form['company_specialties']
        account.CompanyType = request.form['company_type']
        account.Country = request.form['country']
        account.City = request.form['city']
        account.Timezone = request.form['timezone']
        
        try:
            db.session.commit()
            flash('User updated successfully.')
            return redirect(url_for('accounts_list'))
        except:
            flash('User update failed.')
            return render_template('update.html', form=form, account=account)
    
    form.company_name.data = ''
    form.company_revenue.data = ''
    form.employee_head_count.data = ''
    form.company_specialties.data = ''
    form.company_type.data = ''
    form.country.data = ''
    form.city.data = ''
    form.timezone.data = ''    
    
    return render_template('update.html', form=form, account=account, id=id)        
            
            
# Delete record
@app.route('/delete/<int:id>')
def delete(id):
    account = Accounts.query.get_or_404(id)
    try:
        db.session.delete(account)
        db.session.commit()
        flash('Account deleted successfully.')
        return redirect(url_for('accounts_list'))
    
    except:
        flash('Error deleting account.')
        return redirect(url_for('accounts_list'))
        
 

    
# Export records
@app.route('/accounts_list/export/')
def accounts_export():
     ...



# Add account
@app.route('/account_new/', methods=['GET', 'POST'])
def new_account():
    company_name = None
    company_revenue = None
    employee_head_count = None
    company_specialties = None
    company_type = None
    country = None
    company_industry = None
    city = None
    timezone = None
    submit = None    

    db.session.rollback()
    
    ids = pd.read_sql("SELECT AccountID FROM Accounts", con=engine)
    
    if ids['AccountID'].empty:
        next_id = 1000
    else:
        next_id = (ids['AccountID'].max()) + 10
    
    form = AccountForm()
    if form.validate_on_submit():
        account = Accounts(AccountID=next_id, 
                           CompanyName=form.company_name.data, 
                           CompanyRevenue=form.company_revenue.data, 
                           EmployeeHeadCount=form.employee_head_count.data, 
                           CompanySpecialties=form.company_specialties.data, 
                           CompanyIndustry=form.company_industry.data,
                           CompanyType = form.company_type.data, 
                           Country=form.country.data, City=form.city.data, 
                           Timezone=form.timezone.data)
        db.session.add(account)
        db.session.commit()
        
        company_name = request.form['company_name']
        company_revenue = request.form['company_revenue']
        employee_head_count = request.form['employee_head_count']
        company_specialties = request.form['company_specialties']
        company_type = request.form['company_type']
        country = request.form['country']
        city = request.form['city']
        timezone = request.form['timezone']


        
        flash('New account added successfully.')
        return redirect(url_for('accounts_list'))
           
    return render_template('new_account.html', form=form, company_name=company_name)








# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))


# # Internal Server Error
# @app.errorhandler(500)
# def server_error(e):
#     return render_template('.html'), 500
        






@app.route('/')
def index():
    if 'user' in session:
        usr = session['user']
        return render_template('index.html', user=usr)
    else:
        return redirect(url_for('login'))


@app.route('/login/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST': 
        session.permanent = True
        user = request.form['nm']
        password = request.form['pass']
        session['user'] = user
        session['pass'] = password
        
        flash('Login successful.', 'info')
        return redirect(url_for('index'))
    else:
        if 'user' in session:
            return redirect(url_for('index'))
        return render_template('login.html')

@app.route('/logout/')
def logout():
    session.pop('user', None)
    
    session.pop('email', None) # Test
    flash('Successfully logged out.', "info")
    return redirect(url_for('login'))


@app.route('/user/')
def user():
    if 'user' in session:
        user = session['user']
        password = session['pass']
        return render_template('user.html', user=user, password=password)
    else:
        return redirect(url_for('login'))


@app.route('/base/')
def base():
    return render_template('base.html')




# TODO
@app.route('/accounts/')
def accounts():
        return render_template('accounts.html')


@app.route('/leads/')
def leads():
    return render_template('leads.html')

@app.route('/opportunities/')
def opportunities():
    return render_template('opportunities.html')

@app.route('/sales/')
def sales():
    return render_template('sales.html')

@app.route('/marketing/')
def marketing():
    return render_template('marketing.html')

@app.route('/service/')
def service():
    return render_template('service.html')

@app.route('/analytics/')
def analytics():
    return render_template('analytics.html')

@app.route('/help/')
def help():
    return render_template('help.html')

@app.route('/home')
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
    
