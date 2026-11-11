from typing import Optional

from nexla_sdk.models.base import BaseModel


class CatalogRefCreate(BaseModel):
    data_set_id: int
    catalog_config_id: int
    reference_id: Optional[str] = None
    link: Optional[str] = None


class CatalogRefUpdate(BaseModel):
    reference_id: Optional[str] = None
    link: Optional[str] = None
    status: Optional[str] = None
