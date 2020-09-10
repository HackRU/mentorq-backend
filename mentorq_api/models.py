from django.db import models
from django.utils import timezone


class Ticket(models.Model):
    class StatusType(models.TextChoices):
        OPEN = "OPEN"
        CLOSED = "CLOSED"
        CLAIMED = "CLAIMED"
        CANCELLED = "CANCELLED"

    # the email of the person who created the ticket
    owner_email = models.EmailField()
    # the name of the mentor who has claimed this ticket
    mentor = models.CharField(max_length=255, blank=True)
    # the email of the mentor who has claimed this ticket
    mentor_email = models.EmailField(blank=True)
    # the status of the ticket (one of the pre-defined types listed above)
    status = models.CharField(max_length=max(map(lambda st: len(st[0]), StatusType.choices)),
                              choices=StatusType.choices,
                              default=StatusType.OPEN)
    # the title of the ticket
    title = models.CharField(max_length=255)
    # the comment/details of the ticket
    comment = models.CharField(max_length=255, blank=True)
    # the contact info of the owner
    contact = models.CharField(max_length=255, null=True, blank=True)
    # the location of the owner
    location = models.CharField(max_length=255)
    # the datetime when this ticket was created
    created_datetime = models.DateTimeField(auto_now_add=True)
    # the datetime when this ticket was claimed
    claimed_datetime = models.DateTimeField(null=True, editable=False)
    # the datetime when this ticket was closed
    closed_datetime = models.DateTimeField(null=True, editable=False)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"

    # TODO: test transition to the "CANCELLED" status type and validate that arbitrary status changes aren't possible
    def save(self, *args, **kwargs):
        try:
            current_ticket = Ticket.objects.get(pk=self.pk)
            current_status = current_ticket.status
            if self.status == Ticket.StatusType.CLAIMED:
                if current_status == Ticket.StatusType.OPEN:
                    self.claimed_datetime = timezone.now()
            elif self.status == Ticket.StatusType.CLOSED:
                if current_status == Ticket.StatusType.OPEN or current_status == Ticket.StatusType.CLAIMED:
                    self.closed_datetime = timezone.now()
        except self.DoesNotExist:
            pass
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Rating(models.IntegerChoices):
    VERY_DISSATISFIED = 1
    DISSATISFIED = 2
    NEUTRAL = 3
    SATISFIED = 4
    VERY_SATISFIED = 5


class Feedback(models.Model):
    ticket = models.OneToOneField(to=Ticket, primary_key=True, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(choices=Rating.choices)
    comments = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"
