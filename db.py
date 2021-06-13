from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union
from functools import reduce
from pathlib import Path
import random
from tinydb import TinyDB, Query
from tinydb.queries import QueryInstance


def get_db(path: Union[Path, str]) -> TinyDB:
    db = TinyDB(path)
    return db


db = get_db("db.json")


def make_eq_condition(q: Query, field_name: str, field_value: Any) -> QueryInstance:
    return q[field_name] == field_value


def make_exists_condition(q: Query, field_name: str) -> QueryInstance:
    return q[field_name].exists()


def make_not_exists_condition(q: Query, field_name: str) -> QueryInstance:
    return ~q[field_name].exists()


def make_bool_condition(q: Query, field_name: str, field_value: bool) -> QueryInstance:
    return (
        make_exists_condition(q, field_name)
        if field_value
        else make_not_exists_condition(q, field_name)
    )


def make_ge_condition(q: Query, field_name: str, field_value: float) -> QueryInstance:
    return q[field_name] >= field_value


def make_le_condition(q: Query, field_name: str, field_value: float) -> QueryInstance:
    return q[field_name] <= field_value


def make_threshold_conditions(
    q: Query, field_name: str, field_values: Tuple[Optional[float], Optional[float]]
) -> List[QueryInstance]:
    conditions: List[QueryInstance] = []
    if field_values[0]:
        conditions.append(q[field_name] >= field_values[0])
    if field_values[1]:
        conditions.append(q[field_name] <= field_values[1])
    return conditions


def make_all_condition(
    q: Query, field_name: str, field_values: List[Any]
) -> QueryInstance:
    return q[field_name].all(field_values)


def make_any_condition(
    q: Query, field_name: str, field_values: List[Any]
) -> QueryInstance:
    return q[field_name].any(field_values)


def random_choice(vals: Sequence[Any]) -> Any:
    return random.choice(vals)


def get_random_doc() -> Dict[str, Any]:
    length = len(db)
    random_id = random.randint(1, length)
    doc = db.get(doc_id=random_id)
    return doc


def search(
    author: Optional[Union[bool, str]] = None,
    title: Optional[Union[bool, str]] = None,
    like_count: Optional[Tuple[Optional[int], Optional[int]]] = None,
    tags: Optional[Tuple[Literal["all", "any"], List[str]]] = None,
) -> List[Dict[str, Any]]:
    Quote: Query = Query()
    conditions: List[QueryInstance] = [Quote.noop()]
    if author is not None:
        if isinstance(author, str):
            conditions.append(make_eq_condition(Quote, "author", author))
        elif isinstance(author, bool):
            conditions.append(make_bool_condition(Quote, "author", author))
    if title is not None:
        if isinstance(title, str):
            conditions.append(make_eq_condition(Quote, "title", title))
        elif isinstance(title, bool):
            conditions.append(make_bool_condition(Quote, "title", title))
    if like_count is not None:
        if isinstance(like_count, tuple):
            conditions.extend(
                make_threshold_conditions(Quote, "like_count", like_count)
            )
        elif isinstance(like_count, bool):
            conditions.append(make_bool_condition(Quote, "like_count", like_count))
    if tags is not None:
        if tags[0] == "all":
            conditions.append(make_all_condition(Quote, "tags", tags[1]))
        elif tags[0] == "any":
            conditions.append(make_any_condition(Quote, "tags", tags[1]))

    docs = db.search(reduce(lambda x, y: x & y, conditions))
    return docs
