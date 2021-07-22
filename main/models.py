from django.db import models

# Create your models here.


from django.contrib.auth.models import User, AbstractUser


class UserInfo(AbstractUser):
    """
    用户信息
    """
    nid = models.AutoField(primary_key=True)
    telephone = models.CharField(max_length=11, null=True, unique=True)
    # 头像：FileField文件（varchar类型），default：默认值，upload_to 上传的路径
    avatar = models.FileField(upload_to='avatars/', default="/avatars/avatar.png")
    # auto_now_add=True
    '''
    auto_now_add
    配置auto_now_add=True，创建数据记录的时候会把当前时间添加到数据库。
    auto_now
    配置上auto_now=True，每次更新数据记录的时候会更新该字段。
    '''
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)

    # 跟blog表一对一
    # OneToOneField 本质就是ForeignKey，只不过有个唯一性约束
    blog = models.OneToOneField(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.username

    class Meta:
        # db_table = 'xxx'
        # 在admin中显示的表名
        verbose_name = '用户表'
        # 去掉 用户表 后面的s
        verbose_name_plural = verbose_name


class Blog(models.Model):
    """
    博客信息表（站点表）
    """
    nid = models.AutoField(primary_key=True)
    # 站点副标题
    title = models.CharField(verbose_name='个人博客标题', max_length=64)
    # 站点名称
    site_name = models.CharField(verbose_name='站点名称', max_length=64)
    # 不同人不同主题
    theme = models.CharField(verbose_name='博客主题', max_length=32)

    def __str__(self):
        return self.title


# 分类表
class Category(models.Model):
    """
    博主个人文章分类表
    """
    nid = models.AutoField(primary_key=True)
    # 分类名字
    title = models.CharField(verbose_name='分类标题', max_length=32)
    # 跟博客是一对多的关系，关联字段写在多的一方
    # to  是跟哪个表有关联 to_field 跟表中的哪个字段做关联 null = true 表示可以为空
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Tag(models.Model):
    nid = models.AutoField(primary_key=True)
    # 标签名字
    title = models.CharField(verbose_name='标签名称', max_length=32)
    # 跟博客是一对多的关系，关联字段写在多的一方
    blog = models.ForeignKey(verbose_name='所属博客', to='Blog', to_field='nid', on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Article(models.Model):
    nid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50, verbose_name='文章标题')
    desc = models.CharField(max_length=255, verbose_name='文章描述')
    # DateTimeField 年月日时分秒 (注意跟datafield区别)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    content = models.TextField()

    # 评论数
    comment_count = models.IntegerField(default=0)
    # 点赞数
    up_count = models.IntegerField(default=0)
    # 点踩数
    down_count = models.IntegerField(default=0)

    # 一对多的关系
    blog =models.ForeignKey(to='Blog', to_field='nid', null=True, on_delete=models.CASCADE)

    user = models.ForeignKey(verbose_name='作者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    category = models.ForeignKey(to='Category', to_field='nid', null=True, on_delete=models.CASCADE)
    # 多对多的关系 through_fields不能写反了
    tags = models.ManyToManyField(
        to="Tag",
        # 指定的是用哪个中间表
        through='ArticleToTag',
        through_fields=('article', 'tag'),
    )

    def __str__(self):
        return self.title + '----' + self.user.username
        # return self.title + '----' + self.blog.userinfo.username


class ArticleToTag(models.Model):
    nid = models.AutoField(primary_key=True)
    article = models.ForeignKey(verbose_name='文章', to="Article", to_field='nid', on_delete=models.CASCADE)
    tag = models.ForeignKey(verbose_name='标签', to="Tag", to_field='nid', on_delete=models.CASCADE)

    class Meta:
        unique_together = [
            ('article', 'tag'),
        ]

    def __str__(self):
        v = self.article.title + "---" + self.tag.title
        return v


class ArticleUpDown(models.Model):
    """
    点赞表
    """

    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey('UserInfo', null=True, on_delete=models.CASCADE)
    article = models.ForeignKey("Article", null=True, on_delete=models.CASCADE)
    is_up = models.BooleanField(default=True)

    class Meta:
        # 联合唯一，一个用户只能给一篇文章点赞或点踩
        unique_together = [
            ('article', 'user'),
        ]


class Comment(models.Model):
    """

    评论表

    """
    nid = models.AutoField(primary_key=True)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo', to_field='nid', on_delete=models.CASCADE)
    article = models.ForeignKey(verbose_name='评论文章', to='Article', to_field='nid', on_delete=models.CASCADE)
    create_time = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    content = models.CharField(verbose_name='评论内容', max_length=255)
    # 自关联
    parent_comment = models.ForeignKey("self", null=True, blank=True, to_field="nid", on_delete=models.CASCADE)

    def __str__(self):
        return self.content
