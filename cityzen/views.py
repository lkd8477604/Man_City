from django.shortcuts import render, HttpResponse
from django.core.paginator import Paginator,Page
from cityzen.models import n_163, sina, qq
from cityzen.Manchester_City import Man_City
M = Man_City()
# Create your views here.

def get_db(request):
    M.main()
    #按日期只显示60条新闻
    db_sina = sina.objects.order_by('-pub_date')[:60]
    db_163 = n_163.objects.order_by('-pub_date')[:60]
    db_qq = qq.objects.order_by('-pub_date')[:60]
    news_sina = get_page(request, db_sina)
    news_163 = get_page(request, db_163)
    news_qq = get_page(request, db_qq)
    return render(request, 'city.html', {'news_sina':news_sina, 'news_163':news_163, 'news_qq':news_qq})

def get_page(request, soup_db):
    #Django自带的翻页功能，每页显示10条新闻
    page = request.GET.get('page', 1)
    paginator = Paginator(soup_db, 10)
    page_loaded = paginator.page(page)
    return page_loaded

