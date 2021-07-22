import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

# Create your views here.

from django.contrib import auth

from main import models
from main.forms import RegForm
from main.models import Article


# 登录
def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    # 判断是否是ajax请求
    if request.is_ajax():
        response = {
            'code': 100,
            'msg': None
        }
        name = request.POST.get('name')
        pwd = request.POST.get('pwd')
        code = request.POST.get('code')

        if code.upper() == request.session['code'].upper():
            user = auth.authenticate(request, username=name, password=pwd)
            if user:
                response['msg'] = "登录成功"
                # 会将user对象存放到request中去，方便调用
                # 在后续的视图函数中直接request.user 取得当前登录的用户
                auth.login(request, user)
                # return HttpResponse('ok')
            else:
                response['code'] = "101"
                response['msg'] = "用户名或密码错误"
                # return HttpResponse('用户名或密码错误')
        else:
            response['code'] = "102"
            response['msg'] = "验证码错误"
            # return HttpResponse('验证码错误')

        return JsonResponse(response)


# 获取随机颜色
def get_random_color():
    import random
    return (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )


# 生成验证码
def get_code(request):
    # import random
    # 方式一：返回固定图片
    # with open('static/img/lhf.jpg','rb') as f:
    #     data=f.read()
    # 方式二：自动生成图片（需要借助第三方模块pillow） 图像处理模块
    # pip3 install pillow
    # Image 导入, ImageDraw 在图片上写字, ImageFont 写字的格式
    from PIL import Image, ImageDraw, ImageFont
    # 相当于把文件以byte格式存放到内存中
    from io import BytesIO
    import random
    # 新生成一张图片
    img = Image.new("RGB", (270, 40), color=get_random_color())

    draw = ImageDraw.Draw(img)
    kumo_font = ImageFont.truetype("static/font/kumo.ttf", size=32)

    valid_code_str = ""
    for i in range(5):
        random_num = str(random.randint(0, 9))
        random_low_alpha = chr(random.randint(95, 122))
        random_upper_alpha = chr(random.randint(65, 90))
        random_char = random.choice([random_num, random_low_alpha, random_upper_alpha])
        draw.text((i * 50 + 20, 5), random_char, get_random_color(), font=kumo_font)

        # 保存验证码字符串
        valid_code_str += random_char

    print("valid_code_str 验证码", valid_code_str)
    f = BytesIO()
    # 把图片保存起来
    img.save(f, "png")
    data = f.getvalue()
    request.session['code'] = valid_code_str

    return HttpResponse(data)


# 主页
def index(request):
    """
    首页
    :param request:
    :return:
    """
    article_list = models.Article.objects.all().order_by('-create_time')
    content = {
        'article_list': article_list,
    }
    return render(request, 'index.html', content)


# 注册
def register(request):
    """
    注册页面
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = RegForm()
        return render(request, 'register.html', {'form': form})

    # 判断是否是ajax请求
    elif request.is_ajax():
        response = {
            'code': 100,
            'msg': None
        }
        form = RegForm(request.POST)

        if form.is_valid():
            # 校验通过的数据
            clean_data = form.cleaned_data
            # 把多余的数据剔除 re_pwd
            clean_data.pop('re_pwd')
            # 取出头像
            avatar = request.FILES.get('avatar')

            if avatar:
                # 因为用的是FileField,只需要把文件对象赋值给avata字段，自动做保存
                clean_data['avatar'] = avatar

            user = models.UserInfo.objects.create_user(**clean_data)
            # 创建成功
            if user:
                response['msg'] = "用户创建成功"
                # login(request. user)
            else:
                response['code'] = 103
                response['msg'] = "发生未知错误，创建失败"

        else:
            response['code'] = 101
            response['msg'] = form.errors

        return JsonResponse(response, safe=False)

    else:
        print('没有匹配url')


# 注销
def logout(request):
    auth.logout(request)
    return redirect('/index/')


# 个人站点页面
def site_page(request, username, *args, **kwargs):

    # print(args)
    # print(kwargs)

    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')

    # 用户存在
    # 查出用户的所有文章
    # 根据用户得到个人站点
    blog = user.blog
    # print(blog)
    # 取到当前站点下所有文章
    article_list = blog.article_set.all().order_by('-create_time')
    # article_list = Article.objects.filter(user=user.nid).order_by('-create_time')

    # 数据过滤
    condition = kwargs.get('condition')
    param = kwargs.get('param')
    if condition == 'tag':
        article_list = article_list.filter(tags=param)
    elif condition == 'category':
        article_list = article_list.filter(category_id=param)
    elif condition == 'archive':
        # 2021-07
        year_to = param.split('-')
        article_list = article_list.filter(create_time__year=year_to[0], create_time__month=year_to[1])

    # 分组查询
    # 1.分组查询固定规则：
    # filter 在annotate前表示where条件
    # filter 在annotate后表示having条件
    # values 在annotate前表示group by
    # values 在annotate后表示取值

    # 查询当前站点下所有标签对应的文章数
    # 查询所有分类对应的文章数
    # 先进行分组 models.Category.objects.all().values('pk')
    # 然后数每个组中有多少个article__nid
    category__ret = models.Category.objects.all().values('pk').filter(blog=blog).annotate(
        cou=Count('article__nid')).values('title', 'cou', 'nid')

    # 查询当前站点所有分类对应的文章数
    tag__ret = models.Tag.objects.all().values('pk').filter(blog=blog).annotate(
        cou=Count('article__nid')).values('title', 'cou', 'nid')

    # 查询某年某月下对应的文章数
    # 截断月
    from django.db.models.functions import TruncMonth

    month_ret = models.Article.objects.all().values('pk').filter(blog=blog)\
        .annotate(month=TruncMonth('create_time'))\
        .values('month')\
        .annotate(c=Count('nid'))\
        .values_list('month', 'c')                   # (might be redundant,haven't tested) select month and count
    
    '''
        from django.db.models.functions import TruncMonth
        
        Article.objects
        .annotate(month=TruncMonth('timestap'))  # Truncate to month and add to select list
        .values('month')                        # Group By month
        .annotate(c=Count('id'))                # Select the count of the grouping
        .values('month', 'c')                   # (might be redundant,haven't tested) select month and count
        
    '''
    content = {
        'article_list': article_list,
        'blog': blog,
        'category__ret': category__ret,
        'tag__ret': tag__ret,
        'month_ret': month_ret,
    }
    # print(content)
    # locals()  将当前作用域下的所有变量都传入模板
    return render(request, 'site_page.html', locals())


# 文章详情页面
def article_detail(request, username, pk):
    # print(args)
    # print(kwargs)

    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, 'error.html')

    # 用户存在
    # 查出用户的所有文章
    # 根据用户得到个人站点
    blog = user.blog

    # 取到当前对应的文章
    article = Article.objects.get(pk=pk)

    # 分组查询
    # 1.分组查询固定规则：
    # filter 在annotate前表示where条件
    # filter 在annotate后表示having条件
    # values 在annotate前表示group by
    # values 在annotate后表示取值

    # 查询当前站点下所有标签对应的文章数
    # 查询所有分类对应的文章数
    # 先进行分组 models.Category.objects.all().values('pk')
    # 然后数每个组中有多少个article__nid
    category__ret = models.Category.objects.all().values('pk').filter(blog=blog).annotate(
        cou=Count('article__nid')).values('title', 'cou', 'nid')

    # 查询当前站点所有分类对应的文章数
    tag__ret = models.Tag.objects.all().values('pk').filter(blog=blog).annotate(
        cou=Count('article__nid')).values('title', 'cou', 'nid')

    # 查询某年某月下对应的文章数
    # 截断月
    from django.db.models.functions import TruncMonth

    month_ret = models.Article.objects.all().values('pk').filter(blog=blog) \
        .annotate(month=TruncMonth('create_time')) \
        .values('month') \
        .annotate(c=Count('nid')) \
        .values_list('month', 'c')  # (might be redundant,haven't tested) select month and count

    '''
        from django.db.models.functions import TruncMonth

        Article.objects
        .annotate(month=TruncMonth('timestap'))  # Truncate to month and add to select list
        .values('month')                        # Group By month
        .annotate(c=Count('id'))                # Select the count of the grouping
        .values('month', 'c')                   # (might be redundant,haven't tested) select month and count

    '''
    # 取出所有评论
    # comments = article.comment_set.all()
    content = {
        'article': article,
        'blog': blog,
        'category__ret': category__ret,
        'tag__ret': tag__ret,
        'month_ret': month_ret,
    }
    # print(content)
    # locals()  将当前作用域下的所有变量都传入模板
    return render(request, 'article_detail.html', locals())


# 点赞
def diggit(request):
    response = {
        'code': 100,
        'msg': None
    }
    # print(request.user)
    # print(request.user.is_authenticated)
    if request.user.is_authenticated:
        user_id = request.user.nid
        is_up = request.POST.get('is_up')       # 这里返回的是 true 字符串
        # 将json格式转化为python格式
        is_up = json.loads(is_up)               # 将 字符串转化为Boolean值
        article_id = request.POST.get('article_id')
        # 查询是否已经点过赞
        up_ret = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
        if up_ret:
            response['code'] = 102
            response['msg'] = '您已经点过赞了'
        else:
            # 原子性操作 事务性操作 要么成功 要么失败
            from django.db import transaction
            # 开启事务 with 上下文管理
            with transaction.atomic():
                models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
                if is_up:
                    # 对文章表点赞字段+1
                    models.Article.objects.filter(pk=article_id).update(up_count=F('up_count')+1)
                    response['msg'] = '点赞成功'
                else:
                    # 对文章表点赞字段+1 多表操作F字段 取自身的值
                    models.Article.objects.filter(pk=article_id).update(down_count=F('down_count')+1)
                    response['msg'] = '点踩成功'

    else:
        response['code'] = 101
        response['msg'] = '请先登录'

    return JsonResponse(response)


def commit(request):
    # 评论提交
    response = {
        'code': 100,
        'msg': None
    }

    if request.user.is_authenticated:
        user_id = request.user.nid
        content = request.POST.get('content')
        article_id = request.POST.get('article_id')
        parent_id = request.POST.get('parent_id')

        # 原子性操作 事务性操作 要么成功 要么失败
        from django.db import transaction
        # 开启事务 with 上下文管理
        with transaction.atomic():
            ret = models.Comment.objects.create(article_id=article_id, content=content, user_id=user_id, parent_comment_id=parent_id)
            # 对文章表评论字段+1
            models.Article.objects.filter(pk=article_id).update(comment_count=F('comment_count') + 1)
            response['username'] = ret.user.username
            response['reply_content'] = ret.content
            if parent_id:
                response['parent_name'] = ret.parent_comment.user.username
                print(response['parent_name'])
            response['msg'] = '评论成功'
    else:
        response['code'] = 101
        response['msg'] = '请先登录'

    return JsonResponse(response)


# 后台管理
# 后台管理主页面
# path('commit/', login_required(views.commit)), 这里添加了login_required就相当于添加了装饰器
@login_required(login_url='/login/')
def home_backend(request):
    # 查询该人的所有文章
    article_list = models.Article.objects.filter(blog=request.user.blog)
    content = {
        "article_list":article_list,
    }
    return render(request, 'backend/home_backend.html', content)


def auth(func):
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner


# 添加新闻
@login_required(login_url='/login/')
def add_article(request):
    if request.method == "GET":
        content = {
            # "article_list": article_list,
        }
        return render(request, 'backend/add_article.html', content)

    else:
        title = request.POST.get('title')
        content = request.POST.get('content')

        # *****************************

        # 通过bs4 处理XSS攻击（在文章中嵌入js代码进行攻击服务器） HTML文档解析库
        # pip install beautifulsoup4  https://www.cnblogs.com/liuqingzheng/articles/10261331.html
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(content, "html.parser")
        # 查找所有标签
        # tags = soup.find_all('span', attrs={'class': 'errors'})
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                # 过滤出是script的标签
                # 从文档中删除掉script的标签
                tag.decompose()
        # soup.text 文档的内容，不包括标签
        desc = soup.text[:150]

        # *****************************

        models.Article.objects.create(
            title=title,
            desc=desc,
            content=str(soup),
            # content=content,
            blog=request.user.blog,
            user=request.user,
        )

        return redirect('/backend/')


# 图片上传处理
def uploadimg(request):
    response = {
        "error": 0,     # 成功 0 失败1
        "url": None
    }
    file = request.FILES.get('imgFile')
    imgurl = 'media/file/' + file.name
    # print(file)
    with open(imgurl, 'wb') as f:
        for line in file:
            f.write(line)
        response['url'] = imgurl
        # print(response['url'])
    return JsonResponse(response)
