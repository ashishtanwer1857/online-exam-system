import os
from flask import Flask,redirect,request,url_for,flash,session,render_template
from werkzeug.security import check_password_hash,generate_password_hash
from models import Exam, User, Question, Result
from extensions import db
def get_current_user():
    if "user_id" in session:
        return User.query.get(session["user_id"])
    return None

app= Flask(__name__)
app.secret_key="supersecretkey"
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key")
with app.app_context():
    db.create_all()
@app.route("/")
def homepage():
   if "user.id" in session:
       return redirect(url_for("dashboard"))
   return render_template("homepage.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

        # 1️⃣ Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered", "danger")
            return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password)

        # 3️⃣ Create user
        user = User(
            email=email,
            password=hashed_password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method=="POST":
        email= request.form.get("email")
        password= request.form.get("password")
        user= User.query.filter_by(email=email).first()
        if user is None:
            flash("no user found","danger")
            return redirect(url_for("login"))
        if not check_password_hash(user.password,password):
            flash("Wrong Password","danger")
            return redirect(url_for("login"))
        flash("login successfully","success")
        session["user_id"]=user.id
        return redirect(url_for("dashboard"))
    return render_template("login.html")
@app.route("/dashboard")
def dashboard():
    user=get_current_user()
    if not user:
        return redirect(url_for("login"))
    exams=Exam.query.all()
    
    return render_template("dashboard.html",user=user,exams=exams)
@app.route("/logout")
def logout():
    session.pop("user_id",None)
    return redirect(url_for("login"))
@app.route("/admin/exam/add", methods=["GET","POST"])
def add_exam():
    user= get_current_user()
    if not user:
        flash("Please Log In First!!","danger")
        return redirect(url_for("login"))
    if user.role !="Teacher":
        flash("Access Denied!! Only for the Staff","danger")
        return  redirect(url_for("dashboard"))
    if request.method=="POST":
        title=request.form.get("title")
        description=request.form.get("description")
        duration=request.form.get("duration")
        if not title or not duration:
            flash("Title and Duration are required")
            return redirect(url_for("add_exam"))
        exam= Exam (
            title=title,
            description=description,
            duration=duration,
            created_by=user.id
        )
        db.session.add(exam)
        db.session.commit()
        flash("Exam created successfully","success")
        return redirect(url_for("dashboard"))
    return render_template("add_exam.html")

@app.route("/Teacher/exam/<int:exam_id>/question/add", methods=["GET","POST"])
def add_question(exam_id):
    user= get_current_user()
    if not user:
        flash("Please Log In First!!","danger")
        return redirect(url_for("login"))
    if user.role !="Teacher":
        flash("Access Denied!! Only for the Staff","danger")
        return  redirect(url_for("dashboard"))
    exam=Exam.query.get_or_404(exam_id)
    if request.method=="POST":
        question_text=request.form.get("question_text")
        option_a=request.form.get("option_a")
        option_b=request.form.get("option_b")
        option_c=request.form.get("option_c")
        option_d=request.form.get("option_d")
        correct_option=request.form.get("correct_option")
        
        if not all ([question_text,option_a,option_b,option_c,option_d,correct_option]):
            flash("All Fields are required","danger")
            return redirect(url_for("add_question"))
        question = Question(
            exam_id=exam.id,
            question_text=question_text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option
        )

        db.session.add(question)
        db.session.commit()

        flash("Question added successfully", "success")
        return redirect(url_for("dashboard"))

    return render_template("add_question.html", exam=exam)

@app.route("/exam/<int:exam_id>")
def view_exam(exam_id):
    user = get_current_user()

    if not user:
        flash("Please login first", "danger")
        return redirect(url_for("login"))

    exam = Exam.query.get_or_404(exam_id)
    questions = Question.query.filter_by(exam_id=exam.id).all()

    return render_template(
        "view_exam.html",
        exam=exam,
        questions=questions,
        user=user
    )

@app.route("/exam/<int:exam_id>/submit", methods=["POST"])
def submit_exam(exam_id):
    user = get_current_user()

    if not user:
        flash("Please login first", "danger")
        return redirect(url_for("login"))

    exam = Exam.query.get_or_404(exam_id)

    existing_result = Result.query.filter_by(
        user_id=user.id,
        exam_id=exam.id
    ).first()

    if existing_result:
        flash("You have already attempted this exam", "warning")
        return redirect(url_for("dashboard"))

    questions = Question.query.filter_by(exam_id=exam.id).all()

    score = 0
    total = len(questions)

    for q in questions:
        selected = request.form.get(f"question_{q.id}")
        if selected == q.correct_option:
            score += 1

    
    result = Result(
        user_id=user.id,
        exam_id=exam.id,
        score=score,
        total=total
    )

    db.session.add(result)
    db.session.commit()

    flash(f"You scored {score} out of {total}", "success")
    return redirect(url_for("dashboard"))

@app.route("/results")
def results():
    user = get_current_user()

    if not user:
        flash("Please login first", "danger")
        return redirect(url_for("login"))

    results = Result.query.filter_by(user_id=user.id).all()

    return render_template(
        "results.html",
        results=results,
        user=user
    )

@app.route("/teacher/exam/<int:exam_id>/results")
def exam_results(exam_id):
    user = get_current_user()

    if not user:
        flash("Please login first", "danger")
        return redirect(url_for("login"))

    if user.role != "Teacher":
        flash("Access denied", "danger")
        return redirect(url_for("dashboard"))

    exam = Exam.query.get_or_404(exam_id)

    results = Result.query.filter_by(exam_id=exam.id).all()

    return render_template(
        "exam_results.html",
        exam=exam,
        results=results
    )

@app.route("/teacher/exam/<int:exam_id>/delete", methods=["POST"])
def delete_exam(exam_id):
    user = get_current_user()

    if not user:
        flash("Please login first", "danger")
        return redirect(url_for("login"))

    if user.role != "Teacher":
        flash("Access denied", "danger")
        return redirect(url_for("dashboard"))

    exam = Exam.query.get_or_404(exam_id)

    # 🔥 Delete related questions
    Question.query.filter_by(exam_id=exam.id).delete()

    # 🔥 Delete related results
    Result.query.filter_by(exam_id=exam.id).delete()

    # 🔥 Delete exam
    db.session.delete(exam)
    db.session.commit()

    flash("Exam deleted successfully", "success")
    return redirect(url_for("dashboard"))

if __name__=='__main__':
    app.run(debug=True)