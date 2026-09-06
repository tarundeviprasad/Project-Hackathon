from django.contrib import admin
from .models import AuditLog, Consultation, DoctorProfile, FollowUp, Referral


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
	list_display = ('action', 'user', 'target_type', 'target_id', 'success', 'timestamp')
	list_filter = ('action', 'success', 'timestamp')
	readonly_fields = ('user', 'action', 'target_type', 'target_id', 'timestamp', 'success', 'ip_address', 'metadata')

	def has_add_permission(self, request):
		return False

	def has_change_permission(self, request, obj=None):
		return False


admin.site.register(DoctorProfile)
admin.site.register(Consultation)
admin.site.register(Referral)
admin.site.register(FollowUp)
