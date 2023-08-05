
from django.apps import AppConfig


default_app_config = 'leonardo_counters.Config'


LEONARDO_APPS = ['leonardo_counters']

LEONARDO_WIDGETS = ['leonardo_counters.models.CounterWidget',
                    'leonardo_counters.models.CountdownWidget']

LEONARDO_JS_FILES = [
    'js/lib/jquery.counter.js',
    'js/lib/jquery.appear.js',
]
LEONARDO_OPTGROUP = "Counters"


class Config(AppConfig):
    name = 'leonardo_counters'
    verbose_name = "Leonardo Counters"
