Badges are earned by users for meeting some `conditions` defined
in the badge.json file

A Badge object (database model) is then created linking a user to a badge.

conditions
----------

Condition is a sql check to be made for awarding a badge.

You have access to the variable NEW if you set the `trigger_contition`
to "update" or "insert". This is the database object after update or insert.

You have access to the variable OLD if you set the `trigger_contition`
to "update" or "delete". This is the database object after update or delete.


triggers
--------

We want the badges to be given as soon as a condition is meet. Even if
the event come from an event outside the Django application.

We do not want to relly on celery to periodicaly check for badges

- Too often : this is a performance bootleneck
- Too late : annoying for users

The check for each badge is checked when "something" change.

To create the database triggers that will be responsible for badge earning run:

>>> python manage.py create_badge_triggers

When you change `badge.json` (adding, updating or deleting badges) run this commande to reflect those changes in the database.

badge.json example
------------------
```
[{"name": "Pionner",
"code": "pionner",
"condition": "age(NEW.date_joined) > interval '1 year'",
"trigger_condition": "update",
"trigger_table": "auth_user",
"user_field": "id"
},
{"name": "Collector",
"code": "collector"
"condition": "count(id) >= 5 from dummy_sketch where user_id = NEW.user_id",
"trigger_condition": "insert",
"trigger_table": "dummy_sketch",
"user_field": "user_id"
},
{"name": "Star",
"code": "star",
"condition": "hit_views > 1000 ",
"trigger_condition": "update",
"trigger_table": "dummy_sketch",
"user_field": "user_id"
}]
```
`name` is the name of the badge as it will be displayed in the front or the API.

`code` is th unique code name of the badge

`condition` is the query that will be issued to check if the badge
should be earned

`trigger_contition` tell when the check must be made. One of insert,
update or delete

INSTALL
=======

see `INSTALL` file for instructions.
