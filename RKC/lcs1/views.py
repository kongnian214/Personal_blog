import base64
import re
import uuid
from urllib.parse import urlparse
import os

from django.http import JsonResponse
from rest_framework.decorators import api_view

from RKC import settings
from .models import BloggerArticle,BloggerArticleSerializer
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT,HTTP_404_NOT_FOUND
from .models import BloggerArticle
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


@api_view(['POST'])
def increment_click_count(request, pk):
    try:
        article = BloggerArticle.objects.get(pk=pk)
        article.click_num += 1
        article.save()
        return Response({'click_num': article.click_num}, status=HTTP_200_OK)
    except BloggerArticle.DoesNotExist:
        return Response({'error': 'Article not found'}, status=HTTP_404_NOT_FOUND)

@api_view(['POST'])
def create_article(request):
    if request.method == 'POST':
        serializer = BloggerArticleSerializer(data=request.data)
        if serializer.is_valid():
            # 保存文章
            article = serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
@api_view(['GET'])
def get_articles(request):
    classify = request.GET.get('classify')
    query = request.GET.get('query')

    articles = BloggerArticle.objects.all().order_by('-id')  # 按 id 降序排序

    if classify:
        articles = articles.filter(classify=classify)
    if query:
        articles = articles.filter(title__icontains=query)

    page = request.GET.get('page', 1)
    paginator = Paginator(articles, 5)  # 每页显示5篇文章

    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)

    serializer = BloggerArticleSerializer(articles_page, many=True)
    return Response({
        'results': serializer.data,
        'next': articles_page.next_page_number() if articles_page.has_next() else None,
        'previous': articles_page.previous_page_number() if articles_page.has_previous() else None,
        'count': paginator.count
    })



@api_view(['POST'])
def upload_image(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        # 保存文件到 media/article_image
        file_name = default_storage.save(os.path.join('article_image', file.name), ContentFile(file.read()))
        # 返回相对路径而非完整 URL
        relative_path = os.path.join(settings.MEDIA_URL.lstrip('/'), file_name).replace("\\", "/")
        return JsonResponse({'location': relative_path})
    return JsonResponse({'error': 'Invalid request'}, status=400)






class BloggerArticleDetailView(APIView):
    def get(self, request, pk=None):
        if pk is not None:
            article = get_object_or_404(BloggerArticle, pk=pk)
            serializer = BloggerArticleSerializer(article)
            return Response(serializer.data)
        else:
            query = request.query_params.get('query', '')
            classify = request.query_params.get('classify', '')
            pageNum = int(request.query_params.get('pageNum', 1))  # 转换为整数
            pageSize = int(request.query_params.get('pageSize', 5))  # 转换为整数
            articles = BloggerArticle.objects.all()
            if query:
                articles = articles.filter(title__icontains=query)
            if classify:
                articles = articles.filter(classify=classify)
            paginator = Paginator(articles, pageSize)
            try:
                articlesPage = paginator.page(pageNum)
            except PageNotAnInteger:
                articlesPage = paginator.page(1)
            except EmptyPage:
                articlesPage = paginator.page(paginator.num_pages)
            serializer = BloggerArticleSerializer(articlesPage, many=True)
            return Response({
                'results': serializer.data,
                'next': articlesPage.next_page_number() if articlesPage.has_next() else None,
                'previous': articlesPage.previous_page_number() if articlesPage.has_previous() else None,
                'count': paginator.count
            })
    def put(self, request, pk):
        article = get_object_or_404(BloggerArticle, pk=pk)
        serializer = BloggerArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if pk is not None:
            article = get_object_or_404(BloggerArticle, pk=pk)

            try:
                # 删除 picture 字段对应的图片
                if article.picture:
                    image_path = get_media_path(article.picture)
                    if image_path:
                        print(f"Deleting picture: {image_path}")  # 调试信息
                        if os.path.exists(image_path):
                            os.remove(image_path)
                        else:
                            print(f"File not found: {image_path}")  # 调试信息
                    else:
                        print(f"Invalid picture URL: {article.picture}")  # 调试信息

                # 删除 content 字段中引用的所有图片
                if article.content:
                    img_src_list = re.findall(r'<img[^>]+src="([^">]+)"', article.content)
                    for src in img_src_list:
                        image_path = get_media_path(src)
                        if image_path:
                            print(f"Deleting content image: {image_path}")  # 调试信息
                            if os.path.exists(image_path):
                                os.remove(image_path)
                            else:
                                print(f"File not found: {image_path}")  # 调试信息

                article.delete()
                return Response(status=HTTP_204_NO_CONTENT)
            except Exception as e:
                print(f"Error deleting article: {e}")  # 调试信息
                return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def batch_delete_articles(request):
    ids = request.data.get('ids', [])
    if not ids:
        return Response({'error': '未提供文章 ID'}, status=HTTP_400_BAD_REQUEST)

    try:
        articles = BloggerArticle.objects.filter(id__in=ids)
        for article in articles:
            # 删除 picture 字段对应的图片
            if article.picture:
                image_path = get_media_path(article.picture)
                if image_path:
                    print(f"Deleting picture: {image_path}")  # 调试信息
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    else:
                        print(f"File not found: {image_path}")  # 调试信息

            # 删除 content 字段中引用的所有图片
            if article.content:
                img_src_list = re.findall(r'<img[^>]+src="([^">]+)"', article.content)
                for src in img_src_list:
                    image_path = get_media_path(src)
                    if image_path:
                        print(f"Deleting content image: {image_path}")  # 调试信息
                        if os.path.exists(image_path):
                            os.remove(image_path)
                        else:
                            print(f"File not found: {image_path}")  # 调试信息

        articles.delete()
        return Response(status=HTTP_204_NO_CONTENT)
    except Exception as e:
        return Response({'error': str(e)}, status=HTTP_400_BAD_REQUEST)


def get_media_path(url):
    if not url:
        return None
    # 解析完整的 URL
    parsed_url = urlparse(url)
    # 提取路径部分并去除前导斜杠
    path = parsed_url.path.lstrip('/')
    # 去除 MEDIA_URL 部分
    if settings.MEDIA_URL and path.startswith(settings.MEDIA_URL.lstrip('/')):
        relative_path = path[len(settings.MEDIA_URL.lstrip('/')):]
    else:
        relative_path = path
    # 构建物理路径，并确保使用反斜杠作为分隔符
    full_path = os.path.join(settings.MEDIA_ROOT, relative_path).replace('/', '\\')
    return full_path if os.path.exists(full_path) else None

