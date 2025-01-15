from django.apps import AppConfig


class BankingWebsiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'banking_website'

    def ready(self):
        import banking_website.signals