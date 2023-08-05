import requests
from uuid import uuid4


class Agent(object):
    """
    Agent interface for an API.AI agent
    """

    base_url = 'https://api.api.ai/v1'

    def __init__(self, sub_key, client_token, dev_token,
                 session=None, timezone=None):
        """
        :param client_token: client access token
        :param dev_token: developer access token
        :param session: A string token up to 36 symbols long,
                        used to identify the client and to manage
                        sessions parameters (including contexts)
                        per client.
        """
        self.client_token = client_token
        self.dev_token = dev_token
        self.sub_key = sub_key
        self.session = session or str(uuid4())
        self.timezone = timezone

        self.request_session = requests.Session()
        self.request_session.headers.update({
            'Authorization': 'Bearer %s' % self.dev_token or self.client_token,
            'ocp-apim-subscription-key': self.sub_key,
        })

    def get(self, url, **kwargs):
        return self.request_session.get(url, **kwargs).json()

    def post(self, url, data=None, json=None, **kwargs):
        return self.request_session.post(url, data, json, **kwargs).json()

    def put(self, url, data=None, **kwargs):
        response = self.request_session.put(url, data, **kwargs)
        return response.json()

    def query(
            self, query, confidence=None, lang='en', contexts=None,
            resetContexts=False, entities=None, timezone=None, session=None):
        """
        Use when you want to make a single query.

        For multiple queries use multi_query (TODO)

        :param query: The natural language text to be processed.
        :param confidence: The confidence of the corresponding query
                           parameter having been correctly recognized
                           by a speech recognition system. 0 represents
                           no confidence and 1 represents the highest
                           confidence.
        """
        return self.post(
            self.base_url + '/query',
            params={'v': '20150910'},
            json={
                'query': query,

                'lang': lang,
                'contexts': contexts if contexts is not None else [],
                'resetContexts': resetContexts,
                'entities': entities if entities is not None else [],

                'timezone': timezone or self.timezone,
                'sessionId': session if session is not None else self.session,
            }
        )

    @property
    def entities(self):
        """
        Return an entities handler object
        """
        return Entities(self)

    @property
    def intents(self):
        """
        Return an intents handler object
        """
        return Intents(self)


class Endpoint(object):
    version = "20150910"

    def __init__(self, client):
        self.client = client

    def all(self):
        """
        return all the records in the endpoint
        """
        return self.client.get(
            self.client.base_url + self.path,
        )


class Entities(Endpoint):
    """
    An entity is a data type that contains mappings between a set of synonyms
    """

    path = "/entities"

    def create(self, name, entries):
        """
        Create a new entity with the name

        :param name: Name of the entity
        :param entries: List of dictionaries

        .. code-block:: python

            agent.entities.create(
                'EntityName',
                [{
                    "value": "Coffee Maker",
                    "synonyms": ["coffee maker", "coffee machine"]
                }, {
                    "value": "Thermostat",
                    "synonyms": ["Thermostat", "heat", "air conditioning"]
                }, {
                    "value": "Lights",
                    "synonyms": ["lights", "light", "lamps"]
                }, {
                    "value": "Garage door",
                    "synonyms": ["garage door", "garage"]
                }]
            )
        """
        return self.client.post(
            self.client.base_url + self.path,
            params={'v': self.version},
            json={
                'name': name,
                'entries': entries,
            },
        )

    def update(self, entity_id, entries, name=None):
        """
        Update an existing entity
        """
        json = {
            'id': entity_id,
            'entries': entries,
        }
        if name is not None:
            json['name'] = name

        return self.client.put(
            self.client.base_url + self.path + '/%s' % entity_id,
            json=json,
            params={'v': self.version}
        )


class Intents(Endpoint):
    """
    Intents convert a number of user expressions or patterns into an action.
    """

    path = "/intents"

    def create(self, name, contexts=None, templates=None, responses=None):
        """
        For explanation of the params read:
        https://docs.api.ai/docs/intents#intent-object
        """
        json = {
            'name': name,
            'contexts': contexts if contexts is not None else [],
            'templates': templates if templates is not None else [],
            'responses': responses if responses is not None else [],
        }
        return self.client.post(
            self.client.base_url + self.path,
            params={'v': self.version},
            json=json,
        )
