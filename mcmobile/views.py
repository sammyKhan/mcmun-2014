import datetime

from django.shortcuts import render, redirect

from mcmun.models import ScheduleItem
from committees.models import Category, Committee


def schedule(request):
    items = ScheduleItem.objects.filter(is_visible=True).order_by("start_time")
    dates = {}
    for item in items:
        date_str = item.start_time.strftime("%A, %B %d")
        item_object = {}
        item_object["name"] = item.name
        item_object["start_time"] = "%02d:%02d" % (item.start_time.hour,
                                               item.start_time.minute)
        item_object["end_time"] = "%02d:%02d" % (item.end_time.hour,
                                             item.end_time.minute)
        if date_str not in dates:
            dates[date_str] = []
        dates[date_str].append(item_object)
    
    # it seems one can only iterate over lists in django templates
    # want a list like [
    #                    {date_str: "Thurs Jan 22", 
    #                     items: [{name: "Reg", "start_time": 11:00, "end_time": 12:00},
    #                             {name: "ComSess", "start_time"....}]
    #                    },
    #                    {date_str: "Fri Jan 23", 
    #                     items: [{name: "ComSess", "start_time": ....},
    #                             {name: "ComSess",....}]
    #                    }
    # .................]
    date_list = [{"date_str": date, "items": dates[date]} for date in dates]
    date_list.sort(key=lambda d: d["date_str"][-2:])

    data = { "dates": date_list }
    response = render(request, "schedule-mob.html", data)

    response["Access-Control-Allow-Origin"] = "*"
    return response


def committees(request):
    categories = Category.objects.all()
    committees_list = [{"name": x.name, 
        "committees": Committee.objects.filter(category_id=x.id, is_visible=True)} for x in categories]
    data = { "categories_list": committees_list }
    response = render(request, "committees-mob.html", data)

    response["Access-Control-Allow-Origin"] = "*"
    return response

def social_media(request):
    response = render(request, "social-mob.html")
    response["Access-Control-Allow-Origin"] = "*"
    return response

def food(request):
    response = render(request, "food-mob.html")
    response["Access-Control-Allow-Origin"] = "*"
    return response

def contact(request):
    response = render(request, "contact-mob.html")
    response["Access-Control-Allow-Origin"] = "*"
    return response

def sponsors(request):
    response = render(request, "sponsors-mob.html")
    response["Access-Control-Allow-Origin"] = "*"
    return response

def map(request):
    response = render(request, "map-mob.html")
    response["Access-Control-Allow-Origin"] = "*"
    return response
