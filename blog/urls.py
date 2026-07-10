from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.PostListView.as_view(), name="post_list"),
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/new/", views.PostCreateView.as_view(), name="post_create"),
    path("dashboard/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_edit"),
    path("dashboard/<int:pk>/delete/", views.delete_post, name="post_delete"),
    path("dashboard/<int:pk>/toggle-publish/", views.toggle_publish, name="toggle_publish"),
    path("categories/", views.category_list, name="category_list"),
    path("categories/new/", views.category_create, name="category_create"),
    path("tags/", views.tag_list, name="tag_list"),
    path("tags/new/", views.tag_create, name="tag_create"),
    path("category/<slug:slug>/", views.CategoryPostListView.as_view(), name="category_posts"),
    path("tag/<slug:slug>/", views.TagPostListView.as_view(), name="tag_posts"),
    path("<slug:slug>/", views.PostDetailView.as_view(), name="post_detail"),
]