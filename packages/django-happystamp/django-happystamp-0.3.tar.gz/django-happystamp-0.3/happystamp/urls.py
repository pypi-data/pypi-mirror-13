from django.conf.urls import patterns, include, url

from rest_framework import routers
from happystamp.views import reset_password
from happystamp.views import MerchantAPI
from happystamp.views import ProgramAPI
from happystamp.views import CustomerAPI
from happystamp.views import CardAPI
from happystamp.views import TransactionAPI
from happystamp.views import UserPreferencesAPI
from happystamp.views import ProgramStepAPI
from happystamp.views import GCMAPI

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'merchants', MerchantAPI)
router.register(r'programs', ProgramAPI)
router.register(r'steps', ProgramStepAPI)
router.register(r'customers', CustomerAPI)
router.register(r'cards', CardAPI)
router.register(r'transactions', TransactionAPI)
router.register(r'user_preferences', UserPreferencesAPI)
router.register(r'devices', GCMAPI)


urlpatterns = patterns('',
                       #auth                                                                       
                       url(r'^api/accounts/reset_password', reset_password),                       
                       url(r'^api/accounts/auth-token', 'rest_framework.authtoken.views.obtain_auth_token',),                                
                       #api
                       url(r'^api/', include(router.urls)),                       
                       )

