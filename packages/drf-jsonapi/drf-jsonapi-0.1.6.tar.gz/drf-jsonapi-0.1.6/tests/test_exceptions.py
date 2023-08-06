from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.core.exceptions import ImproperlyConfigured
from django.utils import six

import json
import pytest

from tests.models import Person, Comment


pytestmark = pytest.mark.django_db


def test_serializer(client):
    response = client.post(reverse("person-list"), data=json.dumps({
        "incorrect-key": {}
    }), content_type="application/vnd.api+json")
    assert response.status_code == 400
    response_data = json.loads(response.content.decode())
    assert len(response_data["errors"]) is 2
    assert {
        "status": "400",
        "source": {
            "pointer": "/data/attributes/first-name"
        },
        "detail": "This field is required."
    } in response_data["errors"]
    assert {
        "status": "400",
        "source": {
            "pointer": "/data/attributes/last-name"
        },
        "detail": "This field is required."
    } in response_data["errors"]


def test_unauthorized_on_list(client):
    response = client.get(reverse("auth-people-list"))
    assert response.status_code == 403
    response_data = json.loads(response.content.decode())
    assert len(response_data["errors"]) is 1
    assert {
        "status": "403",
        "source": {
            "pointer": "/data"
        },
        "detail": "Authentication credentials were not provided."
    } in response_data["errors"]


def test_not_found(client):
    response = client.get(reverse("person-detail", args=[42]),
                          content_type="application/vnd.api+json")
    assert response.status_code == 404
    assert json.loads(response.content.decode()) == {
        "errors": [
            {
                "status": "404",
                "source": {
                    "pointer": "/data"
                },
                "detail": "Not found."
            }
        ]
    }


def test_method_not_allowed(client):
    response = client.post(reverse("person-detail", args=[42]),
                           content_type="application/vnd.api+json")
    assert response.status_code == 405
    assert json.loads(response.content.decode()) == {
        "errors": [
            {
                "status": "405",
                "source": {
                    "pointer": "/data"
                },
                "detail": "Method \"POST\" not allowed."
            }
        ]
    }


def test_throttling(client):
    response = client.post(reverse("throttled-view"),
                           content_type="application/vnd.api+json")
    assert response.status_code == 429
    assert json.loads(response.content.decode()) == {
        "errors": [
            {
                "status": "429",
                "source": {
                    "pointer": "/data"
                },
                "detail": "Request was throttled. Expected available in "
                          "{} second.".format("1" if six.PY3 else "1.0")
            }
        ]
    }


def test_validation_error(client):
    response = client.get(reverse("validation-error-view"),
                          content_type="application/vnd.api+json")
    assert response.status_code == 400
    assert json.loads(response.content.decode()) == {
        "errors": [
            {
                "status": "400",
                "source": {
                    "pointer": "/data"
                },
                "detail": "Validation error"
            }
        ]
    }


def test_unhandled_exception(client):
    with pytest.raises(NotImplementedError):
        client.get(reverse("errored-view"),
                   content_type="application/vnd.api+json")


def test_improperly_configured_model_map_exception(client):
    buzz = Person.objects.create(last_name="Lightyear", first_name="Buzz")
    Comment.objects.create(body="Buzz' comment", author=buzz)
    with pytest.raises(ImproperlyConfigured):
        client.get("{}?include=author".format(
            reverse("ic-read-only-author-comment-detail", args=[1])))
