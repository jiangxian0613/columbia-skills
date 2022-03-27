from flask import Flask
from flask import render_template
from flask import Response, request, jsonify, redirect, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from helpers import apology, login_required
from werkzeug.utils import secure_filename
import uuid as uuid
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/images/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure database
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'
bcrypt = Bcrypt(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(50), nullable=False, unique=True)
    passwordhash = db.Column(db.String(80), nullable=False, unique=True)
    services = db.relationship('Service', backref='creator', lazy=True)
    user_comments = db.relationship('Comment', backref='commentor', lazy=True)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    image_file = db.Column(db.String(50), nullable=False, default='/static/images/image_placeholder.png')
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_comments = db.relationship('Comment', backref='service', lazy=True)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    commentor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
@login_required
def home():
    services_available = Service.query.all()
    return render_template('home.html', services=services_available)

@app.route('/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    if request.method == "POST":
        if not request.form.get("title"):
            return apology("Missing title")
        file = request.files['image']
        if not request.form.get("description"):
            return apology("Missing description")
        
        # Save the image
        if file.filename == '':
            return apology("No selected file")

        if not (file or allowed_file(file.filename)):
            return apology("Image not allowed")
        
        pic_filename = secure_filename(file.filename)
        pic_name = str(uuid.uuid1()) + "_" + pic_filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))

        # Add to database
        new_service = Service(title=request.form.get("title"), description=request.form.get("description"), image_file="/static/images/"+pic_name, creator_id=session["user_id"])
        db.session.add(new_service)
        db.session.commit()

        return redirect("/account")
    else: 
        return render_template('addservice.html')
    

@app.route('/view_service', methods=['GET', 'POST'])
@login_required
def view_service():
    if request.method == "POST":
        id = request.args.get("id")
        if not id:
            return apology("No link to service")
        service = Service.query.filter_by(id=int(id)).first()
        if not service:
            return apology("Not such service")
        new_comment = Comment(text=request.form.get("comment"), service_id=int(id), commentor_id=session["user_id"])
        db.session.add(new_comment)
        db.session.commit()
        comments = service.service_comments
        if not request.form.get("comment"):
            return apology("No comments entrered")
        return render_template('service.html', service = service, comments = comments)
    else:
        id = request.args.get("id")
        if not id:
            return apology("No link to service")
        service = Service.query.filter_by(id=int(id)).first()
        if not service:
            return apology("Not such service")
        comments = service.service_comments
        return render_template('service.html', service = service, comments = comments)

@app.route('/account')
@login_required
def account():
    user = User.query.filter_by(id=session['user_id']).first()
    if not user:
        return apology("User not found")
    return render_template('account.html', user=user, services=user.services)

@app.route('/search/<search_entry>', methods=['GET', 'POST'])
@login_required
def search(search_entry=None):
    # Array to store our search results
    results = []
    # Iterate our services to find matches
    # for key, value in services.items():
    #     service = value
    #     # Putting the title to lower case
    #     service_title = service['title'].lower()
    #     # Check if characters in the search entry match a title
    #     if search_entry in service_title:
    #         results.append(service)
    return render_template('searchresults.html', results = results)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        if not request.form.get("email"):
            return apology("Missing email", 404)
        if not request.form.get("password"):
            return apology("Missing password", 404)
        
        user = User.query.filter_by(email=request.form.get("email")).first()
        if not user:
            return apology("No such user", 404)
        
        if not bcrypt.check_password_hash(user.passwordhash, request.form.get("password")):
            return apology("Wrong password", 404)
        
        session['user_id'] = user.id
        return redirect("/")
    else: 
        return render_template('login.html')

@app.route("/logout")
def logout():
    """Log user out"""
    session.clear()
    return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    session.clear()    
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("Missing username", 404)
        if not request.form.get("email"):
            return apology("Missing email", 404)
        if not request.form.get("password"):
            return apology("Missing password", 404)
        if not request.form.get("confirmation"):
            return apology("Missing password confirmation", 404)
        if User.query.filter_by(username=request.form.get("username")).first():
            return apology("Username taken. Please choose something else", 404)
        if User.query.filter_by(username=request.form.get("email")).first():
            return apology("Account already created with email. Please log in.", 404)

        if User.query.filter_by(email=request.form.get("email")).first():
            return apology("Email taken. Please choose something else", 404)
        
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match", 404)

        hashed_password = bcrypt.generate_password_hash(request.form.get("password"))
        new_user = User(username=request.form.get("username"), email=request.form.get("email"), passwordhash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect("/")
    else: 
        return render_template('register.html')

if __name__ == '__main__':
   app.run(debug = True)