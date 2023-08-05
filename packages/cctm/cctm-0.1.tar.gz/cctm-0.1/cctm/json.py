# -*- coding:utf-8 -*-
import json
from functools import partial
from collections import OrderedDict

load = partial(json.load, object_pairs_hook=OrderedDict)
loads = partial(json.loads, object_pairs_hook=OrderedDict)
dump = partial(json.dump, indent=2, ensure_ascii=False)
dumps = partial(json.dumps, indent=2, ensure_ascii=False)
