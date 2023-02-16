import os

from django.contrib import admin
from django.urls import path, include
from lcs_client import set_testing

urlpatterns = [
    path('api/', include('mentorq_api.urls')),
    path('admin/', admin.site.urls),
]

# if the environment var LCS_DEV is set, it will use the dev lcs endpoint
# doesn't matter what the actual value is, it just has to be set
#if os.getenv("LCS_DEV"):
#    set_testing(True)
#    print("Set testing mode successfully")
