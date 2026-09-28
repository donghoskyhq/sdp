from redis import Redis
from rq import Queue

from shared.config import get_settings


def enqueue_project_provisioning(project_id: str) -> str:
    settings = get_settings()
    connection = Redis.from_url(str(settings.redis_url))
    queue = Queue(settings.queue_name, connection=connection)
    job = queue.enqueue(
        "worker.jobs.provision_project",
        project_id,
        job_timeout=settings.deployment_timeout_seconds + 120,
    )
    return job.id
