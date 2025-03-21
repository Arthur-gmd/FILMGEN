import requests

class MovieAPIClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def search_movies(self, genre=None, year=None, min_vote_count=100):
        url = f"{self.base_url}/discover/movie"
        params = {
            'api_key': self.api_key,
            'language': 'fr-FR',
            'sort_by': 'popularity.desc',
            'vote_count.gte': min_vote_count,
        }
        if genre:
            params['with_genres'] = genre
        if year:
            params['primary_release_year'] = year

        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results', [])

    def get_movie_details(self, movie_id):
        url = f"{self.base_url}/movie/{movie_id}"
        params = {
            'api_key': self.api_key,
            'language': 'fr-FR',
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def get_movie_videos(self, movie_id):
        url = f"{self.base_url}/movie/{movie_id}/videos"
        params = {
            'api_key': self.api_key,
            'language': 'fr-FR',
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results', [])

    def search_movie_by_name(self, name):
        url = f"{self.base_url}/search/movie"
        params = {
            'api_key': self.api_key,
            'language': 'fr-FR',
            'query': name,
            'sort_by': 'popularity.desc',
            'page': 1,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get('results', [])[:3]
