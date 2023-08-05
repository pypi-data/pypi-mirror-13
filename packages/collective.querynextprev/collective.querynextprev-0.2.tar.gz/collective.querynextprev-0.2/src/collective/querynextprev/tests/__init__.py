# -*- coding: utf-8 -*-
import json


query = json.dumps({
    'portal_type': 'Document',
    'sort_on': 'sortable_title',
    'title': 'é'
})


class DummyView(object):
    pass
