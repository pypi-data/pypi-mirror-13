import json
from django.db import connection
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from os.path import dirname, join

"""
Commands used to create or update badges triggers.
"""

DROP_TEMPLATE = """
SELECT proname, relname FROM
    (pg_trigger JOIN pg_class ON tgrelid=pg_class.oid)
JOIN pg_proc ON (tgfoid=pg_proc.oid) WHERE proname LIKE 'badge_%';
"""

class Command(BaseCommand):
    def add_arguments(self, parser):

        parser.add_argument(
            '--file',
            action='store_true',
            dest='file',
            default=None,
            help='Chose a badge file')

    def handle(self, *args, **options):
        if options["file"]:
            fd = options["file"]
        else:
            if hasattr(settings, "BADGES_FILE"):
                fd = settings.BADGES_FILE
            else:
                raise CommandError(
                    "You must set the BADGES_FILE location in your settings"
                )
        with open(fd) as json_file:
            create_triggers(json_file.read())


def validate(badge_dict):
    for key in ["name", "code", "condition",
                "trigger_condition", "trigger_table",
                "user_field"]:
        if not badge_dict.get(key):
            raise ValueError("the badge definition need a {} key".format(key))


def drop_existing_triggers():
    """
    Every badges triggers are prefixed with "badge_"
    So we first get all the existing triggers and delete them.
    One by one... No mercy.
    """
    with connection.cursor() as cur:
        cur.execute(DROP_TEMPLATE)

        for result in cur.fetchall():
            cur.execute("DROP TRIGGER {} ON {}".format(result[0], result[1]))


def create_trigger(badge_dict, check_needed=True):
    """
    Create the underlying triggers for the badge process to work
    """
    if check_needed:
        validate(badge_dict)
    with open(join(dirname(__file__), "trigger.sql")) as sql:
        with connection.cursor() as cur:
            # We do not catch errors here because we want the user
            # beeing able to easily debug with as much information as
            # possible
            cur.execute(sql.read().format(**badge_dict))


def create_triggers(badge_files):
    """
    Create all the triggers in the badges.json file
    """
    # No error catching here. If there is an error in the json file,
    # we want to know as soon as possible.
    badge_dicts = json.loads(badge_files)
    # We check for missing keys in the badge_dicts because we will
    # soon destroy existing badges and we want to be able to revert
    # before old triggers been destroyed
    for badge_dict in badge_dicts:
        validate(badge_dict)
    # If all triggers validated, we can destroy old triggers:
    drop_existing_triggers()
    # and create triggers for each dict we get without futher validation:
    for badge_dict in badge_dicts:
        create_trigger(badge_dict, check_needed=False)
