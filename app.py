from flask import Flask,session
from views import views

app = Flask(__name__)
app.secret_key = '1234'
app.register_blueprint(views, url_prefix='/views')

if __name__ == '__main__':
    app.run(debug=True, port=8000)





