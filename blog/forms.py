from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "slug", "category", "tags", "content", "excerpt", "cover_image", "published"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200",
                    "placeholder": "Enter a compelling post title",
                }
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200",
                    "placeholder": "short-slug",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
                }
            ),
            "tags": forms.SelectMultiple(
                attrs={
                    "class": "w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "min-h-[280px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200",
                    "placeholder": "Write your blog content here...",
                }
            ),
            "excerpt": forms.Textarea(
                attrs={
                    "class": "min-h-[96px] w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200",
                    "placeholder": "Short summary for previews",
                }
            ),
            "cover_image": forms.ClearableFileInput(
                attrs={
                    "class": "w-full rounded-2xl border border-dashed border-slate-300 bg-slate-50 px-4 py-3 text-sm text-slate-600"
                }
            ),
            "published": forms.CheckboxInput(attrs={"class": "h-4 w-4 rounded border-slate-300 text-slate-900 focus:ring-slate-400"}),
        }
