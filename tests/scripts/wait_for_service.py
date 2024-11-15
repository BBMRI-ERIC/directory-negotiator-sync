import time
import requests

url = 'http://localhost:8080/api/graphql'
timeout = 300  # Wait up to 5 minutes
start_time = time.time()

while time.time() - start_time < timeout:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Service is up and running!")
            exit(0)
    except requests.ConnectionError:
        pass
    print("Waiting for service...")
    time.sleep(5)

print("Service did not start in time.")
exit(1)