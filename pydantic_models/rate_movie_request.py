from pydantic import BaseModel


class RateMovieRequestModel(BaseModel):
    movie: int
    user: int
    rating: int
    text: str = ""
