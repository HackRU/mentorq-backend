from rest_framework import serializers
from rest_framework.reverse import reverse

from mentorq_api.models import Ticket, Feedback


# returns the relevant fields from a Ticket object
class TicketSerializer(serializers.HyperlinkedModelSerializer):
    feedback = serializers.SerializerMethodField()

    def get_feedback(self, obj):
        feedback = ""
        request = self.context["request"]
        lcs_profile = request.user.lcs_profile
        if hasattr(obj, "feedback") and (lcs_profile["role"]["director"] or lcs_profile["email"] == obj.owner_email):
            feedback = reverse("feedback-detail", args=[obj.feedback.pk], request=self.context["request"])
        return feedback

    class Meta:
        model = Ticket
        fields = [
            "id", "url", "owner_email", "mentor", "mentor_email", "status", "title",
            "comment", "contact", "location", "created_datetime", "feedback"
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
        fields = ["ticket", "ticket_url", "rating", "comments"]


class FeedbackEditableSerializer(serializers.ModelSerializer):
    ticket_url = serializers.HyperlinkedIdentityField(view_name="ticket-detail", source="url")

    class Meta:
        model = Feedback
        fields = ["ticket", "ticket_url", "rating", "comments"]
        read_only_fields = ["ticket", "ticket_url"]
