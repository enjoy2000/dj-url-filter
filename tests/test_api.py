# -*- coding: utf-8 -*-
"""
End-to-end tests of the filters through real DRF API endpoints.

Requests go through ``test_project.urls`` (DRF router + viewsets using
``url_filter.integrations.drf.DjangoFilterBackend``) against the
``many_to_one`` fixture:

====  =====================  ==========  ===============
id    headline               pub_date    reporter
====  =====================  ==========  ===============
1     This is a test         2005-07-27  John Smith
2     John's second story    2005-07-29  John Smith
3     Paul's story           2006-01-17  Paul Jones
====  =====================  ==========  ===============
"""

from __future__ import print_function, unicode_literals

import pytest
from rest_framework.test import APIClient

ARTICLES = "/many-to-one/articles/"
REPORTERS = "/many-to-one/reporters/"


@pytest.fixture
def api(many_to_one):
    return APIClient()


def headlines(response):
    assert response.status_code == 200, response.content
    return sorted(i["headline"] for i in response.json())


def test_filter_across_relationships(api):
    # forward foreign key
    response = api.get(ARTICLES, {"reporter__first_name": "John"})
    assert headlines(response) == ["John's second story", "This is a test"]

    # reverse foreign key
    response = api.get(REPORTERS, {"articles__headline": "Paul's story"})
    assert response.status_code == 200
    assert [i["first_name"] for i in response.json()] == ["Paul"]


def test_lookup(api):
    response = api.get(ARTICLES, {"headline__icontains": "STORY"})

    assert headlines(response) == ["John's second story", "Paul's story"]


def test_exclude(api):
    response = api.get(ARTICLES + "?reporter__first_name!=John")

    assert headlines(response) == ["Paul's story"]


def test_multiple_filters_with_multi_value_lookup(api):
    response = api.get(
        ARTICLES,
        {"pub_date__range": "2005-01-01,2005-12-31", "headline__startswith": "John"},
    )

    assert headlines(response) == ["John's second story"]


def test_invalid_value_returns_400(api):
    response = api.get(ARTICLES, {"pub_date": "not-a-date"})

    assert response.status_code == 400
    assert "pub_date" in response.json()
