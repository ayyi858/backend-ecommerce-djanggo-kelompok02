from django.apps import AppConfig


class StoreConfig(AppConfig):
    def ready(self):
        import store.signals
    name = 'store'
