from django.apps import AppConfig


class RrfConfig(AppConfig):
    name = 'pac.rrf'
    label = 'rrf'

    def ready(self):
        from pac import scheduler
        scheduler.start()
