from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a6295f93be3b219d7fe9eaccdb60bbb3ff7f29b09ab2507e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://CM2305.group18.1920:Mw2Z4DeYMm62fPG@csmysql.cs.cf.ac.uk:3306/CM2305_group18_1920'
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)


from claudeFlask import index
