from nexla_sdk.resources.base_resource import BaseResource


class SdkApplicationsResource(BaseResource):
    """Resource for SDK applications.

    The inherited methods serve the list, get, create, update, delete,
    activate, and pause routes. Each route takes an integer app_id, which
    matches the base method signatures.
    """

    def __init__(self, client):
        super().__init__(client)
        self._path = "/sdk_applications"
        self._model_class = None
