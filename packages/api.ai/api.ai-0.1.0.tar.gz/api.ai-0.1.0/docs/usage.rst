=====
Usage
=====

To use api_ai in a project::

    from api.ai import Agent

Configure the agent::

    agent = Agent(
        '<subscription-key>',
        '<client-access-token>',
        '<developer-access-token>', 
    )

Query::

    agent.query("hello there")

Entities
--------

List all entities::

    agent.entities.all()

Create a new Entity::

    agent.entities.create(
        'Languages', [
            {'value': 'Python', 'synonyms': ['python', 'py']},
            {'value': 'Golang', 'synonyms': ['go', 'google go language']},
        ]
    )

Update an entity with new entries::

    agent.entities.update(
        'entity-id-uuid',
        [
            {'value': 'Python', 'synonyms': ['python', 'py']},
            {'value': 'Golang', 'synonyms': ['go', 'google go language']},
        ],
    )

Intents
-------

List all intents::

    agent.intents.all()

Create a new Intent::

    agent.intents.create(
        'name',
        'templates': [
            "Who am I?"
        ]
    )

API Reference
-------------

.. automodule:: api.ai
    :members:
    :inherited-members:
