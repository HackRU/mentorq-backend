from rest_framework import serializers

from mentorq_api.models import Ticket, Feedback


# returns the relevant fields from a Ticket object
class TicketSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id", "url", "owner_email", "mentor", "mentor_email", "status", "title",
            "comment", "contact", "location", "created_datetime"
        ]


class TicketEditableSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id", "url", "owner_email", "mentor", "mentor_email", "status", "title",
            "comment", "contact", "location", "created_datetime"
        ]
        read_only_fields = ["id", "url", "owner_email", "title", "comment", "contact", "location", "created_datetime",
                            "claimed_datetime", "closed_datetime"]


class FeedbackSerializer(serializers.ModelSerializer):
    ticket_url = serializers.HyperlinkedIdentityField(view_name="ticket-detail", source="url")

    class Meta:
        model = Feedback
        fields = ["id", "ticket_url", "rating", "comments"]


class SlackDMSerializer(serializers.Serializer):
    """Your data serializer, define your fields here."""
    other_email = serializers.CharField(max_length=250)

