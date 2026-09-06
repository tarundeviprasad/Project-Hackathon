import hashlib

from django.core.cache import cache

from api.audit import record_audit_event


MAX_LOGIN_FAILURES = 5
LOGIN_FAILURE_TIMEOUT = 900


def login_failure_key(request, identifier):
    raw_key = f'{request.META.get("REMOTE_ADDR", "unknown")}:{identifier.lower()}'
    digest = hashlib.sha256(raw_key.encode()).hexdigest()
    return f'web-login-failures:{digest}'


def login_is_rate_limited(request, identifier):
    return cache.get(login_failure_key(request, identifier), 0) >= MAX_LOGIN_FAILURES


def record_login_failure(request, identifier, reason=None):
    key = login_failure_key(request, identifier)
    failures = cache.get(key, 0) + 1
    cache.set(key, failures, timeout=LOGIN_FAILURE_TIMEOUT)
    metadata = {'reason': reason} if reason else None
    record_audit_event(request, 'LOGIN_FAILURE', success=False, metadata=metadata)


def clear_login_failures(request, identifier):
    cache.delete(login_failure_key(request, identifier))