from typing import List, Literal, Optional, Tuple, Union
from fastapi import FastAPI
from pydantic import BaseModel
from db import (
    get_random_doc,
    random_choice,
    search,
)


app = FastAPI()


class QuoteModel(BaseModel):
    text: str
    author: str
    title: Optional[str] = None
    title_url: Optional[str] = None
    like_count: int
    quote_url: str
    tags: Optional[List[str]] = None


@app.get("/random", response_model=QuoteModel)
def random_quote():
    doc = get_random_doc()
    return doc


@app.get("/search", response_model=List[QuoteModel])
def search_quote(
    author: Optional[Union[bool, str]] = None,
    title: Optional[Union[bool, str]] = None,
    like_count_min: Optional[int] = None,
    like_count_max: Optional[int] = None,
    tags_str: Optional[str] = None,
    tags_type: Literal["all", "any"] = "all",
):
    print(tags_type)
    like_count = (
        (like_count_min, like_count_max) if like_count_min or like_count_max else None
    )
    tags = (tags_type, tags_str.split(",")) if tags_str else None
    docs = search(author, title, like_count, tags)
    return docs


@app.get("/search_then_random", response_model=QuoteModel)
def search_quote_then_random(
    author: Optional[Union[bool, str]] = None,
    title: Optional[Union[bool, str]] = None,
    like_count_min: Optional[int] = None,
    like_count_max: Optional[int] = None,
    tags_str: Optional[str] = None,
    tags_type: Literal["all", "any"] = "all",
):
    like_count = (
        (like_count_min, like_count_max) if like_count_min or like_count_max else None
    )
    tags = (tags_type, tags_str.split(",")) if tags_str else None
    docs = search(author, title, like_count, tags)
    return random_choice(docs)
