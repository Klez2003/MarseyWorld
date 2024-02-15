import json
import time
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.types import int_pk, user_id_fk

if TYPE_CHECKING:
	from files.classes import User

CASINO_GAME_KINDS = ['blackjack', 'slots', 'roulette']

class CasinoGame(Base):
	__tablename__ = "casino_games"

	id: Mapped[int_pk]
	user_id: Mapped[user_id_fk]
	created_utc: Mapped[int]
	active: Mapped[bool] = mapped_column(default=True)
	currency: Mapped[str]
	wager: Mapped[int]
	winnings: Mapped[int]
	kind: Mapped[str]
	game_state: Mapped[str] = mapped_column(JSON)

	user: Mapped["User"] = relationship()

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def game_state_json(self):
		return json.loads(self.game_state)
