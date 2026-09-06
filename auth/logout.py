from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from api.audit import record_audit_event


@require_POST
@login_required
def user_logout(request):
    record_audit_event(request, 'LOGOUT', user=request.user)
    logout(request)
    return JsonResponse({"success": True})