from smtplib import SMTPException
from unittest.mock import patch

from django.core import mail
from django.template.loader import render_to_string
from django.test import (
    Client,
    RequestFactory,
    SimpleTestCase,
    override_settings,
)
from django.urls import resolve, reverse


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    EMAIL_HOST_USER="portfolio@example.com",
    CONTACT_RECIPIENT_EMAIL="owner@example.com",
)
class PortfolioPageTests(SimpleTestCase):
    sample = {
        "name": "Sample Visitor",
        "email": "visitor@example.com",
        "message": (
            "I would like to discuss a software development opportunity."
        ),
    }

    def test_home_and_about_have_separate_routes_and_content(self):
        self.assertEqual(reverse("home"), "/")
        self.assertEqual(reverse("about_me"), "/about/")

        self.assertNotEqual(
            resolve("/").func,
            resolve("/about/").func,
        )

        self.assertContains(
            self.client.get("/"),
            "Building software.",
        )

        self.assertContains(
            self.client.get("/about/"),
            "The experience behind the code.",
        )

    def test_contact_renders_labeled_fields_and_csrf_token(self):
        response = self.client.get(reverse("contact"))

        self.assertContains(response, 'for="id_name"')
        self.assertContains(response, 'for="id_email"')
        self.assertContains(response, 'for="id_message"')

        self.assertContains(
            response,
            'name="csrfmiddlewaretoken"',
        )

    def test_invalid_email_keeps_entries_and_does_not_send(self):
        with patch("pages.views.EmailMessage") as email_message:
            response = self.client.post(
                reverse("contact"),
                {**self.sample, "email": "invalid"},
            )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/contact.html")

        self.assertContains(
            response,
            "Please correct the highlighted fields",
        )

        self.assertContains(
            response,
            'value="Sample Visitor"',
        )

        self.assertContains(response, self.sample["message"])
        email_message.assert_not_called()

    def test_empty_form_shows_required_errors(self):
        response = self.client.post(reverse("contact"), {})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.context["form"].errors),
            3,
        )

    def test_success_uses_reply_to_and_redirect_prevents_refresh_resend(self):
        response = self.client.post(
            reverse("contact"),
            self.sample,
        )

        self.assertRedirects(
            response,
            reverse("contact"),
            fetch_redirect_response=False,
        )

        self.assertEqual(len(mail.outbox), 1)

        self.assertEqual(
            mail.outbox[0].from_email,
            "portfolio@example.com",
        )

        self.assertEqual(
            mail.outbox[0].reply_to,
            [self.sample["email"]],
        )

        self.assertEqual(
            mail.outbox[0].to,
            ["owner@example.com"],
        )

        confirmation = self.client.get(reverse("contact"))

        self.assertContains(
            confirmation,
            "Your message has been sent.",
        )

        self.assertNotContains(
            confirmation,
            'value="Sample Visitor"',
        )

        self.client.get(reverse("contact"))
        self.assertEqual(len(mail.outbox), 1)

    @patch(
        "pages.views.EmailMessage.send",
        side_effect=SMTPException("Test delivery failure"),
    )
    def test_delivery_failure_keeps_entries_and_reports_failure(self, send):
        with self.assertLogs("pages.views", level="ERROR"):
            response = self.client.post(
                reverse("contact"),
                self.sample,
            )

        self.assertContains(
            response,
            "Your message could not be sent right now.",
        )

        self.assertContains(
            response,
            'value="Sample Visitor"',
        )

        self.assertContains(response, self.sample["message"])

        self.assertNotContains(
            response,
            "Your message has been sent.",
        )

    @patch("pages.views.EmailMessage.send", return_value=0)
    def test_unaccepted_message_is_not_reported_as_success(self, send):
        with self.assertLogs("pages.views", level="ERROR"):
            response = self.client.post(
                reverse("contact"),
                self.sample,
            )

        self.assertContains(
            response,
            "Your message could not be sent",
        )

    def test_csrf_protection_is_preserved(self):
        browser = Client(enforce_csrf_checks=True)

        response = browser.post(
            reverse("contact"),
            self.sample,
        )

        self.assertEqual(response.status_code, 403)

    def test_projects_does_not_load_the_new_page_styles(self):
        request = RequestFactory().get(
            reverse("projects_list")
        )

        html = render_to_string(
            "projects/projects_list.html",
            {"projects": []},
            request=request,
        )

        self.assertNotIn("portfolio-pages.css", html)
        self.assertIn("css/styles.css", html)