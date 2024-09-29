from django.contrib import admin
from consumer.models import User, Consumer

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def delete_model(self, request, obj):
        # Delete the related consumer manually
        Consumer.objects.filter(user=obj).delete()
        # Then delete the user
        super().delete_model(request, obj)
