# -*- coding: utf-8 -*-
# :Project:   hurm -- Database modelization
# :Created:   lun 14 dic 2015 15:56:04 CET
# :Author:    Lele Gaifax <lele@metapensiero.it>
# :License:   GNU General Public License version 3 or later
# :Copyright: © 2015, 2016 Lele Gaifax
#

from sqlalchemy import MetaData
from translationstring import TranslationStringFactory


metadata = MetaData()
"Container of all tables meta information."


translatable_string = TranslationStringFactory('hurm-db')
"A function to make a translatable string."


from .tables import *
