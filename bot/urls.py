from django.urls import path

from bot.views.cron.views import SentAdsView
from bot.views.webhook.get_webhook import handle_updates


urlpatterns = [
    path("webhook/<str:bot_id>/updates", handle_updates),

    path('cron/sent-ads/', SentAdsView.as_view())
]