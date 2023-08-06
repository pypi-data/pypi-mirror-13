# django imports
from django.contrib import admin

from .models import CompropagoTransaction
from .models import CompropagoWebHookHit

admin.site.register(CompropagoTransaction)
admin.site.register(CompropagoWebHookHit)
