from .models import AuditLog


def get_client_ip(request):
    return request.META.get('REMOTE_ADDR')


def record_audit_event(
    request,
    action,
    *,
    user=None,
    target=None,
    success=True,
    metadata=None,
):
    target_type = ''
    target_id = ''
    if target is not None:
        target_type = target.__class__.__name__
        target_id = str(getattr(target, 'pk', ''))

    return AuditLog.objects.create(
        user=user or (request.user if request.user.is_authenticated else None),
        action=action,
        target_type=target_type,
        target_id=target_id,
        success=success,
        ip_address=get_client_ip(request),
        metadata=metadata or {},
    )