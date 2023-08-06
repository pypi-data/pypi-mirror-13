from __future__ import absolute_import

from . import Feature


class SphinxFeature(Feature):
    def configure(self):
        self.dispatcher.add_listener('edgy.project.feature.make.on_generate', self.on_make_generate)

    def on_make_generate(self, event):
        makefile = event.makefile

        makefile['SPHINX_OPTS'] = ''
        makefile['SPHINX_BUILD'] = '$(VIRTUALENV_PATH)/bin/sphinx-build'
        makefile['SPHINX_SOURCEDIR'] = 'doc'
        makefile['SPHINX_BUILDDIR'] = '$(SPHINX_SOURCEDIR)/_build'

        makefile.add_target('doc', '''
            $(SPHINX_BUILD) -b html -D latex_paper_size=a4 $(SPHINX_OPTS) $(SPHINX_SOURCEDIR) $(SPHINX_BUILDDIR)/html
        ''', deps=('install', ), phony=True)

__feature__ = SphinxFeature

