from datetime import date, datetime

import pytest

from CS235FLIX.adapters.database_repository import SqlAlchemyRepository
from CS235FLIX.domain.model import Director, Actor, Genre, Movie, Review, User, make_review
from CS235FLIX.adapters.repository import RepositoryException


def test_repository_can_add_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = User('Dave', '123456789')
    print(user)
    repo.add_user(user)

    repo.add_user(User('Martin', '123456789'))

    user2 = repo.get_user('dave')

    assert user2 == user and user2 is user


def test_repository_can_retrieve_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('fmercury')
    assert user == User('fmercury', '8734gfe2058v')


def test_repository_does_not_retrieve_a_non_existent_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('prince')
    assert user is None


def test_repository_can_retrieve_article_count(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    # Check that the query returned 177 Articles.
    assert number_of_movies == 14


def test_repository_can_add_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    number_of_movies = repo.get_number_of_movies()

    new_movie_id = number_of_movies + 1
    movie = Movie(
        movie_id=15,
        title='The Godfather 2',
        release_year=1972,
        description='The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to '
                    'his reluctant son.',
        hyperlink='https://www.imdb.com/title/tt0068646/',
        image_hyperlink='https://i.loli.net/2020/10/10/Y79y2iUj5qGsrHz.png'
    )
    repo.add_movie(movie)

    assert repo.get_movie(new_movie_id) == movie


def test_repository_can_retrieve_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(1)

    # Check that the Article has the expected title.
    assert movie.title == "The Godfather"

    # Check that the Article is commented as expected.
    review_one = [review for review in movie.reviews if review.review_text == 'Oh no, COVID-19 has hit New Zealand'][
        0]
    review_two = [review for review in movie.reviews if review.review_text == 'Yeah Freddie, bad news'][0]

    assert review_one.user.user_name == 'fmercury'
    assert review_two.user.user_name == "thorke"

    # Check that the Article is tagged as expected.
    assert movie.is_tagged_by(Genre('Crime'))
    assert movie.is_tagged_by(Genre('Drama'))


def test_repository_does_not_retrieve_a_non_existent_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(201)
    assert movie is None


def test_repository_can_retrieve_movies_by_date(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    articles = repo.get_movies_by_date(1999)

    # Check that the query returned 3 Articles.
    assert len(articles) == 2


def test_repository_does_not_retrieve_an_movie_when_there_are_no_movies_for_a_given_date(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    articles = repo.get_movies_by_date(3000)
    assert len(articles) == 0


def test_repository_can_retrieve_genres(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genres = repo.get_genres()

    len(genres) == 7

    genre_one = [genre for genre in genres if genre.genre_name == 'Crime'][0]
    genre_two = [genre for genre in genres if genre.genre_name == 'Drama'][0]
    genre_three = [genre for genre in genres if genre.genre_name == 'Movie with director'][0]
    genre_four = [genre for genre in genres if genre.genre_name == 'Action'][0]
    genre_five = [genre for genre in genres if genre.genre_name == 'Sci-Fi'][0]

    assert genre_one.number_of_tagged_movies == 3
    assert genre_two.number_of_tagged_movies == 8
    assert genre_three.number_of_tagged_movies == 5
    assert genre_four.number_of_tagged_movies == 6
    assert genre_five.number_of_tagged_movies == 5


def test_repository_can_get_first_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_first_movie()
    assert movie.title == 'The Godfather'


def test_repository_can_get_last_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_last_movie()
    assert movie.title == 'Dolittle'


def test_repository_can_get_movies_by_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_id([2, 5, 9])

    assert len(movies) == 3
    assert movies[0].title == 'Schindler\'s List'
    assert movies[1].title == 'The Shawshank Redemption'
    assert movies[2].title == 'Gekijouban Steins;Gate: Fuka ryouiki no dejavu'


def test_repository_does_not_retrieve_movie_for_non_existent_id(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_id([0, 10])

    assert len(movies) == 1
    assert movies[0].title == 'Captain America: Civil War'


def test_repository_returns_an_empty_list_for_non_existent_ids(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movies = repo.get_movies_by_id([0, 199])

    assert len(movies) == 0


def test_repository_returns_movie_ids_for_existing_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ids = repo.get_movie_ids_for_genre('Movie with actors')

    assert movie_ids == [10, 11, 12, 14]


def test_repository_returns_an_empty_list_for_non_existent_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie_ids = repo.get_movie_ids_for_genre('United States')

    assert len(movie_ids) == 0


def test_repository_returns_date_of_previous_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(6)
    previous_date = repo.get_date_of_previous_movie(movie)

    assert previous_date == 1994


def test_repository_returns_none_when_there_are_no_previous_movies(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(1)
    previous_date = repo.get_date_of_previous_movie(movie)

    assert previous_date is None


def test_repository_returns_date_of_next_movie(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(5)
    next_date = repo.get_date_of_next_movie(movie)

    assert next_date == 1999


def test_repository_returns_none_when_there_are_no_subsequent_movies(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(13)
    next_date = repo.get_date_of_next_movie(movie)

    assert next_date is None


def test_repository_can_add_a_genre(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    genre = Genre('Motoring')
    repo.add_genre(genre)

    assert genre in repo.get_genres()


def test_repository_can_add_a_comment(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    user = repo.get_user('thorke')
    movie = repo.get_movie(2)
    comment = make_review("Good movie", 10, movie, user)

    repo.add_review(comment)

    assert comment in repo.get_reviews()


def test_repository_does_not_add_a_review_without_a_user(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    movie = repo.get_movie(2)
    review = Review(movie, None, "Good!!!", 10, datetime.today())

    with pytest.raises(RepositoryException):
        repo.add_review(review)


def test_repository_can_retrieve_comments(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    assert len(repo.get_reviews()) == 5


def make_movie(new_movie_date):
    movie = Movie(
        movie_id=15,
        title='The Godfather 2',
        release_year=new_movie_date,
        description='The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to '
                    'his reluctant son.',
        hyperlink='https://www.imdb.com/title/tt0068646/',
        image_hyperlink='https://i.loli.net/2020/10/10/Y79y2iUj5qGsrHz.png'
    )
    return movie


def test_can_retrieve_a_movie_and_add_a_review_to_it(session_factory):
    repo = SqlAlchemyRepository(session_factory)

    # Fetch Article and User.
    movie = repo.get_movie(5)
    user = repo.get_user('thorke')

    # Create a new Comment, connecting it to the Article and User.
    review = make_review("Good movie", 10, movie, user)

    movie_fetched = repo.get_movie(5)
    user_fetched = repo.get_user('thorke')

    assert review in movie_fetched.reviews
    assert review in user_fetched.reviews