from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.database.session import Base


class Package(Base):

    __tablename__ = "packages"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)

    name = Column(String, nullable=False)

    total_sessions = Column(Integer, nullable=False)

    price = Column(Float, nullable=False)

    service = relationship("Service")


class ClientPackage(Base):

    __tablename__ = "client_packages"

    id = Column(Integer, primary_key=True, index=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)

    total_sessions = Column(Integer, nullable=False)

    remaining_sessions = Column(Integer, nullable=False)

    purchased_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )

    package = relationship("Package")

    client = relationship("Client")

    @property
    def package_name(self) -> str:
        return self.package.name

    @property
    def service_id(self) -> int:
        return self.package.service_id
