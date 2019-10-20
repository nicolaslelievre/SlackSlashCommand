from app.tasks import task
import requests
from time import sleep


@task
def generate_report(response_url):
    sleep(10)

    data = {
        'response_type': 'in_channel',
        'text': 'Hello, here is your report'
    }

    requests.post(response_url, json=data)
