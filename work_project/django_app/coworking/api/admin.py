from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Count, Q
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from .models import User, Reservation
from datetime import datetime, timedelta

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'full_name', 'is_active', 'is_staff', 'is_superuser', 'reservation_count', 'created_at', 'last_login')
    ordering = ('email',)
    search_fields = ('email', 'full_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created_at')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')})
    )
    add_fieldsets = ((None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'is_staff', 'is_superuser')}),)
    filter_horizontal = ('groups', 'user_permissions')
    actions = ['make_staff', 'deactivate_users', 'activate_users']

    def reservation_count(self, obj):
        count = Reservation.objects.filter(email=obj.email).count()
        return format_html('<span style="color: {};">{}</span>', 'green' if count > 0 else 'gray', count)
    reservation_count.short_description = 'Reservations'

    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} users promoted to staff.')
    make_staff.short_description = "Make selected users staff"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.')
    deactivate_users.short_description = "Deactivate selected users"

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.')
    activate_users.short_description = "Activate selected users"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.user_analytics), name='user_analytics'),
        ]
        return custom_urls + urls

    def user_analytics(self, request):
        # Analytics data
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        # Recent activity
        last_7_days = datetime.now() - timedelta(days=7)
        new_users = User.objects.filter(created_at__gte=last_7_days).count()
        
        # Most active users
        active_users_data = Reservation.objects.values('email')\
            .annotate(count=Count('email'))\
            .order_by('-count')[:10]
        
        context = {
            'title': 'User Analytics',
            'total_users': total_users,
            'active_users': active_users,
            'staff_users': staff_users,
            'new_users': new_users,
            'active_users_data': active_users_data,
        }
        
        return render(request, 'admin/user_analytics.html', context)

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'seat_id', 'date', 'name', 'email', 'created_at', 'status_badge')
    list_filter = ('date', 'created_at', 'seat_id')
    search_fields = ('id', 'seat_id', 'name', 'email')
    ordering = ('-created_at',)
    actions = ['cancel_reservations', 'export_reservations']

    def status_badge(self, obj):
        today = datetime.now().strftime('%Y-%m-%d')
        if obj.date < today:
            return format_html('<span style="color: gray; font-weight: bold;">PAST</span>')
        elif obj.date == today:
            return format_html('<span style="color: orange; font-weight: bold;">TODAY</span>')
        else:
            return format_html('<span style="color: green; font-weight: bold;">FUTURE</span>')
    status_badge.short_description = 'Status'

    def cancel_reservations(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f'{count} reservations cancelled.')
    cancel_reservations.short_description = "Cancel selected reservations"

    def export_reservations(self, request, queryset):
        # This would typically redirect to a view that generates CSV
        self.message_user(request, f'Export functionality for {queryset.count()} reservations.')
    export_reservations.short_description = "Export selected reservations"
    list_filter = ('date',)
    search_fields = ('id', 'seat_id', 'name', 'email')
