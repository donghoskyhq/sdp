import logging

from redis import Redis
from rq import Queue, Worker

from shared.config import get_settings


def main() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    connection = Redis.from_url(str(settings.redis_url))
    queue = Queue(settings.queue_name, connection=connection)
    logging.getLogger(__name__).info("Starting worker for queue %s", queue.name)
    Worker([queue], connection=connection).work(with_scheduler=False)


if __name__ == "__main__":
    main()
