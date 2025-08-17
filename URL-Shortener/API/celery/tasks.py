from celery import Celery
from API.config import settings

app = Celery("tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
app.conf.broker_connection_retry_on_startup = True
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.enable_utc = True

@app.task(name="test")
def test():
    return "test"