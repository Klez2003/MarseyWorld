from sqlalchemy import Column, Integer, Boolean
from .table import Event

Event.hw_zombie = Column(Integer, default=0, nullable=False)
Event.jumpscare = Column(Integer, default=0)
Event.hwmusic = Column(Boolean, default=False)

COLUMN_DEFAULTS = {
	"hw_zombie": {
		"default": 0
	},
	"jumpscare": {
		"default": 0
	},
	"hwmusic": {
		"default": False
	},
}
