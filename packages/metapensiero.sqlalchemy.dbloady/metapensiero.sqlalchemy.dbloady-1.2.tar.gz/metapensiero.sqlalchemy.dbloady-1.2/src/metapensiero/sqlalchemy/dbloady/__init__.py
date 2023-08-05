# -*- coding: utf-8 -*-
# :Project:   metapensiero.sqlalchemy.dbloady -- YAML based data loader
# :Created:   mer 10 feb 2010 14:35:05 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: Copyright (C) 2010-2016 Lele Gaifax
#

from logging import getLogger
from os.path import abspath, dirname, exists, join, normpath

import yaml

logger = getLogger(__name__)


class File(yaml.YAMLObject):
    """Facility to read the content of an external file.

    A field may be loaded from an external file, given its pathname
    which is interpreted as relative to the position of the YAML file
    currently loading::

        - entity: cpi.models.Document
          key: filename
          data:
            - filename: image.gif
              content: !File {path: ../image.gif}
    """

    yaml_tag = u'!File'

    basedir = None

    def __init__(self, path):
        self.path = path

    def read(self):
        fullpath = normpath(join(self.basedir, self.path))
        return open(fullpath).read()


def resolve_class_name(classname):
    """Import a particular Python class given its full dotted name.

    :param classname: full dotted name of the class,
                      such as "package.module.ClassName"
    :rtype: the Python class
    """

    modulename, _, classname = classname.rpartition('.')
    module = __import__(modulename, fromlist=[classname])
    return getattr(module, classname)



def load(fname, session, dry_run=False, delete=False, save_new_instances=False,
         adaptor=None, show_progress=False):
    """Load a single YAML file.

    :param fname: the name of the YAML file to load
    :param session: the SQLAlchemy session
    :param dry_run: whether to commit data at the end
    :param delete: whether instances shall be deleted instead of updated
    :param save_new_instances: if given, the name of the YAML file where
                               information about created instances will be written
    :param adaptor: either None or a function
    :param show_progress: whether to emit some noise as the process goes on
    :rtype: dict
    :returns: A dictionary with loaded data, keyed by (model class, key): each
              value is a tuple (primarykey, datadict)

    This will open the given file (that should contain a UTF-8 encoded
    YAML structure) and will load/update the data into the database, or
    deleted from there.

    The `adaptor` function, if specified, will be called once for each "record"
    and has the opportunity of deliberately change its content::

        user_id = 999

        def adjust_user(cls, key, data):
            if key == ['username']:
                data['username'] = data['username'] + str(user_id)
                data['user_id'] = user_id
            return data

        load('testdata.yaml', session, adaptor=adjust_user)

    When `delete` is ``True``, then existing instances will be deleted
    from the database instead of created/updated.

    If `save_new_instances` is given, it's a file name that will contain a YAML
    representation of the newly created instances, suitable to be used in a
    subsequent call with `delete` set to ``True``.

    When `dry_run` is ``False`` (the default) the function performs a
    ``flush()`` on the SQLAlchemy session, but does **not** commit the
    transaction.
    """

    from codecs import open
    from sys import stderr
    from sqlalchemy.orm import object_mapper

    from .entity import Entity

    if show_progress:
        stderr.write(fname)
        stderr.write(u': ')

    stream = open(fname, 'r', 'utf-8')

    # Set the base directory: file paths will be considered relative
    # to the directory containing the YAML file
    File.basedir = dirname(abspath(fname))

    idmap = {}
    loader = yaml.Loader(stream)
    while loader.check_data():
        entries = loader.get_data()
        for entry in entries:
            model = resolve_class_name(entry['entity'])
            entity = Entity(model, entry['key'],
                            fields=entry.get('fields', None),
                            data=entry.get('data', []),
                            delete=delete)
            for e in entity(session, idmap, adaptor):
                if show_progress:
                    stderr.write('-' if delete and e is not None else '.')

            if not dry_run:
                logger.debug(u"Flushing changes")
                session.flush()

    if show_progress:
        stderr.write('\n')

    if save_new_instances:
        existing_new_instances = set()
        new_new_instances = {}
        if exists(save_new_instances):
            with open(save_new_instances) as f:
                new_instances = yaml.load(f)
            for i in new_instances:
                entity = resolve_class_name(i['entity'])
                keys = i['key']
                for data in i['data']:
                    key = tuple(data[key] for key in keys)
                    existing_new_instances.add((entity, key))
        else:
            new_instances = []

    result = {}
    for i in idmap.values():
        key = []
        for fname in i.entity.key:
            if '->' in fname:
                attr, _, slot = fname.partition('->')
                value = getattr(i.instance, attr)[slot]
            else:
                value = getattr(i.instance, fname)
            key.append(value)
        if len(i.entity.key) == 1:
            key = key[0]
        else:
            key = tuple(key)
        mapper = object_mapper(i.instance)
        pk = mapper.primary_key_from_instance(i.instance)

        if (save_new_instances and i.created
            and (i.entity.model, tuple(pk)) not in existing_new_instances):
            entity = i.entity.model.__module__ + '.' + i.entity.model.__name__
            pknames = tuple(str(c.key) for c in mapper.primary_key)
            data = new_new_instances.setdefault((entity, pknames), [])
            data.append(dict(zip(pknames, pk)))

        if len(pk) == 1:
            pk = pk[0]
        result[(i.entity.model, key)] = pk, i.data

    if save_new_instances and new_new_instances:
        for entity, pknames in sorted(new_new_instances):
            new_instances.append(dict(entity=entity, key=list(pknames),
                                      data=new_new_instances[(entity, pknames)]))
        with open(save_new_instances, 'w') as f:
            yaml.dump(new_instances, f, default_flow_style=False, allow_unicode=True)

    return result
