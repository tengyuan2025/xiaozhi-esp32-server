#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一HTTP客户端工具类
所有HTTP请求均不使用代理
"""

import httpx
import requests
from typing import Dict, Optional, Any


def create_httpx_client(**kwargs) -> httpx.Client:
    """
    创建同步httpx客户端，禁用代理
    """
    default_kwargs = {
        'trust_env': False,  # 不信任环境变量中的代理设置
        'proxies': {},       # 明确设置空代理
    }
    default_kwargs.update(kwargs)
    return httpx.Client(**default_kwargs)


def create_async_httpx_client(**kwargs) -> httpx.AsyncClient:
    """
    创建异步httpx客户端，禁用代理
    """
    default_kwargs = {
        'trust_env': False,  # 不信任环境变量中的代理设置
        'proxies': {},       # 明确设置空代理
    }
    default_kwargs.update(kwargs)
    return httpx.AsyncClient(**default_kwargs)


def create_requests_session(**kwargs) -> requests.Session:
    """
    创建requests会话，禁用代理
    """
    session = requests.Session()
    session.proxies = {}  # 禁用代理
    
    # 设置其他参数
    for key, value in kwargs.items():
        if hasattr(session, key):
            setattr(session, key, value)
        elif key == 'headers':
            session.headers.update(value)
    
    return session


def get_no_proxy_config() -> Dict[str, Any]:
    """
    获取禁用代理的通用配置
    """
    return {
        'trust_env': False,
        'proxies': {},
        'http': None,
        'https': None
    }