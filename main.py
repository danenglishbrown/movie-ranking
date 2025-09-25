from flask import Flask, render_template, redirect, url_for, request, abort
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, FloatField, TextAreaField
from wtforms.validators import DataRequired
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['UPLOAD_FOLDER'] = 'static/images'
Bootstrap5(app)


class Base(DeclarativeBase):
    pass


# CREATE DB
db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movies.db"
db.init_app(app)


class EditForm(FlaskForm):
    rating = FloatField('Rating', validators=[DataRequired()])
    review = TextAreaField('Review', validators=[DataRequired()])
    submit = SubmitField('Update Movie')


class AddForm(FlaskForm):
    title = StringField('Movie Title', validators=[DataRequired()])
    year = IntegerField('Release Year', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    rating = FloatField('Rating')
    ranking = IntegerField('Ranking')
    review = TextAreaField('Review')
    img_url = StringField('Poster URL', validators=[DataRequired()])
    submit = SubmitField('Add Movie')


# CREATE MOVIE TABLE
class Movie(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    ranking: Mapped[int] = mapped_column(Integer, nullable=True)
    review: Mapped[str] = mapped_column(String(250), nullable=True)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)

    def get_image_url(self):
        if self.img_url.startswith(('http://', 'https://')):
            return self.img_url
        else:
            return url_for('static', filename=f'images/{self.img_url}')


# DEBUG ROUTE - Add this temporarily
@app.route("/debug")
def debug():
    debug_info = []

    # Check if static folder exists
    static_path = os.path.join(app.root_path, 'static', 'images')
    debug_info.append(f"Static images path: {static_path}")
    debug_info.append(f"Static images path exists: {os.path.exists(static_path)}")

    if os.path.exists(static_path):
        files = os.listdir(static_path)
        debug_info.append(f"Files in static/images: {files}")

    # Check what's in the database
    movies = Movie.query.all()
    for movie in movies:
        debug_info.append(f"Movie: {movie.title}, img_url: {movie.img_url}, generated_url: {movie.get_image_url()}")

    return "<br>".join(debug_info)


# Add routes
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    movie = db.get_or_404(Movie, id)
    form = EditForm(obj=movie)

    if form.validate_on_submit():
        movie.rating = form.rating.data
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))

    return render_template("edit.html", movie=movie, form=form)


@app.route("/delete/<int:id>")
def delete(id):
    movie = db.get_or_404(Movie, id)
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddForm()
    if form.validate_on_submit():
        new_movie = Movie(
            title=form.title.data,
            year=form.year.data,
            description=form.description.data,
            rating=form.rating.data,
            ranking=form.ranking.data,
            review=form.review.data,
            img_url=form.img_url.data
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("add.html", form=form)


# CREATE TABLE AND ADD SAMPLE DATA
with app.app_context():
    db.create_all()

    # Clear existing data and add fresh data
    Movie.query.delete()
    db.session.commit()

    # Define all movies to add - with corrected paths
    movies_to_add = [
        Movie(
            title="Phone Booth",
            year=2002,
            description="Publicist Stuart Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
            rating=7.3,
            ranking=10,
            review="My favourite character was the caller.",
            img_url="https://www.themoviedb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
        ),
        Movie(
            title="Puss in Boots: The Last Wish",
            year=2022,
            description="Puss in Boots discovers that his passion for adventure has taken its toll: he has burned through eight of his nine lives. Puss sets out on an epic journey to find the mythical Last Wish and restore his nine lives.",
            rating=8.3,
            ranking=9,
            review="A surprisingly deep and visually stunning animation that appeals to all ages.",
            img_url="https://www.themoviedb.org/t/p/w500/kuf6dutpsT0vSVehic3EZIqkOBt.jpg"
        ),
        Movie(
            title="Spirited Away",
            year=2001,
            description="During her family's move to the suburbs, a sullen 10-year-old girl wanders into a world ruled by gods, witches, and spirits, and where humans are changed into beasts.",
            rating=8.4,
            ranking=8,
            review="Hayao Miyazaki's masterpiece of animation and storytelling.",
            img_url="https://www.themoviedb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg"
        ),
        Movie(
            title="End of Watch",
            year=2012,
            description="Shot documentary-style, this film follows the daily lives of two young police officers in LA who are partners and friends, and what happens when they meet criminal forces greater than themselves.",
            rating=8.5,
            ranking=7,
            review="Gritty, authentic portrayal of police work with incredible chemistry between the leads.",
            img_url="endofwatch.jpg"
        ),
        Movie(
            title="Drive",
            year=2011,
            description="A mysterious Hollywood stuntman and mechanic moonlights as a getaway driver and finds himself in trouble when he helps out his neighbor in this action drama.",
            rating=8.6,
            ranking=6,
            review="Style and substance perfectly blended with an incredible soundtrack.",
            img_url="https://www.themoviedb.org/t/p/w500/602vevIURmpDfzbnv5Ubi6wIkQm.jpg"
        ),
        Movie(
            title="Harry Potter and the Deathly Hallows: Part 2",
            year=2011,
            description="Harry, Ron, and Hermione continue their quest to vanquish the evil Voldemort once and for all. Just as things begin to look hopeless, Harry discovers a trio of magical objects that endow him with powers to rival Voldemort's.",
            rating=8.7,
            ranking=5,
            review="A satisfying conclusion to an epic series that stayed true to the spirit of the books.",
            img_url="harrypotter.jpg"
        ),
        Movie(
            title="Princess Mononoke",
            year=1997,
            description="On a journey to find the cure for a Tatarigami's cruise, Ashitaka finds himself in the middle of a war between the forest gods and Tatara, a mining colony. In this quest he also meets San, the Mononoke Hime.",
            rating=8.8,
            ranking=4,
            review="A beautiful ecological fable with complex characters and stunning animation.",
            img_url="mononoke.jpg"
        ),
        Movie(
            title="Prisoners",
            year=2013,
            description="When Keller Dover's daughter and her friend go missing, he takes matters into his own hands as the police pursue multiple leads and the pressure mounts.",
            rating=9.0,
            ranking=3,
            review="A tense, morally complex thriller with powerhouse performances.",
            img_url="prisoners.jpg"
        ),
        Movie(
            title="Blade Runner 2049",
            year=2017,
            description="Young Blade Runner K's discovery of a long-buried secret leads him to track down former Blade Runner Rick Deckard, who's been missing for thirty years.",
            rating=9.1,
            ranking=2,
            review="A visually stunning and philosophically rich sequel that honors the original.",
            img_url="https://www.themoviedb.org/t/p/w500/gajva2L0rPYkEWjzgFlBXCAVBE5.jpg"
        ),
        Movie(
            title="Brothers",
            year=2009,
            description="A young man comforts his older brother's wife and children after he goes missing in Afghanistan.",
            rating=9.2,
            ranking=1,
            review="A powerful examination of PTSD and family dynamics with incredible performances.",
            img_url="brothers.jpg"
        )
    ]

    # Add all movies
    for movie in movies_to_add:
        db.session.add(movie)

    db.session.commit()


@app.route("/")
def home():
    movies = (
        Movie.query
             .order_by(Movie.rating.asc().nulls_last(), Movie.title.desc())
             .all()
    )
    return render_template("index.html", movies=movies)


if __name__ == '__main__':
    app.run(debug=True)
