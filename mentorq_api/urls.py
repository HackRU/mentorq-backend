from django.urls import path, include
from rest_framework.routers import DefaultRouter

from mentorq_api.views import TicketViewSet, FeedbackViewSet, SlackViewSet

router = DefaultRouter()
router.register(r"tickets", TicketViewSet)
router.register(r"feedback", FeedbackViewSet)
router.register(r"slack", SlackViewSet, 'slack')

urlpatterns = [
    path("auth/", include("mentorq_user.urls")),
    path("", include(router.urls))
]
