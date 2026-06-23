from locust import HttpUser, task


class BotUser(HttpUser):

    @task
    def ping(self):

        self.client.get("/")