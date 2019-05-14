# Modules to build the webserver its associates and mysql database.
from flask import Flask, request, render_template, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from hash_utility import make_pw_hash, check_pw_hash

app = Flask(__name__, static_url_path='/static')
app.config['DEBUG'] = True
# Setting up the database infrastructure.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogging@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '6ks9n20ml0fanb'

# Creating model persistent classes which are basically objects in python and tables in db
# The Object Relational Mapping, Models of (MVC)
class Blog(db.Model):
    """" Modeling blog object in python and respective table in db  """
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog = db.Column(db.String(1000))
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow )
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, blog, owner):
        self.title = title
        self.blog = blog
        self.owner = owner # what data type this need to be - it is a object the user object.

class User(db.Model):
    """" Modeling user object in python and respective table in db  """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    pw_hash = db.Column(db.String(120))
    blogz = db.relationship('Blog',backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

def space_checker(name):
    for char in name:
        if char == " ":
            return True
    return False


def char_count_checker(name):
    counter = 0
    for char in name:
        counter += 1
    if counter < 3 or counter > 20:
        return True
    else:
        return False


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = ""
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        # Validation of user entered information.
        if name.strip() == '':
            flash("User Name field can't be empty.")
        if password.strip() == '':
            flash("Password field can't be empty.")

        else: 
            user = User.query.filter_by(username=name).first()
            
            if not user:
                flash("User does not exist.")
            else:
                username = name
                
                if not check_pw_hash(password, user.pw_hash):
                    flash("")
                    flash("Password is incorrect.")
            
            if user and check_pw_hash(password, user.pw_hash):
                session['username'] = user.username
                flash('Logged in')
                return redirect('/newpost')

    return render_template('login.html',tabtitle='Login',username=username)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']
        verify = request.form['verify']

        # Check for avialability of the username choosen.

        users = User.query.all()
        for user in users:
            if user.username == username:
                flash("User name already exists!!")
                return render_template('signup.html')

        # Validation of Signup form username / password / verify.

        if username.strip() == '':
            flash('User Name can not be left unfilled.')
            return render_template('signup.html', username=username)
        elif space_checker(username):
            flash("User name can't have space character.")
            return render_template('signup.html', username=username)
        elif char_count_checker(username):
            flash("User name can have only 3-20 chars.")
            return render_template('signup.html', username=username)

        if password.strip() == '':
            flash("")
            flash('Please enter the password.')
            return render_template('signup.html', username=username)
        elif space_checker(password):
            flash("")
            flash("Password can't have space character.")
            return render_template('signup.html', username=username)
        elif char_count_checker(password):
            flash("")
            flash("Password can have only 3-20 chars.")
            return render_template('signup.html', username=username)

        if verify.strip() == '':
            flash("")
            flash("")
            flash('Please enter the password to verify.')
            return render_template('signup.html', username=username)
        elif password != verify:
            flash("")
            flash("")
            flash("Passwords not matching")
            return render_template('signup.html', username=username)
      
        else:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            session['username'] = user.username
            flash('Logged in')
            return redirect('/newpost')

    return render_template('signup.html', tabtitle='signup')


@app.route('/blog')
def index():
    user_name = request.args.get('user')
    blog_id = request.args.get('blog_id')
    if user_name:  
        user = User.query.filter_by(username=user_name).first()
        user_blogs = Blog.query.filter_by(owner=user) # this is not a list of user blogs
        blogs = [] # so thats why we created one.
        for blog in user_blogs:
            blogs.append(blog)
        blogs.reverse()
        return render_template('userblogs.html', blogs=blogs, tabtitle='Blogz!!', name=user_name)
    elif blog_id:
        blog = Blog.query.filter_by(id=int(blog_id)).first()
        return render_template('post.html', posted_blog=blog, tabtitle='Blogz!!')
    else:
        blogs = Blog.query.all()
        blogs.reverse()
        return render_template('allposts.html', blogs=blogs, tabtitle='All Blogz!')
    

@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    if session.get('username',False):
        title,blog = "", ""

        if request.method == 'POST':
            title = request.form['title']
            blog = request.form['blog']
        
            if title.strip() == '':
                flash('Please enter title of your blog!')
      
            if blog.strip() == '':
                flash("")
                flash("Blog field can't be submitted empty.")

            else:
                owner = User.query.filter_by(username=session['username']).first()
                new_blog = Blog(title, blog, owner)
                db.session.add(new_blog)
                db.session.commit()
                return render_template('post.html', posted_blog=new_blog, tabtitle='Recent Blog')

        return render_template('add_blog.html',tabtitle='Add a blog!', title=title, blog=blog)
    else:
        return redirect('/login')


@app.route('/home', methods=['GET'])
@app.route('/')
def home():
    users = User.query.all()
    return render_template('home.html', tabtitle='The Amigos Blogz', users=users)


@app.route('/logout', methods=['GET'])
def logout():
    if session.get('username',False):
        del session['username']
        flash("Logged out successfully!")
        return redirect('/home')
    else:
        return redirect('/home')


if __name__ == '__main__':
    app.run()
