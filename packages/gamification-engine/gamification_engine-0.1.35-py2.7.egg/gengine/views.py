# -*- coding: utf-8 -*-
from pyramid.view import view_config
from .models import (
    User,
    Achievement,
    Value
    )

from urlcache import get_or_set
from pyramid.renderers import render, JSON

from .flaskadmin import flaskadminapp
from pyramid.wsgi import wsgiapp2, wsgiapp
from _collections import defaultdict
from gengine.models import Variable, valid_timezone, Goal, AchievementReward, FormularEvaluationException
from werkzeug.exceptions import BadRequest
from gengine.urlcache import set_value
from pyramid.exceptions import NotFound
from werkzeug import DebuggedApplication
from gengine.wsgiutil import HTTPSProxied

import traceback

@view_config(route_name='add_or_update_user', renderer='string', request_method="POST")
def add_or_update_user(request):
    """add a user and set its metadata"""
    
    user_id = long(request.matchdict["user_id"])
    
    lat=None
    if len(request.POST.get("lat",""))>0:
        lat = float(request.POST["lat"])
    
    lon=None
    if len(request.POST.get("lon",""))>0:
        lon = float(request.POST["lon"])
    
    friends=[]
    if len(request.POST.get("friends",""))>0:
        friends = [long(x) for x in request.POST["friends"].split(",")]
    
    groups=[]
    if len(request.POST.get("groups",""))>0:
        groups = [long(x) for x in request.POST["groups"].split(",")]
    
    timezone="UTC"
    if len(request.POST.get("timezone",""))>0:
        timezone = request.POST["timezone"]
    
    if not valid_timezone(timezone):
        timezone = 'UTC'
    
    country=None
    if len(request.POST.get("country",""))>0:
        country = request.POST["country"]
    
    region=None
    if len(request.POST.get("region",""))>0:
        region = request.POST["region"]
    
    city=None
    if len(request.POST.get("city",""))>0:
        city = request.POST["city"]
    
    User.set_infos(user_id=user_id,
                   lat=lat,
                   lng=lon,
                   timezone=timezone,
                   country=country,
                   region=region,
                   city=city,
                   friends=friends,
                   groups=groups)
    
    return {"status" : "OK"}

@view_config(route_name='delete_user', renderer='string', request_method="DELETE")
def delete_user(request):
    """delete a user completely"""
    
    user_id = long(request.matchdict["user_id"])
    User.delete_user(user_id)
    return {"status" : "OK"}

def _get_progress(user,force_generation=False):
    def generate():
        achievements = Achievement.get_achievements_by_user_for_today(user)
        
        def ea(achievement):
            try:
                #print "evaluating "+`achievement["id"]`
                return Achievement.evaluate(user, achievement["id"])
            except FormularEvaluationException as e:
                return { "error": "Cannot evaluate formular: " + e.message, "id" : achievement["id"] }
            except Exception as e:
                tb = traceback.format_exc()
                return { "error": tb, "id" : achievement["id"] }
            
        check = lambda x : x!=None and not x.has_key("error") and (x["hidden"]==False or x["level"]>0)
        
        evaluatelist = [ea(achievement) for achievement in achievements]
        
        ret = {
            "achievements" : {
                x["id"] : x for x in evaluatelist if check(x) 
            },
            "achievement_errors" : {
                x["id"] : x for x in evaluatelist if x!=None and x.has_key("error") 
            }
        }
        
        return render("json",ret),ret
        
    key = "/progress/"+str(user.id)
    
    if not force_generation:
        #in this case, we do not return the decoded json object - the caller has to take of this if needed
        return get_or_set(key,lambda:generate()[0]), None
    else:
        ret_str, ret = generate()
        set_value(key,ret_str)
        return ret_str, ret

@view_config(route_name='get_progress', renderer='json')
def get_progress(request):
    """get all relevant data concerning the user's progress"""
    user_id = long(request.matchdict["user_id"])
    
    user = User.get_user(user_id)
    if not user:
        raise NotFound("user not found")
    
    return _get_progress(user, force_generation=False)[0]
    
@view_config(route_name='increase_value', renderer='json', request_method="POST")
@view_config(route_name='increase_value_with_key', renderer='json', request_method="POST")
def increase_value(request):
    """increase a value for the user"""
    
    user_id = int(request.matchdict["user_id"])
    try:
        value = float(request.POST["value"])
    except:
        raise BadRequest("Invalid value provided")
    
    key = request.matchdict["key"] if request.matchdict.has_key("key") else ""
    variable_name = request.matchdict["variable_name"]
    
    user = User.get_user(user_id)
    if not user:
        raise NotFound("user not found")
    
    variable = Variable.get_variable_by_name(variable_name)
    if not variable:
        raise NotFound("variable not found")
    
    Value.increase_value(variable_name, user, value, key) 
    
    output = _get_progress(user,force_generation=True)[1]
    
    for aid in output["achievements"].keys():
        if len(output["achievements"][aid]["new_levels"])>0:
            del output["achievements"][aid]["levels"]
            del output["achievements"][aid]["priority"]
            del output["achievements"][aid]["goals"]
        else:
            del output["achievements"][aid]
    return output

@view_config(route_name="increase_multi_values", renderer="json", request_method="POST")
def increase_multi_values(request):
    try:
        doc = request.json_body
    except:
        raise BadRequest("no valid json body")
    ret = {}
    for user_id, values in doc.items():
        user = User.get_user(user_id)
        if not user:
            raise BadRequest("user %s not found" % (user_id,))
        
        for variable_name, values_and_keys in values.items():
            for value_and_key in values_and_keys:
                variable = Variable.get_variable_by_name(variable_name)
                
                if not variable:
                    raise BadRequest("variable %s not found" % (variable_name,))
                
                if not 'value' in value_and_key:
                    raise BadRequest("illegal value for %s" % (variable_name,))
                
                value = value_and_key['value']
                key = value_and_key.get('key','')
                
                Value.increase_value(variable_name, user, value, key)
    
        output = _get_progress(user,force_generation=True)[1]
        
        for aid in output["achievements"].keys():
            if len(output["achievements"][aid]["new_levels"])>0:
                del output["achievements"][aid]["levels"]
                del output["achievements"][aid]["priority"]
                del output["achievements"][aid]["goals"]
            else:
                del output["achievements"][aid]
        
        if len(output["achievements"])>0 :
            ret[user_id]=output
    
    return ret

@view_config(route_name='get_achievement_level', renderer='string', request_method="GET")
def get_achievement_level(request):
    """get all information about an achievement for a specific level""" 
    try:
        achievement_id = int(request.matchdict.get("achievement_id",None))
        level = int(request.matchdict.get("level",None))
    except:
        raise BadRequest("invalid input")
         
    def generate():
        achievement = Achievement.get_achievement(achievement_id)
         
        if not achievement:
            raise NotFound("achievement not found")
         
        level_output = Achievement.basic_output(achievement, [], True, level).get("levels").get(str(level), {"properties":{},"rewards":{}})
        if level_output.has_key("goals"):
            del level_output["goals"]
        if level_output.has_key("level"):
            del level_output["level"]
        return render("json",level_output)
     
    key = "/achievement/"+str(achievement_id)+"/level/"+str(level)
    request.response.content_type = 'application/json'
         
    return get_or_set(key,generate)
    
@view_config(route_name='admin')
@wsgiapp2
def admin(environ, start_response):
    return HTTPSProxied(DebuggedApplication(flaskadminapp.wsgi_app, True))(environ,start_response)
    #return 