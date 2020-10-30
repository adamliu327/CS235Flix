from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

import CS235FLIX.adapters.repository as repo
import CS235FLIX.utilities.utilities as utilities
import CS235FLIX.movies.services as services


# Configure Blueprint
actors_blueprint = Blueprint('actors_bp', __name__)


@actors_blueprint.route('/actors', methods=['GET'])
def actors():
    # Read query parameters.
    actor_name = request.args.get("name")
    actor = services.get_actor(actor_name, repo.repo_instance)
    colleagues = services.actors_to_dict(actor['colleagues'])
    print("colleagues:", colleagues)
    movies = services.get_movies_by_id(actor['acted_movies'], repo.repo_instance)

    return render_template(
        'actors/actors.html',
        title='Actors',
        actors_title=actor['full_name'],
        actor=actor,
        colleagues=colleagues,
        movies=movies,
        selected_movies=utilities.get_selected_movies(),
        genre_urls=utilities.get_genre_and_urls(),
        actor_urls=utilities.get_actor_and_urls()
    )