import json

settings_json = json.dumps([
    {'type': 'title',
     'title': 'Integration Settings'},
    {'type': 'numeric',
     'title': 'T Max',
     'desc': 'Seconds of simulation',
     'section': 'ODEsettings',
     'key': 'tmax'},
    {'type': 'numeric',
     'title': 'dt',
     'desc': 'Step of integration',
     'section': 'ODEsettings',
     'key': 'dt'}])