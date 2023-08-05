from .utils import HotfixRegister

__author__ = 'snake'


hotfix_registry = HotfixRegister()
hotfix_registry.autodiscover()

urlpatterns = hotfix_registry.urlpatterns