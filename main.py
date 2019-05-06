# Modules to build the webserver its associates and mysql database.
from flask import Flask, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
# Setting up the database infrastructure.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:blogging@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '6ks9n20ml0fanb'

# Creating model persistent classes which are basically objects in python and tables in db
# The Object Relational Mapping
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    blog = db.Column(db.String(1000))

    def __init__(self, title, blog):
        self.title = title
        self.blog = blog

@app.route('/blog', methods=['GET','POST'])
def index():
    
    blogs = Blog.query.all()
    blog_id = request.args.get('id')

    if request.method == 'POST':
        title_empty, blog_empty = False, False
        title = request.form['title']
        blog = request.form['blog']
        if title.strip() == '':
            flash('Please enter title of your blog!')
            title_empty = True
        if blog.strip() == '':
            flash("Blog field can't be submitted empty.")
            blog_empty = True
        if title_empty or blog_empty:
            return render_template('add_blog.html', title=title.strip(), blog=blog.strip())
        else:
            new_blog = Blog(title, blog)
            db.session.add(new_blog)
            db.session.commit()
            return render_template('post.html', posted_blog=new_blog, tabtitle='Recent Blog')
    
    if blog_id:
        for blog in blogs:
            if blog.id == int(blog_id):
                posted_blog = blog
                return render_template('post.html', posted_blog=posted_blog, tabtitle='Build-a-blog')
    
    return render_template('index.html', tabtile='Build-a-blog',blogs=blogs)


@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    return render_template('add_blog.html',tabtitle='Add a blog!')

if __name__ == '__main__':
    app.run()
