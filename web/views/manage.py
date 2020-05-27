from django.http import JsonResponse
from django.shortcuts import render, redirect



def dashboard(request, pro_id):
    """# 概览"""
    return render(request, 'dashboard.html')


def issues(request, pro_id):
    """# 问题"""
    return render(request, 'issues.html')


def statistics(request, pro_id):
    """统计"""
    return render(request, 'statistics.html')


def setting(request, pro_id):
    """设置"""
    return render(request, 'setting.html')