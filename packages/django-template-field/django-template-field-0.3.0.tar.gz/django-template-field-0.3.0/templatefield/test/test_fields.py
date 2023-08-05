#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-template-field
------------

Tests for `django-template-field` fields.
"""
import pytest
from django.test.utils import override_settings

from .models import RelatedToTemplatedText, TemplatedText


pytestmark = pytest.mark.django_db


class TestTemplatefield(object):

    def setUp(self):
        self.tmpl = "{{ template_var }} are pretty neat"
        self.model = TemplatedText(value=self.tmpl)
        self.model.save()
        self.related_model = RelatedToTemplatedText(templated_text=self.model)
        self.related_model.save()

    def test_none(self):
        tt = TemplatedText(value=None)
        tt.save()
        assert TemplatedText.objects_unrendered.first().value == None

    def test_unrendered(self):
        self.setUp()
        tt = TemplatedText.objects_unrendered.first()
        assert tt.value == self.tmpl

    def test_rendered(self):
        self.setUp()
        tt = TemplatedText.objects_rendered.first()
        assert tt.value == "Dogs are pretty neat"

    def test_rendered_related(self):
        self.setUp()
        rttt = RelatedToTemplatedText.objects.first()
        assert rttt.templated_text.value == "Dogs are pretty neat"

    def test_qs_context(self):
        self.setUp()
        tt = TemplatedText.objects_rendered.with_context(
            {'template_var': 'Cats'}).first()
        assert tt.value == "Cats are pretty neat"
