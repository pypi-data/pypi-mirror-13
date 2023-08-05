import datetime
from django.conf import settings
from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth.models import User
from autofixture import AutoFixture

from badges.models import Badge
from badges.management.commands.create_badge_triggers import (
    create_trigger, drop_existing_triggers)

from dummy.models import Sketch


class TriggerMixin(object):
    """
    A convenient mixin for setup and teardown
    """
    def setUp(self):
        fixture = AutoFixture(User)
        fixture.create(100)

    def tearDown(self):
        drop_existing_triggers()


class PionnerTest(TriggerMixin, TestCase):
    """
    Check if pionner trigger is efficient
    """

    def test_trigger_create(self):
        """
        Create the pionner trigger, check if it does it's work
        """
        data = {
            "code": "pionner",
            "condition": "age(NEW.date_joined) > interval '1 year'",
            "name": "Pionner",
            "trigger_condition": "update",
            "trigger_table": "auth_user",
            "user_field": "id"
        }
        create_trigger(data)

        self.assertEqual(Badge.objects.count(), 0)
        users = User.objects.all()[:10]
        for user in users:
            user.date_joined = user.date_joined - datetime.timedelta(days=370)
            user.save()
        self.assertEqual(Badge.objects.count(), 10)


class CollectorTest(TriggerMixin, TestCase):
    """
    Check if pionner trigger is efficient
    """

    def test_trigger_create(self):
        """
        Create the collector trigger, check if it does it's work
        """

        data = {
            "code": "collector",
            "condition": "count(id) >= 5 from dummy_sketch where user_id = NEW.user_id",
            "name": "Collector",
            "trigger_condition": "insert",
            "trigger_table": "dummy_sketch",
            "user_field": "user_id"
        }
        create_trigger(data)

        self.assertEqual(Badge.objects.count(), 0)
        users = User.objects.all()[:10]
        for user in users:
            fixture = AutoFixture(
                Sketch,
                field_values={"user": user})
            fixture.create(5)
        self.assertEqual(Badge.objects.count(), 10)


class StarTest(TriggerMixin, TestCase):
    """
    Check if pionner trigger is efficient
    """

    def test_trigger_create(self):
        """
        Create the star trigger, check if it does it's work
        """

        data = {
            "code": "star",
            "condition": "NEW.hit_views >= 1000 ",
            "name": "Star",
            "trigger_condition": "update",
            "trigger_table": "dummy_sketch",
            "user_field": "user_id"
        }
        create_trigger(data)

        self.assertEqual(Badge.objects.count(), 0)
        users = User.objects.all()[:10]
        for user in users:
            fixture = AutoFixture(
                Sketch,
                field_values={"user": user, "hit_views": 0})
            sketch = fixture.create(1)[0]
            sketch.hit_views = 1000
            sketch.save()
        self.assertEqual(Badge.objects.count(), 10)


class TestTrigger(TriggerMixin, TestCase):
    """Here we test the whole story. """

    def test_no_triggers(self):
        """
        Try to create event that would normaly launch badge earning.
        Ensure it's not.
        """
        users = User.objects.all()[:10]
        for user in users:
            user.date_joined = user.date_joined - datetime.timedelta(days=370)
            user.save()
        # no pionner
        self.assertEqual(Badge.objects.count(), 0)

        for user in users:
            fixture = AutoFixture(
                Sketch,
                field_values={"user": user})
            fixture.create(5)
        # no collector
        self.assertEqual(Badge.objects.count(), 0)

        for user in users:
            fixture = AutoFixture(
                Sketch,
                field_values={"user": user, "hit_views": 0})
            sketch = fixture.create(1)[0]
            sketch.hit_views = 1000
            sketch.save()
        # no star
        self.assertEqual(Badge.objects.count(), 0)

    def test_with_trigger_file(self):
        """
        So ok no test but with the json file set in the settings
        """
        call_command("create_badge_triggers")
        # Do not be mean with me, we test only one command ok ?
        users = User.objects.all()[:10]
        for user in users:
            user.date_joined = user.date_joined - datetime.timedelta(days=370)
            user.save()
        # pionners \0/
        self.assertEqual(Badge.objects.count(), 10)

    def test_with_file_parameter(self):
        """ You can call the command with your own file, let's test this"""
        call_command("create_badge_triggers", file=settings.BADGES_FILE)
