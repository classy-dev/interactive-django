from django.shortcuts import HttpResponse, get_object_or_404, render, redirect
from django.conf import settings
from django.http import JsonResponse
from django.forms.models import modelform_factory
from django import forms

from tools.models import (
    Universe_Tree, Universe_Folder, Universe_Universe, Universe_Default,
    Lists_Tree, Lists_Folder, Lists_Universe, Lists_Default,
    Benchmarks_Tree, Benchmarks_Folder, Benchmarks_Universe, Benchmarks_Default,
    Ranking_Rule, Ranking_System,  Ranking_Folder, Ranking_Tree,
    Liquidity_System, Liquidity_Folder, Liquidity_Tree, Liquidity_Rule,
    # Indicators_Combination_System, Indicators_Combination, Indicators_Combination_Folder, Indicators_Combination_Tree
)

from tools.forms import (
    UniverseForm, ListForm, BenchmarkForm,
    RankingSystemForm,RankingRuleForm,
    LiquiditySystemForm, LiquidityRuleForm,
    # IndicatorCombinationForm, IndicatorCombinationSystemForm
)
from backtest.models import (Adx, Atrn, BarSinceEntry, Constant,
                             Ema, HighDS, LowDS, OpenDS, Ppo,
                             PriceDS, Roc, Rsi, Slope, Sma,
                             Indicator, Input_data,
                             Rule, RuleCombination, PrimaryRule, 
                             IndicatorProperty, Indicators_Combination )

from backtest.forms import (RuleForm, RuleCombinationForm, IndicatorCombinationForm)

import csv
import os
import pandas as pd
import json
import time
import pickle
# Create your views here.

def Index(request):
    return redirect("tools:manage_universes_default")

#UNIVERSES VIEW

def get_path(parent_folder_id):
    if parent_folder_id == 0:
        return ""
    else:
        folder_element = get_object_or_404(Universe_Folder, id=parent_folder_id)
        return folder_element.path

def get_tree_list(id):
    tree_list = []
    list_item = {}
    get_default_list = Universe_Tree.objects.all().filter(permission=1)
    for element in get_default_list:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission,
        }
        tree_list.append(list_item)
    get_tree_lists = Universe_Tree.objects.all().filter(user_id=id, permission=0)
    for element in get_tree_lists:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission,
        }
        tree_list.append(list_item)
    return tree_list       

def createTree(parent_id, PushData, data):
    for data_element in data:
        if data_element["parent_id"] == parent_id:
            children = []
            if data_element["child_type"] == 1 and data_element["permission"] == 1:
                 PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": createTree(data_element["child_id"], children, data)
                    }
                )
            elif data_element["child_type"] == 1 and data_element["permission"] == 0:
                PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": createTree(data_element["child_id"], children, data)
                    }
                )
            elif data_element["child_type"] ==2 and data_element["permission"] == 1:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })
            elif data_element["child_type"] ==2 and data_element["permission"] == 0:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })
    return PushData


def getElements(indicator_type):
    element_tree = []
    indicators = IndicatorProperty.objects.all()
    for indicator in indicators:
        if indicator.type == indicator_type:
            element_tree.append({
                "id": indicator.id,
                "icon": "fa fa-plus",
                "text": str(indicator),
                "state": {
                    "opened": 1
                },
                "children": [],
            })
    return element_tree

def getIndicatorTree():
    indicator_tree = []
    indicator_types = set()
    indicators = IndicatorProperty.objects.all()
    cnt = 10001
    for indicator in indicators:
        indicator_types.add(indicator.type)
    for indicator_type in indicator_types:
        indicator_tree.append({
            "id": cnt,
            "text": str(indicator_type),
            "state": {
                "opened": 1
            },
            "children": getElements(str(indicator_type))
        })
        cnt += 1  
    return  indicator_tree      

def ajax_get_treeelement(request):
    tree_id = request.GET.get("id")
    tree_element = get_object_or_404(Universe_Tree, id=tree_id)
    msg = {
        "child_type": tree_element.child_type,
        "child_id": tree_element.child_id,
        "permission": tree_element.permission,
    }
    json_data = json.dumps(msg)
    return HttpResponse(json_data, content_type='application/json')

def ManageUniverses_default(request):
    universe_lists = Universe_Default.objects.all()
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'top_folder': 'true',
        'title': 'Default Universes',
        'universe_lists': universe_lists,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/universes/manage_universes.html', ctx)

def ManageUniverses(request, id):
    universe_lists = Universe_Universe.objects.all().filter(parent_id=id, user=request.user)
    if id  :
        folder = get_object_or_404(Universe_Folder, id=id)
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    if id :
        ctx = {
            'title': folder.path + folder.name,
            'tree_structure': tree_structure,
            'universe_lists': universe_lists,
        }
    else:
       ctx = {
            'title': "Top Folder",
            'tree_structure': tree_structure,
            'universe_lists': universe_lists,
        } 
    return render(request, 'tools/universes/manage_universes.html', ctx)

def CreateFolder(request):
    if request.POST:
        new_folder = Universe_Folder()
        new_folder.name = request.POST.get("folder_name")        
        new_folder.user = request.user
        new_folder.parent_id = request.POST.get("parent_id")
        if request.POST.get("parent_id") == '0':
            new_folder.path = request.POST.get("folder_name") + '/'  
        else:
            parent_folder = get_object_or_404(Universe_Folder, id=request.POST.get("parent_id"))
            new_folder.path = parent_folder.path + request.POST.get("folder_name") + '/'
        new_folder.save()
        new_tree = Universe_Tree()
        new_tree.child_id =new_folder.id
        new_tree.child_name = new_folder.name
        new_tree.child_type = 1
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect("tools:manage_universes", id=new_folder.id)
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    folders = Universe_Folder.objects.all().filter(user = request.user)
    ctx = {
        'tree_structure': tree_structure,
        'folders': folders
    }
    return render(request, 'tools/universes/create_folder.html', ctx)

def DeleteFolder(request):
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    folders = Universe_Folder.objects.all().filter(user = request.user)
    if request.POST:
        folder_id = request.POST.get("folder_id")
        if Universe_Tree.objects.all().filter(parent_id=folder_id, user = request.user).exists():
            ctx = {
                'tree_structure': tree_structure,
                'folders': folders,
                'error_message': "Not Empty Folder"
            }
            return render(request, 'tools/universes/delete_folder.html', ctx)
        else:
            folder = get_object_or_404(Universe_Folder, id=folder_id)
            folder.delete()
            tree = get_object_or_404(Universe_Tree, child_id=folder_id, child_type=1)
            tree.delete()
            return redirect("tools:manage_universes_default")
    ctx = {
            'tree_structure': tree_structure,
            'folders': folders
    }
    return render(request, 'tools/universes/delete_folder.html', ctx)

def CreateUniverse(request):
    if request.POST:
        universe_name = request.POST.get("universe_name")
        parent_folder_id = request.POST.get("parent_id")
        new_universe = Universe_Universe()
        new_universe.name = universe_name
        new_universe.user = request.user
        new_universe.parent_id = parent_folder_id
        new_universe.parent_path = get_path(int(parent_folder_id))
        new_universe.save()
        relative_path = get_path(int(parent_folder_id))
        userpath = settings.UNIVERSES +str(request.user) + '/' + relative_path
        if not os.path.exists(userpath):
            os.makedirs(userpath)
        with open(userpath+'/' + universe_name + '.csv', 'wb') as f:
            f.close
        new_tree = Universe_Tree()
        new_tree.child_id =new_universe.id
        new_tree.child_name = universe_name
        new_tree.child_type = 2
        new_tree.parent_id = parent_folder_id
        new_tree.user = request.user
        new_tree.save()
        return redirect("tools:manage_universe", id=new_universe.id)
    folders = Universe_Folder.objects.all().filter(user = request.user)
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'folders': folders,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/universes/create_universe.html', ctx)

def UploadUniverse(request):
    if request.POST:
        time.sleep(1)
        form = UniverseForm(request.POST, request.FILES)
        if form.is_valid():
            universe = form.save()
            with open(settings.BASE_DIR + universe.file.url, 'r') as f:
                reader = csv.reader(f)
                next(reader, None)
                instruments = list(reader)
                filename = universe.file.name
                universe.title = filename.split('.')[0].split('/')[-1]
                universe.count = len(instruments)
                universe.save()
            data = {'is_valid': True}
        else:
            data = {'is_valid': False}
        if not Universe_Tree.objects.all().filter(child_type=1, permission=1).exists():
            default_folder = Universe_Tree()
            default_folder.child_id = 26
            default_folder.child_name = "Default Folder"
            default_folder.child_type = 1
            default_folder.parent_id = 0
            default_folder.user = request.user
            default_folder.permission = 1
            default_folder.save()
        default_folder = get_object_or_404(Universe_Tree, child_type=1, permission=1)
        default_universe_tree = Universe_Tree()
        default_universe_tree.child_id = universe.id
        default_universe_tree.child_name = universe.title
        default_universe_tree.child_type = 2
        default_universe_tree.parent_id = default_folder.child_id
        default_universe_tree.user = request.user
        default_universe_tree.permission = 1
        default_universe_tree.save()        
        return JsonResponse(data)

def DeleteUniverse_default(request):
    universe_default = get_object_or_404(Universe_Default, id=request.POST.get("id"))
    os.remove(settings.BASE_DIR + universe_default.file.url)
    universe_default.delete()
    universe_default_tree = get_object_or_404(Universe_Tree, child_id=request.POST.get("id"), child_type=2, permission=1)
    universe_default_tree.delete()
    return redirect("tools:manage_universes_default")

def DeleteUniverse(request):
    universe_id = request.POST.get("id")
    universe = get_object_or_404(Universe_Universe, id=universe_id)
    universe_path = settings.UNIVERSES  + str(request.user) + '/' +get_path(universe.parent_id)
    os.remove(universe_path + universe.name + '.csv')
    universe.delete()
    universe_tree = get_object_or_404(Universe_Tree, child_id = universe_id, child_type=2, permission=0)
    universe_tree.delete()
    return redirect("tools:manage_universes_default")

def ManageUniverse_default(request):
    parent_universes = []
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    default_universes = Universe_Default.objects.all()
    if Universe_Universe.objects.filter(parent_id=0,user=request.user).exists():
        universe = Universe_Universe.objects.filter(parent_id=0, user=request.user).first()
        user_universes = Universe_Universe.objects.filter(user=request.user).exclude(id=universe.id)
        for default_universe in default_universes:
            parent_universes.append({
                'type': 1,
                'universe': default_universe,
            })
        for user_universe in user_universes:
            parent_universes.append({
                'type': 0,
                'universe': user_universe,
            })
        universe_path = settings.UNIVERSES+ str(request.user) + '/'  + get_path(universe.parent_id)
        with open(universe_path + universe.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments = list(reader)
        ctx = {
            'title': get_path(universe.parent_id) + universe.name,
            'universe': universe,
            'instruments': instruments,
            'tree_structure': tree_structure,
            'parent_universes': parent_universes,            
        }
    else:
        ctx = {
            'error_message': 'no universe',
            'tree_structure': tree_structure,
        }
    return render(request, 'tools/universes/manage_universe.html', ctx)

def AddInstrument_default(request, id):
    symbol = request.POST.get("symbol")
    name = request.POST.get("name")
    universe_default = get_object_or_404(Universe_Default, id=id)
    universe_default.count += 1
    universe_default.save()
    header = ['Ticker', 'Name']
    instrument = {
        'Ticker': symbol,
        'Name': name,
    }
    with open(settings.BASE_DIR + universe_default.file.url, 'a', ) as f:        
        w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
        if f.tell() == 0:
            w.writeheader()
        w.writerow(instrument)
    return redirect("tools:manage_default_universe", id=id)

def AddInstrumenttoUniverse(request):
    universe_id = request.POST.get("universe_id")
    universe = get_object_or_404(Universe_Universe, id=universe_id)
    universe_path = settings.UNIVERSES+ str(request.user) + '/'  + get_path(universe.parent_id)
    instruments = json.loads(request.POST.get("selectedInstrument"))
    header = ['Ticker', 'Name']
    for instrument in instruments:
        symbol = instrument[0]
        name = instrument[1]
        instrument = {
            'Ticker': symbol,
            'Name': name,
        }
        with open(universe_path + universe.name + '.csv', 'a', ) as f:        
            w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
            if f.tell() == 0:
                w.writeheader()
            w.writerow(instrument)
    universe.count += len(instruments)
    universe.save()
    return HttpResponse("success")

def DeleteInstrument_default(request, id):
    universe_default = get_object_or_404(Universe_Default, id=id)
    symbol = request.POST.get("symbol")
    data_universe = pd.read_csv(settings.BASE_DIR + universe_default.file.url, index_col="Ticker")
    data_universe.drop([symbol], inplace=True)
    data_universe.to_csv(settings.BASE_DIR + universe_default.file.url)
    universe_default.count += -1
    universe_default.save()
    return redirect("tools:manage_default_universe", id=id)

def ManageUniverse(request, id):
    parent_universes = []
    universe = get_object_or_404(Universe_Universe, id=id)
    user_universes = Universe_Universe.objects.filter(user=request.user).exclude(id=universe.id)
    default_universes = Universe_Default.objects.all()
    universe_path = settings.UNIVERSES + str(request.user) + '/'  + get_path(universe.parent_id)
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    for default_universe in default_universes:
        parent_universes.append({
            'type': 1,
            'universe': default_universe,
        })
    for user_universe in user_universes:
        parent_universes.append({
            'type': 0,
            'universe': user_universe,
        })
    with open(universe_path + universe.name + '.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        instruments = list(reader)
    ctx = {
        'title': get_path(universe.parent_id) + universe.name,
        'universe': universe,
        'instruments': instruments,
        'tree_structure': tree_structure,
        'parent_universes': parent_universes
    }
    return render(request, 'tools/universes/manage_universe.html', ctx)

def ManageDefaultUniverse(request, id):
    universe = get_object_or_404(Universe_Default, id=id)
    universes = Universe_Universe.objects.all()
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    with open(settings.BASE_DIR + universe.file.url, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        instruments = list(reader)
    ctx = {
        'title': universe.filename,
        'universe': universe,
        'instruments': instruments,
        'tree_structure': tree_structure,
    }
    return render(request, 'tools/universes/manage_universe_default.html', ctx)

def AddInstrument(request, id):
    universe = get_object_or_404(Universe_Universe, id=id)
    if request.POST:
        universe.count += 1
        universe.save()
        symbol = request.POST.get("symbol")
        name = request.POST.get("name")
        universe_path = settings.UNIVERSES + str(request.user) + '/'  + get_path(universe.parent_id)
        header = ['Ticker', 'Name']
        instrument = {
            'Ticker': symbol,
            'Name': name,
        }
        with open(universe_path + universe.name + '.csv', 'a', ) as f:        
            w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
            if f.tell() == 0:
                w.writeheader()
            w.writerow(instrument)
        return redirect("tools:manage_universe", id=id)
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'universe': universe,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/universes/add_instrument.html', ctx)

# def InsertInstrument(request):
#     universe_id = request.POST.get("universe_id")
#     universe = get_object_or_404(Universe_Universe, id=universe_id)
#     universe.count += 1
#     universe.save()
#     symbol = request.POST.get("instrument_symbol")
#     name = request.POST.get("instrument_name")
#     universe_path = settings.UNIVERSES+ str(request.user) + '/'  + get_path(universe.parent_id)
#     header = ['Ticker', 'Name']
#     instrument = {
#         'Ticker': symbol,
#         'Name': name,
#     }
#     with open(universe_path + universe.name + '.csv', 'a', ) as f:        
#         w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
#         if f.tell() == 0:
#             w.writeheader()
#         w.writerow(instrument)
#     return redirect("tools:manage_universe", id=universe_id)

# def UpdateInstrument(request):
#     universe_id = request.POST.get("update_id")
#     original_symbol = request.POST.get("original_symbol")
#     symbol = request.POST.get("update_symbol")
#     name = request.POST.get("update_name")
#     instrument = {
#         'Ticker': symbol,
#         'Name': name,
#     }
#     universe = get_object_or_404(Universe_Universe, id=universe_id)
#     universe_path = settings.UNIVERSES+ str(request.user) + '/'  + get_path(universe.parent_id)
#     data_universe = pd.read_csv(universe_path + universe.name + '.csv',index_col="Ticker")
#     data_universe = data_universe.replace(data_universe.loc[original_symbol], instrument)
#     data_universe.to_csv(universe_path + universe.name + '.csv',)
#     return redirect("tools:manage_universe", id=universe_id)
    

def DeleteInstrument(request):
    symbol = request.POST.get("symbol")
    universe_id = request.POST.get("id")
    universe = get_object_or_404(Universe_Universe, id=universe_id)
    universe_path = settings.UNIVERSES+ str(request.user) + '/'  + get_path(universe.parent_id)
    data_universe = pd.read_csv(universe_path + universe.name + '.csv', index_col="Ticker")
    data_universe.drop([symbol], inplace=True)
    data_universe.to_csv(universe_path + universe.name + '.csv',)
    universe.count += -1
    universe.save()
    return redirect("tools:manage_universe", id=universe_id)

def BooleanOperation(request):
    if request.POST:
        instrument_1_set = set()
        instrument_2_set = set()
        universe_1_id = request.POST.get("universe_1")
        universe_2_id = request.POST.get("universe_2")
        operation = request.POST.get("operation")
        new_universe_name = request.POST.get("universe_name")
        parent_folder_id = request.POST.get("parent_id")
        universe_1 = get_object_or_404(Universe_Universe, id=universe_1_id)
        universe_1_path = settings.UNIVERSES + str(request.user) + '/'  + get_path(universe_1.parent_id)
        with open(universe_1_path + universe_1.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments_1 = list(reader)
        for instrument_1 in instruments_1:
            instrument_1_set.add(instrument_1[0] + '#' + instrument_1[1])
        universe_2 = get_object_or_404(Universe_Universe, id=universe_2_id)
        universe_2_path = settings.UNIVERSES + str(request.user) + '/'  + get_path(universe_2.parent_id)
        with open(universe_2_path + universe_2.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments_2 = list(reader)
        for instrument_2 in instruments_2:
            instrument_2_set.add(instrument_2[0] + '#' + instrument_2[1])
        if operation == '0':
            result_instrument = instrument_1_set.union(instrument_2_set)
        if operation == '1':
            result_instrument = instrument_1_set.difference(instrument_2_set)
        if operation == '2':
            result_instrument = instrument_1_set.intersection(instrument_2_set)
        new_universe = Universe_Universe()
        new_universe.name = new_universe_name
        new_universe.user = request.user
        new_universe.parent_id = parent_folder_id
        new_universe.parent_path = get_path(int(parent_folder_id))
        new_universe.save()
        relative_path = get_path(int(parent_folder_id))
        userpath = settings.UNIVERSES +str(request.user) + '/' + relative_path
        header = ['Ticker', 'Name']
        if not os.path.exists(userpath):
            os.makedirs(userpath)
        with open(userpath+'/' + new_universe_name + '.csv', 'wb') as f:
            f.close
        with open(userpath+'/' + new_universe_name + '.csv', 'a') as f:
            w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
            if f.tell() == 0:
                w.writeheader()
            for element in result_instrument:
                insert_instrument = {
                    'Ticker': element.split('#')[0],
                    'Name': element.split('#')[1],
                }
                new_universe.count += 1
                w.writerow(insert_instrument)
            new_universe.save()
            f.close
        new_tree = Universe_Tree()
        new_tree.child_id =new_universe.id
        new_tree.child_name = new_universe_name
        new_tree.child_type = 2
        new_tree.parent_id = parent_folder_id
        new_tree.user = request.user
        new_tree.save()
        return redirect("tools:manage_universe", id=new_universe.id)
    parent_universes = []
    tree_list = get_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    # default_universes = Universe_Default.objects.all()
    user_universes = Universe_Universe.objects.all().filter(user=request.user)
    folders = Universe_Folder.objects.all().filter(user = request.user)
    # for default_universe in default_universes:
    #     parent_universes.append({
    #         'type': 1,
    #         'universe': default_universe,
    #     })
    for user_universe in user_universes:
        parent_universes.append({
            'type': 0,
            'universe': user_universe,
        }) 
    ctx = {
        'parent_universes': parent_universes,
        'tree_structure': tree_structure,
        'folders': folders,
    }
    return render(request, "tools/universes/boolean_operation.html", ctx)

def ajax_get_instrument_of_universe(request):
    universe_id = request.GET.get("id")
    universe_type = request.GET.get("type")
    if universe_type == "1":
        universe = get_object_or_404(Universe_Default, id=universe_id)
        with open(settings.BASE_DIR + universe.file.url, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments = list(reader)
    elif universe_type == "0":
        universe = get_object_or_404(Universe_Universe, id=universe_id)
        universe_path = settings.UNIVERSES+ str(request.user) + '/'  + get_path(universe.parent_id)
        with open(universe_path + universe.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments = list(reader)
    json_data = json.dumps(instruments)
    return HttpResponse(json_data, content_type='application/json')


#LISTS VIEW

def Lget_path(parent_folder_id):
    if parent_folder_id == 0:
        return ""
    else:
        folder_element = get_object_or_404(Lists_Folder, id=parent_folder_id)
        return folder_element.path

def Lget_tree_list(id):
    tree_list = []
    list_item = {}
    get_default_list = Lists_Tree.objects.all().filter(permission=1)
    for element in get_default_list:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission,
        }
        tree_list.append(list_item)
    get_tree_lists = Lists_Tree.objects.all().filter(user_id=id, permission=0)
    for element in get_tree_lists:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission,
        }
        tree_list.append(list_item)
    return tree_list       

def LcreateTree(parent_id, PushData, data):
    for data_element in data:
        if data_element["parent_id"] == parent_id:
            children = []
            if data_element["child_type"] == 1 and data_element["permission"] == 1:
                 PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": LcreateTree(data_element["child_id"], children, data)
                    }
                )
            elif data_element["child_type"] == 1 and data_element["permission"] == 0:
                PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": LcreateTree(data_element["child_id"], children, data)
                    }
                )
            elif data_element["child_type"] ==2 and data_element["permission"] == 1:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })
            elif data_element["child_type"] ==2 and data_element["permission"] == 0:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })
    return PushData

def Lajax_get_treeelement(request):
    tree_id = request.GET.get("id")
    tree_element = get_object_or_404(Lists_Tree, id=tree_id)
    msg = {
        "child_type": tree_element.child_type,
        "child_id": tree_element.child_id,
        "permission": tree_element.permission,
    }
    json_data = json.dumps(msg)
    return HttpResponse(json_data, content_type='application/json')

def LManageUniverses_default(request):
    universe_lists = Lists_Default.objects.all()
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = LcreateTree(0,[], tree_list)
    ctx = {
        'top_folder': 'true',
        'title': 'Default Lists',
        'universe_lists': universe_lists,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/lists/manage_universes.html', ctx)

def LManageUniverses(request, id):
    universe_lists = Lists_Universe.objects.all().filter(parent_id=id, user=request.user)
    if id  :
        folder = get_object_or_404(Lists_Folder, id=id)
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = LcreateTree(0,[], tree_list)
    if id :
        ctx = {
            'title': folder.path + folder.name,
            'tree_structure': tree_structure,
            'universe_lists': universe_lists,
        }
    else:
       ctx = {
            'title': "Top Folder",
            'tree_structure': tree_structure,
            'universe_lists': universe_lists,
        } 
    return render(request, 'tools/lists/manage_universes.html', ctx)

def LCreateFolder(request):
    if request.POST:
        new_folder = Lists_Folder()
        new_folder.name = request.POST.get("folder_name")        
        new_folder.user = request.user
        new_folder.parent_id = request.POST.get("parent_id")
        if request.POST.get("parent_id") == '0':
            new_folder.path = request.POST.get("folder_name") + '/'  
        else:
            parent_folder = get_object_or_404(Lists_Folder, id=request.POST.get("parent_id"))
            new_folder.path = parent_folder.path + request.POST.get("folder_name") + '/'
        new_folder.save()
        new_tree = Lists_Tree()
        new_tree.child_id =new_folder.id
        new_tree.child_name = new_folder.name
        new_tree.child_type = 1
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect("tools:lists_manage_universes", id=new_folder.id)
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = LcreateTree(0,[], tree_list)
    folders = Lists_Folder.objects.all().filter(user = request.user)
    ctx = {
        'tree_structure': tree_structure,
        'folders': folders
    }
    return render(request, 'tools/lists/create_folder.html', ctx)

def LDeleteFolder(request):
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = LcreateTree(0,[], tree_list)
    folders = Lists_Folder.objects.all().filter(user = request.user)
    if request.POST:
        folder_id = request.POST.get("folder_id")
        if Lists_Tree.objects.all().filter(parent_id=folder_id, user = request.user).exists():
            ctx = {
                'tree_structure': tree_structure,
                'folders': folders,
                'error_message': "Not Empty Folder"
            }
            return render(request, 'tools/lists/delete_folder.html', ctx)
        else:
            folder = get_object_or_404(Lists_Folder, id=folder_id)
            folder.delete()
            tree = get_object_or_404(Lists_Tree, child_id=folder_id, child_type=1)
            tree.delete()
            return redirect("tools:lists_manage_universes_default")
    ctx = {
            'tree_structure': tree_structure,
            'folders': folders
    }
    return render(request, 'tools/lists/delete_folder.html', ctx)

def LCreateUniverse(request):
    if request.POST:
        universe_name = request.POST.get("universe_name")
        parent_folder_id = request.POST.get("parent_id")
        new_universe = Lists_Universe()
        new_universe.name = universe_name
        new_universe.user = request.user
        new_universe.parent_id = parent_folder_id
        new_universe.parent_path = Lget_path(int(parent_folder_id))
        new_universe.save()
        relative_path = Lget_path(int(parent_folder_id))
        userpath = settings.LISTS +str(request.user) + '/' + relative_path
        if not os.path.exists(userpath):
            os.makedirs(userpath)
        with open(userpath+'/' + universe_name + '.csv', 'wb') as f:
            f.close
        new_tree = Lists_Tree()
        new_tree.child_id =new_universe.id
        new_tree.child_name = universe_name
        new_tree.child_type = 2
        new_tree.parent_id = parent_folder_id
        new_tree.user = request.user
        new_tree.save()
        return redirect("tools:lists_manage_universe", id=new_universe.id)
    folders = Lists_Folder.objects.all().filter(user = request.user)
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = LcreateTree(0,[], tree_list)
    ctx = {
        'folders': folders,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/lists/create_universe.html', ctx)

def LUploadUniverse(request):
    if request.POST:
        time.sleep(1)
        form = ListForm(request.POST, request.FILES)
        if form.is_valid():
            universe = form.save()
            with open(settings.BASE_DIR + universe.file.url, 'r') as f:
                reader = csv.reader(f)
                next(reader, None)
                instruments = list(reader)
                filename = universe.file.name
                universe.title = filename.split('.')[0].split('/')[-1]
                universe.count = len(instruments)
                universe.save()
            data = {'is_valid': True}
        else:
            data = {'is_valid': False}
        if not Lists_Tree.objects.all().filter(child_type=1, permission=1).exists():
            default_folder = Lists_Tree()
            default_folder.child_id = 26
            default_folder.child_name = "Default Folder"
            default_folder.child_type = 1
            default_folder.parent_id = 0
            default_folder.user = request.user
            default_folder.permission = 1
            default_folder.save()
        default_folder = get_object_or_404(Lists_Tree, child_type=1, permission=1)
        default_Lists_Tree = Lists_Tree()
        default_Lists_Tree.child_id = universe.id
        default_Lists_Tree.child_name = universe.title
        default_Lists_Tree.child_type = 2
        default_Lists_Tree.parent_id = default_folder.child_id
        default_Lists_Tree.user = request.user
        default_Lists_Tree.permission = 1
        default_Lists_Tree.save()        
        return JsonResponse(data)

def LDeleteUniverse_default(request):
    lists_default = get_object_or_404(Lists_Default, id=request.POST.get("id"))
    os.remove(settings.BASE_DIR + lists_default.file.url)
    lists_default.delete()
    lists_default_tree = get_object_or_404(Lists_Tree, child_id=request.POST.get("id"), child_type=2, permission=1)
    lists_default_tree.delete()
    return redirect("tools:lists_manage_universes_default")

def LDeleteUniverse(request):
    universe_id = request.POST.get("id")
    universe = get_object_or_404(Lists_Universe, id=universe_id)
    universe_path = settings.LISTS  + str(request.user) + '/' +Lget_path(universe.parent_id)
    os.remove(universe_path + universe.name + '.csv')
    universe.delete()
    lists_tree = get_object_or_404(Lists_Tree, child_id = universe_id, child_type=2)
    lists_tree.delete()
    return redirect("tools:lists_manage_universes_default")

def LManageUniverse_default(request):
    parent_universes = []
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = LcreateTree(0,[], tree_list)
    default_universes = Universe_Default.objects.all()
    if Lists_Universe.objects.filter(parent_id=0,user=request.user).exists():
        universe = Lists_Universe.objects.filter(parent_id=0, user=request.user).first()
        user_universes = Universe_Universe.objects.filter(user=request.user)
        for default_universe in default_universes:
            parent_universes.append({
                'type': 1,
                'universe': default_universe,
            })
        for user_universe in user_universes:
            parent_universes.append({
                'type': 0,
                'universe': user_universe,
            })
        universe_path = settings.LISTS+ str(request.user) + '/'  + Lget_path(universe.parent_id)
        with open(universe_path + universe.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments = list(reader)
        ctx = {
            'title': Lget_path(universe.parent_id) + universe.name,
            'universe': universe,
            'instruments': instruments,
            'tree_structure': tree_structure,
            'parent_universes': parent_universes,            
        }
    else:
        ctx = {
            'error_message': 'no universe',
            'tree_structure': tree_structure,
        }
    return render(request, 'tools/lists/manage_universe.html', ctx)

def LAddInstrument_default(request, id):
    symbol = request.POST.get("symbol")
    name = request.POST.get("name")
    lists_default = get_object_or_404(Lists_Default, id=id)
    lists_default.count += 1
    lists_default.save()
    header = ['Ticker', 'Name']
    instrument = {
        'Ticker': symbol,
        'Name': name,
    }
    with open(settings.BASE_DIR + lists_default.file.url, 'a', ) as f:        
        w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
        if f.tell() == 0:
            w.writeheader()
        w.writerow(instrument)
    return redirect("tools:lists_manage_default_universe", id=id)

def LAddInstrumenttoUniverse(request):
    universe_id = request.POST.get("universe_id")
    universe = get_object_or_404(Lists_Universe, id=universe_id)
    universe_path = settings.LISTS+ str(request.user) + '/'  + Lget_path(universe.parent_id)
    instruments = json.loads(request.POST.get("selectedInstrument"))
    header = ['Ticker', 'Name']
    for instrument in instruments:
        symbol = instrument[0]
        name = instrument[1]
        instrument = {
            'Ticker': symbol,
            'Name': name,
        }
        with open(universe_path + universe.name + '.csv', 'a', ) as f:        
            w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
            if f.tell() == 0:
                w.writeheader()
            w.writerow(instrument)
    universe.count += len(instruments)
    universe.save()
    return HttpResponse("success")

def LDeleteInstrument_default(request, id):
    lists_default = get_object_or_404(Lists_Default, id=id)
    symbol = request.POST.get("symbol")
    data_universe = pd.read_csv(settings.BASE_DIR + lists_default.file.url, index_col="Ticker")
    data_universe.drop([symbol], inplace=True)
    data_universe.to_csv(settings.BASE_DIR + lists_default.file.url)
    lists_default.count += -1
    lists_default.save()
    return redirect("tools:lists_manage_default_universe", id=id)

def LManageUniverse(request, id):
    parent_universes = []
    universe = get_object_or_404(Lists_Universe, id=id)
    user_universes = Universe_Universe.objects.filter(user=request.user)
    default_universes = Universe_Default.objects.all()
    universe_path = settings.LISTS + str(request.user) + '/'  + Lget_path(universe.parent_id)
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = LcreateTree(0,[], tree_list)
    for default_universe in default_universes:
        parent_universes.append({
            'type': 1,
            'universe': default_universe,
        })
    for user_universe in user_universes:
        parent_universes.append({
            'type': 0,
            'universe': user_universe,
        })
    with open(universe_path + universe.name + '.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        instruments = list(reader)
    ctx = {
        'title': Lget_path(universe.parent_id) + universe.name,
        'universe': universe,
        'instruments': instruments,
        'tree_structure': tree_structure,
        'parent_universes': parent_universes
    }
    return render(request, 'tools/lists/manage_universe.html', ctx)

def LManageDefaultUniverse(request, id):
    universe = get_object_or_404(Lists_Default, id=id)
    universes = Lists_Universe.objects.all()
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = LcreateTree(0,[], tree_list)
    with open(settings.BASE_DIR + universe.file.url, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        instruments = list(reader)
    ctx = {
        'title': universe.filename,
        'universe': universe,
        'instruments': instruments,
        'tree_structure': tree_structure,
    }
    return render(request, 'tools/lists/manage_universe_default.html', ctx)

def LAddInstrument(request, id):
    universe = get_object_or_404(Lists_Universe, id=id)
    if request.POST:
        universe.count += 1
        universe.save()
        symbol = request.POST.get("symbol")
        name = request.POST.get("name")
        universe_path = settings.LISTS + str(request.user) + '/'  + Lget_path(universe.parent_id)
        header = ['Ticker', 'Name']
        instrument = {
            'Ticker': symbol,
            'Name': name,
        }
        with open(universe_path + universe.name + '.csv', 'a', ) as f:        
            w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
            if f.tell() == 0:
                w.writeheader()
            w.writerow(instrument)
        return redirect("tools:lists_manage_universe", id=id)
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = LcreateTree(0,[], tree_list)
    ctx = {
        'universe': universe,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/lists/add_instrument.html', ctx)

# def InsertInstrument(request):
#     universe_id = request.POST.get("universe_id")
#     universe = get_object_or_404(Lists_Universe, id=universe_id)
#     universe.count += 1
#     universe.save()
#     symbol = request.POST.get("instrument_symbol")
#     name = request.POST.get("instrument_name")
#     universe_path = settings.UNIVERSES+ str(request.user) + '/'  + Lget_path(universe.parent_id)
#     header = ['Ticker', 'Name']
#     instrument = {
#         'Ticker': symbol,
#         'Name': name,
#     }
#     with open(universe_path + universe.name + '.csv', 'a', ) as f:        
#         w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
#         if f.tell() == 0:
#             w.writeheader()
#         w.writerow(instrument)
#     return redirect("tools:lists_manage_universe", id=universe_id)

# def UpdateInstrument(request):
#     universe_id = request.POST.get("update_id")
#     original_symbol = request.POST.get("original_symbol")
#     symbol = request.POST.get("update_symbol")
#     name = request.POST.get("update_name")
#     instrument = {
#         'Ticker': symbol,
#         'Name': name,
#     }
#     universe = get_object_or_404(Lists_Universe, id=universe_id)
#     universe_path = settings.UNIVERSES+ str(request.user) + '/'  + Lget_path(universe.parent_id)
#     data_universe = pd.read_csv(universe_path + universe.name + '.csv',index_col="Ticker")
#     data_universe = data_universe.replace(data_universe.loc[original_symbol], instrument)
#     data_universe.to_csv(universe_path + universe.name + '.csv',)
#     return redirect("tools:lists_manage_universe", id=universe_id)
    

def LDeleteInstrument(request):
    symbol = request.POST.get("symbol")
    universe_id = request.POST.get("id")
    universe = get_object_or_404(Lists_Universe, id=universe_id)
    universe_path = settings.LISTS+ str(request.user) + '/'  + Lget_path(universe.parent_id)
    data_universe = pd.read_csv(universe_path + universe.name + '.csv', index_col="Ticker")
    data_universe.drop([symbol], inplace=True)
    data_universe.to_csv(universe_path + universe.name + '.csv',)
    universe.count += -1
    universe.save()
    return redirect("tools:lists_manage_universe", id=universe_id)

def LBooleanOperation(request):
    if request.POST:
        instrument_1_set = set()
        instrument_2_set = set()
        universe_1_id = request.POST.get("universe_1")
        universe_2_id = request.POST.get("universe_2")
        operation = request.POST.get("operation")
        new_universe_name = request.POST.get("universe_name")
        parent_folder_id = request.POST.get("parent_id")
        universe_1 = get_object_or_404(Lists_Universe, id=universe_1_id)
        universe_1_path = settings.LISTS + str(request.user) + '/'  + Lget_path(universe_1.parent_id)
        with open(universe_1_path + universe_1.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments_1 = list(reader)
        for instrument_1 in instruments_1:
            instrument_1_set.add(instrument_1[0] + '#' + instrument_1[1])
        universe_2 = get_object_or_404(Lists_Universe, id=universe_2_id)
        universe_2_path = settings.LISTS + str(request.user) + '/'  + Lget_path(universe_2.parent_id)
        with open(universe_2_path + universe_2.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments_2 = list(reader)
        for instrument_2 in instruments_2:
            instrument_2_set.add(instrument_2[0] + '#' + instrument_2[1])
        if operation == '0':
            result_instrument = instrument_1_set.union(instrument_2_set)
        if operation == '1':
            result_instrument = instrument_1_set.difference(instrument_2_set)
        if operation == '2':
            result_instrument = instrument_1_set.intersection(instrument_2_set)
        new_universe = Lists_Universe()
        new_universe.name = new_universe_name
        new_universe.user = request.user
        new_universe.parent_id = parent_folder_id
        new_universe.parent_path = Lget_path(int(parent_folder_id))
        new_universe.save()
        relative_path = Lget_path(int(parent_folder_id))
        userpath = settings.LISTS +str(request.user) + '/' + relative_path
        header = ['Ticker', 'Name']
        if not os.path.exists(userpath):
            os.makedirs(userpath)
        with open(userpath+'/' + new_universe_name + '.csv', 'wb') as f:
            f.close
        with open(userpath+'/' + new_universe_name + '.csv', 'a') as f:
            w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
            if f.tell() == 0:
                w.writeheader()
            for element in result_instrument:
                insert_instrument = {
                    'Ticker': element.split('#')[0],
                    'Name': element.split('#')[1],
                }
                new_universe.count += 1
                w.writerow(insert_instrument)
            new_universe.save()
            f.close
        new_tree = Lists_Tree()
        new_tree.child_id =new_universe.id
        new_tree.child_name = new_universe_name
        new_tree.child_type = 2
        new_tree.parent_id = parent_folder_id
        new_tree.user = request.user
        new_tree.save()
        return redirect("tools:lists_manage_universe", id=new_universe.id)
    parent_universes = []
    tree_list = Lget_tree_list(request.user.id)
    tree_structure = createTree(0,[], tree_list)
    # default_universes = Universe_Default.objects.all()
    user_universes = Lists_Universe.objects.all().filter(user=request.user)
    folders = Lists_Folder.objects.all().filter(user = request.user)
    # for default_universe in default_universes:
    #     parent_universes.append({
    #         'type': 1,
    #         'universe': default_universe,
    #     })
    for user_universe in user_universes:
        parent_universes.append({
            'type': 0,
            'universe': user_universe,
        }) 
    ctx = {
        'parent_universes': parent_universes,
        'tree_structure': tree_structure,
        'folders': folders,
    }
    return render(request, "tools/lists/boolean_operation.html", ctx)

def Lajax_get_instrument_of_universe(request):
    universe_id = request.GET.get("id")
    universe_type = request.GET.get("type")
    if universe_type == "1":
        universe = get_object_or_404(Lists_Default, id=universe_id)
        with open(settings.BASE_DIR + universe.file.url, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments = list(reader)
    elif universe_type == "0":
        universe = get_object_or_404(Lists_Universe, id=universe_id)
        universe_path = settings.LISTS+ str(request.user) + '/'  + Lget_path(universe.parent_id)
        with open(universe_path + universe.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments = list(reader)
    json_data = json.dumps(instruments)
    return HttpResponse(json_data, content_type='application/json')


#BENCHMARKS VIEW

def Bget_path(parent_folder_id):
    if parent_folder_id == 0:
        return ""
    else:
        folder_element = get_object_or_404(Benchmarks_Folder, id=parent_folder_id)
        return folder_element.path

def Bget_tree_list(id):
    tree_list = []
    list_item = {}
    get_default_list = Benchmarks_Tree.objects.all().filter(permission=1)
    for element in get_default_list:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission,
        }
        tree_list.append(list_item)
    get_tree_lists = Benchmarks_Tree.objects.all().filter(user_id=id, permission=0)
    for element in get_tree_lists:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission,
        }
        tree_list.append(list_item)
    return tree_list       

def BcreateTree(parent_id, PushData, data):
    for data_element in data:
        if data_element["parent_id"] == parent_id:
            children = []
            if data_element["child_type"] == 1 and data_element["permission"] == 1:
                 PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": BcreateTree(data_element["child_id"], children, data)
                    }
                )
            elif data_element["child_type"] == 1 and data_element["permission"] == 0:
                PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": BcreateTree(data_element["child_id"], children, data)
                    }
                )
            elif data_element["child_type"] ==2 and data_element["permission"] == 1:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })
            elif data_element["child_type"] ==2 and data_element["permission"] == 0:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })
    return PushData

def Bajax_get_treeelement(request):
    tree_id = request.GET.get("id")
    tree_element = get_object_or_404(Benchmarks_Tree, id=tree_id)
    msg = {
        "child_type": tree_element.child_type,
        "child_id": tree_element.child_id,
        "permission": tree_element.permission,
    }
    json_data = json.dumps(msg)
    return HttpResponse(json_data, content_type='application/json')

def BManageUniverses_default(request):
    universe_lists = Benchmarks_Default.objects.all()
    tree_list = Bget_tree_list(request.user.id)
    tree_structure = BcreateTree(0,[], tree_list)
    ctx = {
        'top_folder': 'true',
        'title': 'Default Benchmarks',
        'universe_lists': universe_lists,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/benchmarks/manage_universes.html', ctx)

def BManageUniverses(request, id):
    universe_lists = Benchmarks_Universe.objects.all().filter(parent_id=id, user=request.user)
    if id  :
        folder = get_object_or_404(Benchmarks_Folder, id=id)
    tree_list = Bget_tree_list(request.user.id)
    tree_structure = BcreateTree(0,[], tree_list)
    if id :
        ctx = {
            'title': folder.path + folder.name,
            'tree_structure': tree_structure,
            'universe_lists': universe_lists,
        }
    else:
       ctx = {
            'title': "Top Folder",
            'tree_structure': tree_structure,
            'universe_lists': universe_lists,
        } 
    return render(request, 'tools/benchmarks/manage_universes.html', ctx)

def BCreateFolder(request):
    if request.POST:
        new_folder = Benchmarks_Folder()
        new_folder.name = request.POST.get("folder_name")        
        new_folder.user = request.user
        new_folder.parent_id = request.POST.get("parent_id")
        if request.POST.get("parent_id") == '0':
            new_folder.path = request.POST.get("folder_name") + '/'  
        else:
            parent_folder = get_object_or_404(Benchmarks_Folder, id=request.POST.get("parent_id"))
            new_folder.path = parent_folder.path + request.POST.get("folder_name") + '/'
        new_folder.save()
        new_tree = Benchmarks_Tree()
        new_tree.child_id =new_folder.id
        new_tree.child_name = new_folder.name
        new_tree.child_type = 1
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect("tools:benchmarks_manage_universes", id=new_folder.id)
    tree_list = Bget_tree_list(request.user.id)
    tree_structure = BcreateTree(0,[], tree_list)
    folders = Benchmarks_Folder.objects.all().filter(user = request.user)
    ctx = {
        'tree_structure': tree_structure,
        'folders': folders
    }
    return render(request, 'tools/benchmarks/create_folder.html', ctx)

def BDeleteFolder(request):
    tree_list = Bget_tree_list(request.user.id)
    tree_structure = BcreateTree(0,[], tree_list)
    folders = Benchmarks_Folder.objects.all().filter(user = request.user)
    if request.POST:
        folder_id = request.POST.get("folder_id")
        if Benchmarks_Tree.objects.all().filter(parent_id=folder_id, user = request.user).exists():
            ctx = {
                'tree_structure': tree_structure,
                'folders': folders,
                'error_message': "Not Empty Folder"
            }
            return render(request, 'tools/benchmarks/delete_folder.html', ctx)
        else:
            folder = get_object_or_404(Benchmarks_Folder, id=folder_id)
            folder.delete()
            tree = get_object_or_404(Benchmarks_Tree, child_id=folder_id, child_type=1)
            tree.delete()
            return redirect("tools:benchmarks_manage_universes_default")
    ctx = {
            'tree_structure': tree_structure,
            'folders': folders
    }
    return render(request, 'tools/benchmarks/delete_folder.html', ctx)

def BCreateUniverse(request):
    if request.POST:
        universe_name = request.POST.get("universe_name")
        parent_folder_id = request.POST.get("parent_id")
        new_universe = Benchmarks_Universe()
        new_universe.name = universe_name
        new_universe.user = request.user
        new_universe.parent_id = parent_folder_id
        new_universe.parent_path = Bget_path(int(parent_folder_id))
        new_universe.save()
        relative_path = Bget_path(int(parent_folder_id))
        userpath = settings.BENCHMARKS +str(request.user) + '/' + relative_path
        if not os.path.exists(userpath):
            os.makedirs(userpath)
        with open(userpath+'/' + universe_name + '.csv', 'wb') as f:
            f.close
        new_tree = Benchmarks_Tree()
        new_tree.child_id =new_universe.id
        new_tree.child_name = universe_name
        new_tree.child_type = 2
        new_tree.parent_id = parent_folder_id
        new_tree.user = request.user
        new_tree.save()
        return redirect("tools:benchmarks_manage_universe", id=new_universe.id)
    folders = Benchmarks_Folder.objects.all().filter(user = request.user)
    tree_list = Bget_tree_list(request.user.id)
    tree_structure = BcreateTree(0,[], tree_list)
    ctx = {
        'folders': folders,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/benchmarks/create_universe.html', ctx)

def BUploadUniverse(request):
    if request.POST:
        time.sleep(1)
        form = BenchmarkForm(request.POST, request.FILES)
        if form.is_valid():
            universe = form.save()
            with open(settings.BASE_DIR + universe.file.url, 'r') as f:
                reader = csv.reader(f)
                next(reader, None)
                instruments = list(reader)
                filename = universe.file.name
                universe.title = filename.split('.')[0].split('/')[-1]
                universe.count = len(instruments)
                universe.save()
            data = {'is_valid': True}
        else:
            data = {'is_valid': False}
        if not Benchmarks_Tree.objects.all().filter(child_type=1, permission=1).exists():
            default_folder = Benchmarks_Tree()
            default_folder.child_id = 26
            default_folder.child_name = "Default Folder"
            default_folder.child_type = 1
            default_folder.parent_id = 0
            default_folder.user = request.user
            default_folder.permission = 1
            default_folder.save()
        default_folder = get_object_or_404(Benchmarks_Tree, child_type=1, permission=1)
        default_Benchmarks_Tree = Benchmarks_Tree()
        default_Benchmarks_Tree.child_id = universe.id
        default_Benchmarks_Tree.child_name = universe.title
        default_Benchmarks_Tree.child_type = 2
        default_Benchmarks_Tree.parent_id = default_folder.child_id
        default_Benchmarks_Tree.user = request.user
        default_Benchmarks_Tree.permission = 1
        default_Benchmarks_Tree.save()        
        return JsonResponse(data)

def BDeleteUniverse_default(request):
    benchmarks_default = get_object_or_404(Benchmarks_Default, id=request.POST.get("id"))
    os.remove(settings.BASE_DIR + benchmarks_default.file.url)
    benchmarks_default.delete()
    benchmarks_default = get_object_or_404(Benchmarks_Tree, child_id=request.POST.get("id"), permission=1, child_type=2)
    benchmarks_default.delete()
    return redirect("tools:benchmarks_manage_universes_default")

def BDeleteUniverse(request):
    universe_id = request.POST.get("id")
    universe = get_object_or_404(Benchmarks_Universe, id=universe_id)
    universe_path = settings.BENCHMARKS  + str(request.user) + '/' +Bget_path(universe.parent_id)
    os.remove(universe_path + universe.name + '.csv')
    universe.delete()
    benchmarks_tree = get_object_or_404(Benchmarks_Tree, child_id = universe_id, child_type=2)
    benchmarks_tree.delete()
    return redirect("tools:benchmarks_manage_universes_default")

def BManageUniverse_default(request):
    parent_universes = []
    tree_list = Bget_tree_list(request.user.id)
    tree_structure = BcreateTree(0,[], tree_list)
    default_universes = Universe_Default.objects.all()
    if Benchmarks_Universe.objects.filter(parent_id=0,user=request.user).exists():
        universe = Benchmarks_Universe.objects.filter(parent_id=0, user=request.user).first()
        user_universes = Universe_Universe.objects.filter(user=request.user)
        for default_universe in default_universes:
            parent_universes.append({
                'type': 1,
                'universe': default_universe,
            })
        for user_universe in user_universes:
            parent_universes.append({
                'type': 0,
                'universe': user_universe,
            })
        universe_path = settings.BENCHMARKS+ str(request.user) + '/'  + Bget_path(universe.parent_id)
        with open(universe_path + universe.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments = list(reader)
        ctx = {
            'title': Bget_path(universe.parent_id) + universe.name,
            'universe': universe,
            'instruments': instruments,
            'tree_structure': tree_structure,
            'parent_universes': parent_universes,            
        }
    else:
        ctx = {
            'error_message': 'no universe',
            'tree_structure': tree_structure,
        }
    return render(request, 'tools/benchmarks/manage_universe.html', ctx)

def BAddInstrument_default(request, id):
    symbol = request.POST.get("symbol")
    name = request.POST.get("name")
    benchmarks_default = get_object_or_404(Benchmarks_Default, id=id)
    benchmarks_default.count += 1
    benchmarks_default.save()
    header = ['Ticker', 'Name']
    instrument = {
        'Ticker': symbol,
        'Name': name,
    }
    with open(settings.BASE_DIR + benchmarks_default.file.url, 'a', ) as f:        
        w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
        if f.tell() == 0:
            w.writeheader()
        w.writerow(instrument)
    return redirect("tools:benchmarks_manage_default_universe", id=id)

def BAddInstrumenttoUniverse(request):
    universe_id = request.POST.get("universe_id")
    universe = get_object_or_404(Benchmarks_Universe, id=universe_id)
    universe_path = settings.BENCHMARKS+ str(request.user) + '/'  + Bget_path(universe.parent_id)
    instruments = json.loads(request.POST.get("selectedInstrument"))
    header = ['Ticker', 'Name']
    for instrument in instruments:
        symbol = instrument[0]
        name = instrument[1]
        instrument = {
            'Ticker': symbol,
            'Name': name,
        }
        with open(universe_path + universe.name + '.csv', 'a', ) as f:        
            w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
            if f.tell() == 0:
                w.writeheader()
            w.writerow(instrument)
    universe.count += len(instruments)
    universe.save()
    return HttpResponse("success")

def BDeleteInstrument_default(request, id):
    benchmarks_default = get_object_or_404(Benchmarks_Default, id=id)
    symbol = request.POST.get("symbol")
    data_universe = pd.read_csv(settings.BASE_DIR + benchmarks_default.file.url, index_col="Ticker")
    data_universe.drop([symbol], inplace=True)
    data_universe.to_csv(settings.BASE_DIR + benchmarks_default.file.url)
    benchmarks_default.count += -1
    benchmarks_default.save()
    return redirect("tools:benchmarks_manage_default_universe", id=id)

def BManageUniverse(request, id):
    parent_universes = []
    universe = get_object_or_404(Benchmarks_Universe, id=id)
    user_universes = Universe_Universe.objects.filter(user=request.user)
    default_universes = Universe_Default.objects.all()
    universe_path = settings.BENCHMARKS + str(request.user) + '/'  + Bget_path(universe.parent_id)
    tree_list = Bget_tree_list(request.user.id)
    tree_structure = BcreateTree(0,[], tree_list)
    for default_universe in default_universes:
        parent_universes.append({
            'type': 1,
            'universe': default_universe,
        })
    for user_universe in user_universes:
        parent_universes.append({
            'type': 0,
            'universe': user_universe,
        })
    with open(universe_path + universe.name + '.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        instruments = list(reader)
    ctx = {
        'title': Bget_path(universe.parent_id) + universe.name,
        'universe': universe,
        'instruments': instruments,
        'tree_structure': tree_structure,
        'parent_universes': parent_universes
    }
    return render(request, 'tools/benchmarks/manage_universe.html', ctx)

def BManageDefaultUniverse(request, id):
    universe = get_object_or_404(Benchmarks_Default, id=id)
    universes = Benchmarks_Universe.objects.all()
    tree_list = Bget_tree_list(request.user.id)
    tree_structure = BcreateTree(0,[], tree_list)
    with open(settings.BASE_DIR + universe.file.url, 'r') as f:
        reader = csv.reader(f)
        next(reader, None)
        instruments = list(reader)
    ctx = {
        'title': universe.filename,
        'universe': universe,
        'instruments': instruments,
        'tree_structure': tree_structure,
    }
    return render(request, 'tools/benchmarks/manage_universe_default.html', ctx)

def BAddInstrument(request, id):
    universe = get_object_or_404(Benchmarks_Universe, id=id)
    if request.POST:
        universe.count += 1
        universe.save()
        symbol = request.POST.get("symbol")
        name = request.POST.get("name")
        universe_path = settings.BENCHMARKS + str(request.user) + '/'  + Bget_path(universe.parent_id)
        header = ['Ticker', 'Name']
        instrument = {
            'Ticker': symbol,
            'Name': name,
        }
        with open(universe_path + universe.name + '.csv', 'a', ) as f:        
            w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
            if f.tell() == 0:
                w.writeheader()
            w.writerow(instrument)
        return redirect("tools:benchmarks_manage_universe", id=id)
    tree_list = Bget_tree_list(request.user.id)
    tree_structure = BcreateTree(0,[], tree_list)
    ctx = {
        'universe': universe,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/benchmarks/add_instrument.html', ctx)

# def InsertInstrument(request):
#     universe_id = request.POST.get("universe_id")
#     universe = get_object_or_404(Benchmarks_Universe, id=universe_id)
#     universe.count += 1
#     universe.save()
#     symbol = request.POST.get("instrument_symbol")
#     name = request.POST.get("instrument_name")
#     universe_path = settings.UNIVERSES+ str(request.user) + '/'  + Bget_path(universe.parent_id)
#     header = ['Ticker', 'Name']
#     instrument = {
#         'Ticker': symbol,
#         'Name': name,
#     }
#     with open(universe_path + universe.name + '.csv', 'a', ) as f:        
#         w = csv.DictWriter(f, lineterminator='\n', fieldnames=header)
#         if f.tell() == 0:
#             w.writeheader()
#         w.writerow(instrument)
#     return redirect("tools:benchmarks_manage_universe", id=universe_id)

# def UpdateInstrument(request):
#     universe_id = request.POST.get("update_id")
#     original_symbol = request.POST.get("original_symbol")
#     symbol = request.POST.get("update_symbol")
#     name = request.POST.get("update_name")
#     instrument = {
#         'Ticker': symbol,
#         'Name': name,
#     }
#     universe = get_object_or_404(Benchmarks_Universe, id=universe_id)
#     universe_path = settings.UNIVERSES+ str(request.user) + '/'  + Bget_path(universe.parent_id)
#     data_universe = pd.read_csv(universe_path + universe.name + '.csv',index_col="Ticker")
#     data_universe = data_universe.replace(data_universe.loc[original_symbol], instrument)
#     data_universe.to_csv(universe_path + universe.name + '.csv',)
#     return redirect("tools:benchmarks_manage_universe", id=universe_id)
    

def BDeleteInstrument(request):
    symbol = request.POST.get("symbol")
    universe_id = request.POST.get("id")
    universe = get_object_or_404(Benchmarks_Universe, id=universe_id)
    universe_path = settings.BENCHMARKS+ str(request.user) + '/'  + Bget_path(universe.parent_id)
    data_universe = pd.read_csv(universe_path + universe.name + '.csv', index_col="Ticker")
    data_universe.drop([symbol], inplace=True)
    data_universe.to_csv(universe_path + universe.name + '.csv',)
    universe.count += -1
    universe.save()
    return redirect("tools:benchmarks_manage_universe", id=universe_id)

def Bajax_get_instrument_of_universe(request):
    universe_id = request.GET.get("id")
    universe_type = request.GET.get("type")
    if universe_type == "1":
        universe = get_object_or_404(Benchmarks_Default, id=universe_id)
        with open(settings.BASE_DIR + universe.file.url, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments = list(reader)
    elif universe_type == "0":
        universe = get_object_or_404(Benchmarks_Universe, id=universe_id)
        universe_path = settings.BENCHMARKS+ str(request.user) + '/'  + Bget_path(universe.parent_id)
        with open(universe_path + universe.name + '.csv', 'r') as f:
            reader = csv.reader(f)
            next(reader, None)
            instruments = list(reader)
    json_data = json.dumps(instruments)
    return HttpResponse(json_data, content_type='application/json')


#RANK SYSTEM

def Rget_path(parent_folder_id):
    if parent_folder_id == 0:
        return ""
    else:
        folder_element = get_object_or_404( Ranking_Folder, id=parent_folder_id)
        return folder_element.path

def Rget_tree_list(user_id):
    tree_list = []
    list_item = {}
    get_default_trees = Ranking_Tree.objects.all().filter(permission=1)
    for element in get_default_trees:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission,
        }
        tree_list.append(list_item)    
    get_tree_lists = Ranking_Tree.objects.all().filter(user_id=user_id, permission=0)
    for element in get_tree_lists:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission,
        }
        tree_list.append(list_item)
    return tree_list      

def RcreateTree(parent_id, PushData, data):
    for data_element in data:
        if data_element["parent_id"] == parent_id:
            children = []
            if data_element["child_type"] == 1 and data_element["permission"] == 1:
                PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": RcreateTree(data_element["child_id"], children, data)
                    }
                )
            elif data_element["child_type"] == 1 and data_element["permission"] == 0:
                PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": RcreateTree(data_element["child_id"], children, data)
                    }
                )
            elif data_element["child_type"] == 2 and data_element["permission"] == 1:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })
            elif data_element["child_type"] == 2 and data_element["permission"] == 0:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })                
    return PushData

def RManageRankSystems(request):
    return redirect('tools:rank_manage_default_systems')

def RManageRankSystems_folder(request, parent_id):
    ranking_systems = []
    ranking_system_trees = Ranking_Tree.objects.all().filter(user=request.user, child_type=2, parent_id=parent_id)
    for ranking_system_tree in ranking_system_trees:
        ranking_systems.append(get_object_or_404(Ranking_System, id=ranking_system_tree.child_id))
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    folder = Rget_path(parent_id)
    if parent_id == 0:
        ctx = {
            'ranking_systems': ranking_systems,
            'tree_structure': tree_structure,
            'top_folder': 'top folder'
        }
    else:
        ctx = {
            'ranking_systems': ranking_systems,
            'tree_structure': tree_structure,
            'folder': folder,
            'parent_id': parent_id
        }        
    return render(request, 'tools/ranking_system/manage_ranking_systems.html', ctx)

def RAddRankSystem(request):
    form = RankingSystemForm(request.POST or None)
    if form.is_valid():
        ranking_system = form.save()
        ranking_system.user = request.user
        ranking_system.save()
        new_tree = Ranking_Tree()
        new_tree.child_id =ranking_system.id
        new_tree.child_name = ranking_system.name
        new_tree.child_type = 2
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('tools:rank_manage_ranking_system', id=ranking_system.id)
    categories = Ranking_Folder.objects.all().filter(user=request.user)
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    ctx = {
        'form': form,
        'tree_structure': tree_structure,
        'categories': categories
    }
    return render(request, 'tools/ranking_system/add_ranking_system.html', ctx)

def RDeleteRankingSystem(request, id):
    ranking_system = get_object_or_404(Ranking_System, id=id)
    form = RankingSystemForm(request.POST or None, instance=ranking_system)
    if form.is_valid():
        ranking_system.delete()
        ranking_rules = Ranking_Rule.objects.all().filter(rank_id=id)
        for ranking_rule in ranking_rules:
            ranking_rule.delete()
        indicators = Indicator.objects.all().filter(rank_system_id=id).order_by('-id')
        for indicator in indicators:
            indicator.delete()
        rank_tree = get_object_or_404(Ranking_Tree, child_id=id, child_type=2)
        rank_tree.delete()
        return redirect('tools:rank_manage_rank_systems')
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    ctx = {
        'form': form,
        'ranking_system': ranking_system,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/ranking_system/delete_ranking_system.html', ctx)

def RExportRankingSystem(request, id_rank_system, id_parent):
    rank_system = get_object_or_404(Ranking_System, id=id_rank_system)
    rank_system_dict = {}
    indicators = Indicator.objects.filter(rank_system_id=id_rank_system)
    rank_rules = rank_system.rule.all()
    rank_system_dict['name'] = rank_system.name
    rank_system_dict['indicators'] = []
    rank_system_dict['rules'] = []
    rank_system_dict['indicator_combinations'] = []
    for indicator in indicators:
        if str(indicator.polymorphic_ctype) == "indicators_ combination":
            rank_system_dict['indicator_combinations'].append([str(indicator.coeff), str(indicator.indicator1), str(indicator.operator), str(indicator.indicator2)])
        elif str(indicator.polymorphic_ctype) == "ppo":
            rank_system_dict['indicators'].append([indicator.__class__.__name__,str([indicator.period1]),str([indicator.period2]),str([indicator.period3]),str(indicator.input_data),str(indicator.coeff),str(indicator.lag)])            
        else:
            rank_system_dict['indicators'].append([indicator.__class__.__name__,str([indicator.period]),str(indicator.input_data),str(indicator.coeff),str(indicator.lag)])
    for rank_rule in rank_rules:
        rank_system_dict['rules'].append([str(rank_rule.weight),str(rank_rule.name),str(rank_rule.indicator),str(rank_rule.direction)])
    userpath = settings.RANKING_SYSTEM + str(request.user) + '/export/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    with open(userpath + rank_system_dict['name'] + '.pickle', 'wb') as f:
        pickle.dump(rank_system_dict, f, protocol=2)
    f.close
    if id_parent == 999999999999:
        return redirect('tools:rank_manage_default_systems')
    return redirect('tools:rank_manage_rank_systems_folder', parent_id=id_parent)

def RLoadRankingSystem(request):
    load_files = []
    userpath = settings.RANKING_SYSTEM + str(request.user) + '/export/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)      
    if request.POST:
        file_name = request.POST.get("file_name")
        parent_id = request.POST.get("parent_id")
        ranking_system = Ranking_System()
        ranking_system.name = file_name      
        with open(userpath+file_name+'.pickle','rb') as f:
            ranking_system_dict = pickle.load(f)
        ranking_system.save()
        last_ranking_system = Ranking_System.objects.last()
        technicals = []
        for technical in ranking_system_dict['indicators']:
            try:
                if technical[0] == "Ppo":
                    input_data_id = Input_data.objects.get(input_data=technical[4])
                else:
                    input_data_id = Input_data.objects.get(input_data=technical[2])
                try:
                    technicals.append(eval(technical[0])(coeff=technical[3], input_data=input_data_id, lag=technical[4], strategy_id=0, rank_system_id=last_ranking_system.id).save())
                except:
                    if technical[0] == "Ppo":                        
                        technicals.append(eval(technical[0])(coeff=technical[5], period1=technical[1][1:-1],period2=technical[2][1:-1],period3=technical[3][1:-1], input_data=input_data_id, lag=technical[6],strategy_id=0, rank_system_id=last_ranking_system.id).save())    
                    else:
                        technicals.append(eval(technical[0])(coeff=technical[3], period=technical[1][1:-1], input_data=input_data_id, lag=technical[4],strategy_id=0, rank_system_id=last_ranking_system.id).save())
            except:
                technicals.append(eval(technical[0])(coeff=technical[3], strategy_id=0, rank_system_id=last_ranking_system.id).save())            
        for indicator_comb in ranking_system_dict['indicator_combinations']:
            indicator_combinations = Indicators_Combination(strategy_id=0, rank_system_id=last_ranking_system.id)
            tech_coms = Indicator.objects.filter(rank_system_id=last_ranking_system.id)
            indicator1 = ''
            indicator2 = ''
            for tech in tech_coms:
                if indicator_comb[1] == str(tech):
                    indicator1 = tech
                if indicator_comb[3] == str(tech):
                    indicator2 = tech               
            indicator_combinations.coeff = indicator_comb[0]
            indicator_combinations.indicator1 = indicator1
            indicator_combinations.indicator2 = indicator2
            indicator_combinations.operator = indicator_comb[2]
            indicator_combinations.save()                  
        tech_coms = Indicator.objects.filter(rank_system_id=last_ranking_system.id)
        for rank_rule in ranking_system_dict['rules']:
            tech1 = ''
            for tech in tech_coms:
                if rank_rule[2] == str(tech):
                    tech1 = tech
            ranking_system.rule.create(weight=rank_rule[0], name=rank_rule[1], indicator=tech1, direction=rank_rule[3], rank_id=last_ranking_system.id)
        ranking_system.user = request.user
        ranking_system.save()
        if parent_id == "d":
            if not Ranking_Tree.objects.filter(permission=1).exists():
                default_folder = Ranking_Tree()
                default_folder.child_id = -1
                default_folder.child_type = 1
                default_folder.child_name = "Default Folder"
                default_folder.parent_id = 0
                default_folder.user = request.user
                default_folder.permission = 1
                default_folder.save()
            else:
                default_folder = get_object_or_404(Ranking_Tree, permission=1, child_type=1)
            new_tree = Ranking_Tree()
            new_tree.child_id = ranking_system.id
            new_tree.child_name = ranking_system.name
            new_tree.child_type = 2
            new_tree.parent_id = default_folder.child_id
            new_tree.permission = 1
            new_tree.user = request.user
            new_tree.save()
            return redirect('tools:rank_manage_default_systems')            
        new_tree = Ranking_Tree()
        new_tree.child_id = ranking_system.id
        new_tree.child_name = ranking_system.name
        new_tree.child_type = 2
        new_tree.parent_id = parent_id
        new_tree.user = request.user
        new_tree.save()   
        return redirect('tools:rank_manage_ranking_system', id=ranking_system.id)     
    with os.scandir(userpath) as entries:
        for entry in entries:
            if not entry.is_file():
                continue
            filename, file_extension = os.path.splitext(entry.name)
            if file_extension.lower() != ".pickle":
                continue
            load_files.append(filename)
    folders = Ranking_Folder.objects.all().filter(user=request.user)
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0, [], tree_list)
    ctx = {
        'tree_structure': tree_structure,
        'folders': folders,
        'load_files': load_files
    }   
    return render(request, 'tools/ranking_system/load_file_list.html', ctx) 

def RManageRankingSystem(request, id):
    ranking_system = get_object_or_404(Ranking_System, id=id)
    ranking_rules = Ranking_Rule.objects.filter(rank_id=id)
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    indicator_combinations = Indicators_Combination.objects.filter(rank_system_id=id)
    if get_object_or_404(Ranking_Tree, child_id=id, child_type=2).parent_id == -1:
        ctx = {
            'relative_path': 'Default Folder/',
            'ranking_system': ranking_system,
            'ranking_rules': ranking_rules,
            'tree_structure': tree_structure,
            'indicator_combinations': indicator_combinations
        }   
        return render(request, 'tools/ranking_system/manage_ranking_system.html', ctx)     
    relative_path = Rget_path(get_object_or_404(Ranking_Tree, child_id=id, child_type=2, user=request.user).parent_id)
    ctx = {
        'relative_path': relative_path,
        'ranking_system': ranking_system,
        'ranking_rules': ranking_rules,
        'tree_structure': tree_structure,
        'indicator_combinations': indicator_combinations
    }
    return render(request, 'tools/ranking_system/manage_ranking_system.html', ctx)

def RAddRankingRule(request, id):
    if request.POST:
        post = request.POST.copy() # to make it mutable
        technical = post['indicator']
        tech_coms  = Indicator.objects.filter(rank_system_id=id)
        indicator_id = ''
        for tech_com in tech_coms:
            if technical == str(tech_com).lower():
                indicator_id = tech_com.id
        post['indicator'] = indicator_id
        request.POST = post
    instantiate = Ranking_Rule(rank_id=id)
    form = RankingRuleForm(request.POST or None, instance=instantiate)
    ranking_system = get_object_or_404(Ranking_System, id=id)
    if form.is_valid():
        new_rule = form.save()
        ranking_system.rule.add(new_rule)        
        return redirect("tools:rank_manage_ranking_system", id=id)
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    indicator_tree = []
    indicator_tree = getIndicatorTree()
    ctx = {
        'form': form,
        'rank_system_id': id,
        'tree_structure': tree_structure,
        'indicator_tree': indicator_tree,
    }
    return render(request, 'tools/ranking_system/add_ranking_rule.html', ctx)

def RModifyRule(request, id_rank, id_rule):
    if request.POST:
        post = request.POST.copy() # to make it mutable
        technical = post['indicator']
        tech_coms  = Indicator.objects.filter(rank_system_id=id_rank)
        indicator_id = ''
        for tech_com in tech_coms:
            if technical == str(tech_com).lower():
                indicator_id = tech_com.id
        post['indicator'] = indicator_id
        request.POST = post
    ranking_system = get_object_or_404(Ranking_System, id=id_rank)
    rule = get_object_or_404(Ranking_Rule, id=id_rule)
    form = RankingRuleForm(request.POST or None, instance=rule)
    if form.is_valid():
        new_rule = form.save()
        ranking_system.rule.add(new_rule)
        return redirect("tools:rank_manage_ranking_system", id=id_rank)
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    ctx = {
        'form': form,
        'rank_system_id': id_rank,
        'id_rule': id_rule,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/ranking_system/modify_rule.html', ctx)

def RDeleteRule(request):
    id_rule = request.POST.get("id")
    id_rank = request.POST.get("rank_id")
    type = request.POST.get("type")
    if type == "rule":
        rule = get_object_or_404(Ranking_Rule, id=id_rule)
        rule.delete()
    elif type == "combination":
        indicator_combination = get_object_or_404(Indicators_Combination, indicator_ptr_id=id_rule)
        indicator_combination.delete()
    return redirect("tools:rank_manage_ranking_system", id=id_rank)

def ajax_get_tech(request, id_rule, id_rank):
    technical = ''
    rule = get_object_or_404(Ranking_Rule, id=id_rule)
    technical = get_object_or_404(Indicator, id=rule.indicator_id) 
    technical = str(technical)
    return HttpResponse(technical)

def RAddIndicator(request, source, indicator, id_rank):
    instantiate = eval(indicator+"(rank_system_id=id_rank, strategy_id=0)")
    CustomModel = eval(indicator)
    CustomForm = modelform_factory(model=CustomModel, widgets = {
            'input_data': forms.Select(attrs={'class': 'form-control'}),
            'coeff': forms.NumberInput(attrs={'class': 'form-control'}),
            'lag': forms.NumberInput(attrs={'class': 'form-control'}),
            'period': forms.NumberInput(attrs={'class': 'form-control'}),
            'period1': forms.NumberInput(attrs={'class': 'form-control'}),
            'period2': forms.NumberInput(attrs={'class': 'form-control'}),
            'period3': forms.NumberInput(attrs={'class': 'form-control'}),            
        } ,exclude = ('rule_id','strategy_id','rank_system_id','liquidity_system_id','indicator_combination_id'))
    form = CustomForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        form.save()
        if source == 'add':
            return redirect('tools:rank_add_ranking_rule', id=id_rank)
        elif source == 'comb':
            return redirect('tools:rank_add_indicator_combination', id=id_rank)
    indicator_tree = []
    indicator_tree = getIndicatorTree()    
    indicator_property = get_object_or_404(IndicatorProperty, indicator=indicator)
    ctx = {
        'source': source,
        'indicator': indicator,
        'id_rank': id_rank,
        'form': form,
        'indicator_tree': indicator_tree,
        'indicator_property': indicator_property,
    }
    return render(request, 'tools/ranking_system/add_indicator.html', ctx)

def RGetIndicator(request, id_rank):
    indicators = Indicator.objects.filter(rank_system_id=id_rank)
    rule_str = ''
    for indicator in indicators:
        rule_str = rule_str + str(indicator) + ','
    return HttpResponse(rule_str)

def RGetIndicatorAdd(request):    
    techindicator = request.GET.get('techindicator')
    id_rank = request.GET.get('id_rank')
    requestfrom = request.GET.get('from')
    if requestfrom == 'add':
        requestrule = 0
    elif requestfrom == 'modify':
        requestrule = request.GET.get('ruleid')
    indicator = ''
    tech_coms = Indicator.objects.filter(rank_system_id=id_rank)
    tech_id = ''
    for tech_com in tech_coms:
        if techindicator == str(tech_com).lower():
            tech_id = tech_com.id
    instantiate = get_object_or_404(Indicator, id=tech_id)
    indicator_temp = str(instantiate.polymorphic_ctype).replace(' ', '')
    if indicator_temp == "indicators_combination":
        ctx = {
            'id_rank': id_rank,
            'id': tech_id,
            'type': 'combination'
        }
        return render(request, 'tools/ranking_system/delete_indicator_combination.html', ctx)
    indicator_property = IndicatorProperty.objects.all()
    for element in indicator_property:
        if str(element.indicator).lower() == indicator_temp:
            indicator_obj = element
    indicator = str(indicator_obj)
    CustomModel = eval(indicator)
    CustomForm = modelform_factory(model=CustomModel, widgets = {
            'input_data': forms.Select(attrs={'class': 'form-control'}),
            'coeff': forms.NumberInput(attrs={'class': 'form-control'}),
            'lag': forms.NumberInput(attrs={'class': 'form-control'}),
            'period': forms.NumberInput(attrs={'class': 'form-control'}),
            'period1': forms.NumberInput(attrs={'class': 'form-control'}),
            'period2': forms.NumberInput(attrs={'class': 'form-control'}),
            'period3': forms.NumberInput(attrs={'class': 'form-control'}),            
        } ,exclude = ('rule_id','strategy_id','rank_system_id','liquidity_system_id','indicator_combination_id'))
    form = CustomForm(request.POST or None, instance=instantiate)   
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    ctx = {
        'indicator': indicator,
        'tech_id': tech_id,
        'id_rank': id_rank,
        'requestfrom': requestfrom,
        'requestrule': requestrule,
        'form': form,
        'tree_structure': tree_structure,
        'indicator_property': indicator_obj
    }
    return render(request, 'tools/ranking_system/modify_indicator.html', ctx)

def RModifyIndicator(request, indicator, tech_id, id_rank, requestfrom, requestrule):
    instantiate = get_object_or_404(Indicator, id=tech_id)
    CustomModel = eval(indicator)
    CustomForm = modelform_factory(model=CustomModel, widgets = {
            'input_data': forms.Select(attrs={'class': 'form-control'}),
            'coeff': forms.NumberInput(attrs={'class': 'form-control'}),
            'lag': forms.NumberInput(attrs={'class': 'form-control'}),
            'period': forms.NumberInput(attrs={'class': 'form-control'}),
            'period1': forms.NumberInput(attrs={'class': 'form-control'}),
            'period2': forms.NumberInput(attrs={'class': 'form-control'}),
            'period3': forms.NumberInput(attrs={'class': 'form-control'}),            
        } ,exclude = ('rule_id','strategy_id','rank_system_id','liquidity_system_id','indicator_combination_id'))
    form = CustomForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        form.save()
        if requestfrom == 'add':
            return redirect('tools:rank_add_ranking_rule', id=id_rank)
        elif requestfrom == 'modify':
            return redirect("tools:rank_modify_rule", id_rank=id_rank, id_rule=requestrule)  

def RDeleteIndicator(request, tech_id, id_rank, requestfrom, requestrule):
    tech_indicator = get_object_or_404(Indicator, id=tech_id)
    tech_indicator.delete()
    if requestfrom == 'add':
        return redirect('tools:rank_add_ranking_rule', id=id_rank)
    elif requestfrom == 'modify':
        return redirect("tools:rank_manage_ranking_system", id=id_rank)

def RAddIndicatorCombination(request, id):
    instantiate = Indicators_Combination(strategy_id=0,rank_system_id=id)
    if request.POST:
        post = request.POST.copy()
        technical_1 = post['indicator1']
        technical_2 = post['indicator2']
        tech_coms = Indicator.objects.filter(rank_system_id=id)
        tech1_id=''
        tech2_id=''
        for tech_com in tech_coms:
            if technical_1 == str(tech_com).lower():
                tech1_id = tech_com.id
            if technical_2 == str(tech_com).lower():
                tech2_id = tech_com.id
        post['indicator1'] = tech1_id
        post['indicator2'] = tech2_id
        request.POST = post
    form = IndicatorCombinationForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        form.save()
        return redirect('tools:rank_manage_ranking_system', id=id)
    indicator_tree = []
    indicator_tree = getIndicatorTree()  
    ctx = {
        'rank_system_id': id,
        'form': form,
        'indicator_tree': indicator_tree,
    }
    return render(request, 'tools/ranking_system/add_indicator_combination.html', ctx)

def RModifyIndicatorCombination(request, id_system, id_comb):
    instantiate = get_object_or_404(Indicators_Combination, id=id_comb)
    if request.POST:
        post = request.POST.copy()
        technical_1 = post['indicator1']
        technical_2 = post['indicator2']
        tech_coms = Indicator.objects.filter(rank_system_id=id_system)
        tech1_id=''
        tech2_id=''
        for tech_com in tech_coms:
            if technical_1 == str(tech_com).lower():
                tech1_id = tech_com.id
            if technical_2 == str(tech_com).lower():
                tech2_id = tech_com.id
        post['indicator1'] = tech1_id
        post['indicator2'] = tech2_id
        request.POST = post        
    form = IndicatorCombinationForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        form.save()
        return redirect('tools:rank_manage_ranking_system', id=id_system)
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    ctx = {
        'rank_system_id': id_system,
        'form': form,
        'tree_structure': tree_structure,
        'id_comb': id_comb
    }
    return render(request, 'tools/ranking_system/modify_indicator_combination.html', ctx)

def RGetTechs(request, id_comb):
    technical = ''
    indicator_combination = get_object_or_404(Indicators_Combination, indicator_ptr_id=id_comb)
    technical = str(indicator_combination.indicator1) + ',' + str(indicator_combination.indicator2)
    return HttpResponse(technical)

def RGetIndicatorBasic(request, id_system):
    indicators = Indicator.objects.filter(rank_system_id=id_system)
    rule_str = ''
    for indicator in indicators:
        if not str(indicator.polymorphic_ctype) == "indicators_ combination":
            rule_str = rule_str + str(indicator) + ','
    return HttpResponse(rule_str)    

def RCreateFolder(request):
    if request.POST:
        new_category =  Ranking_Folder()
        new_category.name = request.POST.get("category_name")        
        new_category.user = request.user
        if request.POST.get("parent_id") == '0':
            new_category.path = request.POST.get("category_name") + '/'  
        else:
            parent_category = get_object_or_404( Ranking_Folder, id=request.POST.get("parent_id"))
            new_category.path = parent_category.path + request.POST.get("category_name") + '/'
        new_category.save()
        new_tree = Ranking_Tree()
        new_tree.child_id =new_category.id
        new_tree.child_name = new_category.name
        new_tree.child_type = 1
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('tools:rank_manage_rank_systems_folder', parent_id=new_category.id)
    categories =  Ranking_Folder.objects.all().filter(user=request.user)
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    ctx = {
        'categories': categories,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/ranking_system/create_folder.html', ctx)

def RDeleteFolder(request):
    categories =  Ranking_Folder.objects.all().filter(user=request.user)
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    if request.POST: 
        category_id = request.POST.get("id")
        if Ranking_Tree.objects.all().filter(parent_id=category_id).exists():
            ranking_systems = Ranking_System.objects.all().filter(user=request.user)
            ctx = {
                'ranking_systems': ranking_systems,
                'tree_structure': tree_structure,
                'error_message': "Not Empty Folder"
            }
            return redirect('tools:rank_manage_rank_systems_folder', parent_id=0)
        else:
            category = get_object_or_404( Ranking_Folder, id=category_id)
            category.delete()
            tree = get_object_or_404(Ranking_Tree, child_id=category_id, child_type=1)
            tree.delete()
            return redirect("tools:rank_manage_rank_systems")
    ctx = {
        'categories': categories,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/ranking_system/delete_folder.html', ctx)

def RGetRankData(request):
    tree_id = request.GET.get("id")
    tree_element = get_object_or_404(Ranking_Tree, id=tree_id)
    msg = {
        "child_type": tree_element.child_type,
        "child_id": tree_element.child_id,
        "permission": tree_element.permission,
    }
    json_data = json.dumps(msg)
    return HttpResponse(json_data, content_type='application/json')

def RManageDefaultSystems(request):
    ranking_systems = []
    ranking_system_trees = Ranking_Tree.objects.all().filter(child_type=2, parent_id=-1, permission=1)
    for ranking_system_tree in ranking_system_trees:
        ranking_systems.append(get_object_or_404(Ranking_System, id=ranking_system_tree.child_id))   
    tree_list = Rget_tree_list(request.user)
    tree_structure = RcreateTree(0,[],tree_list)
    folder = 'Default Folder'
    ctx = {
        'ranking_systems': ranking_systems,
        'tree_structure': tree_structure,
        'folder': folder
    }
    return render(request, 'tools/ranking_system/manage_default_systems.html', ctx)             

#LIQUIDTY SYSTEM 

def LSget_path(parent_folder_id):
    if parent_folder_id == 0:
        return ""
    else:
        folder_element = get_object_or_404( Liquidity_Folder, id=parent_folder_id)
        return folder_element.path

def LSget_tree_list(user_id):
    tree_list = []
    list_item = {}
    get_default_trees = Liquidity_Tree.objects.all().filter(permission=1)
    for element in get_default_trees:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission
        }
        tree_list.append(list_item)        
    get_tree_lists = Liquidity_Tree.objects.all().filter(user_id=user_id, permission=0)
    for element in get_tree_lists:
        list_item = {
            "id": element.id,
            "child_id": element.child_id,
            "child_name": element.child_name,
            "parent_id": element.parent_id,
            "child_type": element.child_type,
            "permission": element.permission,
        }
        tree_list.append(list_item)
    return tree_list      

def LScreateTree(parent_id, PushData, data):
    for data_element in data:
        if data_element["parent_id"] == parent_id:
            children = []
            if data_element["child_type"] == 1 and data_element["permission"] == 1:
                PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": LScreateTree(data_element["child_id"], children, data)
                    }
                )
            elif data_element["child_type"] == 1 and data_element["permission"] == 0:
                PushData.append(
                    {
                        "id": data_element["id"],
                        "text": data_element["child_name"],
                        "state": {
                            "opened": 1
                        },
                        "children": LScreateTree(data_element["child_id"], children, data)
                    }
                )                
            elif data_element["child_type"] == 2 and data_element["permission"] == 1:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })
            elif data_element["child_type"] == 2 and data_element["permission"] == 0:
                PushData.append({
                    "id": data_element["id"],
                    "icon": "fa fa-plus",
                    "text": data_element["child_name"],
                    "state": {
                        "opened": 1
                    },
                    "children": []
                })                
    return PushData

def LSManageLiquiditySystems(request):
    return redirect('tools:liquidity_manage_default_systems')

def LSManageLiquiditySystems_folder(request, parent_id):
    liquidity_systems = []
    liquidity_system_trees = Liquidity_Tree.objects.all().filter(user=request.user, child_type=2, parent_id=parent_id)
    for liquidity_system_tree in liquidity_system_trees:
        liquidity_systems.append(get_object_or_404(Liquidity_System, id=liquidity_system_tree.child_id))
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0, [], tree_list)
    folder = LSget_path(parent_id)
    if parent_id == 0:
        ctx = {
            'liquidity_systems': liquidity_systems,
            'tree_structure': tree_structure,
            'top_folder': 'top folder',
        }
    else:
        ctx = {
            'liquidity_systems': liquidity_systems,
            'tree_structure': tree_structure,
            'folder': folder,
            'parent_id':parent_id
        }
    return render(request, 'tools/liquidity_system/manage_liquidity_systems.html', ctx)

def LSAddLiquiditySystem(request):
    form = LiquiditySystemForm(request.POST or None)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0, [], tree_list)
    folders =  Liquidity_Folder.objects.all().filter(user=request.user)
    if form.is_valid():
        liquidity_system = form.save()
        liquidity_system.user = request.user
        liquidity_system.save()
        new_tree = Liquidity_Tree()
        new_tree.child_id =liquidity_system.id
        new_tree.child_name = liquidity_system.name
        new_tree.child_type = 2
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('tools:liquidity_manage_liquidity_system', id=liquidity_system.id)
    ctx = {
        'form': form,
        'tree_structure': tree_structure,
        'folders': folders
    }
    return render(request, 'tools/liquidity_system/add_liquidity_system.html', ctx)

def LSCreateFolder(request):
    if request.POST:
        new_folder =  Liquidity_Folder()
        new_folder.name = request.POST.get("category_name")        
        new_folder.user = request.user
        if request.POST.get("parent_id") == '0':
            new_folder.path = request.POST.get("category_name") + '/'  
        else:
            parent_category = get_object_or_404( Liquidity_Folder, id=request.POST.get("parent_id"))
            new_folder.path = parent_category.path + request.POST.get("category_name") + '/'
        new_folder.save()
        new_tree = Liquidity_Tree()
        new_tree.child_id =new_folder.id
        new_tree.child_name = new_folder.name
        new_tree.child_type = 1
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('tools:liquidity_manage_liquidity_system_folder' ,parent_id=new_folder.id)
    folders = Liquidity_Folder.objects.all().filter(user=request.user)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0, [], tree_list)
    ctx = {
        'folders': folders,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/liquidity_system/create_folder.html', ctx)

def LSExportLiquiditySystem(request, id_system, id_parent):
    liquidity_system = get_object_or_404(Liquidity_System, id=id_system)
    liquidity_system_dict = {}
    indicators = Indicator.objects.filter(liquidity_system_id=id_system)
    rules = liquidity_system.rule.all()
    rulecombinations = liquidity_system.rulecombination.all()
    liquidity_rules = liquidity_system.liquidity_rule.all()
    liquidity_system_dict['name'] = liquidity_system.name
    liquidity_system_dict['indicators'] = []
    liquidity_system_dict['rules'] = []
    liquidity_system_dict['rulecombinations'] = []
    liquidity_system_dict['liquidityrules'] = []
    liquidity_system_dict['indicator_combinations'] = []
    for indicator in indicators:
        if str(indicator.polymorphic_ctype) == "indicators_ combination":
            liquidity_system_dict['indicator_combinations'].append([str(indicator.coeff), str(indicator.indicator1), str(indicator.operator), str(indicator.indicator2)])       
        elif str(indicator.polymorphic_ctype) == "ppo":
            liquidity_system_dict['indicators'].append([indicator.__class__.__name__,str([indicator.period1]),str([indicator.period2]),str([indicator.period3]),str(indicator.input_data),str(indicator.coeff),str(indicator.lag)])             
        else:
            liquidity_system_dict['indicators'].append([indicator.__class__.__name__,str([indicator.period]),str(indicator.input_data),str(indicator.coeff),str(indicator.lag)])
    for rule in rules:
        liquidity_system_dict['rules'].append([str(rule.title),str(rule.technical1),str(rule.operator),str(rule.technical2)])
    for rulecombination in rulecombinations:
        liquidity_system_dict['rulecombinations'].append([str(rulecombination.title),str(rulecombination.rule1),str(rulecombination.operator),str(rulecombination.rule2)])
    for liquidityrule in liquidity_rules:
        liquidity_system_dict['liquidityrules'].append([str(liquidityrule.min_amount),str(liquidityrule.max_amount),str(liquidityrule.rule),str(liquidityrule.name)])
    userpath = settings.LIQUIDITY_SYSTEM + str(request.user) + '/export/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)        
    with open(userpath + liquidity_system_dict['name'] + '.pickle', 'wb') as f:
        pickle.dump(liquidity_system_dict, f, protocol=2)
    f.close
    if id_parent == 99999999999:
        return redirect('tools:liquidity_manage_default_systems')
    return redirect('tools:liquidity_manage_liquidity_system_folder', parent_id=id_parent)

def LSLoadLiquiditySystem(request):
    load_files = []
    userpath = settings.LIQUIDITY_SYSTEM + str(request.user) + '/export/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)       
    if request.POST:
        file_name = request.POST.get("file_name")
        parent_id = request.POST.get("parent_id")
        liquidity_system = Liquidity_System()
        liquidity_system.name = file_name
        with open(userpath+file_name+'.pickle','rb') as f:
            liquidity_system_dict = pickle.load(f)
        liquidity_system.save()
        last_liquidity_system = Liquidity_System.objects.last()
        technicals = []
        for technical in liquidity_system_dict['indicators']:
            try:
                if technical[0] == "Ppo":
                    input_data_id = Input_data.objects.get(input_data=technical[4])
                else:
                    input_data_id = Input_data.objects.get(input_data=technical[2])
                try:
                    technicals.append(eval(technical[0])(coeff=technical[3], input_data=input_data_id, lag=technical[4], strategy_id=0, liquidity_system_id=last_liquidity_system.id).save())
                except:
                    if technical[0] == "Ppo":                        
                        technicals.append(eval(technical[0])(coeff=technical[5], period1=technical[1][1:-1],period2=technical[2][1:-1],period3=technical[3][1:-1], input_data=input_data_id, lag=technical[6],strategy_id=0, liquidity_system_id=last_liquidity_system.id).save())    
                    else:
                        technicals.append(eval(technical[0])(coeff=technical[3], period=technical[1][1:-1], input_data=input_data_id, lag=technical[4],strategy_id=0, liquidity_system_id=last_liquidity_system.id).save())
            except:
                technicals.append(eval(technical[0])(coeff=technical[3], strategy_id=0, liquidity_system_id=last_liquidity_system.id).save())                
        for indicator_comb in liquidity_system_dict['indicator_combinations']:
            indicator_combinations = Indicators_Combination(strategy_id=0, liquidity_system_id=last_liquidity_system.id)
            tech_coms = Indicator.objects.filter(liquidity_system_id=last_liquidity_system.id)
            indicator1 = ''
            indicator2 = ''
            for tech in tech_coms:
                if indicator_comb[1] == str(tech):
                    indicator1 = tech
                if indicator_comb[3] == str(tech):
                    indicator2 = tech               
            indicator_combinations.coeff = indicator_comb[0]
            indicator_combinations.indicator1 = indicator1
            indicator_combinations.indicator2 = indicator2
            indicator_combinations.operator = indicator_comb[2]
            indicator_combinations.save()                
        tech_coms = Indicator.objects.filter(liquidity_system_id=last_liquidity_system.id)    
        for rule in liquidity_system_dict['rules']:
            tech1 = ''
            tech2 = ''
            for tech in tech_coms:
                if rule[1] == str(tech):
                    tech1 = tech
                if rule[3] == str(tech):
                    tech2 = tech
            liquidity_system.rule.create(title=rule[0], technical1=tech1, operator=rule[2], technical2=tech2, strategy_id=0, liquidity_system_id=last_liquidity_system.id)
        for rulecomb in liquidity_system_dict['rulecombinations']:
            rules = PrimaryRule.objects.filter(liquidity_system_id=last_liquidity_system.id)
            rule1 = ''
            rule2 = ''
            for rule in rules:
                if rulecomb[1] == str(rule):
                    rule1 = rule
                if rulecomb[3] == str(rule):
                    rule2 = rule
            liquidity_system.rulecombination.create(title=rulecomb[0], rule1=rule1, operator=rulecomb[2], rule2=rule2,strategy_id=0, liquidity_system_id=last_liquidity_system.id)
        rules = PrimaryRule.objects.filter(liquidity_system_id=last_liquidity_system.id) 
        for liquidity_rule in liquidity_system_dict['liquidityrules']:
            rule1 = ''
            for rule in rules:
                if liquidity_rule[2] == str(rule):
                    rule1 = rule
            liquidity_system.liquidity_rule.create(min_amount=liquidity_rule[0], max_amount=liquidity_rule[1], name=liquidity_rule[3],rule=rule1,)
        liquidity_system.user = request.user
        liquidity_system.save()
        if parent_id == "d":
            if not Liquidity_Tree.objects.filter(permission=1).exists():
                default_folder = Liquidity_Tree()
                default_folder.child_id = -1
                default_folder.child_type = 1
                default_folder.child_name = "Default Folder"
                default_folder.parent_id = 0
                default_folder.user = request.user
                default_folder.permission = 1
                default_folder.save()
            else:
                default_folder = get_object_or_404(Liquidity_Tree, permission=1, child_type=1)
            new_tree = Liquidity_Tree()
            new_tree.child_id = liquidity_system.id
            new_tree.child_name = liquidity_system.name
            new_tree.child_type = 2
            new_tree.parent_id = default_folder.child_id
            new_tree.permission = 1
            new_tree.user = request.user
            new_tree.save()
            return redirect('tools:liquidity_manage_default_systems')
        new_tree = Liquidity_Tree()
        new_tree.child_id = liquidity_system.id
        new_tree.child_name = liquidity_system.name
        new_tree.child_type = 2
        new_tree.parent_id = parent_id
        new_tree.user = request.user
        new_tree.save()
        return redirect('tools:liquidity_manage_liquidity_system', id=liquidity_system.id)    
    with os.scandir(userpath) as entries:
        for entry in entries:
            if not entry.is_file():
                continue
            filename, file_extension = os.path.splitext(entry.name)
            if file_extension.lower() != ".pickle":
                continue
            load_files.append(filename)
    folders = Liquidity_Folder.objects.all().filter(user=request.user)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0, [], tree_list)
    ctx = {
        'tree_structure': tree_structure,
        'folders': folders,
        'load_files': load_files
    }
    return render(request, 'tools/liquidity_system/load_file_list.html', ctx)

def LSDeleteFolder(request):
    folders =  Liquidity_Folder.objects.all().filter(user=request.user)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0, [], tree_list)
    if request.POST: 
        folder_id = request.POST.get("id")
        if Liquidity_Tree.objects.all().filter(parent_id=folder_id).exists():
            liquidity_systems = Liquidity_System.objects.all().filter(user=request.user)
            ctx = {
                'liquidity_systems': liquidity_systems,
                'tree_structure': tree_structure,
                'error_message': "Not Empty Folder",
                'parent_id': 0
            }
            return redirect('tools:liquidity_manage_liquidity_system_folder', parent_id=0)
        else:
            folder = get_object_or_404( Liquidity_Folder, id=folder_id)
            folder.delete()
            tree = get_object_or_404(Liquidity_Tree, child_id=folder_id, child_type=1)
            tree.delete()
            return redirect('tools:liqudity_manage_liquidity_systems')
    ctx = {
        'folders': folders,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/liquidity_system/delete_folder.html', ctx)    

def LSGetLiquidityData(request):
    tree_id = request.GET.get("id")
    tree_element = get_object_or_404(Liquidity_Tree, id=tree_id)
    msg = {
        "child_type": tree_element.child_type,
        "child_id": tree_element.child_id,
        "permission": tree_element.permission,
    }
    json_data = json.dumps(msg)
    return HttpResponse(json_data, content_type='application/json')

def LSManageLiquiditySystem(request, id):
    liquidity_system = get_object_or_404(Liquidity_System, id=id)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0,[],tree_list)
    indicator_combinations = Indicators_Combination.objects.filter(liquidity_system_id=id)
    if get_object_or_404(Liquidity_Tree, child_id=id, child_type=2).parent_id == -1:
        ctx = {
            'relative_path': 'Default Folder/',
            'liquidity_system': liquidity_system,
            'tree_structure': tree_structure,
            'indicator_combinations': indicator_combinations
        }
        return render(request, 'tools/liquidity_system/manage_liquidity_system.html', ctx)    
    relative_path = LSget_path(get_object_or_404(Liquidity_Tree, child_id=id, child_type=2, user=request.user).parent_id)
    ctx = {
        'relative_path': relative_path,
        'liquidity_system': liquidity_system,
        'tree_structure': tree_structure,
        'indicator_combinations': indicator_combinations
    }
    return render(request, 'tools/liquidity_system/manage_liquidity_system.html', ctx)    

def LSDeleteLiquiditySystem(request, id_system):
    liquidity_system = get_object_or_404(Liquidity_System, id=id_system)
    form = LiquiditySystemForm(request.POST or None, instance=liquidity_system)
    if form.is_valid():
        liquidity_system.delete()
        rules = Rule.objects.all().filter(liquidity_system_id=id_system)
        for rule in rules:
            rule.delete()
        rule_combinations = RuleCombination.objects.all().filter(liquidity_system_id=id_system)
        for rule_combination in rule_combinations:
            rule_combination.delete()
        indicators = Indicator.objects.all().filter(liquidity_system_id=id_system).order_by('-id')
        for indicator in indicators:
            indicator.delete()
        liquidity_tree = get_object_or_404(Liquidity_Tree, child_type=2, child_id=id_system)
        liquidity_tree.delete()
        return redirect('tools:liquidity_manage_liquidity_system_folder', parent_id=0)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0,[],tree_list)
    ctx = {
        'form': form,
        'id_system': id_system,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/liquidity_system/delete_liquidity_system.html', ctx)


def LSAddRule(request, id_system):
    instantiate = Rule(strategy_id=0, liquidity_system_id=id_system)
    if request.POST:
        post = request.POST.copy() # to make it mutable
        technical_1 = post['technical1']
        technical_2 = post['technical2']
        tech_coms  = Indicator.objects.filter(strategy_id=0, liquidity_system_id=id_system)
        tech1_id = ''
        tech2_id = ''
        for tech_com in tech_coms:
            if technical_1 == str(tech_com).lower():
                tech1_id = tech_com.id
            if technical_2 == str(tech_com).lower():
                tech2_id = tech_com.id
        post['technical1'] = tech1_id
        post['technical2'] = tech2_id
        request.POST = post
    form = RuleForm(0,999999999,request.POST or None, instance=instantiate)
    liquid_system = get_object_or_404(Liquidity_System, id=id_system)
    if form.is_valid():
        new_rule = form.save()
        liquid_system.rule.add(new_rule)        
        return redirect('tools:liquidity_manage_liquidity_system', id=id_system)
    indicator_tree = []
    indicator_tree = getIndicatorTree()        
    ctx = {
        'form': form,
        'id_system': id_system,
        'indicator_tree': indicator_tree
    }
    return render(request, 'tools/liquidity_system/add_rule.html', ctx)

def LSModifyRule(request, id_rule, id_system):
    instantiate = get_object_or_404(Rule, id=id_rule)
    liquid_system = get_object_or_404(Liquidity_System, id=id_system)
    if request.POST:
        post = request.POST.copy() # to make it mutable
        technical_1 = post['technical1']
        technical_2 = post['technical2']
        tech_coms  = Indicator.objects.filter(strategy_id=0, liquidity_system_id=id_system)
        tech1_id = ''
        tech2_id = ''
        for tech_com in tech_coms:
            if technical_1 == str(tech_com).lower():
                tech1_id = tech_com.id
            if technical_2 == str(tech_com).lower():
                tech2_id = tech_com.id
        post['technical1'] = tech1_id
        post['technical2'] = tech2_id
        request.POST = post
    form = RuleForm(0,999999999, request.POST or None, instance=instantiate)
    if form.is_valid():
        modify_rule = form.save()
        liquid_system.rule.add(modify_rule)
        return redirect('tools:liquidity_manage_liquidity_system', id=id_system)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0,[],tree_list)
    ctx = {
        'form': form,
        'tree_structure': tree_structure,
        'id_system': id_system,
        'id_rule':id_rule
    }
    return render(request, 'tools/liquidity_system/modify_rule.html', ctx)

def LSAddRuleCombination(request, id_system):
    instantiate = RuleCombination(strategy_id=0,liquidity_system_id=id_system)
    if request.POST:
        post = request.POST.copy() # to make it mutable
        rule_coms = PrimaryRule.objects.filter(liquidity_system_id=id_system)
        pr1_id = ''
        pr2_id = ''
        for rule_com in rule_coms:
            if request.POST.get('rule1') == str(rule_com).lower():
                pr1_id = rule_com.id
            if request.POST.get('rule2') == str(rule_com).lower():
                pr2_id = rule_com.id
        post['rule1'] = pr1_id
        post['rule2'] = pr2_id
        request.POST = post
    form = RuleCombinationForm(0,request.POST or None, instance=instantiate)
    liquid_system = get_object_or_404(Liquidity_System, id=id_system)
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if form.is_valid():
        new_rulecombination = form.save()
        liquid_system.rulecombination.add(new_rulecombination)        
        return redirect('tools:liquidity_manage_liquidity_system', id=id_system)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0,[],tree_list)
    ctx = {
        'id_system': id_system,
        'form': form,
        'tree_structure': tree_structure
    }
    return render(request, 'tools/liquidity_system/add_rulecombination.html', ctx)

def LSModifyRuleCombination(request, id_rule, id_system):
    if request.POST:
        post = request.POST.copy() # to make it mutable
        rule_coms = PrimaryRule.objects.filter(liquidity_system_id=id_system)
        pr1_id = ''
        pr2_id = ''
        for rule_com in rule_coms:
            if request.POST.get('rule1') == str(rule_com).lower():
                pr1_id = rule_com.id
            if request.POST.get('rule2') == str(rule_com).lower():
                pr2_id = rule_com.id
        post['rule1'] = pr1_id
        post['rule2'] = pr2_id
        request.POST = post    
    liquid_system = get_object_or_404(Liquidity_System, id=id_system)
    rulecombination = get_object_or_404(RuleCombination, id=id_rule)
    form = RuleCombinationForm(0, request.POST or None, instance=rulecombination)
    if form.is_valid():
        modify_rulecombination = form.save()
        liquid_system.rulecombination.add(modify_rulecombination)
        return redirect('tools:liquidity_manage_liquidity_system', id=id_system)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0,[],tree_list)
    ctx = {
        'id_system': id_system,
        'id_rule': id_rule,
        'form': form,
        'tree_structure': tree_structure,
    }    
    return render(request, 'tools/liquidity_system/modify_rulecombination.html', ctx)

def LSajax_get_rule_combination(request, id_system):
    technical_1 = PrimaryRule.objects.filter(liquidity_system_id=id_system)
    rule_str = ''
    for technical in technical_1:
        rule_str = rule_str + str(technical) + ','
    return HttpResponse(rule_str)

def LSajax_get_rule_combination_modify(request, id_system):
    technicals = Rule.objects.all().filter(liquidity_system_id=id_system)
    rule_str = ''
    for technical in technicals:
        rule_str = rule_str + str(technical) + ','
    return HttpResponse(rule_str)

def LSAddLiquidityRule(request, id_system):
    liquid_system = get_object_or_404(Liquidity_System, id=id_system)
    instantiate = Liquidity_Rule()
    if request.POST:
        post = request.POST.copy() # to make it mutable
        rule_coms = PrimaryRule.objects.filter(liquidity_system_id=id_system)
        pr_id = ''
        for rule_com in rule_coms:
            if request.POST.get('rule') == str(rule_com).lower():
                pr_id = rule_com.id
        post['rule'] = pr_id
        request.POST = post        
    form = LiquidityRuleForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        liquidity_rule = form.save()
        liquid_system.liquidity_rule.add(liquidity_rule)
        return redirect('tools:liquidity_manage_liquidity_system', id=id_system)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0,[],tree_list)
    ctx = {
        'tree_structure':tree_structure,
        'form': form,
        'id_system': id_system
    }
    return render(request, 'tools/liquidity_system/add_liquidity_rule.html', ctx)

def LSModifyLiquidityRule(request, id_rule, id_system):
    liquid_system = get_object_or_404(Liquidity_System, id=id_system)
    instantiate = get_object_or_404(Liquidity_Rule, id=id_rule)
    if request.POST:
        post = request.POST.copy() # to make it mutable
        rule_coms = PrimaryRule.objects.filter(liquidity_system_id=id_system)
        pr_id = ''
        for rule_com in rule_coms:
            if request.POST.get('rule') == str(rule_com).lower():
                pr_id = rule_com.id
        post['rule'] = pr_id
        request.POST = post        
    form = LiquidityRuleForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        liquidity_rule = form.save()
        liquid_system.liquidity_rule.add(liquidity_rule)
        return redirect('tools:liquidity_manage_liquidity_system', id=id_system)    
    form = LiquidityRuleForm(request.POST or None, instance=instantiate)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0,[],tree_list)
    ctx = {
        'form': form,
        'id_rule': id_rule,
        'id_system': id_system,
        'tree_structure': tree_structure,
    }
    return render(request, 'tools/liquidity_system/modify_liquidity_rule.html', ctx)

def LSAddIndicator(request,source, indicator, id_system):
    instantiate = eval(indicator+"(liquidity_system_id=id_system, strategy_id=0)")
    CustomModel = eval(indicator)
    CustomForm = modelform_factory(model=CustomModel, widgets = {
            'input_data': forms.Select(attrs={'class': 'form-control'}),
            'coeff': forms.NumberInput(attrs={'class': 'form-control'}),
            'lag': forms.NumberInput(attrs={'class': 'form-control'}),
            'period': forms.NumberInput(attrs={'class': 'form-control'}),
            'period1': forms.NumberInput(attrs={'class': 'form-control'}),
            'period2': forms.NumberInput(attrs={'class': 'form-control'}),
            'period3': forms.NumberInput(attrs={'class': 'form-control'}),            
        } ,exclude = ('rule_id','strategy_id','rank_system_id','liquidity_system_id','indicator_combination_id'))
    form = CustomForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        form.save()
        if source == 'add':
            return redirect('tools:liquidity_add_rule', id_system=id_system)
        elif source == 'comb':
            return redirect('tools:liquidity_add_indicator_combination',id_system=id_system)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0,[],tree_list)
    indicator_property = get_object_or_404(IndicatorProperty, indicator=indicator)
    ctx = {
        'source': source,
        'indicator': indicator,
        'id_system': id_system,
        'form': form,
        'tree_structure': tree_structure,
        'indicator_property': indicator_property
    }
    return render(request, 'tools/liquidity_system/add_indicator.html', ctx)

def LSGetIndicator(request, id_system):
    indicators = Indicator.objects.filter(liquidity_system_id=id_system)
    rule_str = ''
    for indicator in indicators:
        rule_str = rule_str + str(indicator) + ','
    return HttpResponse(rule_str)

def LSAddIndicatorCombination(request, id_system):
    instantiate = Indicators_Combination(strategy_id=0,liquidity_system_id=id_system)
    if request.POST:
        post = request.POST.copy()
        technical_1 = post['indicator1']
        technical_2 = post['indicator2']
        tech_coms = Indicator.objects.filter(liquidity_system_id=id_system)
        tech1_id=''
        tech2_id=''
        for tech_com in tech_coms:
            if technical_1 == str(tech_com).lower():
                tech1_id = tech_com.id
            if technical_2 == str(tech_com).lower():
                tech2_id = tech_com.id
        post['indicator1'] = tech1_id
        post['indicator2'] = tech2_id
        request.POST = post
    form = IndicatorCombinationForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        form.save()
        return redirect('tools:liquidity_manage_liquidity_system', id=id_system)
    indicator_tree = []
    indicator_tree = getIndicatorTree()    
    ctx = {
        'id_system': id_system,
        'form': form,
        'indicator_tree': indicator_tree,
    }
    return render(request, 'tools/liquidity_system/add_indicator_combination.html', ctx)     

def LSModifyIndicatorCombination(request, id_system, id_comb):
    instantiate = get_object_or_404(Indicators_Combination, id=id_comb)
    if request.POST:
        post = request.POST.copy()
        technical_1 = post['indicator1']
        technical_2 = post['indicator2']
        tech_coms = Indicator.objects.filter(liquidity_system_id=id_system)
        tech1_id=''
        tech2_id=''
        for tech_com in tech_coms:
            if technical_1 == str(tech_com).lower():
                tech1_id = tech_com.id
            if technical_2 == str(tech_com).lower():
                tech2_id = tech_com.id
        post['indicator1'] = tech1_id
        post['indicator2'] = tech2_id
        request.POST = post        
    form = IndicatorCombinationForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        form.save()
        return redirect('tools:liquidity_manage_liquidity_system', id=id_system)
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0, [], tree_list)
    ctx = {
        'id_system': id_system,
        'form': form,
        'tree_structure': tree_structure,
        'id_comb': id_comb
    }
    return render(request, 'tools/liquidity_system/modify_indicator_combination.html', ctx)    

def LSGetTechs(request, id_comb):
    technical = ''
    indicator_combination = get_object_or_404(Indicators_Combination, indicator_ptr_id=id_comb)
    technical = str(indicator_combination.indicator1) + ',' + str(indicator_combination.indicator2)
    return HttpResponse(technical)

def LSGetIndicatorBasic(request, id_system):
    indicators = Indicator.objects.filter(liquidity_system_id=id_system)
    rule_str = ''
    for indicator in indicators:
        if not str(indicator.polymorphic_ctype) == "indicators_ combination":
            rule_str = rule_str + str(indicator) + ','
    return HttpResponse(rule_str)      

def LSDelete(request):
    id_system = request.POST.get("id_system")
    id_element = request.POST.get("id_element")
    element_type = request.POST.get("type")
    if element_type == "rule":
        rule = get_object_or_404(Rule, id=id_element)
        rule.delete()
    if element_type == "rulecombination":
        rulecombination = get_object_or_404(RuleCombination, id=id_element)
        rulecombination.delete()
    if element_type == "liquidityrule":
        liquidity_rule = get_object_or_404(Liquidity_Rule, id=id_element)
        liquidity_rule.delete()
    if element_type == "combination":
        indicator_combination = get_object_or_404(Indicators_Combination, indicator_ptr_id=id_element)
        indicator_combination.delete()
    return redirect('tools:liquidity_manage_liquidity_system', id=id_system)

def LSajax_get_rule_modify(request, id_rule, id_system):
    liquidity_rule = get_object_or_404(Liquidity_Rule, id=id_rule)
    indicator = get_object_or_404(PrimaryRule, id=liquidity_rule.rule_id)
    return HttpResponse(str(indicator))

def LSGetIndicatorForm(request):
    techindicator = request.GET.get('techindicator')
    id_system = request.GET.get('id_system')
    requestfrom = request.GET.get('from')
    if requestfrom == 'add':
        requestrule = 0
    elif requestfrom == 'modify':
        requestrule = request.GET.get('ruleid')
    indicator = ''
    tech_coms = Indicator.objects.filter(liquidity_system_id=id_system)
    tech_id = ''
    for tech_com in tech_coms:
        if techindicator == str(tech_com).lower():
            tech_id = tech_com.id
    instantiate = get_object_or_404(Indicator, id=tech_id)
    indicator_temp = str(instantiate.polymorphic_ctype).replace(' ', '')
    if indicator_temp == "indicators_combination":
        ctx = {
            'id_system': id_system,
            'id_element': tech_id,
            'type': 'combination'
        }
        return render(request, 'tools/liquidity_system/delete_indicator_combination.html', ctx)
    indicator_property = IndicatorProperty.objects.all()
    for element in indicator_property:
        if str(element.indicator).lower() == indicator_temp:
            indicator_obj = element
    indicator = str(indicator_obj)
    CustomModel = eval(indicator)
    CustomForm = modelform_factory(model=CustomModel, widgets = {
            'input_data': forms.Select(attrs={'class': 'form-control'}),
            'coeff': forms.NumberInput(attrs={'class': 'form-control'}),
            'lag': forms.NumberInput(attrs={'class': 'form-control'}),
            'period': forms.NumberInput(attrs={'class': 'form-control'}),
            'period1': forms.NumberInput(attrs={'class': 'form-control'}),
            'period2': forms.NumberInput(attrs={'class': 'form-control'}),
            'period3': forms.NumberInput(attrs={'class': 'form-control'}),            
        } ,exclude = ('rule_id','strategy_id','rank_system_id','liquidity_system_id','indicator_combination_id'))
    form = CustomForm(request.POST or None, instance=instantiate)   
    ctx = {
        'indicator': indicator,
        'tech_id': tech_id,
        'id_system': id_system,
        'requestfrom': requestfrom,
        'requestrule': requestrule,
        'form': form,
        'indicator_property': indicator_obj
    }
    return render(request, 'tools/liquidity_system/modify_indicator.html', ctx)

def LSDeleteIndicator(request, tech_id, id_system, requestfrom, requestrule):
    tech_indicator = get_object_or_404(Indicator, id=tech_id)
    tech_indicator.delete()
    if requestfrom == 'add':
        return redirect("tools:liquidity_add_rule", id_system=id_system)
    elif requestfrom == 'modify':
        return redirect("tools:liquidity_manage_liquidity_system", id=id_system)   

def LSModifyIndicator(request, indicator, tech_id, id_system, requestfrom, requestrule):
    instantiate = get_object_or_404(Indicator, id=tech_id)
    CustomModel = eval(indicator)
    CustomForm = modelform_factory(model=CustomModel, widgets = {
            'input_data': forms.Select(attrs={'class': 'form-control'}),
            'coeff': forms.NumberInput(attrs={'class': 'form-control'}),
            'lag': forms.NumberInput(attrs={'class': 'form-control'}),
            'period': forms.NumberInput(attrs={'class': 'form-control'}),
            'period1': forms.NumberInput(attrs={'class': 'form-control'}),
            'period2': forms.NumberInput(attrs={'class': 'form-control'}),
            'period3': forms.NumberInput(attrs={'class': 'form-control'}),            
        } ,exclude = ('rule_id','strategy_id','rank_system_id','liquidity_system_id','indicator_combination_id'))
    form = CustomForm(request.POST or None, instance=instantiate)
    if form.is_valid():
        form.save()
        if requestfrom == 'add':
            return redirect("tools:liquidity_add_rule", id_system=id_system)
        elif requestfrom == 'modify':
            return redirect("tools:liquidity_modify_rule", id_rule=requestrule, id_system=id_system)  

def LSManageDefaultSystems(request):
    liquidity_systems = []
    liquidity_system_trees = Liquidity_Tree.objects.all().filter(child_type=2, parent_id=-1, permission=1)
    for liquidity_tree in liquidity_system_trees:
        liquidity_systems.append(get_object_or_404(Liquidity_System, id=liquidity_tree.child_id))
    tree_list = LSget_tree_list(request.user)
    tree_structure = LScreateTree(0, [], tree_list)
    folder = 'Default Folder'
    ctx = {
        'liquidity_systems': liquidity_systems,
        'tree_structure': tree_structure,
        'folder': folder
    }
    return render(request, 'tools/liquidity_system/manage_default_systems.html', ctx)