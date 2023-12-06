from blog.models import Post
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Comments, Post
from .forms import CommentsForm
from django.urls import reverse


class PostMixin(LoginRequiredMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)


class CommentMixin(LoginRequiredMixin):
    model = Comments
    form_class = CommentsForm
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comments, id=kwargs['comment_id'])
        if comment.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={'post_id': self.kwargs['post_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = get_object_or_404(
            Comments, id=self.kwargs['comment_id'])
        return context
