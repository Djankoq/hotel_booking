"""SQLAlchemy models.

Imported here to make sure Alembic autogenerate sees all tables.
"""

from app.models.user import User  # noqa: F401
from app.models.hotel import Hotel  # noqa: F401
from app.models.room import Room  # noqa: F401
from app.models.booking import Booking  # noqa: F401
from app.models.booking import BookingStatus  # noqa: F401

