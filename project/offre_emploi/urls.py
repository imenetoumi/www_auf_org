# -*- encoding: utf-8 -*-
from django.conf import settings
from django.conf.urls.defaults import *


urlpatterns = patterns('offre_emploi.views',
    url(r'^$', 'offre_emploi_liste', name='offre_emploi_liste'),
)