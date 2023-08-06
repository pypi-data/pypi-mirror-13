from optparse import make_option
import django
from django.core.management.base import NoArgsCommand
from django.core.management.sql import sql_flush
from django.db import connections, DEFAULT_DB_ALIAS

SQL_DROP = 'DROP TABLE'


class Command(NoArgsCommand):
    help = "Returns a DROP TABLE SQL statement for all tables in the given database."

    option_list = NoArgsCommand.option_list + (
        make_option(
            '--database', action='store', dest='database',
            default=DEFAULT_DB_ALIAS,
            help='Nominates a database to print the SQL for. '
                 'Defaults to the "default" database.'),
    )

    output_transaction = True

    def handle(self, *args, **options):
        kwargs = dict(only_django=False, reset_sequences=False)
        if django.VERSION >= (1, 6):
            kwargs['allow_cascade'] = True
        s = '\n'.join(sql_flush(
            self.style, connections[options.get('database')], **kwargs))
        return s.replace('TRUNCATE', SQL_DROP).replace('DELETE FROM', SQL_DROP)
