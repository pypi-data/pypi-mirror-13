""" Command to do a database dump using database's native tools.
Originally inspired by http://djangosnippets.org/snippets/823/
"""
import os
import time
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        'Dump database into a file. Only MySQL and PostgreSQL engines are '
        'supported.'
    )

    option_list = BaseCommand.option_list + (
        make_option('--destination', dest='backup_directory',
                    help='Destination (path) where to place database dump file.'),
        make_option('--filename', dest='filename', default=False,
                    help='Name of the file, or - for stdout'),
        make_option('--db-name', dest='database_name', default='default',
                    help='Name of database (as defined in settings.DATABASES[]) to dump.'),
        make_option('--compress', dest='compression_command',
                    help='Optional command to run (e.g., gzip) to compress output file.'),
        make_option('--quiet', dest='quiet', action='store_true', default=False,
                    help='Be silent.'),
        make_option('--debug', dest='debug', action='store_true', default=False,
                    help='Show commands that are being executed.'),
    )

    OUTPUT_STDOUT = object()

    def handle(self, *args, **options):
        self.db_name = options.get('database_name', 'default')
        self.compress = options.get('compression_command')
        self.quiet = options.get('quiet')
        self.debug = options.get('debug')

        if self.db_name not in settings.DATABASES:
            raise CommandError(
                'Database %s is not defined in settings.DATABASES' % self.db_name)

        db_config = settings.DATABASES[self.db_name]
        self.engine = db_config.get('ENGINE')
        self.db = db_config.get('NAME')
        self.user = db_config.get('USER')
        self.password = db_config.get('PASSWORD')
        self.host = db_config.get('HOST')
        self.port = db_config.get('PORT')
        self.excluded_tables = db_config.get('DB_DUMP_EXCLUDED_TABLES', [])
        self.empty_tables = db_config.get('DB_DUMP_EMPTY_TABLES', [])

        backup_directory = db_config.get('DUMP_PATH', 'backups')
        backup_directory = options.get('backup_directory') or backup_directory
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)

        filename = options['filename']
        if not filename:
            outfile = self.destination_filename(backup_directory, self.db)
        elif filename == "-":
            outfile = self.OUTPUT_STDOUT
            self.quiet = True
        else:
            outfile = os.path.join(backup_directory, filename)

        if 'mysql' in self.engine:
            self.do_mysql_backup(outfile)
        elif 'postgresql' in self.engine:
            self.do_postgresql_backup(outfile)
        elif 'sqlite3' in self.engine:
            self.do_sqlite3_backup(outfile)
        else:
            raise CommandError(
                'Backups of %s engine are not implemented.' % self.engine)

        if self.compress:
            self.run_command('%s %s' % (self.compress, outfile))

    def destination_filename(self, backup_directory, database_name):
        filename = '{0:s}_backup_{1:s}.sql'\
            .format(database_name, time.strftime('%Y%m%d%H%M%S'))
        return os.path.join(backup_directory, filename)

    def do_sqlite3_backup(self, outfile):
        if not self.quiet:
            print 'Doing SQLite backup of database "%s" into %s' % (
            self.db, outfile)

        main_args = []
        excluded_args = main_args[:]

        command = 'sqlite3 %s .dump' % (self.db,)

        if outfile != self.OUTPUT_STDOUT:
            command += " > %s" % outfile

        self.run_command(command)

    def do_mysql_backup(self, outfile):
        if not self.quiet:
            print 'Doing MySQL backup of database "{0:s}" into {1:s}'\
                .format(self.db, outfile)

        main_args = []
        if self.user:
            main_args += ['--user=%s' % self.user]
        if self.password:
            main_args += ['--password=%s' % self.password]
        if self.host:
            main_args += ['--host=%s' % self.host]
        if self.port:
            main_args += ['--port=%s' % self.port]

        excluded_args = main_args[:]
        if self.excluded_tables or self.empty_tables:
            excluded_args += ['--ignore-table=%s.%s' % (self.db, excluded_table)
                              for excluded_table in
                              self.excluded_tables + self.empty_tables]

        command = 'mysqldump %s' % (' '.join(excluded_args + [self.db]))
        if outfile != self.OUTPUT_STDOUT:
            command += " > %s" % outfile
        self.run_command(command)

        if self.empty_tables:
            no_data_args = main_args[:] + ['--no-data', self.db]
            no_data_args += [empty_table for empty_table in self.empty_tables]
            command = 'mysqldump %s' % (' '.join(no_data_args))
            if outfile != self.OUTPUT_STDOUT:
                command += " >> %s" % outfile
            self.run_command(command)

    def run_command(self, command):
        if self.debug:
            print command
        os.system(command)

    def do_postgresql_backup(self, outfile):
        if not self.quiet:
            print 'Doing PostgreSQL backup of database "{0:s}" into {1:s}'\
                .format(self.db, outfile)

        env = {}
        if self.password:
            env['PGPASSWORD'] = self.password
        if self.user:
            # This is important! Sometimes pg_dump doesn't respect -U argument
            # and tries to connect to the database with the name of
            # the current user.
            env['PGUSER'] = self.user
        env_vars = ' '.join(["=".join(e) for e in env.items()],)

        main_args = []
        if self.user:
            main_args += ['-U %s' % self.user]
        main_args += ['--no-password']
        if self.host:
            main_args += ['--host=%s' % self.host]
        if self.port:
            main_args += ['--port=%s' % self.port]
        if outfile != self.OUTPUT_STDOUT:
            main_args += ['-f "%s"' % outfile]

        excluded_args = main_args[:]
        if self.excluded_tables or self.empty_tables:
            excluded_args += ['--exclude-table=%s' % excluded_table for
                              excluded_table in
                              self.excluded_tables + self.empty_tables]
        excluded_args += [self.db]
        command = '%s pg_dump -O %s ' % (env_vars, ' '.join(excluded_args))
        if outfile != self.OUTPUT_STDOUT:
            command += ' > %s' % outfile
        self.run_command(command)

        if self.empty_tables:
            no_data_args = main_args[:] + ['--schema-only']
            no_data_args += ['--table=%s' % empty_table for empty_table in self.empty_tables]
            no_data_args += [self.db]
            command = '%s pg_dump %s %s' % (env_vars, ' '.join(no_data_args), self.db)
            if outfile != self.OUTPUT_STDOUT:
                command += ' >> %s' % outfile
        self.run_command(command)
