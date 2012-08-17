from django.db.models import Aggregate
from django.db.models.sql.aggregates import Aggregate as AggregateSQL
from django.db.models import Field
from django.utils.crypto import get_random_string


default_separator = '\\\",\\\"'
group_concat_sql_template = "%%(%s)s(DISTINCT REPLACE(REPLACE(%%(%s)s, '%%(%s)s', '%%(%s)s'), '%%(%s)s', '%%(%s)s') ORDER BY %%(%s)s SEPARATOR '%%(%s)s')" % (
    "function",
    "field",
    "bs",
    "bs_escaped",
    "quote",
    "quote_escaped",
    "field",
    "separator",
)

#group_concat_sql_template = "%%(%s)s(DISTINCT %%(%s)s ORDER BY %%(%s)s SEPARATOR '%%(%s)s')" % (
    #"function",
    #"field",
    #"field",
    #"separator",
#)


class ConcatenateSQL(AggregateSQL):
    sql_function = 'GROUP_CONCAT'
    def __init__(self, col, source=None, **extra):
        separator = extra.setdefault("separator", default_separator)
        extra.setdefault("bs", '\\\\')
        extra.setdefault("bs_escaped", '\\\\\\\\')
        extra.setdefault("quote", '\\\"')
        extra.setdefault("quote_escaped", '\\\\\\\"')
        
        self.sql_template = group_concat_sql_template
        c = ConcatonatedGroupField(separator=separator) # XXX
        super(ConcatenateSQL, self).__init__(col, source=c, **extra)

class Concatenate(Aggregate):
    name = 'Concatenate'
    
    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = ConcatenateSQL(col, separator=self.extra.get("separator", default_separator), is_summary=is_summary)
        #query.connection.ops.check_aggregate_support(aggregate)
        query.aggregates[alias] = aggregate

class ConcatonatedGroupField(Field):
    description = "Concatonated Group Field"
    
    def __init__(self, verbose_name=None, name=None, separator=default_separator, **kwargs):
        self.separator = separator
        Field.__init__(self, verbose_name, name, **kwargs)
    
    def get_internal_type(self):
        return "DecimalField" # because of bad default convert_value
        
def parse_concat(concatonated_group):
    unescape = lambda str : str.replace('\\\"', '\"').replace('\\\\', '\\')
    for item in getattr(concatonated_group, "split", lambda x: ())('\",\"'):
        yield unescape(item)
    
    
