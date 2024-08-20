from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import UserMixin, login_user, logout_user, current_user, login_required, LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from dotenv import load_dotenv
import datetime
import json
import os

# Redundant
# from sqlalchemy import create_engine, text

from openai import OpenAI

import pandas as pd
import numpy as np

# Forms 
from forms import LoginForm, SearchForm, UserForm, PasswordForm, FileForm, \
    UserUpdateForm, AccountForm, OpportunityForm, TextForm, AdminUpdateForm

app = Flask(__name__) 

# MySQL Database Connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://erpcrm:Erpcrmpass1!@erpcrmdb.cfg0ok8iismy.us-west-1.rds.amazonaws.com:3306/erpcrmdb' 

# OpenAI API Client
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key = OPENAI_API_KEY)

# Secret key
app.config['SECRET_KEY'] = '9b2a012a1a1c425a8c86'

# Uploads folder
app.config['UPLOAD_FOLDER'] = 'static/files'

# Set session timeout duration
app.permanent_session_lifetime = timedelta(minutes=30) 

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

# Standard engine
# engine = create_engine('mysql+pymysql://erpcrm:Erpcrmpass1!@erpcrmdb.cfg0ok8iismy.us-west-1.rds.amazonaws.com:3306/erpcrmdb')

# mydb = mysql.connector.connect(
#     host = 'aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com',
#     user = 'erpcrm', 
#     passwd = 'Erpcrmpass1!',
#     database = 'erpcrmdb'
# )

# Admin page
@app.route('/admin/')
@login_required
def admin():
    if session['admin']:
        users = None
        users = Users.query.order_by(Users.UserID.desc())
        return render_template('admin.html', users=users)
    return redirect(url_for('index'))

##############################################################################

# Models

# Clients model
class Clients(db.Model):
    __tablename__ = 'Clients'
    ClientID = db.Column(db.Integer, primary_key=True)
    Client = db.Column(db.String(50), nullable=False, unique=True)
    License = db.Column(db.String(20), nullable=False, unique=True)
    Image = db.Column(db.String(255), unique=True)
    ValidFrom = db.Column(db.Date, default=datetime.datetime.now(datetime.timezone.utc))
    ValidTo = db.Column(db.Date)
    
    # References
    User = db.relationship('Users', backref='Client')
    Account = db.relationship('Accounts', backref='Client')
    Opportunity = db.relationship('Opportunities', backref='Client')
    
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
    ClientID = db.Column(db.Integer, db.ForeignKey(Clients.ClientID)) # Foreign key to ClientID
    
    # References
    Opportunity = db.relationship('Opportunities', backref='Account')
    
    
# Opportunities model    
class Opportunities(db.Model):
    __tablename__ = 'Opportunities'
    OpportunityID = db.Column(db.Integer, primary_key=True)
    AccountID = db.Column(db.Integer, db.ForeignKey(Accounts.AccountID)) # Foreign Key to AccountID
    LeadID = db.Column(db.Integer)
    Opportunity = db.Column(db.Text)
    Value = db.Column(db.String(255))
    Stage = db.Column(db.String(100))
    CreationDate = db.Column(db.Date, default=datetime.datetime.now(datetime.timezone.utc))
    CloseDate = db.Column(db.Date)
    ClientID = db.Column(db.Integer, db.ForeignKey(Clients.ClientID)) # Foreign Key to ClientID
      
# Users model
class Users(db.Model, UserMixin):
    __tablename__ = 'Users'
    UserID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Email = db.Column(db.String(50), unique=True, nullable=False)
    FirstName = db.Column(db.String(50), nullable=False)
    LastName = db.Column(db.String(50), nullable=False)
    PasswordHash = db.Column(db.String(255), nullable=False)
    License = db.Column(db.String(20), nullable=False)
    ValidFrom = db.Column(db.Date, default=datetime.datetime.now(datetime.timezone.utc))
    ValidTo = db.Column(db.Date)
    ClientID = db.Column(db.Integer, db.ForeignKey(Clients.ClientID)) # Foreign key to ClientID
    
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
        return True  # Assuming the presence of a valid session tokenp
    
# Admins model
class Admins(db.Model):
    __tablename__ = 'Admins'
    User = db.Column(db.String(50), primary_key=True)
    
##############################################################################  

# Login
@app.route('/login/', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
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
                session['image'] = str(current_user.Client.Image)
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

# Update user/management
@app.route('/user/user_management/', methods=['GET', 'POST'])
@login_required
def user_management():
    form = UserUpdateForm()
    email = None
    if form.validate_on_submit():
        email = Users.query.filter_by(Email=form.email.data).first()
        admin = Admins.query.filter_by(User=form.email.data).first()
        if email is None and admin is None:
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

# Admin: Update user
@app.route('/admin/update_user/<int:userID>', methods=['GET', 'POST'])
@login_required
def update_user(userID):
    user = db.session.get(userID)
    # user = Users.query.get_or_404(userID)
    form = AdminUpdateForm()
    if form.validate_on_submit():
        admin = None
        admin = Admins.query.filter_by(User=user.Email).first()
        if admin:
            flash('Access denied.')
            return redirect(url_for('admin'))
        user.Email = form.email.data
        hashed_password = generate_password_hash(form.password.data, 'scrypt')
        user.PasswordHash = hashed_password
        db.session.commit()
        return redirect(url_for('admin'))
    
    return render_template('update_user.html', form=form, user=user)



# Admin: Delete user
@app.route('/user/delete/<int:userID>')
@login_required
def delete_user(userID):
    if session['admin']:
        user = Users.query.get_or_404(userID)
        
        # Admin restriction
        admin = None
        admin = Admins.query.filter_by(User=user.Email).first()
        if admin:
            flash('Access denied.')
            return redirect(url_for('admin'))
        
        # try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.')
        return redirect(url_for('admin'))
        
        # except:
        #     flash('Error deleting user.')
        #     return redirect(url_for('user'))
    else: 
        flash('Access denied.')
        return redirect(url_for('user'))
 


# Clear opportunities
@app.route('/clear_opportunities/')
@login_required
def clear_opportunities():
    Opportunities.query.filter_by(ClientID=current_user.ClientID).delete()
    db.session.commit()
    flash('Opportunities list cleared.')
    return redirect(url_for('opportunities_list'))
    


# New opportunity
@app.route('/opportunities/new_opportunity/', methods=['GET', 'POST'])
@login_required
def new_opportunity():
    form = OpportunityForm()
    if form.validate_on_submit():
        try:
            opportunity = Opportunities(AccountID=form.account.data,
                                        ClientID=current_user.ClientID,
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

# New opportunity from AccountID
@app.route('/opportunities/new_opportunity/<int:id>', methods=['GET', 'POST'])
@login_required
def new_opportunity_id(id):
    form = OpportunityForm()
    if form.validate_on_submit():
        try:
            opportunity = Opportunities(AccountID=form.account.data,
                                        ClientID=current_user.ClientID,
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
            return redirect(url_for('new_opportunity_id', id=id))
    
    return render_template('new_opportunity.html', form=form, id=id)

# Opportunities list
@app.route('/opportunities/opportunities_list')
@login_required
def opportunities_list():
    try:
        opportunities = None
        opportunities = Opportunities.query.filter_by(ClientID=current_user.ClientID).order_by(Opportunities.OpportunityID.desc())
        return render_template('opportunities_list.html', opportunities=opportunities)
    except:
        flash('Error loading database, please try again.')
        return redirect(url_for('opportunities'))

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
    client = None
    form = UserForm()
    # Method == Post
    if form.validate_on_submit():
        user = Users.query.filter_by(Email=form.email.data).first()
        client = Clients.query.filter_by(License=form.license.data).first()
        # User does not exist
        if user is None:
            # Valid license key 
            if client:
                # Hash password
                hashed_password = generate_password_hash(form.password.data, 'scrypt')
                
                # Grab max id
                id = None
                id = Users.query.order_by(Users.UserID.desc()).first()
            
                if id is None:
                        id = 100
                else:
                    id = id.UserID + 1
                    
                new_user = Users(UserID=id,
                                Email=form.email.data,
                                FirstName=form.first_name.data,
                                LastName=form.last_name.data, 
                                PasswordHash=hashed_password,
                                License=form.license.data,
                                ValidTo='00-00-0000',
                                ClientID=client.ClientID)
                    
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
            df = df.replace({np.nan: None})
            
            df = df.rename(columns={df.columns[0]: 'CompanyName',
                                    df.columns[1]: 'CompanyRevenue',
                                    df.columns[2]: 'EmployeeHeadCount',
                                    df.columns[3]: 'CompanyIndustry',
                                    df.columns[4]: 'CompanySpecialties',
                                    df.columns[5]: 'CompanyType',
                                    df.columns[6]: 'Country',
                                    df.columns[7]: 'City',
                                    df.columns[8]: 'Timezone'})
            
            # Grab max id
            id = Accounts.query.order_by(Accounts.AccountID.desc()).first()
        
            if id is None:
                    id = 1000
            else:
                id = id.AccountID + 10
            
            # ids = pd.read_sql("SELECT AccountID FROM Accounts", con=engine)

            # if ids['AccountID'].empty:
            #     id = 1000
                # else:
            #     id = ids['AccountID'].max() + 10
                
            for index, row in df.iterrows():
                dct = row.to_dict()
                dct.update({'AccountID': id, 'ClientID': current_user.ClientID})
                id += 10
                account = Accounts(**dct)
                db.session.add(account)
            db.session.commit()
            os.remove(filepath)        
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
    
@app.route('/clear_accounts/')
@login_required
def clear_accounts():
    Accounts.query.filter_by(ClientID=current_user.ClientID).delete()
    db.session.commit()
    flash('Accounts list cleared.')
    return redirect(url_for('accounts_list'))

# Accounts list    
@app.route('/accounts/accounts_list/')
@login_required
def accounts_list():
    try:
        accounts = None
        accounts = Accounts.query.filter_by(ClientID=current_user.ClientID)
            
        # Sorting
        sort_by = request.args.get('sort_by')
        order = request.args.get('order')
        
        if sort_by == 'revenue':
            if order == 'asc':
                accounts = accounts.order_by(Accounts.CompanyRevenue)
            else:
                accounts = accounts.order_by(Accounts.CompanyRevenue.desc())
        elif sort_by == 'head_count':
            if order == 'asc':
                accounts = accounts.order_by(Accounts.EmployeeHeadCount)
            else:
                accounts = accounts.order_by(Accounts.EmployeeHeadCount.desc())
        else:
                accounts = accounts.order_by(Accounts.AccountID.desc())
            
        # Industry filter query
        industries = db.session.query(Accounts.CompanyIndustry).distinct().filter_by(ClientID=current_user.ClientID).all()
        industries = sorted([str(industry).strip('(').strip(')').strip(',').strip("'") for industry in industries])
        if 'None' in industries:
            industries.remove('None')
        industry = request.args.get('industry')
        if industry:
            accounts = accounts.filter_by(CompanyIndustry=industry)
            
        # Company type filter query
        types = db.session.query(Accounts.CompanyType).distinct().filter_by(ClientID=current_user.ClientID).all()
        types = sorted([str(type).strip('(').strip(')').strip(',').strip("'") for type in types])
        if 'None' in types:
            types.remove('None')
        type = request.args.get('type')
        if type:
            accounts = accounts.filter_by(CompanyType=type)
        
        # Countries filter query                    
        countries = db.session.query(Accounts.Country).distinct().filter_by(ClientID=current_user.ClientID).all()
        countries = sorted([str(country).strip('(').strip(')').strip(',').strip("'") for country in countries])
        if 'None' in countries:
            countries.remove('None')
        country = request.args.get('country')
        if country:
            accounts = accounts.filter_by(Country=country)
        
        # Cities filter query
        cities = db.session.query(Accounts.City).distinct().filter_by(ClientID=current_user.ClientID).all()
        cities = sorted([str(city).strip('(').strip(')').strip(',').strip("'") for city in cities])
        # cities = sorted(['Hail' if str(city).strip('(').strip(')').strip(',').strip("'") == '"Ha\'Il"' \
        #     else str(city).strip('(').strip(')').strip(',').strip("'") for city in cities])
        if 'None' in cities:
            cities.remove('None')
        city = request.args.get('city')  
        if city:
            accounts = accounts.filter_by(City=city)
        
        # Timezone filter query
        timezones = db.session.query(Accounts.Timezone).distinct().filter_by(ClientID=current_user.ClientID).all()
        timezones = sorted([str(timezone).strip('(').strip(')').strip(',').strip("'") for timezone in timezones])
        if 'None' in timezones:
            timezones.remove('None')
        timezone = request.args.get('timezone')
        if timezone:
            accounts = accounts.filter_by(Timezone=timezone)
                            
        return render_template('accounts_list.html', accounts=accounts,
            countries=countries, industries=industries, types=types, cities=cities,
            timezones=timezones)
    except:
        flash('Error loading database, please try again.')
        return redirect(url_for('accounts'))


# Update account
@app.route('/accounts/<int:id>', methods=['GET', 'POST'])
@login_required
def account(id):
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
            return render_template('account.html', form=form, account=account)
        
    return render_template('account.html', form=form, account=account, id=id)        
            
            
# Delete account
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
                            Country=form.country.data, 
                            City=form.city.data, 
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
@login_required
def accounts():
        return render_template('accounts.html')


@app.route('/leads/')
@login_required
def leads():
    return render_template('leads.html')

@app.route('/opportunities/')
@login_required
def opportunities():
    return render_template('opportunities.html')

@app.route('/sales/')
@login_required
def sales():
    return render_template('sales.html')

@app.route('/marketing/')
@login_required
def marketing():
    return render_template('marketing.html')

@app.route('/service/')
@login_required
def service():
    return render_template('service.html')

@app.route('/analytics/')
@login_required
def analytics():
    assistant = client.beta.assistants.retrieve("asst_X75bBijkhsWoJDJm2IYUTK44")
    thread = client.beta.threads.create()
    run = client.beta.threads.runs.create_and_poll(thread_id=thread.id,
                                                   assistant_id=assistant.id,
                                                   instructions="Please provide insights on the accounts, useful statistics on aspects of the data, and accounts \
    that could be good potential clients and your reasoning as for why. The name of our company is \
      ERP Center, Inc., and we connect companies with SAP software catered to their specific needs and demands.")
    if run.status == 'completed': 
        message = client.beta.threads.messages.list(thread_id=thread.id)
        message = json.loads(message.json())
        message = message['data'][0]['content'][0]['text']['value']
    else:
        message = None
    
    return render_template('analytics.html', message=message)

@app.route('/help/')
@login_required
def help():
    return render_template('help.html')

@app.route('/home')
@login_required
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
    
