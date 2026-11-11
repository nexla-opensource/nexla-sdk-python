from datetime import datetime
from typing import Optional

from nexla_sdk.models.base import BaseModel
from nexla_sdk.models.catalog_configs.responses import CatalogConfig


class CatalogRef(BaseModel):
    id: int
    data_set_id: Optional[int] = None
    status: Optional[str] = None
    reference_id: Optional[str] = None
    link: Optional[str] = None
    error_msg: Optional[str] = None
    updated_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    catalog_config: Optional[CatalogConfig] = None
