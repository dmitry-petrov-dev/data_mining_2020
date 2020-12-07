from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import lesson3_SQlite.models as models


class DataBase:
    def __init__(self, db_url):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.session_m = sessionmaker(bind=engine)

    @staticmethod
    def __get_or_create(session, model, **data):
        db_model = session.query(model).filter(model.url == data['url']).first()
        if not db_model:
            db_model = model(**data)

        return db_model

    def create_post(self, data):
        session = self.session_m()
        tags = map(lambda tag_data: self.__get_or_create(session, models.Tag, **tag_data), data['tags'])
        writer = self.__get_or_create(session, models.Writer, **data['writer'])
        post = self.__get_or_create(session, models.Post, **data['post'])
#        comment = self.__get_or_create(session, models.Comment, **data['comments'])
        post.writer = writer
#        comment.post = post
        post.tags.extend(tags)
        session.add(post)
        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
        finally:
            session.close()