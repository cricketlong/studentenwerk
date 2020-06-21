import json
import requests
import array
import common.errors as errors
import redis_query.query as RedisQuery
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from query.meal import MealQuery, Meal
from django.views.decorators.csrf import csrf_exempt

base_url = "https://api.studentenwerk-dresden.de/openmensa/v2"

def list_canteens(request):
    url = base_url + "/canteens"

    return JsonResponse(requests.get(url).json(), safe = False)

def canteen_info(request, canteen_id):
    url = base_url + "/canteens/" + canteen_id

    return JsonResponse(requests.get(url).json(), safe = False)

def canteen_dates(request, canteen_id):
    url = base_url + "/canteens/" + canteen_id + "/days/"

    return JsonResponse(requests.get(url).json(), safe = False)

def canteen_date(request, canteen_id, date):
    url = base_url + "/canteens/" + canteen_id + "/days/" + date

    return JsonResponse(requests.get(url).json(), safe = False)

@csrf_exempt
def canteen_meals(request, canteen_id, date):
    url = base_url + "/canteens/" + canteen_id + "/days/" + date + "/meals/"
    meals = requests.get(url).json()

    """
    meals = [{ "id": 260,
                    "name": "Gemüse-Couscouspfanne mit Joghurt-Ingwer-Dip, dazu bunter Blattsalat",
                    "image": "https://static.studentenwerk-dresden.de/bilder/mensen/studentenwerk-dresden-lieber-mensen-gehen.jpg",
                    "notes": ["ovo-lacto-vegetabil", "mensaVital"],
                    "prices": {"students": 2.3, "employees": 3.65, "others": 4.6},
                    "category": "Alternativ-Angebot",
                    "likes": 0
                 },
                 {
                    "id": 10900,
                    "name": "Hähnchenschnitzel mit Brötchen",
                    "image": "https://static.studentenwerk-dresden.de/bilder/mensen/studentenwerk-dresden-lieber-mensen-gehen.jpg",
                    "notes": [],
                    "prices": { "pupils": 2.4, "others": 4.3},
                    "category": "Cafeteria Heiße Theke",
                    "likes": 0
                 }]
    """

    # extend meal info
    for m in meals:
        result = MealQuery().get_meal(m["id"])
        if len(result):
            uid = 0 # id == 0 is reserved
            token = ""

            if "wechat_uid" in request.POST and len(request.POST["wechat_uid"]):
                uid = int(request.POST["wechat_uid"])

            if "token" in request.POST:
                token = request.POST["token"]

            liked_users = array.array('L', result[0].liked_users).tolist()
            m["likes"] = len(liked_users)
            if RedisQuery.verify_token(uid, token):
                if uid in liked_users:
                    m["liked"] = True
            else:
                # show static values for not logged in users
                m["liked"] = False
        else:
            meal = Meal(m["id"])
            meal.save()

    return JsonResponse(meals, safe = False)

@csrf_exempt
def canteen_meal_detail(request, canteen_id, date, meal_id):
    url = base_url + "/canteens/" + canteen_id + "/days/" + date + "/meals/" + meal_id
    meal_info = requests.get(url).json()

    """
    meal_info = {"status": 404, "message": "meal not found"}
    if int(meal_id) == 260:
        meal_info = {
                        "id": 260,
                        "name": "Gemüse-Couscouspfanne mit Joghurt-Ingwer-Dip, dazu bunter Blattsalat",
                        "image": "https://static.studentenwerk-dresden.de/bilder/mensen/studentenwerk-dresden-lieber-mensen-gehen.jpg",
                        "notes": ["ovo-lacto-vegetabil", "mensaVital"],
                        "prices": {"students": 2.3, "employees": 3.65, "others": 4.6},
                        "category": "Alternativ-Angebot",
                        "likes": 0
                     }

    elif int(meal_id) == 10900:
        meal_info = {
                        "id": 10900,
                        "name": "Hähnchenschnitzel mit Brötchen",
                        "image": "https://static.studentenwerk-dresden.de/bilder/mensen/studentenwerk-dresden-lieber-mensen-gehen.jpg",
                        "notes": [],
                        "prices": { "pupils": 2.4, "others": 4.3},
                        "category": "Cafeteria Heiße Theke",
                        "likes": 0
                     }
                     """

    meal_info["likes"] = 0
    meal_info["liked"] = False
    wechat_uid = 0
    liked_users = []
    updated = False
    result = MealQuery().get_meal(meal_id)

    if len(result):
        meal = result[0]
        liked_users = array.array('L', meal.liked_users).tolist()

        if {"action", "wechat_uid", "token"} <= set(request.POST):
            action = request.POST["action"] 
            uid = int(request.POST["wechat_uid"]) 
            token = request.POST["token"] 
            meal_info["action"] = action

            # verify user token
            if RedisQuery.verify_token(uid, token) == False:
                return JsonResponse(errors.InvalidToken().dict(), safe = False)

            if action == "like":
                if uid not in liked_users:
                    liked_users.append(uid)
                    meal_info["liked"] = True

                    updated = True
            elif action == "dislike":
                if uid in liked_users:
                    liked_users.remove(uid)

                    updated = True

            if updated:
                meal.liked_users = array.array('L', liked_users)
                meal.update_data()

        meal_info["likes"] = len(liked_users)

    meal_info["status"] = 200
    return JsonResponse(meal_info, safe = False)

def likes(request, canteen_id, date, meal_id):
    
    resp = {"status": 200, "liked_users": []}
    result = MealQuery().get_meal(meal_id)

    if len(result):
        meal = result[0]
        resp["liked_users"] = array.array('L', meal.liked_users).tolist()

    return JsonResponse(resp, safe = False)

def get_canteen_comments(request, canteen_id):
    """
    comments = {
        4: ["今天老食堂有番茄炒蛋噢", "今天的苹果派超级恶心", "意大利面好吃！", "Wok有炒面"],
        29: ["沸点食堂有汉堡", "沙拉很棒", "今天没啥好吃的"]
    }
    """

    return JsonResponse(RedisQuery.get_canteen_comments(canteen_id), safe = False)

@csrf_exempt
def add_canteen_comment(request, canteen_id):
    if {"wechat_uid", "token", "comment"} > set(request.POST):
        return JsonResponse(errors.StatusError("missing argument").dict(), safe = False)

    try:
        uid = int(request.POST["wechat_uid"])
        if uid < 1:
            raise Exception("invalid wechat uid")
    except Exception as e:
        return JsonResponse(errors.StatusError(str(e)).dict(), safe = False)

    token = request.POST["token"] 
    comment = request.POST["comment"] 

    # verify user token
    if RedisQuery.verify_token(uid, token) == False:
        return JsonResponse(errors.InvalidToken().dict(), safe = False)

    if RedisQuery.add_canteen_comment(canteen_id, comment) == False:
        return JsonResponse(errors.StatusError("failed to add comment").dict(), safe = False)

    return JsonResponse(errors.StatusOK("one comment added").dict(), safe = False)

