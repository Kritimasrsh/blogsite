from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render


class CommentForm(forms.Form):
    body = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-textarea", "rows": 4, "placeholder": "Write a comment..."}),
        required=True,
    )
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from .forms import PostForm, CategoryForm, TagForm
from .models import Post, Category, Tag, Comment

class PostListView(ListView):
    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 6

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return dashboard(request)
        return super().dispatch(request, *args, **kwargs)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context["comments"] = post.comments.select_related("author").all()
        context["related_posts"] = (
            Post.objects.filter(published=True, category=post.category)
            .exclude(pk=post.pk)
            .order_by("-created_at")[:3]
        )
        context["comment_form"] = CommentForm()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to leave a comment.")
            return redirect(self.object.get_absolute_url())

        form = CommentForm(request.POST)
        if form.is_valid():
            Comment.objects.create(post=self.object, author=request.user, body=form.cleaned_data["body"])
            messages.success(request, "Your comment has been added.")
        else:
            messages.error(request, "Comment could not be added.")
        return redirect(self.object.get_absolute_url())

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


class SecureUserCreationForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-input", "placeholder": "Choose a username"}),
        required=True,
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Create a strong password"}),
        required=True,
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input", "placeholder": "Confirm your password"}),
        required=True,
    )

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if password:
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long and include a number and a special character.")
            if not any(char.isdigit() for char in password):
                raise ValidationError("Password must be at least 8 characters long and include a number and a special character.")
            if not any(not char.isalnum() for char in password):
                raise ValidationError("Password must be at least 8 characters long and include a number and a special character.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords must match.")
        return cleaned_data


def signup_view(request):
    if request.method == "POST":
        form = SecureUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("blog:post_list")
    else:
        form = SecureUserCreationForm()

    return render(request, "blog/signup.html", {"form": form})


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
        form.instance.published = form.cleaned_data.get("status") == "published"
        messages.success(self.request, "Post created successfully.")
        return super().form_valid(form)


@method_decorator([staff_member_required, login_required], name="dispatch")
class PostUpdateView(UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/post_form.html"
    success_url = reverse_lazy("blog:dashboard")

    def form_valid(self, form):
        form.instance.published = form.cleaned_data.get("status") == "published"
        messages.success(self.request, "Post updated successfully.")
        return super().form_valid(form)


@staff_member_required
@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.delete()
    messages.success(request, "Post deleted successfully.")
    return redirect("blog:dashboard")


@staff_member_required
@login_required
def category_list(request):
    categories = Category.objects.all().order_by("name")
    return render(request, "blog/category_list.html", {"categories": categories})


@staff_member_required
@login_required
def category_create(request):
    if request.method == "POST":
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created successfully.")
            return redirect("blog:category_list")
    else:
        form = CategoryForm()
    return render(request, "blog/category_form.html", {"form": form, "title": "Create category"})


@staff_member_required
@login_required
def tag_list(request):
    tags = Tag.objects.all().order_by("name")
    return render(request, "blog/tag_list.html", {"tags": tags})


@staff_member_required
@login_required
def tag_create(request):
    if request.method == "POST":
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag created successfully.")
            return redirect("blog:tag_list")
    else:
        form = TagForm()
    return render(request, "blog/tag_form.html", {"form": form, "title": "Create tag"})