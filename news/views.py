from django.urls import reverse_lazy
from django.views.generic import ListView, \
    DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Post, Category
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# from django.http import HttpResponse
# from .tasks import hello, send_email_post, printer
# from django.core.cache import cache

class MyView(PermissionRequiredMixin, View):
    permission_required = ('<news>.<add>_<post>',
                           '<news>.<change>_<post>')


class PostList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-time_in'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'news.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    paginate_by = 10


class PostDetail(DetailView):
    # Модель всё та же, но мы хотим получать информацию по отдельному товару
    model = Post
    # Используем другой шаблон — product.html
    template_name = 'new.html'
    # Название объекта, в котором будет выбранный пользователем продукт
    context_object_name = 'post'

class PostSearchList(ListView):
    # Указываем модель, объекты которой мы будем выводить
    model = Post
    # Поле, которое будет использоваться для сортировки объектов
    ordering = '-time_in'
    # Указываем имя шаблона, в котором будут все инструкции о том,
    # как именно пользователю должны быть показаны наши объекты
    template_name = 'search.html'
    # Это имя списка, в котором будут лежать все объекты.
    # Его надо указать, чтобы обратиться к списку объектов в html-шаблоне.
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post', )
    # Указываем нашу разработанную форму
    form_class = PostForm
    # form_valid = PostForm
    # модель товаров
    model = Post
    # и новый шаблон, в котором используется форма.
    template_name = 'post_edit.html'

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if 'news' in self.request.path:
            type_ = 'NW'
        elif 'article' in self.request.path:
            type_ = 'ST'
        self.object.type = type_
        # post = form.save(commit=False)
        # post.type = 13
        return super().form_valid(form)


class PostUpdate(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):
    permission_required = ('news.change_post', )
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'


class PostDelete(DeleteView):
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')


@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    message = "Вы в рассылке категории"
    return render(request, 'subscribe.html', {'category': category, 'message': message})


class PostCategory(PostList):
    model = Post
    template_name = 'category.html'
    context_object_name = 'category'

    def get_queryset(self):
        self.category = get_object_or_404(Category,id= self.kwargs ['pk'])
        queryset=Post.objects.filter(category=self.category).order_by('-time_in')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_not_subscriber"] = self.request.user not in self.category.subscribers.all()
        context['category']=self.category
        return context