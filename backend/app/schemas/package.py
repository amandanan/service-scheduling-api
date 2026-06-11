from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PackageBase(BaseModel):

    name: str

    service_id: int

    total_sessions: int

    price: float


class PackageCreate(PackageBase):
    pass


class PackageResponse(PackageBase):

    id: int

    model_config = ConfigDict(from_attributes=True)


class ClientPackagePurchase(BaseModel):

    client_id: int

    package_id: int


class ClientPackageResponse(BaseModel):

    id: int

    client_id: int

    package_id: int

    package_name: str

    service_id: int

    total_sessions: int

    remaining_sessions: int

    purchased_at: datetime

    model_config = ConfigDict(from_attributes=True)
