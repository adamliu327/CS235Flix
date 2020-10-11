from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

import CS235FLIX.adapters.repository as repo
import CS235FLIX.utilities.utilities as utilities
import CS235FLIX.movies.services as services


# Configure Blueprint
directors_blueprint = Blueprint('directors_bp', __name__)


@directors_blueprint.route('/directors', methods=['GET'])
def directors():
    # Read query parameters.
    director_name = request.args.get("name")
    director = services.get_director(director_name, repo.repo_instance)
    movies = services.get_movies_by_id(director['directed_movies'], repo.repo_instance)

    return render_template(
        'directors/directors.html',
        title='Director',
        directors_title=director['full_name'],
        director=director,
        movies=movies,
        selected_movies=utilities.get_selected_movies(),
        genre_urls=utilities.get_genre_and_urls(),
        actor_urls=utilities.get_actor_and_urls(),
        director_urls=utilities.get_director_and_urls()
    )