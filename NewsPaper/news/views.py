from django.urls import reverse_lazy
from django.views.generic import ListView, \
    DetailView, CreateView, UpdateView, DeleteView, TemplateView
from .models import Post, Category
from .filters import PostFilter
from .forms import PostForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.shortcuts import get_object_or_404
from django.shortcuts import render, reverse, redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import datetime
from NewsPaper.settings import DEFAULT_FROM_EMAIL, SITE_URL
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from django.core.cache import cache


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


@method_decorator(login_required, name='dispatch')
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
        send_email_post.delay(post.pk)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_authors'] = not self.request.user.groups.filter(name='authors').exists()
        return context

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
    context_object_name = 'categories'

    def get_queryset(self):
        self.category = get_object_or_404(Category,id= self.kwargs ['pk'])
        queryset=Post.objects.filter(category=self.category).order_by('-time_in')
        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_not_subscriber"] = self.request.user not in self.category.subscribers.all()
        context['category']=self.category
        return context


# class AppointmentView(View):
#     def get(self, request, *args, **kwargs):
#         return render(request, 'make_appointment.html', {})
#
#     def post(self, request, *args, **kwargs):
#         appointment = Appointment(
#             date=datetime.strptime(request.POST['date'], '%Y-%m-%d'),
#             client_name=request.POST['client_name'],
#             message=request.POST['message'],
#         )
#         appointment.save()
#
#         # получаем наш html
#         html_content = render_to_string(
#             'appointment_created.html',
#             {
#                 'appointment': appointment,
#             }
#         )
#
#         # в конструкторе уже знакомые нам параметры, да? Называются правда немного по-другому, но суть та же.
#         msg = EmailMultiAlternatives(
#             subject=f'{appointment.client_name} {appointment.date.strftime("%Y-%M-%d")}',
#             body=appointment.message,  # это то же, что и message
#             from_email='peterbadson@yandex.ru',
#             to=['skavik46111@gmail.com'],  # это то же, что и recipients_list
#         )
#         msg.attach_alternative(html_content, "text/html")  # добавляем html
#         msg.send()  # отсылаем
#
#         return redirect('appointments:make_appointment')

# class IndexView(View):
#     def get(self, request):
#         printer.delay(10)
#         hello.delay()
#         return HttpResponse('Hello!')

# @shared_task
# def hello():
#     time.sleep(10)
#     print("Hello, world!")
#
# @shared_task
# def printer(N):
#     for i in range(N):
#         time.sleep(1)
#         print(i+1)

# @shared_task
def weekly_sending():
    #  Your job processing logic here...
    today = datetime.datetime.now()
    last_week = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(time_in__gte = last_week)
    categories = set(posts.values_list('category__name_category', flat = True))
    subscribers = set(Category.objects.filter(name_category__in = categories).values_list('subscribers__email', flat = True))

    html_contetnt = render_to_string(
        "weekly_post.html",
        {
            'link': SITE_URL,
            'posts': posts
        }

    )

    msg = EmailMultiAlternatives(
        subject="Статьи за неделю",
        body= "",
        from_email= DEFAULT_FROM_EMAIL,
        to= subscribers,
    )

    msg.attach_alternative(html_contetnt, 'text/html')
    msg.send()


# @shared_task
def send_email_post(pk):
    post = Post.objects.get(pk=pk)
    categories = post.category.all()
    title = post.header
    subscribers_emails = []
    for category in categories:
        subscribers_users = category.subscribers.all()
        for user in subscribers_users:
            subscribers_emails.append(user.email)

    html_content = render_to_string(
        'post_created_email.html',
        {
            'text': post.preview,
            'link': f'{SITE_URL}/news/{pk}',

        }
    )

    msg = EmailMultiAlternatives(
        subject=title,
        body='',
        from_email=DEFAULT_FROM_EMAIL,
        to=subscribers_emails,
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()
    #return HttpResponse("New news sent successfully!")