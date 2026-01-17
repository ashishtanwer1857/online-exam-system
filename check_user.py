from app import app
from extensions import db
from models import User
with app.app_context():
    user=User.query.first()
    print(user.email,user.password, user.role)