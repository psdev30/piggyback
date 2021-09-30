from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def root():
    return render_template("login.html")


@app.route('/create_account')
def create_account():
    return render_template("create_account.html")


@app.route('/profile')
def profile():
    return render_template("profile.html")


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
