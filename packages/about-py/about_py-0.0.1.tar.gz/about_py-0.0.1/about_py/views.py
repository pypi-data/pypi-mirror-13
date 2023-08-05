import logging
import sys

import collections
from django.views.generic import TemplateView

from about_py.core.vcs import get_vcs_info
from utils.exceptions import AboutPyException

LOG = logging.getLogger(__name__)


class AboutView(TemplateView):
    template_name = 'about_py/about.html'

    def get_context_data(self, **kwargs):
        context_data = super(AboutView, self).get_context_data(**kwargs)
        context_data['vcs'] = self.get_vcs()
        context_data['python'] = self.python_info()
        context_data['libs'] = self.get_libs()
        return context_data

    def get_vcs(self):
        try:
            return get_vcs_info()
        except AboutPyException as e:
            LOG.warn('no vcs detected. cause: {}'.format(e.message))
            return {}

    def python_info(self):
        return {'version': '{0}.{1}.{2}'.format(sys.version_info.major,
                                                sys.version_info.minor,
                                                sys.version_info.micro)}

    def get_libs(self):
        import pip
        installed_packages = pip.get_installed_distributions()
        libs = {i.project_name: i.version for i in installed_packages}
        return collections.OrderedDict(sorted(libs.items(), key=lambda s: s[0].lower()))
