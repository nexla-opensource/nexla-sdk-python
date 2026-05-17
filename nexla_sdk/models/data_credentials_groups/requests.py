from typing import List, Optional

from nexla_sdk.models.base import BaseModel


class DataCredentialsGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    credentials_type: Optional[str] = None
    data_credentials: Optional[List[int]] = None


class DataCredentialsGroupUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    credentials_type: Optional[str] = None
    data_credentials: Optional[List[int]] = None


class DataCredentialsGroupRemoveCredentials(BaseModel):
    data_credentials: List[int]
