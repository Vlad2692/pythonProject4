from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum

# Create your models here.
article = 'ST'
news = 'NW'

POST = [
    (article, 'Статья'),
    (news, 'Новость')
]


class Author(models.Model):
    users = models.OneToOneField(User, on_delete=models.PROTECT, verbose_name='Имя')
    rating = models.IntegerField(default=0)

    def update_rating(self):
        author_posts_rating = Post.objects.filter(author_id=self).aggregate(Sum('rating'))['rating__sum'] * 3
        author_comment_rating = Comment.objects.filter(user_id=self.users).aggregate(Sum('rating'))['rating__sum']
        author_post_comment_rating = Comment.objects.filter(post__author__users=self.users).aggregate(Sum('rating'))['rating__sum']
        self.rating = author_posts_rating + author_comment_rating + author_post_comment_rating
        self.save()



class Category(models.Model):
    name_category = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name_category.title()

class Post(models.Model):
    objects = None
    author = models.ForeignKey('Author', on_delete=models.PROTECT, verbose_name='Автор')
    type = models.CharField(max_length=2, choices=POST, default=article, verbose_name='Вид поста')
    time_in = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    category = models.ManyToManyField('Category', through='PostCategory')
    header = models.CharField(max_length=255, default='Defaullt title', verbose_name='Заголовок')
    content = models.TextField(default="...", verbose_name='Контент')
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        return f"{self.content[:124]}..." if len(self.content) > 124 else self.content


    def __str__(self):
        return self.header.title()


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.PROTECT, verbose_name='Пост')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')


class Comment(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text_comment = models.TextField(default='Default content', verbose_name='Текст коммента')
    time_in_comment = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    rating = models.IntegerField(default=0)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()




# Create your models here.
