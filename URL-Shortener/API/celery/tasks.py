from API.config import settings
from celery import Celery

app = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
app.conf.broker_connection_retry_on_startup = True
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.enable_utc = True


@app.task(name="test")
def prepare_report(load:dict) -> dict:
    return load
