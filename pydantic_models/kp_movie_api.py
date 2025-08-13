from dataclasses import field
from typing import Optional

from pydantic import AliasChoices, AliasPath, BaseModel, Field, field_serializer


def create_empty_list():
    return []


n_url = "https://banner2.cleanpng.com/20180715/yag/aavjmwzok.webp"

ListDict = Optional[list[dict[str, str]]]


class KpFilmGenresModel(BaseModel):
    genres: ListDict = field(default_factory=create_empty_list)

    @field_serializer("genres")
    def serialize_genres(self, genres: list[dict], _info):
        gr = genres or []
        return gr


class KpFilmPersonModel(BaseModel):
    kp_id: int = Field(..., validation_alias="id")
    name: str | None = ""
    photo: str | None = ""


class KPFilmModel(BaseModel):
    kp_id: int = Field(..., validation_alias="id")
    name: str

    countries: ListDict = field(default_factory=create_empty_list)

    budget: int | None = Field(0, validation_alias=AliasChoices("", AliasPath("budget", "value")))
    fees: int | None = Field(0, validation_alias=AliasChoices("", AliasPath("fees", "world", "value")))
    premiere: str | None = Field("1970-01-01T00:00:00.000Z", validation_alias=AliasPath("premiere", "world"))
    description: str | None
    short_description: str | None = Field("...", validation_alias="shortDescription")
    slogan: str | None
    duration: int | None = Field(0, validation_alias="movieLength")
    poster: str | None = Field(n_url, validation_alias=AliasPath("poster", "url"))
    rating_kp: float | None = Field(0.0, validation_alias=AliasPath("rating", "kp"))
    rating_imdb: float | None = Field(0.0, validation_alias=AliasPath("rating", "imdb"))
    votes_kp: int | None = Field(0, validation_alias=AliasPath("votes", "kp"))
    votes_imdb: int | None = Field(0, validation_alias=AliasPath("votes", "imdb"))
    is_archive: bool = Field(False)

    # @field_serializer('premiere')
    # def serialize_premier(self, premiere: str, _info):
    #     return pendulum.parse(premiere).format('DD/MM/YYYY')

    @field_serializer("countries")
    def serialize_countries(self, countries: list[dict], _info):
        return [c["name"] for c in countries if c.get("name")]


if __name__ == "main":
    pass
    # with open('../data/api_response.json', 'r') as f:
    #     res = json.load(f)
    #
    # # rs = KpFilmGenresModel()
    # rs = KpFilmGenresModel(genres=res.get('genres'))
    #
    # ic(rs.dict())
