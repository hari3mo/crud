from flask import Flask, render_template, redirect, url_for, request, session
from datetime import timedelta

app = Flask(__name__)

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
        user = request.form['nm']
        session['user'] = user
        return redirect(url_for('index'))
    else:
        if 'user' in session:
            return redirect(url_for('index'))
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/user')
def user():
    if 'user' in session:
        usr = session['user']
        return f'<h1>{usr}</h1>'
    else:
        return redirect(url_for('login'))


# @app.route('/test/')
# def test():
#     return render_template("py.html")
    

# @app.route('/<loop>/')
# def test(loop):
#         return f"Hello {loop}"
    
# @app.route('/admin/')
# def admin():
#     return redirect(url_for("test", loop='hello'))

if __name__ == "__main__":
    app.run(debug=True)
    
