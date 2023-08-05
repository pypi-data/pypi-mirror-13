# coding: utf-8

"""
django informer checker for Database
"""

import logging

from datetime import datetime

from django.conf import settings
from django.db import (
    connection, Error, InterfaceError, DatabaseError, DataError,
    OperationalError, IntegrityError, InternalError, ProgrammingError,
    NotSupportedError)

from informer.checker.base import BaseInformer, InformerException
from informer.models import Raw


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseInformer(BaseInformer):
    """
    Database Informer.
    """

    def __str__(self):
        return u'Check if Database is operational.'

    def check_availability(self):
        """
        Inspect default database configuration.
        """
        try:
            Raw.objects.count()
        except (Error, InterfaceError, DatabaseError, DataError,
                OperationalError, IntegrityError, InternalError,
                ProgrammingError, NotSupportedError):
            return False, 'Oh no. Your database is out!'
        except Exception as error:
            raise InformerException(
                'An error occured when trying access database: %s' % error)
        else:
            return True, 'Your database is operational.'


class PostgresInformer(DatabaseInformer):
    """
    Extends default (Database Informer) and add PG stats.

    The queries and some insights, started from this gist:
    https://gist.github.com/robertsosinski/6345564
    """

    def __init__(self):
        self.database = settings.DATABASES.get('default').get('NAME')
        self.cursor = connection.cursor()

        self.EXCEPTIONS = (
            Error, InterfaceError, DatabaseError, DataError, OperationalError,
            IntegrityError, InternalError, ProgrammingError, NotSupportedError)

    def check_size(self):
        try:
            query = self.get_query_database_stats()
            self.cursor.execute(query)

            db, size, commit, rollback, read, hit = self.cursor.fetchone()
        except self.EXCEPTIONS as db_err:
            return 0, 'We can not get the database size (%s).' % db_err
        except Exception as err:
            raise InformerException('Failure to access the database: %s' % err)
        else:
            return size, 'size on %s' % datetime.now()

    def check_commit(self):
        try:
            query = self.get_query_database_stats()
            self.cursor.execute(query)

            db, size, commit, rollback, read, hit = self.cursor.fetchone()
        except self.EXCEPTIONS as db_err:
            return 0, 'We can not get the database commit (%s).' % db_err
        except Exception as err:
            raise InformerException('Failure to access the database: %s' % err)
        else:
            return commit, 'commit on %s' % datetime.now()

    def check_rollback(self):
        try:
            query = self.get_query_database_stats()
            self.cursor.execute(query)

            db, size, commit, rollback, read, hit = self.cursor.fetchone()
        except self.EXCEPTIONS as db_err:
            return 0, 'We can not get the database rollback (%s).' % db_err
        except Exception as err:
            raise InformerException('Failure to access the database: %s' % err)
        else:
            return rollback, 'rollback on %s' % datetime.now()

    def check_read(self):
        try:
            query = self.get_query_database_stats()
            self.cursor.execute(query)

            db, size, commit, rollback, read, hit = self.cursor.fetchone()
        except self.EXCEPTIONS as db_err:
            return 0, 'We can not get the database read (%s).' % db_err
        except Exception as err:
            raise InformerException('Failure to access the database: %s' % err)
        else:
            return read, 'read on %s' % datetime.now()

    def check_hit(self):
        try:
            query = self.get_query_database_stats()
            self.cursor.execute(query)

            db, size, commit, rollback, read, hit = self.cursor.fetchone()
        except self.EXCEPTIONS as db_err:
            return 0, 'We can not get the database hit (%s).' % db_err
        except Exception as err:
            raise InformerException('Failure to access the database: %s' % err)
        else:
            return hit, 'hit on %s' % datetime.now()

    def get_query_database_stats(self):
        return """
            SELECT
                datname,
                pg_database_size('{0}') db_size,
                xact_commit,
                xact_rollback,
                blks_read,
                blks_hit
            FROM
                pg_stat_database
            WHERE
                datname = '{0}'""".format(self.database)
