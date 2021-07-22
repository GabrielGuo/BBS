# python 3.6
# -*- coding: utf-8 -*-
# @Time    : 2021-07-19 21:50
# @Author  : 乐天派逗逗 Gabriel
# @Site    : Windows 10
# @File    : forms.py
# @Software: PyCharm
# @Contact : 1584838420@qq.com
# @Features: 用于表单的验证
from django import forms
from django.core.exceptions import ValidationError
from django.forms import widgets


# 写一个类，继承Form 没有头像校验的字段
from main import models


class RegForm(forms.Form):
    """
    表单验证
    """
    username = forms.CharField(max_length=18, min_length=3, label="用户名",
                           error_messages={
                             'max_length': "用户名太长了",
                             'min_length': "用户名太短了",
                             'required': "不能为空"},
                           widget=widgets.TextInput(attrs={'class': 'form-control'}),)

    password = forms.CharField(max_length=18, min_length=3, label="密码",
                               error_messages={
                                   'max_length': "密码太长了",
                                   'min_length': "密码太短了",
                                   'required': "不能为空"},
                               widget=widgets.PasswordInput(attrs={'class': 'form-control'}),)

    re_pwd = forms.CharField(max_length=18, min_length=3, label="确认密码",
                             error_messages={
                              'max_length': "密码太长了",
                              'min_length': "密码太短了",
                              'required': "不能为空"},
                             widget=widgets.PasswordInput(attrs={'class': 'form-control'}), )

    email = forms.EmailField(label="邮箱", error_messages={'required': "不能为空"},
                             widget=widgets.EmailInput(attrs={'class': 'form-control'}), )

    # 自定义 局部钩子 局部校验 针对username这一个值进行校验
    def clean_username(self):
        # 取出username对应的值
        username = self.cleaned_data.get('username')
        # # 用户名不允许以'sb'开头
        # if username.startswitch('sb'):
        #     # 校验不通过，抛异常
        #     raise ValidationError('不能以sb开头')
        # else:
        #     # 校验通过，直接return username 值
        #     return username

        user = models.UserInfo.objects.filter(username=username).first()
        if user:
            # 用户存在，抛异常
            raise ValidationError('用户名已存在')
        else:
            # 校验通过，直接return username 值
            return username

    # 全局钩子 针对两个值进行校验
    def clean(self):
        password = self.cleaned_data.get('password')
        re_pwd = self.cleaned_data.get('re_pwd')

        # if pwd and re_pwd:
        # else:
        #     return self.cleaned_data

        if password == re_pwd:
            # 校验通过，返回清洗后的数据
            return self.cleaned_data
        else:
            raise ValidationError('两次密码不一致')




