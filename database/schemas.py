from pydantic import BaseModel


class ReviewsSchema(BaseModel):
    id: int = 0
    user: str = ''
    date_created: str = ''
    rating: int = 0
    text: str = ''

    class Config:
        orm_mode = True


class ReviewsCountSchema(BaseModel):
    id: int = 0
    reviews_count: int = 0
    place_id: str = 0

    class Config:
        orm_mode = True
