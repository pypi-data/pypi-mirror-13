from doublex import Stub

from linkstore.linkstore import Linkstore
from linkstore.link_storage import SqliteLinkStorage, SqliteConnectionFactory
from linkstore.clock import Clock


def an_in_memory_sqlite_link_storage_on_any_date():
    return an_in_memory_sqlite_link_storage_on_date('18/12/2015')

def an_in_memory_sqlite_link_storage_on_date(a_date):
    with Stub(Clock) as clock_stub:
        clock_stub.date_of_today().returns(a_date)

    return SqliteLinkStorage(SqliteConnectionFactory.create_in_memory(), clock_stub)

def before_scenario(context, scenario):
    context.link_storage = an_in_memory_sqlite_link_storage_on_any_date()
    context.linkstore = Linkstore(context.link_storage)
