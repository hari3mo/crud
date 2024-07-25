from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, EmailField
from wtforms.validators import DataRequired, Email
import datetime
from datetime import timedelta
import mysql.connector



# # Invalid URL
# @app.errorhandler(404)
# def page_not_found(e):
#     return render_template('404.html'), 404

# # Internal Server Error
# @app.errorhandler(500)
# def server_error(e):
#     return render_template('404.html'), 500


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://erpcrm:Erpcrmpass1!@aws-erp.cxugcosgcicf.us-east-2.rds.amazonaws.com:3306/erpcrmdb' # MySQL Database
app.config['SECRET_KEY'] = 'key'

app.permanent_session_lifetime = timedelta(minutes=30) # Sets session timeout duration


db = SQLAlchemy(app)


# Create Model
class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    
    # Create a string
    def __repr__(self):
        return '<Name %r>' % self.name


# Form Class
class TestForm(FlaskForm):
    name = StringField('UserID:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    email = EmailField('Email:', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

# Test Form
@app.route('/test/', methods=['GET', 'POST'])
def test():
    name = None
    password = None
    email = None
    form = TestForm()
    # Validate form
    if form.validate_on_submit():
        user = Test.query.filter_by(email=form.email.data).first()
        if user is None:     
            user = Test(name=form.name.data, email=form.email.data, password=form.password.data)
            db.session.add(user)
            db.session.commit()
            
        name = form.name.data
        password = form.password.data
        email = form.email.data
        form.name.data = ''
        form.email.data = ''
        form.password.data = ''
        flash('User added successfully.')
    our_users = Test.query.order_by(Test.date_added)
    return render_template('test.html', form=form, name=name, password=password, email=email, our_users=our_users)

# Test update
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = TestForm()
    user_to_update = Test.query.get_or_404(id)
    if form.validate_on_submit():
        user_to_update.name = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.password = request.form['password']
        try:
            db.session.commit()
            flash('User updated successfully.')
            return render_template('update.html', form=form, user_to_update=user_to_update)
        except:
            flash('User update failed.')
            return render_template('update.html', form=form, user_to_update=user_to_update)
    else:
        return render_template('update.html', form=form, user_to_update=user_to_update)
        
    



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




# Need login/user authentication
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
    
