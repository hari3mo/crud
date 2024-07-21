from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

url_for('static', filename='style.css')

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/leads/')
def leads():
    return render_template("leads.html")


@app.route('/accounts/')
def accounts():
    return render_template("accounts.html")

@app.route('/test/')
def test():
    return render_template("py.html")
    


# @app.route('/<loop>/')
# def test(loop):
#         return f"Hello {loop}"
    
# @app.route('/admin/')
# def admin():
#     return redirect(url_for("test", loop='hello'))

if __name__ == "__main__":
    app.run(debug=True)
    
