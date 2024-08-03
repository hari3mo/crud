from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import UserMixin, login_user, logout_user, current_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import datetime
import mysql.connector
import os

# Redundant
# from sqlalchemy import create_engine

import pandas as pd
import numpy as np

# Forms 
from forms import LoginForm, SearchForm, UserForm, PasswordForm, FileForm, \
    UserUpdateForm, AccountForm, OpportunityForm, TextForm

app = Flask(__name__) 

# MySQL Database Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://erpcrm:Erpcrmpass1!@aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com:3306/erpcrmdb' 

# Secret key
app.config['SECRET_KEY'] = '9b2a012a1a1c425a8c86'

# Uploads folder
app.config['UPLOAD_FOLDER'] = 'static/files'

# Set session timeout duration
app.permanent_session_lifetime = timedelta(minutes=25) 

# Login initialize
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Pass to base file
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Initialize database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Standard engine(s)
# engine = create_engine('mysql+pymysql://erpcrm:Erpcrmpass1!@aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com:3306/erpcrmdb')

# mydb = mysql.connector.connect(
#     host = 'aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com',
#     user = 'erpcrm', 
#     passwd = 'Erpcrmpass1!',
#     database = 'erpcrmdb'
# )

@app.route('/admin/')
def admin():
    if session['admin']:
        users = Users.query
        return render_template('admin.html', users=users)
    return redirect(url_for('index'))

##############################################################################

# Models

# Accounts model
class Accounts(db.Model):
    __tablename__ = 'Accounts'
    AccountID = db.Column(db.Integer, primary_key=True)
    CompanyName = db.Column(db.String(100), nullable=False)
    CompanyRevenue = db.Column(db.Integer, nullable=False)
    EmployeeHeadCount = db.Column(db.Integer, nullable=False)
    CompanyIndustry = db.Column(db.String(100))
    CompanySpecialties = db.Column(db.Text)
    CompanyType = db.Column(db.String(50))
    Country = db.Column(db.String(50), nullable=False)
    City = db.Column(db.String(50))
    Timezone = db.Column(db.String(50))
    
    # Opportunities reference 
    Opportunity = db.relationship('Opportunities', backref='Account')
    
# Clients model
class Clients(db.Model):
    __tablename__ = 'Clients'
    ClientID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Client = db.Column(db.String(50), nullable=False, unique=True)
    License = db.Column(db.String(20), nullable=False, unique=True)
    Image = db.Column(db.String(255), unique=True)
    ValidFrom = db.Column(db.Date, default=datetime.datetime.now(datetime.timezone.utc))
    ValidTo = db.Column(db.Date)
    
# Opportunities model    
class Opportunities(db.Model):
    __tablename__ = 'Opportunities'
    OpportunityID = db.Column(db.Integer, primary_key=True)
    # Foreign Key to AccountID
    AccountID = db.Column(db.Integer, db.ForeignKey(Accounts.AccountID))
    LeadID = db.Column(db.Integer)
    ClientID = db.Column(db.Integer)
    Opportunity = db.Column(db.Text)
    Value = db.Column(db.String(255))
    Stage = db.Column(db.String(100))
    CreationDate = db.Column(db.Date, default=datetime.datetime.now(datetime.timezone.utc))
    CloseDate = db.Column(db.Date)
    


# Users model
class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Email = db.Column(db.String(50), unique=True, nullable=False)
    PasswordHash = db.Column(db.String(128), nullable=False)
    License = db.Column(db.String(20), nullable=False)
    Client = db.Column(db.String(50), nullable=False)
    ValidFrom = db.Column(db.Date, default=datetime.datetime.now(datetime.timezone.utc))
    ValidTo = db.Column(db.Date)
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        self.PasswordHash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.PasswordHash, password)  
    
    
    # Override get_id to return the correct identifier
    def get_id(self):
        return str(self.UserID)

    @property
    def is_authenticated(self):
        return True  # Assuming the presence of a valid session token
    
# Admins model
class Admins(db.Model):
    __tablename__ = 'Admins'
    User = db.Column(db.String(50), primary_key=True)
    
##############################################################################  

# Login
@app.route('/login/', methods=['POST', 'GET'])
def login():
    db.session.rollback()
    user = None
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(Email=form.email.data).first()
        # User exists
        if user:
            admin = None
            if user.verify_password(form.password.data):
                login_user(user)
                admin = Admins.query.filter_by(User=current_user.Email).first()
                session['admin'] = True if admin else False
                session['image'] = Clients.query.filter_by(License=user.License).first().Image
                flash('Logged in successfully.', 'success')
                return redirect(url_for('index'))
            else:
                flash('Incorrect password.', 'error')
                return redirect(url_for('login'))
        else:
            flash('User does not exist.', 'error')
            return redirect(url_for('login'))
        
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            flash(err, 'error')      
    return render_template('login.html', form=form)

# Test 
@app.route('/test/', methods=['GET', 'POST'])
def text():
    form = TextForm()
    if form.validate_on_submit():
        return render_template('test.html', form=form)
    return render_template('test.html', form=form)

# User update/management
@app.route('/user/user_management/', methods=['GET', 'POST'])
@login_required
def user_management():
    form = UserUpdateForm()
    email = None
    if form.validate_on_submit():
        email = Users.query.filter_by(Email=form.email.data).first()
        if email is None:
            if current_user.verify_password(form.password.data):
                current_user.Email = form.email.data
                hashed_password = generate_password_hash(form.new_password.data, 'scrypt')
                current_user.PasswordHash = hashed_password
                try:
                    db.session.commit()
                    logout_user()
                    flash('User updated successfully. Please sign in again.', 'success')
                    return redirect(url_for('login'))
                except:
                    flash('User update failed.', 'error')
                    return redirect(url_for('user_management'))
            else:
                flash('Incorrect password.')
                return redirect(url_for('user_management'))
                
        else:
            flash('User with specified email already exists.', 'error')
            return redirect(url_for('user_management'))
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            flash(err, 'error')    
        
    return render_template('user_management.html', form=form)



# Clear opportunities
@app.route('/clear_opportunities/')
@login_required
def clear_opportunities():
    Opportunities.query.delete()
    db.session.commit()
    
    flash('Opportunities list cleared.')
    return redirect(url_for('accounts_list'))
    


# New opportunity
@app.route('/opportunities/new_opportunity/', methods=['GET', 'POST'])
@login_required
def new_opportunity():
    form = OpportunityForm()
    if form.validate_on_submit():
        try:
            opportunity = Opportunities(AccountID=form.account.data,
                                        Opportunity=form.opportunity.data,
                                        Value=form.value.data,
                                        Stage=form.stage.data)
            db.session.add(opportunity)
            db.session.commit()
            
            flash('Opportunity added successfully.')
            return redirect(url_for('opportunities_list'))
        except:
            db.session.rollback()
            flash('Opportunity add failed.')
            return redirect(url_for('new_opportunity'))
    
    return render_template('new_opportunity.html', form=form)

# Opportunities list
@app.route('/opportunities/opportunities_list')
@login_required
def opportunities_list():
    db.session.rollback()
    try:
        opportunities = Opportunities.query.order_by(Opportunities.OpportunityID.desc())
        return render_template('opportunities_list.html', opportunities=opportunities)
    except:
        # flash('Error loading database, please try again.')
        return redirect(url_for('opportunities_list'))



# New user
@app.route('/new_user/', methods=['GET', 'POST'])
@login_required
def new_user():
    user = None
    license = None
    form = UserForm()
    # Method == Post
    if form.validate_on_submit():
        user = Users.query.filter_by(Email=form.email.data).first()
        license = Clients.query.filter_by(License=form.license.data).first()
        # User does not exist
        if user is None:
            # Valid license key 
            if license:
                # Hash password
                hashed_password = generate_password_hash(form.password.data, 'scrypt')
                new_user = Users(Email=form.email.data,
                                PasswordHash=hashed_password,
                                License=form.license.data,
                                Client=license.Client,
                                ValidTo='00-00-0000')
                    
                db.session.add(new_user)
                db.session.commit()
                flash('User added successfully.', 'success')
                return redirect(url_for('new_user'))
        
            else:
                flash('Invalid license key.', 'error')
                return redirect(url_for('new_user'))
            
        else:
            flash('User already exists.')
            return redirect(url_for('new_user'))
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            flash(err, 'error')    
    return render_template('new_user.html', form=form)

@app.route('/password/', methods=['GET', 'POST'])
@login_required
def password():
    hashed_password = None
    password = None
    passed = None
    submit = False
    form = PasswordForm()
    
    if form.validate_on_submit():
        hashed_password = form.hashed_password.data
        password = form.password.data
        passed = check_password_hash(hashed_password, password)
        submit = True

    return render_template('password.html', form=form, passed=passed,
                           password=password, hashed_password=hashed_password,
                           submit=submit)


# User signup page
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    user = None
    license = None
    form = UserForm()
    # Method == Post
    if form.validate_on_submit():
        user = Users.query.filter_by(Email=form.email.data).first()
        license = Clients.query.filter_by(License=form.license.data).first()
        # User does not exist
        if user is None:
            # Valid license key 
            if license:
                # Hash password
                hashed_password = generate_password_hash(form.password.data, 'scrypt')
                new_user = Users(Email=form.email.data,
                                PasswordHash=hashed_password,
                                License=form.license.data,
                                Client=license.Client,
                                ValidTo='00-00-0000')
                    
                db.session.add(new_user)
                db.session.commit()
                flash('User added successfully.', 'success')
                return redirect(url_for('index'))
        
            else:
                flash('Invalid license key.', 'error')
                return redirect(url_for('signup'))
            
        else:
            flash('User already exists.')
            return redirect(url_for('signup'))
    for fieldName, errorMessages in form.errors.items():
        for err in errorMessages:
            flash(err, 'error')    
    return render_template('signup.html', form=form)


# Account import
@app.route('/accounts/accounts_import/', methods=['GET', 'POST'])
@login_required
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
            
            # Rename function
            while os.path.exists(filepath):
                filename = filename.split('.')[0] + ' copy.csv'
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    
            file.save(filepath)
            
            df = pd.read_csv('static/files/{filename}'.format(filename=filename))
            # Replace NaN with None
            df = df.where(pd.notnull(df), None)
            
            id = Accounts.query.order_by(Accounts.AccountID.desc()).first()
    
            if id is None:
                id = 1000
            else:
                id = id.AccountID + 10
    
            # Grab max id
            # ids = pd.read_sql("SELECT AccountID FROM Accounts", con=engine)

            # if ids['AccountID'].empty:
            #     id = 1000
            # else:
            #     id = ids['AccountID'].max() + 10
            
            for index, row in df.iterrows():
                dct = row.to_dict()
                dct.update({'AccountID': id})
                id += 10
                account = Accounts(**dct)
                db.session.add(account)
                
            db.session.commit()
            flash('Import successful.')
            return redirect(url_for('accounts_list'))    
                
        except():
            db.session.rollback()
            flash('Import failed. Please ensure .csv file is ordered as \
                follows: Company Name, Company Revenue, Employee Head Count, \
                Company Industry, Company Specialties, Company Type, Country, \
                City, Timezone.')
            return redirect(url_for('accounts_import'))
        
    return render_template('accounts_import.html', form=form)
    
@app.route('/clear_accounts/')
@login_required
def clear_accounts():
    Accounts.query.delete()
    db.session.commit()
    flash('Accounts list cleared.')
    return redirect(url_for('accounts_list'))

# Accounts list    
@app.route('/accounts/accounts_list/')
@login_required
def accounts_list():
    db.session.rollback()
    try:
        accounts = Accounts.query.order_by(Accounts.AccountID.desc())
        return render_template('accounts_list.html', accounts=accounts)
    except:
        # flash('Error loading database, please try again.')
        return redirect(url_for('accounts_list'))


# Update account
@app.route('/update_account/<int:id>', methods=['GET', 'POST'])
@login_required
def update_account(id):
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
            flash('Account updated successfully.')
            return redirect(url_for('accounts_list'))
        except:
            flash('Account update failed.')
            return render_template('update_account.html', form=form, account=account)
        
    return render_template('update_account.html', form=form, account=account, id=id)        
            
            
# Delete record
@app.route('/delete_account/<int:id>')
@login_required
def delete_account(id):
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
# @app.route('/accounts_list/export/')
# def accounts_export():
#      ...

# Search function
@app.route('/search_accounts/', methods=['POST'])
@login_required
def search_accounts():
    form = SearchForm()
    accounts = Accounts.query
    if form.validate_on_submit():
        search = form.search.data
        accounts = accounts.filter(Accounts.CompanyName.like('%' + \
            search + ''))
        accounts = accounts.order_by(Accounts.CompanyName).all()
        return render_template('search.html', form=form, search=search,
                               accounts=accounts)
    return redirect(url_for('index'))

# New account
@app.route('/accounts/new_account/', methods=['GET', 'POST'])
@login_required
def new_account():
    try:
        id = Accounts.query.order_by(Accounts.AccountID.desc()).first()
        
        if id is None:
            id = 1000
        else:
            id = id.AccountID + 10
        
        # ids = pd.read_sql("SELECT AccountID FROM Accounts", con=engine)
        
        # if ids['AccountID'].empty:
        #     next_id = 1000
        # else:
        #     next_id = (ids['AccountID'].max()) + 10
        
        form = AccountForm()
        if form.validate_on_submit():
            account = Accounts(AccountID=id,
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
            
            flash('Account added successfully.')
            return redirect(url_for('accounts_list'))
        
    except:
        return redirect('new_account')
           
    return render_template('new_account.html', form=form)

# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for('index'))

# # Internal Server Error
# @app.errorhandler(500)
# def server_error(e):
#     return render_template('.html'), 500
    

# Index/favorites page
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('login'))


# Logout function
@app.route('/logout/')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/user/')
@login_required
def user():
    return render_template('user.html')
    

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
    
