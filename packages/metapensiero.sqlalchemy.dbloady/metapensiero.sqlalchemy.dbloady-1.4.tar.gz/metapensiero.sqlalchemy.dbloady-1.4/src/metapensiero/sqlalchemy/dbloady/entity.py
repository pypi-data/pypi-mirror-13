# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   sab 02 gen 2016 16:16:52 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: Copyright (C) 2016 Lele Gaifax
#

import sys
from logging import getLogger

from sqlalchemy.orm import object_mapper

if sys.version_info.major >= 3:
    from itertools import zip_longest
else:
    from itertools import izip_longest as zip_longest


logger = getLogger(__name__)

if sys.version_info.major >= 3:
    basestring = str


class Entity(object):
    """Model instances factory."""

    def __init__(self, model, key, fields=None, data=None, delete=False):
        """Initialize a new factory.

        :type model: string
        :param model: the dotted full name of a mapped class
        :type key: either a string or a sequence of strings
        :param key: name(s) of the field(s) used to lookup existing instance
        :type fields: either None or a sequence of strings
        :param fields: if given, a list of field names
        :type data: either a single mapping or a list
        :param data: values used to initialize/update instances
        :type delete: boolean
        :param delete: if ``True``, existing instances will be deleted
        """
        self.model = model
        if isinstance(key, basestring):
            key = [key]
        self.key = key
        self.fields = fields
        if isinstance(data, dict):
            data = [data]
        self.data = data
        self.delete = delete

    def __repr__(self):
        return "%s(model=%r, key=%r)" % (
            self.__class__.__name__,
            self.model, self.key)

    def __call__(self, session, idmap, adaptor=None):
        """Create and or update a sequence of instances.

        :param adaptor: either None or a callable
        :rtype: an iterator over created/referenced instances
        """

        instances = self.data
        if instances is None:
            return

        for data in instances:
            instance = Instance(self, data, self.fields, idmap, adaptor)
            yield instance(session, self.delete)


class Instance(object):
    """A single model instance."""

    def __init__(self, entity, data, fields, idmap, adaptor):
        self.entity = entity
        self.data = data
        self.fields = fields
        self.idmap = idmap
        self.adaptor = adaptor
        self.instance = None
        self.created = False

    def __call__(self, session, delete=False):
        "Load an existing instance, create a new one or delete it if it exists"

        from . import File

        if self.instance is not None:
            return self.instance

        model = self.entity.model
        key = self.entity.key

        data = self.data
        if (self.fields is not None and isinstance(data, list)
            and len(self.fields) == len(data)):
            data = {f: v for f, v in zip(self.fields, data)}

        if self.adaptor is not None:
            data = self.adaptor(self.entity.model, self.entity.key, data)

        def getvalue(key):
            value = data.get(key, None)
            return self.idmap.get(id(value), value)

        filter = []
        for fname in key:
            if '->' in fname:
                attrname, _, slot = fname.partition('->')
                fvalue = getvalue(attrname)[slot]
            else:
                attrname = fname
                slot = None
                fvalue = getvalue(fname)

            if (sys.version_info.major < 3
                and isinstance(fvalue, basestring)
                and not isinstance(fvalue, unicode)):
                fvalue = fvalue.decode('utf-8')

            if isinstance(fvalue, Instance):
                instance = fvalue(session)

                mapper = object_mapper(instance)
                pkeyf = mapper.primary_key
                pkeyv = mapper.primary_key_from_instance(instance)
                pkey = {f.name: v for f, v in zip_longest(pkeyf, pkeyv)}

                for l, r in getattr(model, attrname).property.local_remote_pairs:
                    filter.append(getattr(model, l.name) == pkey[r.name])
            else:
                attr = getattr(model, attrname)
                if slot is not None:
                    attr = attr[slot]
                filter.append(attr == fvalue)

        q = session.query(model)
        q = q.filter(*filter)
        obj = q.first()

        if delete:
            if obj is not None:
                session.delete(obj)
            return obj

        if obj is None:
            # Create a new one
            obj = model()
            session.add(obj)
            self.created = True

        self.idmap[id(self.data)] = self
        self.instance = obj

        # Update it
        for f,v in data.items():
            v = self.idmap.get(id(v), v)
            if isinstance(v, Instance):
                v = v(session)
            elif isinstance(v, File):
                v = v.read()
            setattr(obj, f, v)

        return obj
