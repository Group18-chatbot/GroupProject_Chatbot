#from "folder_with_webapp_in" import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from claudeFlask import db, login_manager
from sqlalchemy import Table, Column, Integer, ForeignKey

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username= db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Grades(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False,primary_key=True)
    ModuleCode = db.Column(db.String(100),primary_key=True)
    ModuleName = db.Column(db.String(100),nullable=False)
    GradePercentage = db.Column(db.Integer,nullable=False)

class Timetable(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    Date = db.Column(db.String(100), primary_key=True)
    Time = db.Column(db.String(100), primary_key=True)
    ModuleCode = db.Column(db.String(100),nullable=False)
    ModuleName = db.Column(db.String(100),nullable=False)
    Location = db.Column(db.String(100),nullable=False)
    Type = db.Column(db.String(50),nullable=False)
    

class Sports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Sport = db.Column(db.String(120), nullable=False)
    Team1 = db.Column(db.String(100), nullable=False)
    Team2 = db.Column(db.String(100), nullable=False)
    Score = db.Column(db.String(3), nullable=False)