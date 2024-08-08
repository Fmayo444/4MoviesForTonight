from flask import Flask, request, render_template, jsonify
import requests
import pandas as pd

app = Flask(__name__)

API_KEY = '24961c82b0a3d52de26dc807f4ea5ca4'
BASE_URL = 'https://api.themoviedb.org/3'

def fetch_genres():
    response = requests.get(f"{BASE_URL}/genre/movie/list", params={'api_key': API_KEY})
    if response.status_code == 200:
        return response.json()['genres']
    return []

def fetch_movies(genre_id, start_year, end_year, min_vote_avarage):
    movies = []
    for year in range(start_year, end_year + 1):
        for page in range(1, 6):  # Fetch multiple pages to get more results
            response = requests.get(
                f"{BASE_URL}/discover/movie",
                params={
                    'api_key': API_KEY,
                    'with_genres': genre_id,
                    'primary_release_year': year,
                    'vote_average.gte': min_vote_avarage,
                    'page': page
                }
            )
            if response.status_code == 200:
                data = response.json()
                movies.extend(data['results'])
            else:
                break
    return movies

def get_genre_id(genre_name):
    response = requests.get(f"{BASE_URL}/genre/movie/list", params={'api_key': API_KEY})
    if response.status_code == 200:
        genres = response.json()['genres']
        for genre in genres:
            if genre['name'].lower() == genre_name.lower():
                return genre['id']
    return None


@app.route('/')
def index():
    genres = fetch_genres()
    return render_template('index.html', genres=genres)


@app.route('/recommend', methods=['POST'])
def recommend():
    genre = request.form.get('genre')
    start_year = int(request.form.get('start_year'))
    end_year = int(request.form.get('end_year'))
    min_vote = float(request.form.get('min_vote'))

    genre_id = get_genre_id(genre)

    if genre_id is None:
        return jsonify({"error": f"Genre '{genre}' not found."})

    movies = fetch_movies(genre_id, start_year, end_year, min_vote)

    if not movies:
        return jsonify({"error": "No movies found with the given criteria."})

    movie_df = pd.DataFrame(movies)
    movie_df = movie_df[['title', 'release_date', 'vote_average', 'overview']]

    return jsonify(movie_df.to_dict(orient='records'))


if __name__ == '__main__':
    app.run(debug=True)