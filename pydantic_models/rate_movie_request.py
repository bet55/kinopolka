from pydantic import BaseModel


class RateMovieRequestModel(BaseModel):
    film: int
    user: int
    rating: int
    text: str = ''

