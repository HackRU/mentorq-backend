from rest_framework import serializers

from mentorq_api.models import Ticket, Feedback


# returns the relevant fields from a Ticket object
class TicketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id", "owner_email", "mentor", "mentor_email", "status", "title",
            "comment", "contact", "location", "created_datetime"
        ]


class TicketEditableSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id", "owner_email", "mentor", "mentor_email", "status", "title",
            "comment", "contact", "location", "created_datetime"
        ]
        read_only_fields = ["id", "owner_email", "title", "comment", "contact", "location", "created_datetime",
                            "claimed_datetime", "closed_datetime"]


class FeedbackSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Feedback
        fields = ["ticket", "rating", "comments"]
