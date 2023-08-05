from django.contrib import admin


class NotDeletableAdmin(admin.ModelAdmin):

    def get_actions(self, request):
        actions = super(NotDeletableAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def has_delete_permission(self, request, obj=None):
        return False
