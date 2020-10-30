
import pytest

import datetime

from sqlalchemy.exc import IntegrityError

from CS235FLIX.domain.model import Director, Actor, Genre, Movie, Review, User, make_review, make_genre_association

movie_year = 2020


def insert_user(empty_session, values=None):
    new_name = "adam"
    new_password = "1234567890"

    if values is not None:
        new_name = values[0]
        new_password = values[1]

    empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                          {'username': new_name, 'password': new_password})
    row = empty_session.execute('SELECT id from users where username = :username',
                                {'username': new_name}).fetchone()
    return row[0]


def insert_users(empty_session, values):
    for value in values:
        empty_session.execute('INSERT INTO users (username, password) VALUES (:username, :password)',
                              {'username': value[0], 'password': value[1]})
    rows = list(empty_session.execute('SELECT id from users'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_movie(empty_session):
    empty_session.execute(
        'INSERT INTO movies (title, release_year, description, hyperlink, image_hyperlink) VALUES '
        '("The Godfather 2", :release_year,'
        '"Ywwuyi", '
        '"https://www.imdb.com/title/tt0068646/", '
        '"https://i.loli.net/2020/10/10/Y79y2iUj5qGsrHz.png")',
        {'release_year': movie_year}
    )
    row = empty_session.execute('SELECT id from movies').fetchone()
    return row[0]


def insert_genres(empty_session):
    empty_session.execute(
        'INSERT INTO genres (name) VALUES ("Sci-Fi"), ("Action")'
    )
    rows = list(empty_session.execute('SELECT id from genres'))
    keys = tuple(row[0] for row in rows)
    return keys


def insert_movie_genre_associations(empty_session, movie_key, genre_keys):
    stmt = 'INSERT INTO movie_genres (movie_id, genre_id) VALUES (:movie_id, :genre_id)'
    for genre_key in genre_keys:
        empty_session.execute(stmt, {'movie_id': movie_key, 'genre_id': genre_key})


def insert_commented_article(empty_session):
    movie_key = insert_movie(empty_session)
    user_key = insert_user(empty_session)

    timestamp_1 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    timestamp_2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    empty_session.execute(
        'INSERT INTO reviews (user_id, movie_id, rating, review_text, timestamp) VALUES '
        '(:user_id, :movie_id, 8, "Comment 1", :timestamp_1),'
        '(:user_id, :movie_id, 9, "Comment 2", :timestamp_2)',
        {'user_id': user_key, 'movie_id': movie_key, 'timestamp_1': timestamp_1, 'timestamp_2': timestamp_2}
    )

    row = empty_session.execute('SELECT id from movies').fetchone()
    return row[0]


def make_movie(new_movie_date):
    movie = Movie(
        movie_id=1,
        title="The Godfather 2",
        release_year=new_movie_date,
        description="Ywwuyi",
        hyperlink="https://www.imdb.com/title/tt0068646/",
        image_hyperlink="https://i.loli.net/2020/10/10/Y79y2iUj5qGsrHz.png"
    )
    return movie


def make_user():
    user = User("adam", "1112223333")
    return user


def make_genre():
    genre = Genre("Sci-Fi")
    return genre


def test_loading_of_users(empty_session):
    users = list()
    users.append(("andrew", "1234"))
    users.append(("cindy", "1111"))
    insert_users(empty_session, users)

    expected = [
        User("andrew", "1234"),
        User("cindy", "999")
    ]
    assert empty_session.query(User).all() == expected


def test_saving_of_users(empty_session):
    user = make_user()
    empty_session.add(user)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT username, password FROM users'))
    assert rows == [("adam", "1112223333")]


def test_saving_of_users_with_common_username(empty_session):
    insert_user(empty_session, ("andrew", "1234"))
    empty_session.commit()

    with pytest.raises(IntegrityError):
        user = User("andrew", "111")
        empty_session.add(user)
        empty_session.commit()


def test_loading_of_article(empty_session):
    movie_key = insert_movie(empty_session)
    expected_movie = make_movie(2020)
    fetched_movie = empty_session.query(Movie).one()

    assert expected_movie == fetched_movie
    assert movie_key == fetched_movie.movie_id


def test_loading_of_tagged_movie(empty_session):
    movie_key = insert_movie(empty_session)
    genre_keys = insert_genres(empty_session)
    insert_movie_genre_associations(empty_session, movie_key, genre_keys)

    movie = empty_session.query(Movie).get(movie_key)
    genres = [empty_session.query(Genre).get(key) for key in genre_keys]

    for genre in genres:
        assert movie.is_tagged_by(genre)
        assert genre.is_applied_to(movie)


def test_loading_of_reviewed_movie(empty_session):
    insert_commented_article(empty_session)

    rows = empty_session.query(Movie).all()
    movie = rows[0]

    assert len(list(movie.reviews)) == 2

    for review in movie.reviews:
        assert review.movie is movie


def test_saving_of_review(empty_session):
    movie_key = insert_movie(empty_session)
    user_key = insert_user(empty_session, ("andrew", "1234"))

    rows = empty_session.query(Movie).all()
    movie = rows[0]
    user = empty_session.query(User).filter(User._User__user_name == "andrew").one()

    # Create a new Comment that is bidirectionally linked with the User and Article.
    review_text = "Some comment text."
    rating = 10
    review = make_review(review_text, rating, movie, user)

    # Note: if the bidirectional links between the new Comment and the User and
    # Article objects hadn't been established in memory, they would exist following
    # committing the addition of the Comment to the database.
    empty_session.add(review)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT user_id, movie_id, review_text, rating FROM reviews'))

    assert rows == [(user_key, movie_key, review_text, rating)]


def test_saving_of_movie(empty_session):
    movie = make_movie(movie_year)
    empty_session.add(movie)
    empty_session.commit()

    rows = list(empty_session.execute('SELECT release_year, title, description, hyperlink, image_hyperlink FROM movies'))
    date = movie_year
    assert rows == [(date,
                     "The Godfather 2",
                     "Ywwuyi",
                     "https://www.imdb.com/title/tt0068646/",
                     "https://i.loli.net/2020/10/10/Y79y2iUj5qGsrHz.png"
                     )]


def test_saving_tagged_movie(empty_session):
    movie = make_movie(movie_year)
    genre = make_genre()

    # Establish the bidirectional relationship between the Article and the Tag.
    make_genre_association(movie, genre)

    # Persist the Article (and Tag).
    # Note: it doesn't matter whether we add the Tag or the Article. They are connected
    # bidirectionally, so persisting either one will persist the other.
    empty_session.add(movie)
    empty_session.commit()

    # Test test_saving_of_article() checks for insertion into the articles table.
    rows = list(empty_session.execute('SELECT id FROM movies'))
    movie_key = rows[0][0]

    # Check that the tags table has a new record.
    rows = list(empty_session.execute('SELECT id, name FROM genres'))
    genre_key = rows[0][0]
    assert rows[0][1] == "Sci-Fi"

    # Check that the article_tags table has a new record.
    rows = list(empty_session.execute('SELECT movie_id, genre_id from movie_genres'))
    movie_foreign_key = rows[0][0]
    genre_foreign_key = rows[0][1]

    assert movie_key == movie_foreign_key
    assert genre_key == genre_foreign_key


def test_save_reviewed_article(empty_session):
    # Create Article User objects.
    movie = make_movie(movie_year)
    user = make_user()

    # Create a new Comment that is bidirectionally linked with the User and Article.
    review_text = "Some comment text."
    review = make_review(review_text, 10, movie, user)

    # Save the new Article.
    empty_session.add(movie)
    empty_session.commit()

    # Test test_saving_of_article() checks for insertion into the articles table.
    rows = list(empty_session.execute('SELECT id FROM movies'))
    movie_key = rows[0][0]

    # Test test_saving_of_users() checks for insertion into the users table.
    rows = list(empty_session.execute('SELECT id FROM users'))
    user_key = rows[0][0]

    # Check that the comments table has a new record that links to the articles and users
    # tables.
    rows = list(empty_session.execute('SELECT user_id, movie_id, review_text FROM reviews'))
    assert rows == [(user_key, movie_key, review_text)]