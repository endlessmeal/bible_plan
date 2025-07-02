from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class ReadingPlan(Base):
    """Reading plan model."""
    __tablename__ = "reading_plan"

    id: Mapped[int] = mapped_column(primary_key=True)
    month: Mapped[int] = mapped_column(nullable=False)
    day: Mapped[int] = mapped_column(nullable=False)
    psalm: Mapped[str] = mapped_column(String(50), nullable=False)
    new_testament: Mapped[str] = mapped_column(String(50), nullable=False)
    old_testament: Mapped[str] = mapped_column(String(50), nullable=False)
