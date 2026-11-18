import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from .forms import ContactForm

logger = logging.getLogger(__name__)


def home_view(request):
    return render(request, "pages/home.html")


def about_me_view(request):
    return render(request, "pages/about_me.html")


def experience_view(request):
    return render(request, "pages/experience.html")


def contact_view(request):
    # Keep the visitor's entries if validation or email delivery fails.
    form = ContactForm(
        request.POST if request.method == "POST" else None
    )

    delivery_error = ""

    if request.method == "POST" and form.is_valid():
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        message = form.cleaned_data["message"]

        message_body = (
            "You have a new message from your portfolio contact form.\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n\n"
            f"Message:\n{message}"
        )

        # Send from your configured mailbox.
        # Replies go to the visitor's email address.
        outgoing = EmailMessage(
            subject="Message from your Portfolio contact form",
            body=message_body,
            from_email=(
                settings.EMAIL_HOST_USER
                or settings.DEFAULT_FROM_EMAIL
            ),
            to=[
                getattr(
                    settings,
                    "CONTACT_RECIPIENT_EMAIL",
                    "edwinphone182@gmail.com",
                )
            ],
            reply_to=[email],
        )

        try:
            sent_count = outgoing.send(fail_silently=False)

            if sent_count != 1:
                raise SMTPException(
                    "The email backend did not accept the message."
                )

        except (SMTPException, OSError):
            logger.exception(
                "Portfolio contact email delivery failed."
            )

            delivery_error = (
                "Your message could not be sent right now. "
                "Your entries are still here. "
                "Please try again later."
            )

        else:
            messages.success(
                request,
                "Your message has been sent. "
                "Thank you for getting in touch.",
            )

            # Prevent a browser refresh from sending the same POST again.
            return redirect("contact")

    return render(
        request,
        "pages/contact.html",
        {
            "form": form,
            "delivery_error": delivery_error,
        },
    )