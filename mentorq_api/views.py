from datetime import timedelta

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotAuthenticated, NotFound
from rest_framework.response import Response

from mentorq_api.models import Ticket, Feedback
from mentorq_api.serializers import TicketSerializer, TicketEditableSerializer, FeedbackSerializer, \
    FeedbackEditableSerializer


class LCSAuthenticatedMixin:
    def initial(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise NotAuthenticated
        # the lcs profile is stored in as arguments
        self.kwargs["lcs_profile"] = request.user.lcs_profile
        return super().initial(request, *args, **kwargs)


# view for the /tickets endpoint
class TicketViewSet(LCSAuthenticatedMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                    mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method in ("PATCH", "PUT"):
            serializer_class = TicketEditableSerializer
        return serializer_class

    # queryset is filtered according to user's role within LCS
    def get_queryset(self):
        lcs_profile = self.kwargs.get("lcs_profile")
        user_roles = lcs_profile["role"]
        queryset = super().get_queryset()
        if not (user_roles["organizer"] or user_roles["director"] or user_roles["mentor"]):
            queryset = queryset.filter(owner_email=lcs_profile["email"])
        if user_roles["mentor"]:
            queryset = queryset.exclude(status=Ticket.StatusType.CLOSED)
        return queryset

    def perform_create(self, serializer):
        if self.kwargs.get("lcs_profile")["email"] != serializer.validated_data["owner_email"]:
            raise PermissionDenied("You cannot create a ticket on behalf of another user")
        super().perform_create(serializer)

    @action(methods=["get"], detail=False, url_path="stats", url_name="stats")
    def get_stats(self, request, *args, **kwargs):
        roles = kwargs["lcs_profile"]["role"]
        if not roles["director"]:
            raise PermissionDenied

        claimed_datetime_deltas = list(map(lambda ticket: ticket.claimed_datetime - ticket.created_datetime,
                                           Ticket.objects.exclude(claimed_datetime__isnull=True).only(
                                                   "created_datetime",
                                                   "claimed_datetime")))
        num_of_claimed_datetime_deltas = len(claimed_datetime_deltas)
        closed_datetime_deltas = list(map(lambda ticket: ticket.closed_datetime - ticket.created_datetime,
                                          Ticket.objects.exclude(closed_datetime__isnull=True).only("created_datetime",
                                                                                                    "closed_datetime")))
        num_of_closed_datetime_deltas = len(closed_datetime_deltas)
        average_claimed_datetime = (sum(claimed_datetime_deltas, timedelta(
                0)) / num_of_claimed_datetime_deltas) if num_of_claimed_datetime_deltas > 0 else None
        average_closed_datetime = (sum(closed_datetime_deltas, timedelta(
                0)) / num_of_closed_datetime_deltas) if num_of_closed_datetime_deltas > 0 else None
        return Response(
                {"average_claimed_datetime_seconds": average_claimed_datetime,
                 "average_closed_datetime_seconds": average_closed_datetime})


# view for the /feedback endpoint
class FeedbackViewSet(LCSAuthenticatedMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                      mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method in ("PATCH", "PUT"):
            serializer_class = FeedbackEditableSerializer
        return serializer_class

    def get_queryset(self):
        lcs_profile = self.kwargs.get("lcs_profile")
        user_roles = lcs_profile["role"]
        queryset = super().get_queryset()
        if not user_roles["director"]:
            queryset = queryset.filter(ticket__owner_email=lcs_profile["email"])
        return queryset

    def perform_create(self, serializer):
        if serializer.validated_data["ticket"].owner_email != self.kwargs["lcs_profile"]["email"]:
            raise NotFound
        if serializer.validated_data["ticket"].status != Ticket.StatusType.CLOSED:
            raise PermissionDenied("Ticket must be closed to submit feedback")
        return super().perform_create(serializer)
