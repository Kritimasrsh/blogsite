from django import forms
from .models import Post, Category, Tag


class PostForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by("name"),
        required=False,
        empty_label="Select a category",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        choices=[("draft", "Draft"), ("published", "Published")],
        initial="draft",
        required=True,
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = Post
        fields = ["title", "slug", "category", "content", "excerpt", "cover_image", "published"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-input", "placeholder": "Enter a compelling post title"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "placeholder": "short-slug"}),
            "content": forms.Textarea(attrs={"class": "form-textarea", "placeholder": "Write your blog content here..."}),
            "excerpt": forms.Textarea(attrs={"class": "form-textarea", "placeholder": "Short summary for previews"}),
            "cover_image": forms.ClearableFileInput(attrs={"class": "form-input"}),
            "published": forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["status"].initial = "published" if self.instance.published else "draft"
        else:
            self.fields["status"].initial = "draft"

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data["published"] = cleaned_data.get("status") == "published"
        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Category name"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "placeholder": "category-slug"}),
        }


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["name", "slug"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-input", "placeholder": "Tag name"}),
            "slug": forms.TextInput(attrs={"class": "form-input", "placeholder": "tag-slug"}),
        }
