from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms
from django.contrib.auth import forms as admin_forms
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

User = get_user_model()

QUESTIONS = [
    {"question": _("Am the life of the party."), "type": 1, "math": "+"},
    {"question": _("Feel little concern for others."), "type": 2, "math": "-"},
    {"question": _("Am always prepared."), "type": 3, "math": "+"},
    {"question": _("Get stressed out easily."), "type": 4, "math": "-"},
    {"question": _("Have a rich vocabulary."), "type": 5, "math": "+"},
    {"question": _("Don't talk a lot."), "type": 1, "math": "-"},
    {"question": _("Am interested in people."), "type": 2, "math": "+"},
    {"question": _("Leave my belongings around."), "type": 3, "math": "-"},
    {"question": _("Am relaxed most of the time."), "type": 4, "math": "+"},
    {
        "question": _("Have difficulty understanding abstract ideas."),
        "type": 5,
        "math": "-",
    },
    {"question": _("Feel comfortable around people."), "type": 1, "math": "+"},
    {"question": _("Insult people."), "type": 2, "math": "-"},
    {"question": _("Pay attention to details."), "type": 3, "math": "+"},
    {"question": _("Worry about things."), "type": 4, "math": "-"},
    {"question": _("Have a vivid imagination."), "type": 5, "math": "+"},
    {"question": _("Keep in the background."), "type": 1, "math": "-"},
    {"question": _("Sympathize with others' feelings."), "type": 2, "math": "+"},
    {"question": _("Make a mess of things."), "type": 3, "math": "-"},
    {"question": _("Seldom feel blue."), "type": 4, "math": "+"},
    {"question": _("Am not interested in abstract ideas."), "type": 5, "math": "-"},
    {"question": _("Start conversations."), "type": 1, "math": "+"},
    {
        "question": _("Am not interested in other people's problems."),
        "type": 2,
        "math": "-",
    },
    {"question": _("Get chores done right away."), "type": 3, "math": "+"},
    {"question": _("Am easily disturbed."), "type": 4, "math": "-"},
    {"question": _("Have excellent ideas."), "type": 5, "math": "+"},
    {"question": _("Have little to say."), "type": 1, "math": "-"},
    {"question": _("Have a soft heart."), "type": 2, "math": "+"},
    {
        "question": _("Often forget to put things back in their proper place."),
        "type": 3,
        "math": "-",
    },
    {"question": _("Get upset easily."), "type": 4, "math": "-"},
    {"question": _("Do not have a good imagination."), "type": 5, "math": "-"},
    {
        "question": _("Talk to a lot of different people at parties."),
        "type": 1,
        "math": "+",
    },
    {"question": _("Am not really interested in others."), "type": 2, "math": "-"},
    {"question": _("Like order."), "type": 3, "math": "+"},
    {"question": _("Change my mood a lot."), "type": 4, "math": "-"},
    {"question": _("Am quick to understand things."), "type": 5, "math": "+"},
    {"question": _("Don't like to draw attention to myself."), "type": 1, "math": "-"},
    {"question": _("Take time out for others."), "type": 2, "math": "+"},
    {"question": _("Shirk my duties."), "type": 3, "math": "-"},
    {"question": _("Have frequent mood swings."), "type": 4, "math": "-"},
    {"question": _("Use difficult words."), "type": 5, "math": "+"},
    {
        "question": _("Don't mind being the center of attention."),
        "type": 1,
        "math": "+",
    },
    {"question": _("Feel others' emotions."), "type": 2, "math": "+"},
    {"question": _("Follow a schedule."), "type": 3, "math": "+"},
    {"question": _("Get irritated easily."), "type": 4, "math": "-"},
    {"question": _("Spend time reflecting on things."), "type": 5, "math": "+"},
    {"question": _("Am quiet around strangers."), "type": 1, "math": "-"},
    {"question": _("Make people feel at ease."), "type": 2, "math": "+"},
    {"question": _("Am exacting in my work."), "type": 3, "math": "+"},
    {"question": _("Often feel blue."), "type": 4, "math": "-"},
    {"question": _("Am full of ideas."), "type": 5, "math": "+"},
]


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User


class UserAdminCreationForm(admin_forms.UserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User

        error_messages = {
            "username": {"unique": _("This username has already been taken.")}
        }


class UserSignupForm(SignupForm):
    """
    Form that will be rendered on a user sign up section/screen.
    Default fields will be added automatically.
    Check UserSocialSignupForm for accounts created from social.
    """


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """


class UserPersonalityForm(forms.Form):
    CHOICES = [(1, ""), (2, ""), (3, ""), (4, ""), (5, "")]
    WIDGET = forms.RadioSelect(attrs={"class": "input_question"})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i, question in enumerate(QUESTIONS):
            self.fields[f"question_{i}"] = forms.ChoiceField(
                choices=self.CHOICES,
                label=question["question"],
                widget=self.WIDGET,
                initial=(3, ""),
            )
