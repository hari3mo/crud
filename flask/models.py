from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import datetime

db = SQLAlchemy()

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
    AccountID = db.Column(db.Integer)
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
##############################################################################  

