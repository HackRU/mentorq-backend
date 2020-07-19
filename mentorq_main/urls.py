from django.contrib import admin
from django.urls import path, include
from lcs_client import set_testing

from mentorq_main.settings import DEV

urlpatterns = [
    path('api/', include('mentorq_api.urls')),
    path('admin/', admin.site.urls),
]
if DEV:
    set_testing(True)
    print("Set testing mode successfully")
