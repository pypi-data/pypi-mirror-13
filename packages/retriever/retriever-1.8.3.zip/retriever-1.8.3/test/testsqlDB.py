#retriever
from retriever.lib.templates import BasicTextTemplate
from retriever.lib.models import Table, Cleanup, correct_invalid_value

SCRIPT = BasicTextTemplate(tables={},
                           name="testing data",
                           citation="Henry's dataset check ur sql keywords",
                           urls={'testsql': 'file:///C:/Users/Henry/Documents/GitHub/retriever/test/testdatachecksql'},
                           shortname="testsqlDB",
                           description="testing data for sql keywords .")