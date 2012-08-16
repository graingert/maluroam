from django.db.models import Aggregate
from django.db.models.sql.aggregates import Aggregate as AggregateSQL
from django.db.models import Field
from django.utils.crypto import get_random_string

class ConcatenateSQL(AggregateSQL):
    sql_function = 'GROUP_CONCAT'
    def __init__(self, col, separator=' / ', source=None, **extra):
        self.sql_template = "%%(function)s(DISTINCT(%%(field)s) ORDER BY %%(field)s SEPARATOR '%s')" % separator
        c = ConcatonatedGroupField(separator=separator) # XXX
        super(ConcatenateSQL, self).__init__(col, source=c, **extra)

class Concatenate(Aggregate):
    name = 'Concatenate'
    
    def add_to_query(self, query, alias, col, source, is_summary):
        aggregate = ConcatenateSQL(col, separator=self.extra.get("separator", ' / '), is_summary=is_summary)
        #query.connection.ops.check_aggregate_support(aggregate)
        query.aggregates[alias] = aggregate

class ConcatonatedGroupField(Field):
    description = "Concatonated Group Field"
    
    def __init__(self, verbose_name=None, name=None, separator=' / ', **kwargs):
        self.separator = separator
        Field.__init__(self, verbose_name, name, **kwargs)
    
    def get_internal_type(self):
        return "DecimalField" # because of bad default convert_value
    
    def to_python(self, value):
        print "converted to python"
        return value.split(separator)
