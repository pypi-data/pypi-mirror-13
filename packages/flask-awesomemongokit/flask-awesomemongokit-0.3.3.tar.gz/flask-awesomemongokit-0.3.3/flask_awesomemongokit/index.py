#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pymongo
from pymongo.errors import DuplicateKeyError

from .extension import AwesomeMongoKit


def index_helper(flask_app, mongokit_doc):
    """ Given a MongoKit document, using the "old" syntax for specifying
    collection indexes, create an index on a MongoDB collection.

    :param mongokit_doc: MongoKit Document-subclass
    :return: Results as a list of tuples in the form of
    (MongoDB parsed indexes, pymongo ensure_index result)
    """
    results = []
    for index_group in mongokit_doc.indexes:
        indexes = [(key, pymongo.ASCENDING) for key in index_group['fields']]
        mongo = AwesomeMongoKit(flask_app)
        db = getattr(mongo.connection, mongokit_doc.__database__)
        coll = mongokit_doc.__collection__
        unique = index_group.get('unique', False)
        try:
            result = db[coll].ensure_index(indexes, unique=unique)
        except DuplicateKeyError as e:
            result = e
        results.append((indexes, result))
    return results


def index_all_docs(flask_app):
    mongo = flask_app.extensions['raxentmongokit']
    rdct = {}
    for doc in mongo.connection._registered_documents.values():
        result = index_helper(flask_app, doc)
        rdct[doc] = result
    return rdct
