from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:MyNewPass@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner=db.relationship('User', backref='blog')

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.route('/', methods=['GET'])
def main():
    return redirect("/index")

@app.route('/blog', methods=['GET'])
def blog():
    encoded_id = request.args.get("id", "")
    encoded_user = request.args.get("user", "")
    if encoded_id == "":
        if encoded_user == "":
            owners = User.query.all()
            entries = Blog.query.all()
            return render_template( 'blog.html',
                                    title="Build a Blog", 
                                    entries=entries,
                                    users=owners,
                                    id="",
                                    owner_name="")
        else:
            owner = User.query.filter_by(username=encoded_user).first()
            entries = Blog.query.filter_by(owner_id=owner.id).all()
            return render_template( 'blog.html',
                                    title="Build a Blog",
                                    entries=entries,
                                    users="",
                                    id="",
                                    owner_name=encoded_user)
    else:
        entry = Blog.query.get(encoded_id)
        owner = User.query.filter_by(id=entry.owner_id).first()
        return render_template( 'blog.html',
                                title="Build a Blog", 
                                entries=entry,
                                users="",
                                id=encoded_id,
                                owner_name=owner.username)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    error1 = ""
    error2 = ""
    if request.method == 'POST':
        entry_name = request.form['title']
        if entry_name == "":
            error1="Please fill in the title"
        entry_body = request.form['body']
        if entry_body == "":
            error2="Please fill in the body"
        owner_id = ""
        if error1 == "" and error2 == "":
            owner = User.query.filter_by(username=session['user']).first()
            new_entry = Blog(entry_name, entry_body, owner.id)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog?id=' + str(new_entry.id))

    return render_template( 'newpost.html',
                            title="Add a Blog Entry",
                            error1=error1,
                            error2=error2)

def verifySpaceAndLength(text):
    result = False
    space=text.find(' ')
    if space > -1:
        result=True
    elif len(text) < 3 or len(text) > 20:
        result=True
    return result

@app.route('/create', methods=['POST'])
def create():
    return render_template('signup.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    username = request.form['username']
    password = request.form['password']
    verify = request.form['verify']

    error1=""
    error2=""
    error3=""

    if username=="":
        error1="That's not a valid username"
    elif verifySpaceAndLength(username):
        error1="That's not a valid username"

    if password=="":
        error2="That's not a valid password"
    elif verifySpaceAndLength(password):
        error2="That's not a valid password"

    if verify!=password:
        error3="Passwords don't match"
    
    if error1=="" and error2=="" and error3=="":
        user = User.query.filter_by(username=username).first()
        if user != None:
            flash("A user with that username already exists")
            return render_template( 'signup.html',
                                    error1=error1,
                                    error2=error2,
                                    error3=error3,
                                    username=username)
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            return render_template( 'newpost.html',
                                    title="Add a Blog Entry",
                                    error1=error1,
                                    error2=error2)
    else:
        return render_template( 'signup.html',
                                error1=error1,
                                error2=error2,
                                error3=error3,
                                username=username)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user != None:
            password = request.form['password']
            if user.password == password:
                session['user'] = user.username
                return redirect("/newpost")
            else:
                flash('wrong password')
                return render_template('login.html')
        else:
            flash(username + ' does not exist')
            return render_template('login.html')

@app.route('/index')
def index():
    authors = User.query.all()
    return render_template( 'index.html',
                            title="",
                            authors=authors)

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint == 'main' or request.endpoint == 'login' or request.endpoint == 'blog' or request.endpoint == 'index' or request.endpoint == 'create' or request.endpoint == 'signup'):
        return redirect("/login")

@app.route("/logout", methods=['GET'])
def logout():
    del session['user']
    return redirect("/blog")

app.secret_key = 'secret_key'

if __name__ == '__main__':
    app.run()