from sqlalchemy import Column, String, Integer, Index

from core.db import Base, engine


class Review(Base):
    __tablename__ = 'review'

    id = Column(Integer, primary_key=True)
    user = Column(String, nullable=False)
    date_created = Column(String, nullable=False)
    rating = Column(Integer, nullable=False)
    text = Column(String, nullable=False)


class ReviewsCount(Base):
    __tablename__ = 'double_gis_reviews_count'

    id = Column(Integer, primary_key=True)
    place_id = Column(String, nullable=False)
    reviews_count = Column(Integer, nullable=False)

    __table_args__ = (
        Index('idx_place_id', place_id),
    )
