from pathlib import Path

from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path

ROOT_HTML_DIR = Path(__file__).resolve().parent.parent.parent


def serve_html(request, filename):
    file_path = ROOT_HTML_DIR / filename
    if file_path.exists() and file_path.suffix.lower() == '.html':
        return FileResponse(file_path.open('rb'))
    raise Http404(f'{filename} not found')


urlpatterns = [
    path('', include('auth.urls')),
    path('index.html', lambda request: serve_html(request, 'index.html')),
    path('patient-login.html', lambda request: serve_html(request, 'patient-login.html')),
    path('doctor-login.html', lambda request: serve_html(request, 'doctor-login.html')),
    path('admin-login.html', lambda request: serve_html(request, 'admin-login.html')),
    path('patient_portal.html', lambda request: serve_html(request, 'patient_portal.html')),
    path('doctor-dashboard.html', lambda request: serve_html(request, 'doctor-dashboard.html')),
    path('admin-login.html', lambda request: serve_html(request, 'admin-login.html')),
    path('registrationofpatient.html', lambda request: serve_html(request, 'registrationofpatient.html')),
    path('loginpage.html', lambda request: serve_html(request, 'loginpage.html')),
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
]