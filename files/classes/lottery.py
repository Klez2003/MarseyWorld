import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy

class Lottery(Base):
	__tablename__ = "lotteries"

	id: Mapped[int] = mapped_column(primary_key=True)
	is_active: Mapped[bool] = mapped_column(default=False)
	ends_at: Mapped[int]
	prize: Mapped[int] = mapped_column(default=0)
	tickets_sold: Mapped[int] = mapped_column(default=0)
	winner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	created_utc: Mapped[int]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def timeleft(self):
		if not self.is_active:
			return 0

		epoch_time = int(time.time())
		remaining_time = self.ends_at - epoch_time

		return 0 if remaining_time < 0 else remaining_time

	@property
	@lazy
	def stats(self):
		return {"active": self.is_active, "timeLeft": self.timeleft, "prize": self.prize, "ticketsSoldThisSession": self.tickets_sold,}
