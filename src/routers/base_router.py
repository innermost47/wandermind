from fastapi.routing import APIRouter


class BaseRouter:
    def __init__(self, service):
        try:
            self._router = APIRouter()
            self._service = service
        except Exception as e:
            print(f"An error occured while trying to initialize base router: {e}")
