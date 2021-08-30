from operator import pos
import os, math
from flask import Flask, url_for, request,session
from flask.helpers import flash
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
import sqlalchemy
from datetime import datetime
import json
from flask_mail import Mail
from werkzeug.utils import redirect, secure_filename

app = Flask("__name__")
# app.config.update(
#     MAIL_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL = True,
#     MAIL_USERNAME = 'pranaya9211@gmail.com',
#     MAIL_PASSWORD = ''
# )
# mail=Mail(app)

app.config['SECRET_KEY'] = '30d122bba7eac0a4a2fd6db318eeb509'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

with open("templates/config.json", "r") as f:
    url = json.load(f)["url"]
    # dhome = json.load(f)["home"]
    # dabout = json.load(f)["about"]

app.config['UPLOAD_FOLDER'] = url["path"]
class Posts(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    slug = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    img_file = db.Column(db.Text, nullable=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<post %r>' % self.title

class Contact(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(10), nullable=False)
    messege = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    def __repr__(self):
        return '<contact %r>' % self.name

@app.route("/")
@app.route("/home")
def home():
    posts = Posts.query.filter_by().all()
    last = math.floor(len(posts)/int(url["blog_num"]))
    page = request.args.get("number")
    if (not str(page).isnumeric() ):
        page = 1
    page= int(page)
    posts = posts[int(page-1)*int(url["blog_num"]):int(page-1)*int(url["blog_num"])+int(url["blog_num"])]
    if page == 1:
        prev = "#"
        next = "/?number="+str(page+1)

    elif page == last:
        next = "#"
        prev = "/?number="+str(page-1)
    else:
        next = "/?number="+str(page+1)
        prev = "/?number="+str(page-1)
    
   
    return render_template("index.html", url=url, posts=posts,prev=prev,next=next)

@app.route("/about")
def about():
    return render_template("about.html", url=url)

@app.route("/login", methods=['POST','GET'])
def login():
    if 'user' in session and session['user'] == url["username"]:
            return redirect("/dashboard")
    if request.method == 'POST':
        username = url["username"]
        password = url["password"]

        if request.form.get("username") == username and request.form.get("password")==password:
            session['user'] = "username"
            return redirect ("/dashboard")
        else:
            flash(f"unable to login","Danger")
            return redirect("/login")
    else:
        return render_template("login.html", url=url)

@app.route("/dashboard")
def dashboard():
    data = Posts.query.all()
    return render_template("dasboard.html",url=url,data=data)

@app.route("/post/<string:slug>", methods=['GET',"POST"])
def post(slug):
    post = Posts.query.filter_by(slug=slug).first()
    return render_template('post.html', url=url, post_data=post)

@app.route("/edit/<string:id>", methods=['GET',"POST"])
def edit(id):
    if request.method == "POST":
        title = request.form.get("title")
        slug = request.form.get("slug")
        img_file = request.form.get("imgfile")
        content = request.form.get("content")
        if id == '0':
            entey = Posts(title=title, slug=slug,content=content,img_file=img_file)
            db.session.add(entey)
            db.session.commit()
            return redirect("/dashboard")
        else:
            post = Posts.query.filter_by(id=id).first()
            post.title=title
            post.slug=slug
            post.img_file=img_file
            post.content=content
            db.session.commit()
            return redirect("/edit/"+id)
    post_data = Posts.query.filter_by(id=id).first()
    return render_template('edit.html', url=url,post_data=post_data)

@app.route("/contact", methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contact(name=name,email=email,phone_number=phone,messege=message)
        db.session.add(entry)
        db.session.commit()
        flash(f"Your message have beenn submited", "success")
        # mail.send_message(f"New message from blog {name}",
        #                     sender=email,
        #                     recipients = "pranaya9211@gmail.com",
        #                     body = message + "\n" + phone
        #                 )

    return render_template("contact.html",url=url)

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect("/login")

@app.route("/uploder", methods=['GET','POST'])
def uploder():
    if 'user' in session and session['user']==url["username"]:
        if request.method == 'POST':
            file1 = request.files['file1']
            file1.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename (file1.filename)))
            return redirect("/dashboard")
    return redirect("/dashboard")

@app.route("/delete/<string:id>")
def delete(id):
    post = Posts.query.filter_by(id=id).first()
    db.session.delete(post)
    db.session.commit()
    return redirect("/dashboard")

if __name__ == "__main__":
    app.run(debug=True)