from django.urls import path
from .views import (
    user_signup,
    user_signin,
    user_logout,
    dashboard,
    ApplicationListView,
    ApplicationDetailView,
    submit_application,
    update_application,
    paynow_webhook
)

urlpatterns = [
    path("signup", user_signup, name="signup"),
    path("signin", user_signin, name="signin"),
    path("logout", user_logout, name="logout"),
    path("", dashboard, name="dashboard"),
    path("applications", ApplicationListView.as_view(), name="application_list"),
    path("applications/submit", submit_application, name="submit_application"),
    path("applications/<pk>", ApplicationDetailView.as_view(),
         name="application_detail"),
    path("applications/<pk>/edit", update_application, name="update_application"),
    path("webhook/<int:pk>", paynow_webhook, name="paynow_webhook")
]
