from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm,LoginForm , RateMovieForm,NewMovieForm,CreateListForm
from flask_gravatar import Gravatar
import requests

MOVIE_DB_API_KEY = "686548ae8bdc2048ba00af9d9df322d2"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies.db"
#Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.app_context().push()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Movie(db.Model):
    list_id = db.Column(db.Integer, db.ForeignKey("list.id"))
    parent_list = relationship("List", back_populates="movies")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    movie_author = relationship("User", back_populates="movies")
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=True)
    year = db.Column(db.String(250),  nullable=True)
    description = db.Column(db.String(250),  nullable=True)
    rating = db.Column(db.String(250), nullable=True)
    ranking = db.Column(db.String(250),  nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=True)
    category=db.Column(db.String(250),nullable=True)
       #*******Add child relationship*******#
    #"users.id" The users refers to the tablename of the Users class.
    #"comments" refers to the comments property in the User class.
   

    

    def __repr__(self):
        return '<User %r>' % self.username

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    posts = relationship("List", back_populates="author")
    #*******Add parent relationship*******#
    #"comment_author" refers to the comment_author property in the Comment class.
    movies = relationship("Movie", back_populates="movie_author")

class List(db.Model):
    _tablename_="list"
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(100))
    #Create Foreign Key, "users.id" the users refers to the tablename of User.
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    #Create reference to the User object, the "posts" refers to the posts protperty in the User class.
    author = relationship("User", back_populates="posts")

     #***************Parent Relationship*************#
    movies = relationship("Movie", back_populates="parent_list")

db.create_all()


@app.route("/")
def home():
    #This line creates a list of all the movies sorted by rating
    my_movie_data = Movie.query.all()
    all_movies=my_movie_data[::-1]
    all_list=List.query.all()
    return render_template("index.html", movies=all_movies,list=all_list)

@app.route('/show_list/<int:list_id>',methods=["GET", "POST"])
def show_list(list_id):
    requested_list = list_id
    result = Movie.query.filter(Movie.list_id==requested_list).all()
    return render_template("det_list.html",result=result)



@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
          
    return render_template("login.html", form=form)


@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():

        hash_and_salted_password = generate_password_hash(
            form.password.data,
            method='pbkdf2:sha256',
            salt_length=8
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_and_salted_password,
        )
        db.session.add(new_user)
        db.session.commit()
        
        return redirect(url_for("home"))

    return render_template("register.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get("id")
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("edit.html", movie=movie, form=form)

@app.route("/delete", methods=["GET", "POST"])
def delete_movie():
    movie_id = request.args.get("id")
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    category= SelectField('Movie Category', choices=[('horror', 'horror'), ('action', 'Action'), ('Comedy', 'Comedy')],validators=[DataRequired()])
    submit = SubmitField("Add Movie")

@app.route("/create_list" ,methods=["GET", "POST"])
def create_list():
    form = CreateListForm()
    if form.validate_on_submit():
        new_list = List(
            name=form.list_name.data,
            author=current_user,
        )
        db.session.add(new_list)
        db.session.commit()
        return redirect(url_for("show_all_list"))
    return render_template("create_list.html", form=form)

@app.route("/list", methods=["GET", "POST"])
def show_all_list():
    all_list= List.query.all()
    return render_template("list.html", list=all_list, current_user=current_user)

@app.route("/delete_list", methods=["GET", "POST"])
def delete_list():
    list_id = request.args.get("id")
    list_to_delete = List.query.get(list_id)
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add/<int:list_id>", methods=["GET", "POST"])
def add_movie(list_id):
    requested_list = list_id
    requested_list = List.query.get(list_id)
    
    form = FindMovieForm()
    if form.validate_on_submit():
        movie_title = form.title.data
        category=form.category.data
        requested_list=requested_list
        API_KEY = MOVIE_DB_API_KEY
        MOVIE_SEARCH_ENDPOINT = f'https://api.themoviedb.org/3/search/movie?api_key='
        response = requests.get(f'{MOVIE_SEARCH_ENDPOINT}{API_KEY}&query={movie_title}')
        data = response.json()["results"]
        return render_template("select.html", options=data, category = category,list=requested_list)
      
    return render_template("add.html", form=form)

@app.route("/find/<int:list_id>",methods=["GET", "POST"])
def find_movie(list_id):
    movie_api_id = request.args.get("id")
    category = request.args.get("category")
    requested_list=List.query.get(list_id)
   
    if movie_api_id:
        movie_api_url = f"{MOVIE_DB_INFO_URL}/{movie_api_id}"
        #The language parameter is optional, if you were making the website for a different audience 
        #e.g. Hindi speakers then you might choose "hi-IN"
        response = requests.get(movie_api_url, params={"api_key": MOVIE_DB_API_KEY, "language": "en-US"})
        data = response.json()
        new_movie = Movie(
            title=data["title"],
            #The data in release_date includes month and day, we will want to get rid of.
            year=data["release_date"].split("-")[0],
            img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
            category = category,
            description=data["overview"],
            movie_author=current_user,
            parent_list=requested_list
           
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for("rate_movie",id=new_movie.id))

@app.route("/find_category")
def find_category():
    category = request.args.get("category")
    result = Movie.query.filter(Movie.category==category).all()
    return render_template("category.html", category1=result)



if __name__ == '__main__':
    app.run(debug=True)
