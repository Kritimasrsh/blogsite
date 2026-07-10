from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .forms import PostForm
from .models import Post, Category, Tag

class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        qs = Post.objects.filter(published=True)
        query = self.request.GET.get("q")
        if query:
            qs = qs.filter(Q(title__icontains=query) | Q(content__icontains=query))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        context["categories"] = Category.objects.all()
        return context

class PostDetailView(DetailView):
    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_field = "slug"

class CategoryPostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs["slug"])
        return Post.objects.filter(published=True, category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["current_category"] = self.category
        return context

class TagPostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["slug"])
        return Post.objects.filter(published=True, tags=self.tag)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        context["current_tag"] = self.tag
        return context


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_staff or user.is_superuser:
                messages.success(request, "Welcome back, admin.")
                return redirect("blog:dashboard")
            messages.success(request, "Welcome back.")
            return redirect("blog:post_list")
        messages.error(request, "Invalid username or password.")

    return render(request, "blog/login.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("blog:post_list")


@staff_member_required
@login_required
def dashboard(request):
    query = request.GET.get("q", "").strip()
    posts = Post.objects.select_related("author", "category").prefetch_related("tags")
    if query:
        posts = posts.filter(Q(title__icontains=query) | Q(content__icontains=query) | Q(author__username__icontains=query))

    context = {
        "posts": posts.order_by("-created_at"),
        "query": query,
        "draft_count": Post.objects.filter(published=False).count(),
        "published_count": Post.objects.filter(published=True).count(),
    }
    return render(request, "blog/dashboard.html", context)


@staff_member_required
@login_required
def toggle_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.published = not post.published
    post.save(update_fields=["published", "updated_at"])
    messages.success(request, f"Post '{post.title}' is now {'published' if post.published else 'draft'}.")
    return redirect("blog:dashboard")


@method_decorator([staff_member_required, login_required], name="dispatch")
class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:dashboard")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, "Post created successfully.")
        return super().form_valid(form)


@method_decorator([staff_member_required, login_required], name="dispatch")
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:dashboard")

    def form_valid(self, form):
        messages.success(self.request, "Post updated successfully.")
        return super().form_valid(form)


@staff_member_required
@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect("blog:dashboard")