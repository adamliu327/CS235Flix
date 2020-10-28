from sqlalchemy import (
    Table, MetaData, Column, Integer, String, Date, DateTime,
    ForeignKey
)
from sqlalchemy.orm import mapper, relationship

from CS235FLIX.domain import model


metadata = MetaData()

users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('username', String(255), unique=True, nullable=False),
    Column('password', String(255), nullable=False)
)

reviews = Table(
    'reviews', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('user_id', ForeignKey('users.id')),
    Column('movie_id', ForeignKey('movies.id')),
    Column('rating', Integer, nullable=False),
    Column('review_text', String(1024), nullable=False),
    Column('timestamp', DateTime, nullable=False)
)

movies = Table(
    'movies', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String(255), nullable=False),
    Column('release_year', Integer, nullable=False),
    Column('description', String(1024), nullable=False),
    Column('hyperlink', String(255), nullable=False),
    Column('image_hyperlink', String(255), nullable=False)
)

directors = Table(
    'directors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('description', String(1024), nullable=False),
    Column('hyperlink', String(255), nullable=False),
    Column('image_hyperlink', String(255), nullable=False)
)

actors = Table(
    'actors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(255), nullable=False),
    Column('description', String(1024), nullable=False),
    Column('hyperlink', String(255), nullable=False),
    Column('image_hyperlink', String(255), nullable=False)
)

genres = Table(
    'genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(64), nullable=False)
)

movie_genres = Table(
    'movie_genres', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_id', ForeignKey('movies.id')),
    Column('genre_id', ForeignKey('genres.id'))
)

movie_actors = Table(
    'movie_actors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_id', ForeignKey('movies.id')),
    Column('actor_id', ForeignKey('actors.id'))
)

movie_directors = Table(
    'movie_directors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie_id', ForeignKey('movies.id')),
    Column('director_id', ForeignKey('directors.id'))
)

actor_actors = Table(
    'actor_actors', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('actor_id', ForeignKey('actors.id')),
    Column('colleague_id', Integer, nullable=False)
)


def map_model_to_tables():
    mapper(model.User, users, properties={
        '_User__user_name': users.c.username,
        '_User__password': users.c.password,
        '_User__reviews': relationship(model.Review, backref='_Review__user')
        # '__watched_movies': relationship(model.Movie, backref='__user')
    })
    mapper(model.Review, reviews, properties={
        '_Review__rating': reviews.c.rating,
        '_Review__review_text': reviews.c.review_text,
        '_Review__timestamp': reviews.c.timestamp,
    })
    movies_mapper = mapper(model.Movie, movies, properties={
        '_Movie__movie_id': movies.c.id,
        '_Movie__title': movies.c.title,
        '_Movie__release_year': movies.c.release_year,
        '_Movie__description': movies.c.description,
        '_Movie__hyperlink': movies.c.hyperlink,
        '_Movie__image_hyperlink': movies.c.image_hyperlink,
        '_Movie__reviews': relationship(model.Review, backref='_Review__movie')
    })
    mapper(model.Genre, genres, properties={
        '_Genre__genre_name': genres.c.name,
        '_Genre__movie_with_genre': relationship(
            movies_mapper,
            secondary=movie_genres,
            backref="_Movie__genres"
        )
    })
    mapper(model.Director, directors, properties={
        '_Director__director_full_name': directors.c.name,
        '_Director__description': directors.c.description,
        '_Director__hyperlink': directors.c.hyperlink,
        '_Director__image_hyperlink': directors.c.image_hyperlink,
        '_Director__directed_movies': relationship(
            movies_mapper,
            secondary=movie_directors,
            backref="_Movie__director"
        )
    })

    test = mapper(model.Actor, actors, properties={
        '_Actor__actor_full_name': actors.c.name,
        '_Actor__description': actors.c.description,
        '_Actor__hyperlink': actors.c.hyperlink,
        '_Actor__image_hyperlink': actors.c.image_hyperlink,
        '_Actor__acted_movies': relationship(
            movies_mapper,
            secondary=movie_actors,
            backref="_Movie__actors"
        ),
        '_Actor__actors_this_one_has_worked_with': relationship(
            model.Actor,
            secondary=actor_actors,
        )
    })
