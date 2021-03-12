from datetime import timedelta

import lcs_client
from django.db.models import Avg
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, NotAuthenticated, NotFound
from rest_framework.response import Response
from django.db.models import Q

from mentorq_api.models import Ticket, Feedback
from mentorq_api.serializers import TicketSerializer, TicketEditableSerializer, FeedbackSerializer, \
    FeedbackEditableSerializer

import json


class LCSAuthenticatedMixin:
    def initial(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise NotAuthenticated
        # the lcs profile is stored in as arguments

        self.kwargs["lcs_profile"] = request.user.lcs_profile
        self.kwargs["lcs_user"] = request.user.lcs_user
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
            raise PermissionDenied(
                "You cannot create a ticket on behalf of another user")
        super().perform_create(serializer)

    # Get stats about tickets
    @action(methods=["get"], detail=False, url_path="stats", url_name="stats")
    def get_stats(self, request, *args, **kwargs):
        roles = kwargs["lcs_profile"]["role"]

        total_tickets = Ticket.objects.count();

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

        #Stats for director
        if roles["director"]:
            tickets_open = Ticket.objects.filter(status="OPEN").count()
            tickets_cancelled = Ticket.objects.filter(status="CANCELLED").count()
            tickets_claimed = Ticket.objects.filter(status="CLAIMED").count()
            tickets_closed = Ticket.objects.filter(status="CLOSED").count()
            number_of_mentors = Ticket.objects.values('mentor_email').exclude(mentor_email='').distinct().count()
            number_of_users = Ticket.objects.values('owner_email').exclude(owner_email="").distinct().count()

            return Response(
                {"average_claimed_datetime_seconds": average_claimed_datetime,
                 "average_closed_datetime_seconds": average_closed_datetime,
                 "Total tickets": total_tickets,
                 "Open tickets": tickets_open,
                 "Claimed tickets": tickets_claimed,
                 "Closed Tickets": tickets_closed,
                 "Closed Tickets": tickets_closed,
                 "Number of mentors": number_of_mentors,
                 "Number of users": number_of_users,
                 "Average Rating": Feedback.objects.all().aggregate(Avg('rating'))})

        #Stats for everyone
        return Response(
            {"average_claimed_datetime_seconds": average_claimed_datetime,
             "average_closed_datetime_seconds": average_closed_datetime,
             "Total tickets": total_tickets,})

    @action(methods=["get"], detail=True, url_path="slack-dm", url_name="slack-dm")
    def get_slack_dm(self, request, *args, **kwargs):
        self.object = self.get_object()
        mentor_email = self.object.mentor_email
        owner_email = self.object.owner_email
        lcs_user = self.kwargs.get("lcs_user")
        lcs_profile =  self.kwargs.get("lcs_profile")
        request_email = lcs_profile["email"]
        other_email = ""
        if request_email == mentor_email:
            other_email = owner_email
        else:
            other_email = mentor_email
        try:
            return Response(lcs_user.create_dm_link_to(other_email))
        except lcs_client.CredentialError as c:
            statusCode = c.response.json()["statusCode"]
            body = c.response.json()["body"]
            return Response(body, status=statusCode)
        except lcs_client.RequestError as r:
            statusCode = r.response.json()["statusCode"]
            body = r.response.json()["body"]
            return Response(body, status=statusCode)
        except lcs_client.InternalServerError as i:
            statusCode = i.response.json()["statusCode"]
            body = i.response.json()["body"]
            return Response(body, status=statusCode)


# view for the /feedback endpoint
class FeedbackViewSet(LCSAuthenticatedMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin,
                      mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    LEADERBOARD_DEFAULT_SIZE = 5

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
            queryset = queryset.filter(
                ticket__owner_email=lcs_profile["email"])
        return queryset

#     def list(self, request, *args, **kwargs):
#         if not kwargs["lcs_profile"]["role"]["director"]:
#             raise PermissionDenied
#         return super().list(request, *args, **kwargs)


# # view for the /slack endpoint
# class SlackViewSet(LCSAuthenticatedMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
#     serializer_class = SlackDMSerializer

#     def create(self, request, *args, **kwargs):
#         lcs_user = self.kwargs.get("lcs_user")
#         try:
#             return Response(lcs_user.create_dm_link_to(self.request.data["other_email"]))
#         except lcs_client.CredentialError as c:
#             return Response(c.response)
#         except lcs_client.RequestError as r:
#             return Response(r.response)
#         except lcs_client.InternalServerError as i:
#             return Response(i.response)


    def perform_create(self, serializer):
        if serializer.validated_data["ticket"].owner_email != self.kwargs["lcs_profile"]["email"]:
            raise NotFound
        if serializer.validated_data["ticket"].status != Ticket.StatusType.CLOSED:
            raise PermissionDenied("Ticket must be closed to submit feedback")
        if not serializer.validated_data["ticket"].mentor_email:
            raise PermissionDenied(
                "Cannot leave feedback for a ticket with no mentor")
        return super().perform_create(serializer)

    @action(methods=["get"], detail=False, url_path="leaderboard", url_name="leaderboard")
    def get_leaderboard(self, request, *args, **kwargs):
        limit = int(self.request.query_params.get(
            "limit", FeedbackViewSet.LEADERBOARD_DEFAULT_SIZE))
        queryset = Feedback.objects.values("ticket__mentor_email") \
            .annotate(average_rating=Avg("rating")) \
            .order_by("-average_rating")
        queryset = queryset[:min(len(queryset), limit)]
        leaderboard = []
        for elem in queryset:
            mentor = Ticket.objects.filter(
                mentor_email__exact=elem["ticket__mentor_email"])[0].mentor
            leaderboard.append(
                {"mentor": mentor, "average_rating": elem["average_rating"]})
        return Response(leaderboard, content_type="application/json")
