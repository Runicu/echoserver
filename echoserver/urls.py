from django.urls import include, path

urlpatterns = [
    path('', include('bookstore_app.urls')),
]
