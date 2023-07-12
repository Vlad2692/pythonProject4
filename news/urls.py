from django.urls import path
# Импортируем созданное нами представление
from .views import PostList, PostDetail, PostSearchList, PostCreate, PostUpdate, PostDelete


urlpatterns = [
   path('', PostList.as_view()),
   path('<int:pk>', PostDetail.as_view()),
   path('search/', PostSearchList.as_view(), name='post_search'),
   path('create/', PostCreate.as_view(), name='post_create'),
   path('<int:pk>/edit/', PostUpdate.as_view(), name='post_update'),
   path('<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
   # path('upgrade/', upgrade_me, name='upgrade_status')

]