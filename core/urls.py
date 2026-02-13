from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('donate/', TemplateView.as_view(template_name="core/donate.html"), name='donate'),
    path('payments/', include('payments.urls')),  
]
