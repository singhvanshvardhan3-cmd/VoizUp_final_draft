from django.urls import path
from . import views
app_name = "complaints"
urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
   # path("home/",views.home,name="home"),
    # path("", views.dashboard, name="dashboard"),
      path("portal", views.portal_view, name="portal"),
    path("staff/", views.staff_list_view, name="staff_list"),
    path("staff/<int:pk>/", views.staff_detail_view, name="staff_detail"),
    path("staff/<int:pk>/update/", views.staff_update_view, name="staff_update"),
]