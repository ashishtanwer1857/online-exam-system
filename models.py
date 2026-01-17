from extensions import db
class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(200),unique=True,nullable=False)
    password=db.Column(db.String(200),nullable=False)
    role=db.Column(db.String(10),nullable=False,default='Student')

class Exam(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(200),nullable=False)
    description=db.Column(db.Text,nullable=True)
    duration=db.Column(db.Integer,nullable=False)
    created_by=db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)

class Question(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    exam_id= db.Column(db.Integer,db.ForeignKey('exam.id'),nullable=False)
    question_text=db.Column(db.Text,nullable=False)
    option_a=db.Column(db.String(200),nullable=False)
    option_b=db.Column(db.String(200),nullable=False)
    option_c=db.Column(db.String(200),nullable=False)
    option_d=db.Column(db.String(200),nullable=True)

    correct_option=db.Column(db.String(1),nullable=False)

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id'),
        nullable=False
    )

    exam_id = db.Column(
        db.Integer,
        db.ForeignKey('exam.id'),
        nullable=False
    )

    score = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Integer, nullable=False)
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
    exam = db.relationship('Exam',backref='results')
    user=db.relationship('User',backref='results')
