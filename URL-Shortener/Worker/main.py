from celery import Celery

app = Celery("tasks", broker="redis://dragonfly:6379/0", backend="redis://dragonfly:6379/0")
app.conf.broker_connection_retry_on_startup = True
app.conf.task_serializer = "json"
app.conf.result_serializer = "json"
app.conf.accept_content = ["json"]
app.conf.enable_utc = True

@app.task(name="test")
def test():
    return "test"