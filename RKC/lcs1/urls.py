# lcs1/urls.py
from django.urls import path
from .views import create_article, get_articles, upload_image, BloggerArticleDetailView, batch_delete_articles, \
    increment_click_count

urlpatterns = [
    path('articles/', create_article, name='create_article'),  # 注意末尾斜杠
    path('blogger_articles/', get_articles, name='get_articles'),  # 注意末尾斜杠
    path('upload_image/', upload_image, name='upload_image'),  # 注意末尾斜杠
    path('blogger_articles/<int:pk>/', BloggerArticleDetailView.as_view(), name='blogger_article_detail'),
    path('blogger_articles/batch_delete/', batch_delete_articles, name='batch_delete_articles'),  # 添加批量删除路径
    path('articles/<int:pk>/click/', increment_click_count, name='increment_click_count'),


]

