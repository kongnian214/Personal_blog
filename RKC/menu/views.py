# views.py
from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import SysMenu,SysMenuSerializer
import logging
# 设置日志记录器
logger = logging.getLogger(__name__)

class SysMenuNameListView(APIView):
    def get(self, request):
        menus = SysMenu.objects.all()
        # 打印获取的数据
        logger.debug(f"Retrieved menus: {menus}")
        serializer = SysMenuSerializer(menus, many=True)
        # 打印序列化后的数据
        logger.debug(f"Serialized data: {serializer.data}")
        return Response(serializer.data)


class MenuListView(APIView):
    def get(self, request):
        menus = SysMenu.objects.all().order_by('order_num')
        serializer = SysMenuSerializer(menus, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
