from django.http import JsonResponse
from django.shortcuts import render, redirect


def statistics(request, pro_id):
    """统计"""
    return render(request, 'statistics.html')