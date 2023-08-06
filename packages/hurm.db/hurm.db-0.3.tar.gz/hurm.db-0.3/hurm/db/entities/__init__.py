# -*- coding: utf-8 -*-
# :Project:   hurm -- Abstract base class for entities
# :Created:   sab 02 gen 2016 15:24:29 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

import sqlalchemy as sa
from sqlalchemy import orm

from .. import tables


DBSession = orm.scoped_session(orm.sessionmaker())
"The global SA session maker"


class AbstractBase(object):
    "Abstract base entity class."

    def __init__(self, **kwargs):
        """Initialize an instance of this class.

        :param kwargs: initial values for the instance attributes

        Initialize a new instance of this class, copying any keyword
        argument into the corresponding instance attribute.
        """

        cls_ = type(self)
        for k in kwargs:
            if not hasattr(cls_, k):
                raise TypeError(
                    "%r is an invalid keyword argument for %s" %
                    (k, cls_.__name__))
            setattr(self, k, kwargs[k])

    def delete(self):
        "Delete this instance from the database."

        sa.orm.object_session(self).delete(self)

    def update(self, data, missing_only=False):
        """Update the instance with given data.

        :param data: a mapping kind of container
        :param missing_only: a boolean flag, ``False`` by default
        :rtype: dict
        :returns: a mapping between field name and a tuple ``(oldvalue, newvalue)``,
                  for each modified field

        If `missing_only` is ``True`` then only the fields that are currently `empty`
        (that is, their value is either ``None`` or an empty string) are updated.
        """

        changes = {}

        for attr in data:
            if hasattr(self, attr):
                cvalue = getattr(self, attr)
                if missing_only:
                    if not (cvalue is None or cvalue == '' or
                            cvalue is True or cvalue is False):
                        continue
                nvalue = data[attr]
                if cvalue != nvalue:
                    setattr(self, attr, nvalue)
                    changes[attr] = (cvalue, nvalue)

        return changes

    def __repr__(self):
        "Return an ASCII representation of the entity."

        from itertools import zip_longest

        mapper = sa.orm.object_mapper(self)
        pkeyf = mapper.primary_key
        try:
            pkeyv = mapper.primary_key_from_instance(self)
        except sa.orm.exc.DetachedInstanceError:
            keys = u"detached-instance"
        else:
            keys = u', '.join(u'%s=%s' % (f.name, v)
                              for f, v in zip_longest(pkeyf, pkeyv))
        return u'<%s %s>' % (# pragma: no cover
                             self.__class__.__name__, keys)


from .activity import Activity
from .availability import Availability
from .duty import Duty
from .edition import Edition
from .location import Location
from .person import Person
from .task import Task


orm.mapper(Activity, tables.activities, properties={
})

orm.mapper(Availability, tables.availabilities, properties={
    'edition': orm.relationship(Edition),
})

orm.mapper(Duty, tables.duties, properties={
    'task_date': sa.orm.deferred(sa.select([tables.tasks.c.date])
                                 .where(tables.tasks.c.idtask == tables.duties.c.idtask)),
})

orm.mapper(Person, tables.persons, properties={
    'availabilities': orm.relationship(Availability,
                                       backref='person',
                                       order_by=[Availability.date, Availability.starttime]),
    'duties': orm.relationship(Duty,
                               backref='person',
                               order_by=[Duty.task_date, Duty.starttime]),
})

orm.mapper(Task, tables.tasks, properties={
    'activity': orm.relationship(Activity),
    'duties': orm.relationship(Duty,
                               backref='task',
                               order_by=[Duty.starttime]),
})

orm.mapper(Edition, tables.editions, properties={
    'tasks': orm.relationship(Task,
                              backref='edition',
                              order_by=[Task.date, Task.starttime]),
})

orm.mapper(Location, tables.locations, properties={
    'tasks': orm.relationship(Task,
                              backref='location',
                              order_by=[Task.date, Task.starttime]),
})
