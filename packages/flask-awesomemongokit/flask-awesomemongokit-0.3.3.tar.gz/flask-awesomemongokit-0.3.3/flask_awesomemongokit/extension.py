#!/usr/bin/env python
# -*- coding: utf-8 -*-

import importlib

import pymongo

from mongokit import ReplicaSetConnection, Connection


class Singleton(object):
    """ Base class or mixin for classes that wish to implement Singleton
    functionality.  If an instance of the class exists, it's returned,
    otherwise a single instance is instantiated and returned.

    Metaclasses were not used because it's too magical.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                Singleton, cls
            ).__new__(
                cls, *args, **kwargs
            )
        return cls._instance


class AwesomeMongoKitError(Exception):
    pass


class AwesomeMongoKit(Singleton):
    """ A Mongo connection class that automagically returns a MongoKit
    ReplicaSetConnection or Connection instance as appropriate.  Inherits from
    Singleton to prevent instantiation of multiple instances, thus preventing
    unneeded database connections.

    This module looks for a list of Mongo document instances in the config.
    """
    def __init__(self, flask_app):
        self._connection = None
        self.app = flask_app
        if not hasattr(flask_app, 'extensions'):
            flask_app.extensions = {}
        flask_app.extensions['raxentmongokit'] = self

    @property
    def connection(self):
        """ This dangling participle (some might call it an instance attribute)
        on which to grab MongoKit Document objects that have, or should have,
        been registered.  Dynamically returns the appropriate instance of a
        ReplicaSet or standard MongoDB connection instance.
        """
        if self._connection:
            return self._connection

        uri = self.app.config.get('MONGODB_URI')
        kwargs = self.app.config.get('MONGO_KWARGS', {})

        if not uri:
            raise AwesomeMongoKitError('Missing MONGODB_URI in app config')

        parsed = pymongo.uri_parser.parse_uri(uri)
        if len(parsed.get('nodelist', [])) > 1:
            cls = ReplicaSetConnection
        else:
            cls = Connection

        self._connection = cls(uri, **kwargs)
        self._connection.register(self._handle_registrations())

        return self._connection

    def _handle_registrations(self, ignore_missing_docs=True):
        """ This method looks to a Flask app's config object, and fetches
        MONGOKIT_DOCUMENTS attribute.  It parses this list of strings, and
        imports the classes using the dot-notated package.module.Class names,
        returning the Class objects in a list.

        :return: A list of MongoKit document classes
        """
        documents = []
        try:
            MONGOKIT_DOCUMENTS = self.app.config['MONGOKIT_DOCUMENTS']
        except KeyError:
            return documents

        for docname in MONGOKIT_DOCUMENTS:
            try:
                mod_name = ".".join(str(docname).split('.')[:-1])
            except IndexError:
                raise AwesomeMongoKitError(
                    'Unable to parse MongoKit document class from %s' % docname
                )

            try:
                module = importlib.import_module(mod_name)
            except ImportError:
                raise AwesomeMongoKitError(
                    'Unable to import MongoKit module from %s' % mod_name
                )

            try:
                cls_name = str(docname).split('.')[-1]
            except IndexError:
                raise AwesomeMongoKitError(
                    'Unable to parse MongoKit document class name from '
                    '%s' % docname
                )

            try:
                doc_cls = getattr(module, cls_name)
            except AttributeError as e:
                raise AwesomeMongoKitError(e.message)

            documents.append(doc_cls)
        return documents
