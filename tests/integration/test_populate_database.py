from sqlalchemy import select, inspect

from CS235FLIX.adapters.orm import metadata


def test_database_populate_inspect_table_names(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    assert inspector.get_table_names() == ['actor_actors', 'actors', 'directors', 'genres', 'movie_actors',
                                           'movie_directors', 'movie_genres', 'movies', 'reviews', 'users']


def test_database_populate_select_all_genres(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_tags_table = inspector.get_table_names()[3]

    with database_engine.connect() as connection:
        # query for records in table tags
        select_statement = select([metadata.tables[name_of_tags_table]])
        result = connection.execute(select_statement)

        all_tag_names = []
        for row in result:
            all_tag_names.append(row['name'])

        assert all_tag_names == ['Crime', 'Drama', 'Movie with director', 'Action', 'Sci-Fi', 'Movie with actors',
                                 'Adventure']


def test_database_populate_select_all_users(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_users_table = inspector.get_table_names()[9]

    with database_engine.connect() as connection:
        # query for records in table users
        select_statement = select([metadata.tables[name_of_users_table]])
        result = connection.execute(select_statement)

        all_users = []
        for row in result:
            all_users.append(row['username'])

        assert all_users == ['thorke', 'fmercury', 'mjackson', 'adamliu']


def test_database_populate_select_all_reviews(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_reviews_table = inspector.get_table_names()[8]

    with database_engine.connect() as connection:
        # query for records in table comments
        select_statement = select([metadata.tables[name_of_reviews_table]])
        result = connection.execute(select_statement)

        all_reviews = []
        for row in result:
            all_reviews.append((row['id'], row['user_id'], row['movie_id'], row['rating'], row['review_text']))

        assert all_reviews == [(1, 2, 1, 9, "Oh no, COVID-19 has hit New Zealand"),
                               (2, 1, 1, 8, "Yeah Freddie, bad news"),
                               (3, 3, 1, 7, "I hope it's not as bad here as Italy!"),
                               (4, 4, 1, 2, "hahahahhhha"),
                               (5, 4, 9, 10, "Best movie")]


def test_database_populate_select_all_articles(database_engine):
    # Get table information
    inspector = inspect(database_engine)
    name_of_movies_table = inspector.get_table_names()[7]

    with database_engine.connect() as connection:
        # query for records in table articles
        select_statement = select([metadata.tables[name_of_movies_table]])
        result = connection.execute(select_statement)

        all_movies = []
        for row in result:
            all_movies.append((row['id'], row['title']))

        nr_movies = len(all_movies)

        assert all_movies[0] == (1, 'The Godfather')
        assert all_movies[nr_movies // 2] == (8, 'The Dark Knight')
        assert all_movies[nr_movies - 1] == (14, 'Dolittle')
