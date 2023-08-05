from .urls import urlpatterns

#
#    Create views from functions in the hotfix.py file of every installed apps
#    and add them to the root urls with the `hotfix` prefix. A function called
#    ``update_users`` will have the following url: /hotfix/update_users
#
#
#    These created views will have "superuser_required" when settings.DEBUG
#    is False. Their results are converted into HttpResponse if needed.
#
#
#    Install:
#        Add the following url object to the main urls.py urlpatterns:
#
#        >>  url(r'^hotfix/', include(hotfix)),
#

__author__ = 'snake'
__all__ = 'urlpatterns',
__version__ = '1.0'