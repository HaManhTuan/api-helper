from app.models.report_export_job import ReportExportJob
from app.repositories.core import RepositoryImpl
from app.repositories.factory import repository_factory


class ReportExportJobRepository(RepositoryImpl[ReportExportJob]):
    def __init__(self) -> None:
        repo = repository_factory.create_repository(ReportExportJob)
        super().__init__(
            model=ReportExportJob,
            query_builder=repo.query_builder,
            optimistic_lock_validator=repo.optimistic_lock_validator,
        )


report_export_job_repository = ReportExportJobRepository()
