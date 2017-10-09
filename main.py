from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/', methods=['GET'])
def index():

    entries = Blog.query.all()
    return render_template( 'blog.html',
                            title="Build a Blog", 
                            entries=entries,
                            id="")

@app.route('/blog', methods=['GET'])
def blog():
    encoded_id = request.args.get("id", "")
    if encoded_id == "":
        entries = Blog.query.all()
        return render_template( 'blog.html',
                                title="Build a Blog", 
                                entries=entries,
                                id="")
    else:
        entry = Blog.query.get(encoded_id)
        return render_template( 'blog.html',
                                title="Build a Blog",
                                entries=entry,
                                id=encoded_id)


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
        if error1 == "" and error2 == "":
            new_entry = Blog(entry_name, entry_body)
            db.session.add(new_entry)
            db.session.commit()
            return redirect('/blog?id=' + str(new_entry.id))

    return render_template( 'newpost.html',
                            title="Add a Blog Entry",
                            error1=error1,
                            error2=error2)

@app.route('/view-entry')
def view_entry():

    entry_id = int(request.form['entry-id'])
    entry = Blog.query.get(entry_id)

    return redirect('/blog?id=' + entry)


if __name__ == '__main__':
    app.run()