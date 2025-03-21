from flask import Flask, render_template, request, redirect, url_for, flash, session
from api_client import MovieAPIClient
from config import API_KEY, BASE_URL, IMAGE_BASE_URL, DATABASE_PATH
import random
from database import initialize_database, add_movie_rating, get_watched_movies, get_user, add_user, delete_movie_rating


app = Flask(__name__)
app.secret_key = 'supersecretkey'

initialize_database(DATABASE_PATH)
api_client = MovieAPIClient(API_KEY, BASE_URL)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    genres = ["Action", "Aventure", "Animation", "Comédie", "Crime", "Documentaire",
              "Drame", "Famille", "Fantastique", "Guerre", "Histoire", "Horreur",
              "Musique", "Mystère", "Romance", "Science-Fiction", "TV Movie", "Thriller", "Western"]
    return render_template('index.html', genres=genres)

@app.route('/search', methods=['POST'])
def search():
    if 'username' not in session:
        return redirect(url_for('login'))

    selected_genres = request.form.getlist('genre')
    years = request.form.getlist('year')

    if not selected_genres and not years:
        flash("Veuillez sélectionner au moins un genre ou une année.", "warning")
        return redirect(url_for('index'))

    genre_id = {
        "action": 28, "aventure": 12, "animation": 16, "comédie": 35, "crime": 80,
        "documentaire": 99, "drame": 18, "famille": 10751, "fantastique": 14,
        "guerre": 10752, "histoire": 36, "horreur": 27, "musique": 10402,
        "mystère": 9648, "romance": 10749, "science-fiction": 878, "tv movie": 10770,
        "thriller": 53, "western": 37
    }

    genre_ids = [genre_id[genre.lower()] for genre in selected_genres]

    movies = []
    for year in years:
        movies.extend(api_client.search_movies(genre=genre_ids[0] if genre_ids else None, year=year))

    if not movies:
        flash("Aucun film trouvé.", "info")
        return redirect(url_for('index'))

    selected_movies = random.sample(movies, min(3, len(movies)))
    return render_template('search_results.html', movies=selected_movies, image_base_url=IMAGE_BASE_URL)

@app.route('/search_by_name', methods=['POST'])
def search_by_name():
    if 'username' not in session:
        return redirect(url_for('login'))

    name = request.form['movie_name']
    if not name:
        flash("Veuillez entrer le nom du film.", "warning")
        return redirect(url_for('index'))

    movies = api_client.search_movie_by_name(name)

    if not movies:
        flash("Aucun film trouvé.", "info")
        return redirect(url_for('index'))

    return render_template('search_results.html', movies=movies, image_base_url=IMAGE_BASE_URL)

@app.route('/rate_movie', methods=['POST'])
def rate_movie():
    if 'username' not in session:
        return redirect(url_for('login'))

    movie_id = request.form['movie_id']
    rating = request.form['rating']

    add_movie_rating(DATABASE_PATH, session['username'], movie_id, rating)
    flash("Film noté avec succès!", "success")
    return redirect(url_for('index'))

@app.route('/library')
def library():
    if 'username' not in session:
        return redirect(url_for('login'))

    watched_movies = get_watched_movies(DATABASE_PATH, session['username'])
    movie_details = [api_client.get_movie_details(movie_id) for _, movie_id, _ in watched_movies]
    return render_template('library.html', movies=movie_details, image_base_url=IMAGE_BASE_URL)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        user = get_user(DATABASE_PATH, username)
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash("Nom d'utilisateur incorrect.", "warning")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if get_user(DATABASE_PATH, username):
            flash("Ce nom d'utilisateur est déjà pris.", "warning")
        else:
            add_user(DATABASE_PATH, username)
            flash("Utilisateur enregistré avec succès!", "success")
            return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/de', methods=['POST'])
def delete_movie():
    if 'username' not in session:
        return redirect(url_for('login'))

    movie_id = request.form['movie_id']
    delete_movie_rating(DATABASE_PATH, session['username'], movie_id)
    flash("Film supprimé de la bibliothèque avec succès!", "success")
    return redirect(url_for('library'))



@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))




if __name__ == '__main__':
    app.run(debug=True)
