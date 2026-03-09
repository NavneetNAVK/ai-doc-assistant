from django.contrib import admin
from django.urls import path
from chat import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.chat_view, name='home'),
    path('new/', views.new_chat, name='new_chat'),
    path('chat/<int:session_id>/', views.chat_view, name='chat_session'),
    path('delete/<int:session_id>/', views.delete_chat, name='delete_chat'),
]

# This allows opening PDFs in the browser during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)