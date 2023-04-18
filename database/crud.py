from sqlalchemy import select

from core.db import async_session
from database.models import Review, ReviewsCount
from database.schemas import ReviewsSchema, ReviewsCountSchema


async def get_review(review_id: int):
    async with async_session() as session:
        review = await session.execute(
            select(Review).filter(Review.id == review_id))

        review = review.scalars().first()
        if review is None:
            return Review()
        else:
            return Review().from_orm(review)


async def add_new_review(review: ReviewsSchema):
    async with async_session() as session:
        new_review = Review(
            id=review.id,
            user=review.user,
            date_created=review.date_created,
            rating=review.rating,
            text=review.text,
        )
        await session.merge(new_review)
        await session.commit()


async def get_reviews_count(place: ReviewsCountSchema):
    async with async_session() as session:
        reviews_count = await session.execute(
            select(ReviewsCount).filter(ReviewsCount.place_id == place.place_id))

        reviews_count = reviews_count.scalars().first()
        if reviews_count is None:
            return ReviewsCountSchema()
        else:
            return ReviewsCountSchema().from_orm(reviews_count)


async def add_reviews_count(place: ReviewsCountSchema):
    async with async_session() as session:
        new_place = ReviewsCount(
            place_id=place.place_id,
            reviews_count=place.reviews_count
        )
        session.add(new_place)
        await session.commit()


async def update_reviews_count(update_place: ReviewsCountSchema):
    async with async_session() as session:
        review = await session.execute(
            select(ReviewsCount).filter(ReviewsCount.place_id == update_place.place_id))
        review.scalar().reviews_count = update_place.reviews_count
        await session.commit()
