from django.contrib import admin

from .models import (
    Universe_Default, Universe_Folder, Universe_Tree, Universe_Universe,
    Lists_Default, Lists_Folder, Lists_Tree, Lists_Universe
)
# Register your models here.
admin.site.register(Universe_Default)
admin.site.register(Universe_Folder)
admin.site.register(Universe_Tree)
admin.site.register(Universe_Universe)
admin.site.register(Lists_Default)
admin.site.register(Lists_Folder)
admin.site.register(Lists_Tree)
admin.site.register(Lists_Universe)