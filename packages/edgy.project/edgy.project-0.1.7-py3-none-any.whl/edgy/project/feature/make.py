from __future__ import absolute_import

import textwrap

from collections import OrderedDict, deque
from edgy.event import Event

from . import Feature


class Makefile(object):
    def __init__(self):
        self._env_order, self._env_values = deque(), {}
        self._target_order, self._target_values = deque(), {}
        self.phony = set()

    def add_target(self, target, rule, deps=None, phony=False, first=False):
        self._target_values[target] = (
            deps or list(),
            textwrap.dedent(rule).strip(),
        )
        self._target_order.appendleft(target) if first else self._target_order.append(target)

        if phony:
            self.phony.add(target)

    def __str__(self):
        content = []

        if len(self):
            for k, v in self:
                content.append('{} ?= {}'.format(k, v))
            content.append('')

        if len(self.phony):
            content.append('.PHONY: ' + ' '.join(self.phony))
            content.append('')

        for target, details in self.targets:
            deps, rule = details
            content.append('{}: {}'.format(target, ' '.join(deps)).strip())
            for line in rule.split('\n'):
                content.append('	' + line)
            content.append('')

        return '\n'.join(content)

    def __setitem__(self, key, value):
        self._env_values[key] = value
        if not key in self._env_order:
            self._env_order.append(key)

    def setleft(self, key, value):
        self._env_values[key] = value
        if not key in self._env_order:
            self._env_order.appendleft(key)

    def updateleft(self, *lst):
        for key, value in reversed(lst):
            self.setleft(key, value)

    def __getitem__(self, item):
        return self._env_values[item]

    def __delitem__(self, key):
        self._env_order.remove(key)
        del self._env_values[key]

    def __len__(self):
        return len(self._env_order)

    def __iter__(self):
        for key in self._env_order:
            yield key, self._env_values[key]

    @property
    def targets(self):
        for key in self._target_order:
            yield key, self._target_values[key]


class MakefileEvent(Event):
    def __init__(self, package_name, makefile):
        self.package_name = package_name
        self.makefile = makefile
        super(MakefileEvent, self).__init__()


class MakeFeature(Feature):
    def configure(self):
        self.makefile = Makefile()
        self.dispatcher.add_listener('edgy.project.on_start', self.on_start)

    def on_start(self, event):
        for k in event.variables:
            self.makefile[k.upper()] = event.variables[k]

        self.makefile.updateleft(
            ('PYTHON', '$(shell which python)', ),
            ('PYTHON_BASENAME', '$(shell basename $(PYTHON))', ),
        )

        self.makefile['PIP'] = '$(VIRTUALENV_PATH)/bin/pip --cache-dir=$(PIPCACHE_PATH)'

        self.makefile.add_target('install', '''
            $(PIP) wheel -w $(WHEELHOUSE) -f $(WHEELHOUSE) -r requirements.txt
            $(PIP) install -Ue .
            $(PIP) install -f $(WHEELHOUSE) -Ur requirements.txt
        ''', deps=('$(VIRTUALENV_PATH)', ), phony=True)

        self.makefile.add_target('$(VIRTUALENV_PATH)', '''
            virtualenv -p $(PYTHON) $(VIRTUALENV_PATH)
            $(VIRTUALENV_PATH)/bin/pip install -U pip\>=7.0,\<8.0 wheel\>=0.24,\<1.0
            ln -fs $(VIRTUALENV_PATH)/bin/activate $(PYTHON_BASENAME)-activate
        ''')

        self.makefile.add_target('clean', '''
            rm -rf $(VIRTUALENV_PATH) $(WHEELHOUSE) $(PIPCACHE_PATH)
        ''', phony=True)

        self.dispatcher.dispatch(__name__ + '.on_generate', MakefileEvent(event.setup['name'], self.makefile))

        self.render_file_inline('Makefile', self.makefile.__str__(), override=True)


__feature__ = MakeFeature
