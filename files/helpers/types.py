from typing import Annotated

from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.orm import mapped_column

int_pk = Annotated[int, mapped_column(primary_key=True)]
str_pk = Annotated[str, mapped_column(primary_key=True)]

user_id_fk = Annotated[int, mapped_column(ForeignKey("users.id"))]
user_id_fk_pk = Annotated[int, mapped_column(ForeignKey("users.id"), primary_key=True)]
post_id_fk = Annotated[int, mapped_column(ForeignKey("posts.id"))]
post_id_fk_pk = Annotated[int, mapped_column(ForeignKey("posts.id"), primary_key=True)]
comment_id_fk = Annotated[int, mapped_column(ForeignKey("comments.id"))]
comment_id_fk_pk = Annotated[int, mapped_column(ForeignKey("comments.id"), primary_key=True)]