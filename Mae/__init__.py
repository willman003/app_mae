
from flask import Flask
# from flask_sqlalchemy import SQLAlchemy




app = Flask(__name__)
app.config['SECRET_KEY'] = "Impossible to guess"

#---CONFIG-----
app.config['DATABASE_FILE'] = 'du_lieu/ql_mae.db?check_same_thread=False'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True

# app.config['MAIL_SERVER'] = "smtp.gmail.com"
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USERNAME'] = 'willman0031@gmail.com'
# app.config['MAIL_PASSWORD'] = 'chugacon'
# app.config['MAIL_USE_TLS'] = False
# app.config['MAIL_USE_SSL'] = True

# db = SQLAlchemy(app)


import Mae.xu_ly.xu_ly_model
# import Mae.app_Web_ban_hang
import Mae.app_quan_ly
import Mae.app_admin