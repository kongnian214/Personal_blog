
from django.db import models
from rest_framework import serializers

# 抽象基类，包含共性的字段
class CommonFields(models.Model):
    addtime = models.DateTimeField(auto_now_add=True)  # 创建时间，默认为当前时间
    content = models.TextField(null=True, blank=True)  # 内容，允许为空
    video = models.CharField(max_length=255, null=True, blank=True)  # 视频路径，允许为空
    title = models.CharField(max_length=255, null=False, blank=False)  # 标题，不允许为空
    picture = models.CharField(max_length=255, null=True, blank=True)  # 图片路径，允许为空
    introduction = models.CharField(max_length=255, null=True, blank=True)  # 简介/描述，允许为空
    section_name = models.CharField(max_length=255, null=True, blank=True)  # 板块名称，允许为空
    click_num = models.IntegerField(default=0)  # 点击次数，默认为0
    class Meta:
        abstract = True  # 设置为抽象基类
# 具体文章表
class BloggerArticle(CommonFields):
    classify = models.CharField(max_length=255, null=True, blank=True)  # 文章分类，允许为空
    class Meta:
        db_table = "blogger_article"
#序列化
class BloggerArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloggerArticle
        fields = '__all__'



