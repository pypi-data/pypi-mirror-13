import json

from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from vizydrop.fields import *
from vizydrop.sdk.account import Account
from vizydrop.sdk.application import Application
from vizydrop.sdk.source import DataSource
from vizydrop.sdk.source import SourceSchema
from .filter import BlankFilter
from .schema import ApiExampleSchema

"""
The **APIExample** is a simple Vizydrop Third-Party Application (TPA) that demonstrates
how to create an application that interfaces with an external REST API.
"""

# === The Application class ===

class ApiExample(Application):
    """
    The Application class is what ties together the multiple pieces of an application - sources and
    authentication schemes - as well as provides basic identifying information about the application.
    """
    class Meta:
        """
        All elements are tied together in our Meta class
        """
        version = "1.0"
        name = "External API Example"
        website = "http://www.vizydrop.com/"
        color = "#FF9900"
        description = "This is just an API example from the Vizydrop Python SDK."
        tags = ['example', 'api', ]

        # Give our list of available authentication options...
        authentication = [NoAuth, ]

        # ...and do the same with our sources
        sources = [ApiExampleSource, ]

# === The Account class ===

class NoAuth(Account):
    """
    The Account class is how we specify what authentication schemes are available for our application
    """
    class Meta:
        identifier = 'none'
        name = "No Auth"
        description = "No Authentication Necessary"

    def get_request(self, url, **kwargs):
        """
        In the real world, `get_request` would add to an HTTP request whatever information for authentication
        is required, such as HTTP Headers, OAuth Tokens, API tokens, etc.
        """
        return HTTPRequest(url, **kwargs)

    @gen.coroutine
    def validate(self):
        """
        Our `validate` routine performs the actual validation of an account and returns a tuple (bool, str)
        indicating whether an account is valid and what error(s) have occurred
        """
        return True, None

    def get_friendly_name(self):
        """
        We must also provide a way to give a friendly name to an account - in the real world, this would include
        identifying information such as account name, email, etc.
        """
        return "Vizydrop flatfile App Example"


# === The SourceSchema class ===

class ApiExampleSchema(SourceSchema):
    """
    Here we define what fields we will receive back from our API, if it is well-formed.  Specifying a schema is
    not required, but recommended if your data is consistent and can be statically defined.
    """
    id = TextField(name="ID")
    name = TextField(name="Name")
    publicationStage = TextField(name="Publication Stage")
    downloadCount = TextField(name="Download Count")
    viewCount = TextField(name="View Count")
    numberOfComments = TextField(name="Comment Count")
    # Notice the `response_loc` kwarg - this is used by an internal helper to grab the value for this field.  In our
    # data, `owner` is a dict, therefore we must tell Vizydrop to take the value of the `displayName` key within the
    # `owner` dict.
    owner = TextField(name="Owner", response_loc="owner-displayName")



# === The Data Source ===
class ApiExampleSource(DataSource):
    """
    Our DataSource class is where the main magic of a Vizydrop TPA happens - this is where we actually retrieve
    data.
    """
    class Meta:
        # Like all classes, we must have a Meta class with some basic identifying information
        identifier = "views"
        name = "Views"
        tags = ["view", ]
        description = "Views available in the Consumer Complaints Database"
        filter = BlankFilter

    # Be sure to include our source schema
    class Schema(ApiExampleSchema):
        pass

    @classmethod
    @gen.coroutine
    def get_data(cls, account, source_filter, limit=100, skip=0):
        """
        This is where we actually gather data.  In this example, we are grabbing information from a public
        API.
        """
        client = AsyncHTTPClient()

        uri = 'http://data.consumerfinance.gov/api/views.json'

        # Be sure to use account.get_request so that any authentication information can be added
        req = account.get_request(uri)
        resp = yield client.fetch(req)

        # load the response
        data = json.loads(resp.body.decode('utf-8'))

        # this helper function will "format" our data according to the schema we've specified above
        formatted = cls.format_data_to_schema(data)

        # and we finish up by sending our formatted data away
        return json.dumps(formatted)
