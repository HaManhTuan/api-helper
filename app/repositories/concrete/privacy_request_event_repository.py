from app.models.privacy_request_event import PrivacyRequestEvent
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class PrivacyRequestEventRepository(RepositoryImpl[PrivacyRequestEvent]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(PrivacyRequestEvent)
        super().__init__(
            model=PrivacyRequestEvent,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )


privacy_request_event_repository = PrivacyRequestEventRepository()
