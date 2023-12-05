from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from blog.models import Post, Category
from django.utils import timezone
from django.views.generic import (
    ListView, CreateView, UpdateView,
    DeleteView, DetailView, View)
from .models import Comments, Post
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .forms import UserUpdateForm, PostCreateForm, CommentsForm
from django.urls import reverse
from django.db.models import Count
from django.core.paginator import Paginator

last = 5
PAGINATE_NUMBER = 10


def filter_queryset(queryset):
    return queryset.filter(pub_date__lte=timezone.now(),
                           is_published=True,
                           category__is_published=True)


class IndexListView(ListView):
    model = Post
    queryset = filter_queryset(
        Post.objects.annotate(comment_count=Count('comment')))
    paginate_by = PAGINATE_NUMBER
    template_name = 'blog/index.html'
    ordering = '-pub_date'



class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    paginate_by = PAGINATE_NUMBER

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category.objects.filter(
            is_published=True),slug=self.kwargs['category_slug'])
        context["category"] = category
        posts = category.posts.filter(
            pub_date__lte=timezone.now(),is_published=True).annotate(
            comment_count=Count('comment')).order_by('-pub_date')
        paginator = Paginator(posts, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context["page_obj"] = page_obj
        return context


class ProfileListView(ListView):
    model = Post
    paginate_by = PAGINATE_NUMBER
    template_name = 'blog/profile.html'
    
    def get_queryset(self):
        try:
            user = User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            raise Http404("Пользователь не найден")
        return Post.objects.filter(author=user).annotate(
            comment_count=Count('comment')).order_by('-pub_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = User.objects.filter(username=self.kwargs['username']).first()
        context['profile'] = user
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        return self.request.user


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['post_id'])
        if not post.is_published and post.author != request.user:
            raise Http404
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentsForm()
        comments = self.object.comment.select_related('author')
        context['comments'] = comments
        context['comment_count'] = comments.count()
        return context


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        post_id = self.object.id
        return reverse('blog:post_detail', kwargs={'post_id': post_id})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if instance.author != request.user:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        instance = self.get_object()
        context['form'] = PostCreateForm(instance=instance)
        return context

    def get_success_url(self):
        return reverse('blog:profile',
                       kwargs={'username': self.request.user.username})


class CommentsCreateView(LoginRequiredMixin, CreateView):
    model = Comments
    form_class = CommentsForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'post_id'
    post_obj = None

    def dispatch(self, request, *args, **kwargs):
        self.post_obj = get_object_or_404(
            filter_queryset(Post.objects.all()), pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_obj
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentMixin(LoginRequiredMixin, View):
    model = Comments
    form_class = CommentsForm
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(
            Comments,
            id=kwargs['comment_id'],
        )
        if comment.author != request.user:
            return redirect('blog:post_detail', pk=kwargs['post_id'])
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("blog:post_detail",
                       kwargs={'post_id': self.kwargs['post_id']})


class CommentUpdateView(CommentMixin, UpdateView):
    ...


class CommentDeleteView(CommentMixin, DeleteView):
    ...
