from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import os, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
try: 
    os.makedirs(app.instance_path)
except OSError:
    pass

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

with app.app_context():
    db.create_all()

def username_enter(username):
    new_event = Event(name=username)
    db.session.add(new_event)
    db.session.commit()    

if __name__ == '__main__':
    app.run(debug=True)