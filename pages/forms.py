from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Your name",
        max_length=50,
        widget=forms.TextInput(attrs={
            "placeholder": "Your full name",
            "autocomplete": "name",
        }),
    )

    email = forms.EmailField(
        label="Email address",
        max_length=254,
        widget=forms.EmailInput(attrs={
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )

    message = forms.CharField(
        label="Your message",
        max_length=5000,
        widget=forms.Textarea(attrs={
            "placeholder": "Tell me about your project, opportunity, or question...",
            "rows": 6,
        }),
    )