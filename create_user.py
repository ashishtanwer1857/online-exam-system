from app import app
from extensions import db
from models import User
from werkzeug.security import generate_password_hash
with app.app_context():
    hashed_password= generate_password_hash('ashish123')
    user= User(email="ashishtanwer1856@gmail.com",password=hashed_password,role="Teacher")
    db.session.add(user)
    db.session.commit()

print("password hashed succesfully")




