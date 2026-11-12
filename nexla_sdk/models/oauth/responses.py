from nexla_sdk.models.base import BaseModel


class OauthStartResponse(BaseModel):
    """Response model for POST /oauth/start.

    popup_url is the URL to open in a popup window. sid identifies the session.
    """

    popup_url: str
    sid: str
