# Tracks the `role` field that app_cc/models.py attaches to the built-in
# User model via `User.add_to_class('role', ...)`.
#
# Django's autodetector normally puts an AddField for this under
# django.contrib.auth's own migrations (since that's where User lives),
# which would land outside this project (in Django's installed package)
# and never get committed. A plain AddField placed here instead fails —
# Django resolves it against `('app_cc', 'user')` in its migration state,
# which doesn't exist, since User genuinely belongs to 'auth'.
#
# SeparateDatabaseAndState works around that: the database_operations
# below add the column for real (skipped if it's already there, e.g. on
# a database that predates this migration), while state_operations is
# left empty so we never touch Django's 'auth' app state from here. One
# consequence: `makemigrations --check` will keep reporting this field as
# "pending" for the 'auth' app — that's expected given the add_to_class
# pattern, not a sign this migration didn't work.
#
# Must depend on auth's LAST migration, not just an earlier one: SQLite
# can't alter a column in place, so Django rebuilds the whole table for
# some auth migrations (e.g. changing first_name's max_length) — rebuilt
# from Django's own tracked state, which doesn't know about `role`. Run
# this after all of those, or the rebuild silently drops the column again.

from django.db import migrations


def add_role_column(apps, schema_editor):
    connection = schema_editor.connection
    with connection.cursor() as cursor:
        existing_columns = {
            column.name
            for column in connection.introspection.get_table_description(
                cursor, "auth_user"
            )
        }
    if "role" in existing_columns:
        return

    sql = "ALTER TABLE auth_user ADD COLUMN role varchar(50) NOT NULL DEFAULT 'Aluno'"
    schema_editor.execute(sql)


class Migration(migrations.Migration):

    dependencies = [
        ('app_cc', '0011_todoitem_priority_todoitem_priority_value_and_more'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(add_role_column, migrations.RunPython.noop),
            ],
            state_operations=[],
        ),
    ]
