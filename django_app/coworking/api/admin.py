from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Reservation

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'full_name', 'is_active', 'is_staff', 'is_superuser', 'created_at')
    ordering = ('email',)
    search_fields = ('email', 'full_name')
    fieldsets = ((None, {'fields': ('email', 'password')}), ('Personal info', {'fields': ('full_name',)}), ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}), ('Important dates', {'fields': ('last_login', 'created_at')}))
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser')}),)
    filter_horizontal = ('groups', 'user_permissions')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'seat_id', 'date', 'name', 'email', 'created_at')
    list_filter = ('date',)
    search_fields = ('id', 'seat_id', 'name', 'email')
