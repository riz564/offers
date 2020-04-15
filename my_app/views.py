import requests
from django.shortcuts import render
from bs4 import BeautifulSoup
from requests.compat import quote_plus
from . import models
import re
# Create your views here.

BASE_AMAZON_URL='https://www.amazon.in/s?k={}&ref=nb_sb_noss_2'
def home(request):
    return render(request,'base.html')

def new_search(request):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64;     x64; rv:66.0) Gecko/20100101 Firefox/66.0", "Accept-Encoding":"gzip, deflate",     "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}
    search = request.POST.get('search')
    models.Search.objects.create(search=search)
    final_url=BASE_AMAZON_URL.format(quote_plus(search))
    response = requests.get(final_url,headers=headers)
    data = response.text
    print(final_url)
    soup = BeautifulSoup(data, features='html.parser')
    final_postings=[]
    for d in soup.findAll('div', attrs={'class':'sg-col-4-of-24 sg-col-4-of-12 sg-col-4-of-36 s-result-item s-asin sg-col-4-of-28 sg-col-4-of-16 sg-col sg-col-4-of-20 sg-col-4-of-32'}):
        link = d.find('a', attrs={'class':'a-link-normal a-text-normal'}).get('href')
        link='https://www.amazon.in/'+link
        images = d.find('img', {'src':re.compile('.jpg')})
        name = d.find('span', attrs={'class':'a-size-base-plus a-color-base a-text-normal'})
        pricediv= d.find('div', attrs={'class':'a-row a-size-base a-color-base'})
        price=None
        if pricediv is not None:
            price=pricediv.find('span', attrs={'class':'a-offscreen'})
        if name is not None and price is not None:
            final_postings.append((link,name.text,price.text,images['src']))
        elif price is None:
            final_postings.append((link,name.text,'Not Available',images['src']))
        else:
            final_postings.append("unknown-product")
    context={'search':search,'final_postings':final_postings,}
    return render(request,'my_app/new_search.html',context)
