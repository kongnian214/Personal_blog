import random
import base64
import json
import uuid

import hashlib
from io import BytesIO
from captcha.image import ImageCaptcha  # 导入 ImageCaptcha 类
from django.http import JsonResponse
from datetime import datetime
from django.views import View
from rest_framework_jwt.settings import api_settings
import json
from RKC import settings
from user.models import SysUser, SysUserSerializer
from django.core.cache import cache  # 导入缓存模块

import os




class LoginView(View):

    def post(self, request):
        username = request.POST.get("username")
        password = request.POST.get("password")
        code = request.POST.get("code")
        uuid = request.POST.get("uuid")

        print("Received login request with data:", request.POST)  # 添加日志

        if not code or not uuid:
            return JsonResponse({'code': 500, 'info': '验证码或UUID缺失！'})

        captcha = cache.get(uuid, "")
        print("captcha1111:", captcha)  # 添加日志

        if not captcha or captcha.lower() != code.lower():
            return JsonResponse({"code": 500, "info": "验证码错误"})

        cache.delete(uuid)  # 删除已使用的验证码

        try:
            user = SysUser.objects.get(username=username, password=hashlib.md5(password.encode()).hexdigest())
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)
        except Exception as e:
            print(e)
            return JsonResponse({'code': 500, 'info': '用户名或者密码错误！'})
        return JsonResponse({'code': 200, 'token': token, 'user': SysUserSerializer(user).data, 'info': '登录成功'})



# Create your views here.
class TestView(View):

    def get(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token != None and token != '':
            userList_obj = SysUser.objects.all()
            print(userList_obj, type(userList_obj))
            userList_dict = userList_obj.values()  # 转存字典
            print(userList_dict, type(userList_dict))
            userList = list(userList_dict)  # 把外层的容器转存List
            print(userList, type(userList))
            return JsonResponse({'code': 200, 'info': '测试！', 'data': userList})
        else:
            return JsonResponse({'code': 401, 'info': '没有访问权限！'})


class JwtTestView(View):

    def get(self, request):
        user = SysUser.objects.get(username='python222', password='123456')
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # 将用户对象传递进去，获取到该对象的属性值
        payload = jwt_payload_handler(user)
        # 将属性值编码成jwt格式的字符串
        token = jwt_encode_handler(payload)
        return JsonResponse({'code': 200, 'token': token})



class PwdView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        oldPassword = data['oldPassword']
        newPassword = data['newPassword']
        obj_user = SysUser.objects.get(id=id)
        if obj_user.password == hashlib.md5(oldPassword.encode()).hexdigest():
            obj_user.password = hashlib.md5(newPassword.encode()).hexdigest()
            obj_user.update_time = datetime.now().date()
            obj_user.save()
            return JsonResponse({'code': 200})
        else:
            return JsonResponse({'code': 500, 'errorInfo': '原密码错误！'})
class ImageView(View):

    def post(self, request):
        file = request.FILES.get('avatar')
        print("Received file:", file)

        if file:
            # 获取文件名（去掉路径）
            file_name = os.path.basename(file.name)
            print("File name:", file_name)

            # 获取文件后缀
            suffixName = os.path.splitext(file_name)[1]
            print("File suffix:", suffixName)

            # 生成新的文件名（时间戳 + 后缀）
            new_file_name = datetime.now().strftime('%Y%m%d%H%M%S') + suffixName
            print("New file name:", new_file_name)

            # 定义 userAvatar 目录
            user_avatar_dir = os.path.join(settings.MEDIA_ROOT, 'userAvatar')
            print("User avatar directory:", user_avatar_dir)

            # 确保目录存在
            if not os.path.exists(user_avatar_dir):
                os.makedirs(user_avatar_dir)
                print("Created directory:", user_avatar_dir)

            # 定义文件保存路径
            file_path = os.path.join(user_avatar_dir, new_file_name)
            print("File path:", file_path)

            try:
                # 保存文件
                with open(file_path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                print("File successfully saved to:", file_path)

                # 返回成功响应
                return JsonResponse({'code': 200, 'title': new_file_name})
            except Exception as e:
                print("Error saving file:", e)
                return JsonResponse({'code': 500, 'errorInfo': '上传头像失败'})
        else:
            print("No file received")
            return JsonResponse({'code': 400, 'errorInfo': '未收到文件'})



class AvatarView(View):

    def post(self, request):
        try:
            data = json.loads(request.body.decode("utf-8"))
            id = data.get('id')
            avatar = data.get('avatar')

            if not id or not avatar:
                return JsonResponse({'code': 400, 'errorInfo': '缺少必要的参数：id 或 avatar'})

            obj_user = SysUser.objects.get(id=id)
            obj_user.avatar = avatar
            obj_user.save()
            return JsonResponse({'code': 200})
        except SysUser.DoesNotExist:
            return JsonResponse({'code': 404, 'errorInfo': '用户不存在'})
        except Exception as e:
            print(e)
            return JsonResponse({'code': 500, 'errorInfo': '服务器内部错误'})
# 用户信息查询

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class SearchView(View):
    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        pageNum = data.get('pageNum', 1)  # 默认页码为1
        pageSize = data.get('pageSize', 10)  # 默认每页大小为10
        query = data.get('query', '')  # 查询参数
        # 使用 Django ORM 进行分页查询
        userList = SysUser.objects.filter(username__icontains=query)
        paginator = Paginator(userList, pageSize)

        try:
            userListPage = paginator.page(pageNum)
        except PageNotAnInteger:
            # 如果页码不是整数，返回第一页
            userListPage = paginator.page(1)
        except EmptyPage:
            # 如果页码超出范围，返回最后一页
            userListPage = paginator.page(paginator.num_pages)
        obj_users = userListPage.object_list.values()  # 转成字典
        users = list(obj_users)  # 把外层的容器转成 List
        total = paginator.count
        return JsonResponse({'code': 200, 'userList': users, 'total': total})


class SaveView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        print(data)
        if data['id'] == -1:  # 添加
            obj_sysUser = SysUser(username=data['username'], password=data['password'],
                                  email=data['email'], phonenumber=data['phonenumber'],
                                  status=data['status'],
                                  remark=data['remark'])
            obj_sysUser.create_time = datetime.now().date()
            obj_sysUser.avatar = 'default.jpg'
            obj_sysUser.password = hashlib.md5("123456".encode()).hexdigest()
            obj_sysUser.save()
        else:  # 修改
            obj_sysUser = SysUser(id=data['id'], username=data['username'], password=data['password'],
                                  avatar=data['avatar'], email=data['email'], phonenumber=data['phonenumber'],
                                  login_date=data['login_date'], status=data['status'],
                                  create_time=data['create_time'],
                                  update_time=data['update_time'], remark=data['remark'])
            obj_sysUser.update_time = datetime.now().date()
            obj_sysUser.save()
        return JsonResponse({'code': 200})

class CheckView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        username = data['username']
        print("username=", username)
        if SysUser.objects.filter(username=username).exists():
            return JsonResponse({'code': 500})
        else:
            return JsonResponse({'code': 200})

class ActionView(View):

    def get(self, request):
        """
        根据id获取用户信息
        :param request:
        :return:
        """
        id = request.GET.get("id")
        user_object = SysUser.objects.get(id=id)
        return JsonResponse({'code': 200, 'user': SysUserSerializer(user_object).data})

    def delete(self, request):
        """
        删除操作
        :param request:
        :return:
        """
        idList = json.loads(request.body.decode("utf-8"))
        SysUser.objects.filter(id__in=idList).delete()
        return JsonResponse({'code': 200})
# 重置密码
class PasswordView(View):

    def get(self, request):
        id = request.GET.get("id")
        user_object = SysUser.objects.get(id=id)
        user_object.password = hashlib.md5("123456".encode()).hexdigest()
        user_object.update_time = datetime.now().date()
        user_object.save()
        return JsonResponse({'code': 200})


# 用户状态修改
class StatusView(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        id = data['id']
        status = data['status']
        user_object = SysUser.objects.get(id=id)
        user_object.status = status
        user_object.save()
        return JsonResponse({'code': 200})


# 用户角色授权

class GrantRole(View):

    def post(self, request):
        data = json.loads(request.body.decode("utf-8"))
        user_id = data['id']
        roleIdList = data['roleIds']
        print(user_id, roleIdList)

        try:
            user = SysUser.objects.get(id=user_id)
            user.role_ids = roleIdList
            user.save()
            return JsonResponse({'code': 200})
        except SysUser.DoesNotExist:
            return JsonResponse({'code': 404, 'message': 'User not found'})


class CaptchaView(View):
    def get(self, request):
        characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        data = "".join(random.sample(characters, 4))
        print("data:", data)
        captcha = ImageCaptcha()
        imageData: BytesIO = captcha.generate(data)
        base64_str = base64.b64encode(imageData.getvalue()).decode()
        random_uuid = uuid.uuid4()  # 生成一个随机数
        print(random_uuid)
        cache.set(random_uuid, data, timeout=300)  # 存到Redis缓存中，有效期5分钟

        return JsonResponse({"code": 200, "base64str": 'data:image/png;base64,' + base64_str, 'uuid': random_uuid})

    def post(self, request):
        code = request.GET.get("code")  # 用户填写的验证码
        uuid = request.GET.get("uuid")  # 验证码的唯一标识
        captcha = cache.get(uuid, "")  # 从缓存中获取生成的验证码
        print("captcha1111:", captcha)
        if not captcha or captcha.lower() != code.lower():  # 判断验证码
            return JsonResponse({"code": 500, "info": "验证码错误"})

        # 验证码正确，可以进行后续操作
        cache.delete(uuid)  # 删除已使用的验证码
        return JsonResponse({"code": 200, "info": "验证码正确"})
