import smtplib
from flask import Flask, flash, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,SelectField,TextAreaField
from wtforms.validators import DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm,LoginForm , RateMovieForm,NewMovieForm,CreateListForm
from flask_gravatar import Gravatar
import requests
from datetime import date, datetime
import os
MOVIE_DB_API_KEY = "686548ae8bdc2048ba00af9d9df322d2"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"
YOUR_ACCESS_KEY = "92a3f583a5fac57093ba6878c54a7268"
Rapid_API_KEY = os.environ.get("RAPI-KEY") 





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

class NewsArticles(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(250))
    image = db.Column(db.String(250))
    description = db.Column(db.String(250))
    url=db.Column(db.String(250))
    author=db.Column(db.String(250))

class Popular_Movies(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(250))
    image = db.Column(db.String(250))
    description = db.Column(db.String(250))
    numberOfEpisodes = db.Column(db.String(250))

class Reviews(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    image = db.Column(db.String(250))
    review_text=db.Column(db.String(250))
    author=db.Column(db.String(250))
    reviewTitle =db.Column(db.String(250))
  

db.create_all()


class FindMovieForm(FlaskForm):
    title = StringField("Movie Title", validators=[DataRequired()])
    category= SelectField('Movie Category', choices=[('horror', 'horror'), ('action', 'Action'), ('Comedy', 'Comedy')],validators=[DataRequired()])
    submit = SubmitField("Add Movie")

class FindCategoryForm(FlaskForm):
    category= SelectField('Movie Category', choices=[('horror', 'horror'), ('action', 'Action'), ('Comedy', 'Comedy')],validators=[DataRequired()])
    submit = SubmitField("Filter")


class ContactForm(FlaskForm):
    Name=StringField("Name", validators=[DataRequired()])
    Email=StringField("Email", validators=[DataRequired()])
    Phone=StringField("Phone", validators=[DataRequired()])
    Message=TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Submit Message")

today = date.today()
now = datetime.now().hour
news_list = []
news_parameters= {
    "access_key" : YOUR_ACCESS_KEY,
    "languages" : "en",
    "categories" : "entertainment","-sports"
    "date":f"{today}",

}
if now==20:
    response = requests.get("http://api.mediastack.com/v1/news", params=news_parameters)
    news_data = response.json()
    news_list = news_data["data"][::5]


for i in news_list:
    if now == 20:
        new_article = NewsArticles(    
                title=i["title"],
                description =i["description"],
                url = i["url"],
                image=i["image"],
                author = i["author"]

            )
        db.session.add(new_article)
        db.session.commit()

#code for getting popular tv shows and storing them in the database
url = "https://imdb8.p.rapidapi.com/title/get-most-popular-tv-shows"

querystring = {"homeCountry":"US","purchaseCountry":"US","currentCountry":"US"}

headers = {
	"X-RapidAPI-Key": "b3edda5913mshcc905235f1241e8p132e18jsne2ffb0d927d6",
	"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
}
if now ==16:
    response = requests.request("GET", url, headers=headers, params=querystring)
    data =response.json()
    new_data = data[0:6]
    empty_data = []
    for data in new_data:
        stripped_data = data.strip("/title/ /")
        empty_data.append(stripped_data)


#finding details of the tv shows that are popular
if now == 16:
    for i in empty_data:    
        url = "https://imdb8.p.rapidapi.com/title/find"

        querystring = {"q":f"tt{i}"}

        headers = {
	        "X-RapidAPI-Key": "b3edda5913mshcc905235f1241e8p132e18jsne2ffb0d927d6",
	        "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
        }

        response = requests.request("GET", url, headers=headers, params=querystring)
        data = response.json()
        tv_news=data["results"]
        tv_data = tv_news[0]
            #print(tv_data["image"]["url"])
        new_tvShow = Popular_Movies(    
                title=tv_data["title"],
                image=tv_data["image"]["url"],
                numberOfEpisodes =tv_data["numberOfEpisodes"]
            )
        db.session.add(new_tvShow)
        db.session.commit()

        
url = "https://imdb8.p.rapidapi.com/title/get-most-popular-tv-shows"

querystring = {"homeCountry":"US","purchaseCountry":"US","currentCountry":"US"}

headers = {
	"X-RapidAPI-Key": "b3edda5913mshcc905235f1241e8p132e18jsne2ffb0d927d6",
	"X-RapidAPI-Host": "imdb8.p.rapidapi.com"
}
if now ==16:
    response = requests.request("GET", url, headers=headers, params=querystring)
    data =response.json()
    new_data = data[0:6]
    empty_data = []
    for data in new_data:
        stripped_data = data.strip("/title/ /")
        empty_data.append(stripped_data)


if now == 16:
    for i in empty_data:   
         url = "https://imdb8.p.rapidapi.com/title/get-reviews"
         querystring = {"tconst":f"tt{i}","currentCountry":"US","purchaseCountry":"US"}

         headers = {
	        "X-RapidAPI-Key": "b3edda5913mshcc905235f1241e8p132e18jsne2ffb0d927d6",
	        "X-RapidAPI-Host": "imdb8.p.rapidapi.com"
                    }

         response = requests.request("GET", url, headers=headers, params=querystring)
         data = response.json()

         new_review = Reviews( 
           
            image = data["featuredUserReview"]["base"]["image"]["url"],
            review_text=data["featuredUserReview"]["review"]["reviewText"],
            author=data["featuredUserReview"]["review"]["author"]["displayName"],
            reviewTitle= data["featuredUserReview"]["review"]["reviewTitle"]
            
            )
         db.session.add(new_review)
         db.session.commit()


@app.route("/")
def home():
    news = NewsArticles.query.all()
    popular = Popular_Movies.query.all()
    my_movie_data = Movie.query.all()
    reviews = Reviews.query.all()
    all_movies=my_movie_data[::-1]
    first_three_movies = all_movies[0:3]
    last_three_movies=all_movies[4:7]
    new_popular = popular[0:3]
    next_popular = popular[4:7]

    return render_template(
    "index.html",popular=popular,news=news,new_popular=new_popular,next_popular=next_popular,
     movies=all_movies,first_three_movies=first_three_movies,
     last_three_movies=last_three_movies,reviews=reviews
     )


@app.route("/watchlist",methods=["GET", "POST"])
def watchlist(): 
    my_movie_data = Movie.query.all()
    all_movies=my_movie_data[::-1]
    all_list=List.query.all()
    return render_template("watchlist.html",movies=all_movies,list=all_list)


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
        flash('Successfully registered!! ')
  
        
        return redirect(url_for("login"))

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
    return redirect(url_for('watchlist'))



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
        return redirect(url_for('watchlist'))
    return render_template("create_list.html", form=form)


@app.route("/delete_list", methods=["GET", "POST"])
def delete_list():
    list_id = request.args.get("id")
    list_to_delete = List.query.get(list_id)
    db.session.delete(list_to_delete)
    db.session.commit()
    return redirect(url_for('watchlist'))


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
    all_list=List.query.all()

    return render_template("category.html", category1=result, all_list = all_list)

@app.route("/category", methods=["GET", "POST"])
def filter_category():
    name = request.args.get("category")
    result = Movie.query.filter(Movie.category==name).all()
    all_list=List.query.all()

    return render_template("category.html",category1=result,all_list=all_list)


@app.route("/contact" , methods=["GET", "POST"])
def contact():
    form=ContactForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to send contact messages.")
            return redirect(url_for("login"))
        name = form.Name.data
        email= form.Email.data
        phone=form.Phone.data
        message=form.Message.data
        my_email = "kimulumichael@gmail.com"
        password = "mbxccnyfiymvmmnv"
        with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email,
                        to_addrs=my_email,
                        msg=f"{name}{email}{phone}{message}")
        flash("Message sent successfully!!")
        


    return render_template("contact.html", form=form)



if __name__ == '__main__':
    app.run(debug=True)
