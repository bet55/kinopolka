from pydantic import BaseModel, Field


class RateMovieRequestModel(BaseModel):
    user: int = Field(..., gt=0)
    movie: int = Field(..., gt=0)  # Or str if kp_id is a string
    rating: int = Field(..., ge=1, le=10)
    text: str = ""
