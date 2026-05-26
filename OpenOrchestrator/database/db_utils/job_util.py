"""Database access functions for jobs.

A Job represents one launched process. The Scheduler creates a Job
when it starts a process and updates its status when the process
exits (or is killed).
"""

from datetime import datetime
from uuid import UUID

from sqlalchemy import select, desc

from OpenOrchestrator.database.db_util import _get_session
from OpenOrchestrator.database.exceptions import JobNotFoundError
from OpenOrchestrator.database.jobs import Job, JobStatus


def get_jobs(status: JobStatus | None = None, process_name: str | None = None) -> tuple[Job]:
    """Get jobs matching the requested status or process name.

    Args:
        status: Status of jobs, RUNNING, DONE, FAILED or KILLED. Defaults to None.
        process_name: Process name matching the jobs. Defaults to None.

    Returns:
        Tuple containing jobs matching the filters.
    """
    query = (
        select(Job)
        .order_by(desc(Job.start_time))
    )

    if status:
        query = query.where(Job.status == status)

    if process_name:
        query = query.where(Job.process_name == process_name)

    with _get_session() as session:
        result = session.scalars(query).all()
        return tuple(result)


def start_job(process_name: str, scheduler_name: str) -> Job:
    """Create a new RUNNING job for the given process.

    Args:
        process_name: Process name starting this job.
        scheduler_name: Name of the Scheduler launching the job.

    Returns:
        The newly created Job.
    """
    with _get_session() as session:
        job = Job(
            process_name=process_name,
            scheduler_name=scheduler_name,
            status=JobStatus.RUNNING,
        )
        session.add(job)
        session.commit()
        session.refresh(job)
        session.expunge(job)
        return job


def set_job_status(job_id: UUID | str, status: JobStatus):
    """Set status of job and update end_time, based on status.

    Args:
        job_id: Job ID to set status on.
        status: Status to set. Either RUNNING, DONE, FAILED or KILLED.
            Will set end_time to null if RUNNING or current time if not.

    Raises:
        JobNotFoundError: If no job with the given id exists.
    """
    if isinstance(job_id, str):
        job_id = UUID(job_id)

    with _get_session() as session:
        job = session.get(Job, job_id)

        if not job:
            raise JobNotFoundError("No job with the given id was found.")

        job.status = status
        if status == JobStatus.RUNNING:
            job.end_time = None
        else:
            job.end_time = datetime.now()
        session.commit()


def get_job(job_id: UUID | str) -> Job:
    """Get a job by ID.

    Args:
        job_id: The ID of the job to get.

    Returns:
        The Job object.

    Raises:
        JobNotFoundError: If no job with the given id exists.
    """
    if isinstance(job_id, str):
        job_id = UUID(job_id)
    with _get_session() as session:
        job = session.get(Job, job_id)

        if not job:
            raise JobNotFoundError("No job with the given id was found.")

        session.expunge(job)
        return job
