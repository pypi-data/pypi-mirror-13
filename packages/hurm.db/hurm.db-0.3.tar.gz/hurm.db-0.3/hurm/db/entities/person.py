# -*- coding: utf-8 -*-
# :Project:   hurm -- Person class, mapped to table persons
# :Created:   sab 02 gen 2016 15:34:36 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2016 Lele Gaifax
#

from .. import translatable_string as N_
from . import AbstractBase


class Person(AbstractBase):
    @property
    def fullname(self):
        # TRANSLATORS: this is the full name of a person
        return N_('$firstname $lastname',
                  mapping=dict(firstname=self.firstname,
                               lastname=self.lastname))

    @property
    def abbreviated_fullname(self):
        # TRANSLATORS: this is the abbreviated full name of a person
        return N_('$firstname_initial. $lastname',
                  mapping=dict(firstname_initial=self.firstname[0],
                               lastname=self.lastname))
