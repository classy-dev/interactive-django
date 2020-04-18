import json
import pickle
from os.path import exists
import re
import os
import time
import datetime

from celery.result import AsyncResult
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import HttpResponse, get_object_or_404, render, redirect
from django.template.response import TemplateResponse
from django.forms.models import modelform_factory
from django.db.models import Q
from django import forms

from .models import ( PeriodFolder, PeriodTree, PeriodStrategy, Result )
from .forms import ( PeriodStrategyForm, GeneralPeriodStrategyForm )
from backtest.models import (Adx, Atrn, BarSinceEntry, Benchmark, BuyRule,
                             Constant, Ema, HighDS, LowDS, OpenDS, Ppo,
                             PriceDS, PrimaryRule,  Roc, Rsi, Rule,
                             RuleCombination, SellRule,  Slope, Sma, Universe,
                             Strategy, Indicator, Input_data, Category, Tree, IndicatorProperty, 
                             Indicators_Combination, CombFolder, CombTree, CombinationStrategy,
                             BuyStrategy)
                             
from tools.models import ( Universe_Tree, Universe_Universe, Benchmarks_Tree, Benchmarks_Universe,
                           Liquidity_System, Liquidity_Tree, Ranking_System, Ranking_Tree )

from backtest.Script import interactive_process
from django.conf import settings
from django.views import View
# Create your views here.

def get_tree_list(user_id):
    tree_list = []
    list_item = {}
    get_default_trees = PeriodTree.objects.all().filter(permission=1)
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
    get_tree_lists = PeriodTree.objects.all().filter(user_id=user_id, permission=0)
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

def get_path(strategy_id):
    tree_element = get_object_or_404(PeriodTree, child_id=strategy_id, child_type=2)
    if tree_element.parent_id == 0:
        return ""
    elif tree_element.parent_id == -1:
        return "Default Folder/"
    else:
        category_element = get_object_or_404(PeriodFolder, id=tree_element.parent_id)
        return category_element.path        

def Index(request):
    return redirect('optimize:period_manage')

def PeriodCreateFolder(request):
    if request.POST:
        new_folder = PeriodFolder()
        new_folder.name = request.POST.get("folder_name")
        new_folder.user = request.user
        if request.POST.get("parent_id") == '0':
            new_folder.path = request.POST.get("folder_name") + '/'
        else:
            parent_folder = get_object_or_404(PeriodFolder, id=request.POST.get("parent_id"))
            new_folder.path = parent_folder.path + request.POST.get("folder_name") + "/"
        new_folder.save()
        new_tree = PeriodTree()
        new_tree.child_id = new_folder.id
        new_tree.child_name = new_folder.name
        new_tree.child_type = 1
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('optimize:period_manage')
    folders = PeriodFolder.objects.all().filter(user_id=request.user)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'folders': folders,
        'tree_structure': tree_structure,
    }        
    return render(request, 'optimize/period_test/create_folder.html', ctx)

def PeriodDeleteFolder(request):
    folders = PeriodFolder.objects.all().filter(user_id=request.user)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    if request.POST:
        folder_id = request.POST.get("id")
        if PeriodTree.objects.all().filter(parent_id=folder_id).exists():
            ctx = {
                'folders': folders,
                'tree_structure': tree_structure,
                'error_message': "Not Empty Folder",
            }
            return render(request, 'optimize/period_test/delete_folder.html', ctx)
        else:
            folder = get_object_or_404(PeriodFolder, id=folder_id)
            folder.delete()
            tree = get_object_or_404(PeriodTree, child_id=folder_id, child_type=1, permission=0)
            tree.delete()
            return redirect('optimize:period_manage')  
    ctx = {
        'tree_structure': tree_structure,
        'folders': folders,
    }
    return render(request, 'optimize/period_test/delete_folder.html', ctx)    

def PeriodManageIndex(request):
    period_tree = PeriodTree.objects.all().filter(child_type=2, user=request.user).last()
    if period_tree:
        period_strategy = get_object_or_404(PeriodStrategy, id=period_tree.child_id)
        return redirect('optimize:period_manage_strategy', id_strategy=period_strategy.id)
    else:
        tree_list = get_tree_list(request.user)
        tree_structure = createTree(0,[], tree_list)        
        ctx = {
            'tree_structure': tree_structure,
            'nostrategy': 'No Period Strategy!',
        }
        return render(request, 'optimize/period_test/manage_strategy.html', ctx)   

def PeriodCreateStrategy(request):
    folders = PeriodFolder.objects.all().filter(user_id=request.user)
    form = PeriodStrategyForm(request.POST or None)
    if form.is_valid():
        new_strategy = form.save()
        new_strategy.user = request.user
        new_strategy.save()
        new_tree = PeriodTree()
        new_tree.child_id = new_strategy.id
        new_tree.child_name = new_strategy.name
        new_tree.child_type = 2
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('optimize:period_manage_strategy', id_strategy=new_strategy.id)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'form': form,
        'tree_structure': tree_structure,
        'folders': folders,
    }    
    return render(request, 'optimize/period_test/create_strategy.html', ctx)

def PeriodDeleteStrategy(request, id_strategy):
    period_strategy = get_object_or_404(PeriodStrategy, id=id_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)    
    form = PeriodStrategyForm(request.POST or None, instance=period_strategy)
    if form.is_valid():
        tree_element = get_object_or_404(PeriodTree, child_id=id_strategy, child_type=2)
        parent_id = tree_element.parent_id
        tree_element.delete()
        if period_strategy.results:
            period_strategy.results.delete()
        period_strategy.delete()
        if parent_id == -1:
            return redirect('optimize:period_manage_folder', id_folder=99999999999)
        else:
            return redirect('optimize:period_manage_folder', id_folder=parent_id)
        return redirect('optimize:')
    ctx = {
        'form': form,
        'tree_structure': tree_structure,
    }
    return render(request, 'optimize/period_test/delete_strategy.html', ctx)

def PeriodManageStrategy(request, id_strategy):
    period_strategy = get_object_or_404(PeriodStrategy, id=id_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)    
    parent_path = get_path(id_strategy)
    userpath = settings.USERS_DIRECTORY + str(request.user) + "/period_bias_test/" + parent_path + str(period_strategy.name)
    if os.path.exists(userpath + '/Results.pickle'):
        period_strategy.state = "green"
    else:
        period_strategy.state = "red"
    period_strategy.save()    
    strategies = []
    tree_strategy_defaults = Tree.objects.all().filter(permission=1, child_type=2)
    for element in tree_strategy_defaults:
        strategies.append(get_object_or_404(Strategy, id=element.child_id))
    tree_strategy_user = Tree.objects.all().filter(permission=0, child_type=2, user=request.user)
    for element in tree_strategy_user:
        strategies.append(get_object_or_404(Strategy, id=element.child_id))    
    ctx = {
        'strategies': strategies,
        'tree_structure': tree_structure,
        'period_strategy': period_strategy,
        'parent_path': parent_path,
    }
    return render(request, 'optimize/period_test/manage_strategy.html', ctx)    

def PeriodModifyGeneral(request, id_strategy):
    period_strategy = get_object_or_404(PeriodStrategy, id=id_strategy)
    form = GeneralPeriodStrategyForm(request.POST or None, instance=period_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list) 
    if form.is_valid():
        form.save()
        return redirect('optimize:period_manage_strategy', id_strategy=id_strategy)
    ctx = {
        'form': form,
        'tree_structure': tree_structure,
    }
    return render(request, 'optimize/period_test/modify_general.html', ctx)

def PeriodAddStrategy(request, id_strategy):
    period_strategy = get_object_or_404(PeriodStrategy, id=id_strategy)
    strategy = get_object_or_404(Strategy, id=request.POST.get("add_strategy"))
    period_strategy.strategy = strategy
    period_strategy.save()
    return redirect('optimize:period_manage_strategy', id_strategy=id_strategy)

def PeriodChangeStrategy(request, id_strategy):
    period_strategy = get_object_or_404(PeriodStrategy, id=id_strategy)
    strategy = get_object_or_404(Strategy, id=request.POST.get("add_strategy"))
    period_strategy.strategy = strategy
    period_strategy.save()
    return redirect('optimize:period_manage_strategy', id_strategy=id_strategy)        

def PeriodRemoveStrategy(request, id_strategy):
    period_strategy = get_object_or_404(PeriodStrategy, id=id_strategy)
    period_strategy.strategy = None
    period_strategy.save()
    return redirect('optimize:period_manage_strategy', id_strategy=id_strategy)            

def PeriodManage(request):
    return redirect('optimize:period_manage_folder', id_folder=99999999999)

def PeriodManageFolder(request, id_folder):
    periods = []
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)    
    if id_folder == 99999999999:
        tree_element = PeriodTree.objects.all().filter(child_type=2, parent_id=-1, user=request.user)    
    else:
        tree_element = PeriodTree.objects.all().filter(child_type=2, parent_id=id_folder, user=request.user)
    for element in tree_element:
        periods.append(get_object_or_404(PeriodStrategy, id=element.child_id))
    if id_folder == 0:
        ctx = {
            'id_folder': id_folder,
            'title': 'Top Folder',
            'periods': periods,
            'tree_structure': tree_structure,
        }
        return render(request, 'optimize/period_test/manage_strategies.html', ctx)
    else:
        if id_folder == 99999999999:
            ctx = {
                'id_folder': id_folder,
                'title': 'Default Folder/',
                'periods': periods,
                'tree_structure': tree_structure,
            }
        else:
            parent_folder = get_object_or_404(PeriodFolder, id=id_folder)
            ctx = {
                'id_folder': id_folder,
                'title': parent_folder.path,
                'periods': periods,
                'tree_structure': tree_structure,
            }
        return render(request, 'optimize/period_test/manage_strategies.html', ctx)    

def period_ajax_get_tree_element(request):
    tree_id = request.GET.get("id")
    tree_element = get_object_or_404(PeriodTree, id=tree_id)
    msg = {
        'child_type': tree_element.child_type,
        'child_id': tree_element.child_id,
        'permission': tree_element.permission,
    }
    return HttpResponse(json.dumps(msg), content_type='application/json')             

def PeriodLaunchStrategy(request, id_strategy):
    strategy_dict = {}
    strategy_dict['technicals'] = []
    strategy_dict['buyrules'] = []
    strategy_dict['sellrules'] = []
    strategy_dict['indicator_combinations'] = []    
    period_strategy = get_object_or_404(PeriodStrategy, id=id_strategy)
    if not period_strategy.strategy:
        return HttpResponse('error')
    else:
        if period_strategy.strategy.buyrule.all().filter(active=1).count() < 1 or period_strategy.strategy.sellrule.all().filter(active=1).count() < 1:
            return HttpResponse('error1')
        strategy_dict['name'] = str(period_strategy.name)
        strategy_dict['offset'] = str(period_strategy.offset)
        strategy_dict['period'] = str(period_strategy.period)
        strategy_dict['startdate'] = str(period_strategy.startdate)
        strategy_dict['enddate'] = str(period_strategy.enddate)
        strategy_dict['strategy_name'] = str(period_strategy.strategy.name)
        strategy_dict['strategy_capital'] = str(period_strategy.strategy.capital)
        strategy_dict['strategy_positions'] = str(period_strategy.strategy.positions)
        strategy_dict['strategy_commissions'] = str(period_strategy.strategy.commissions)
        strategy_dict['strategy_benchmark'] = str(period_strategy.strategy.benchmark)
        strategy_dict['strategy_transaction_type'] = str(period_strategy.strategy.transaction_type)
        strategy_dict['strategy_frequency'] = str(period_strategy.strategy.frequency)
        strategy_dict['strategy_universe'] = str(period_strategy.strategy.universe)
        strategy_dict['strategy_startdate'] = str(period_strategy.strategy.startdate)
        strategy_dict['strategy_enddate'] = str(period_strategy.strategy.enddate)
        rule_id_active = []
        rule_active = []
        tech_id_active = []
        tech_temp = []
        technicals = []
        buyrules = period_strategy.strategy.buyrule.all().filter(active=1)
        for buyrule in buyrules:
            if buyrule.buyrules_id not in rule_id_active:
                rule_id_active.append(buyrule.buyrules_id) 
        sellrules = period_strategy.strategy.sellrule.all().filter(active=1)
        for sellrule in sellrules:
            if sellrule.sellrules_id not in rule_id_active:
                rule_id_active.append(sellrule.sellrules_id)
        for ruleid in rule_id_active:
            rule_active.append(get_object_or_404(PrimaryRule, id=ruleid))
        for rule in rule_active:
            tech_temp = rule.get_technical_id().split(',')
            for tech in tech_temp:            
                if tech not in tech_id_active:
                    tech_id_active.append(tech)
        for tech_id in tech_id_active:
            technicals.append(get_object_or_404(Indicator, id=tech_id))   
        for technical in technicals:
            if str(technical.polymorphic_ctype) == "indicators_ combination":
                strategy_dict['indicator_combinations'].append([str(technical.coeff), str(technical.indicator1), str(technical.operator), str(technical.indicator2)])
            elif str(technical.polymorphic_ctype) == "ppo":
                strategy_dict['technicals'].append([technical.__class__.__name__,str([technical.period1]),str([technical.period2]),str([technical.period3]),str(technical.input_data),str(technical.coeff),str(technical.lag)])                    
            else:
                strategy_dict['technicals'].append([technical.__class__.__name__,str([technical.period]),str(technical.input_data),str(technical.coeff),str(technical.lag)])
        for BR in buyrules: #Need to recover only Buy Rules that are active
            strategy_dict['buyrules'].append([str(BR.buyrules.title), str(BR.output())])
        for SR in sellrules: #Need to recover only Sell Rules that are active
            strategy_dict['sellrules'].append([str(SR.sellrules.title), str(SR.output())])                                 
        relative_path = get_path(id_strategy)
        userpath = settings.USERS_DIRECTORY + str(request.user) + "/period_bias_test/" + relative_path + str(period_strategy.name)
        if not os.path.exists(userpath):
            os.makedirs(userpath)
        with open(userpath+'/inputs.pickle', 'wb') as f:
            pickle.dump(strategy_dict, f, protocol=2)
        f.close
        process_result = interactive_process.delay(userpath)
        return HttpResponse(process_result)

def PeriodLaunchState(request):
    data = 'Fail'
    if request.is_ajax():
        if 'task_id' in request.POST.keys() and request.POST['task_id']:
            task_id = request.POST['task_id']
            task = AsyncResult(task_id)
            data = task.result or task.state
        else:
            data = 'No task_id in the request'
    else:
        data = 'This is not an ajax request'
    json_data = json.dumps(data)
    return HttpResponse(json_data, content_type='application/json')

def PeriodLaunchResult(request, id_strategy):
    period_strategy = get_object_or_404(PeriodStrategy, id=id_strategy)
    relative_path = get_path(period_strategy.id)
    userpath = settings.USERS_DIRECTORY + str(request.user) + "/period_bias_test/" + relative_path + str(period_strategy.name)
    with open(userpath+'/Results.pickle', 'rb') as f:
        Results = pickle.load(f)
    if period_strategy.results == None:
        new_result = Result()
        new_result.Total_return = Results["Total_Return"]
        new_result.Benchmark_return = Results["Benchmark_Return"]
        new_result.Annualized_return = Results["Annualized_Return"]
        new_result.Max_drawdown = Results["Max_Drowdown"]
        new_result.Benchmark_max_drawdown = Results["Benchmark_Max_Drowdown"]
        new_result.pctwinners = Results["Winner_Percentage"]
        new_result.Sharpe_ratio = Results["Sharpe_Ratio"]
        new_result.save() 
        period_strategy.results = new_result
        period_strategy.save()
    else:
        period_strategy.results.Total_return = Results["Total_Return"]
        period_strategy.results.Benchmark_return = Results["Benchmark_Return"]
        period_strategy.results.Annualized_return = Results["Annualized_Return"]
        period_strategy.results.Max_drawdown = Results["Max_Drowdown"]
        period_strategy.results.Benchmark_max_drawdown = Results["Benchmark_Max_Drowdown"]
        period_strategy.results.pctwinners = Results["Winner_Percentage"]
        period_strategy.results.Sharpe_ratio = Results["Sharpe_Ratio"]
        period_strategy.save()
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)        
    ctx = {
        'strategy': period_strategy,
        'Results': Results,
        'tree_structure': tree_structure,
        'relative_path': relative_path,
    }
    return render(request, 'optimize/period_test/display_strategy_results.html',ctx)    

def PeriodExportStrategy(request, id_strategy):
    period_strategy = get_object_or_404(PeriodStrategy, id=id_strategy)
    period_strategy_dict = {}
    period_strategy_dict['strategies'] = []
    period_strategy_dict['name'] = str(period_strategy.name)
    period_strategy_dict['offset'] = str(period_strategy.offset)
    period_strategy_dict['period'] = str(period_strategy.period)
    period_strategy_dict['startdate'] = str(period_strategy.startdate)
    period_strategy_dict['enddate'] = str(period_strategy.enddate)
    if period_strategy.strategy:
        strategy_dict = {} #model_to_dict(strategy)
        technicals = Indicator.objects.filter(strategy_id = period_strategy.strategy.id)   #.exclude(rule_id = 999999999)
        buyrules = period_strategy.strategy.buyrule.all()
        sellrules = period_strategy.strategy.sellrule.all()
        rules = period_strategy.strategy.rule.all()
        rulecombinations = period_strategy.strategy.rulecombination.all()
        strategy_dict['name'] = str(period_strategy.strategy.name)
        strategy_dict['capital'] = str(period_strategy.strategy.capital)
        strategy_dict['positions'] = str(period_strategy.strategy.positions)
        strategy_dict['commissions'] = str(period_strategy.strategy.commissions)
        strategy_dict['benchmark'] = str(period_strategy.strategy.benchmark)
        strategy_dict['transaction_type'] = str(period_strategy.strategy.transaction_type)
        strategy_dict['frequency'] = str(period_strategy.strategy.frequency)
        strategy_dict['universe'] = str(period_strategy.strategy.universe)
        strategy_dict['rank_rebalance_type'] = str(period_strategy.strategy.rank_rebalance_type)
        strategy_dict['startdate'] = str(period_strategy.strategy.startdate)
        strategy_dict['enddate'] = str(period_strategy.strategy.enddate)
        strategy_dict['technicals'] = []
        strategy_dict['buyrules'] = []
        strategy_dict['sellrules'] = []
        strategy_dict['rules'] = []
        strategy_dict['rulecombinations'] = []
        strategy_dict['is_liquidity_system'] = 0
        strategy_dict['is_rank_system'] = 0
        strategy_dict['indicator_combinations'] = []
        if period_strategy.strategy.liquidity_system:
            strategy_dict['is_liquidity_system'] = 1
            strategy_dict['liquidity_name'] = period_strategy.strategy.liquidity_system.name
            liquidity_indicators = Indicator.objects.filter(liquidity_system_id=period_strategy.strategy.liquidity_system.id)
            liquidity_rules = period_strategy.strategy.liquidity_system.rule.all()
            liquidity_rule_combs = period_strategy.strategy.liquidity_system.rulecombination.all()
            liquidity_liquidity_rules = period_strategy.strategy.liquidity_system.liquidity_rule.all()
            strategy_dict['liquidity_indicators'] = []    
            strategy_dict['liquidity_rules'] = []
            strategy_dict['liquidity_rulecombinations'] = []
            strategy_dict['liquidity_liquidity_rules'] = []
            strategy_dict['liquidity_indicator_combinations'] = []
            for indicator in liquidity_indicators:
                if str(indicator.polymorphic_ctype) == "indicators_ combination":
                    strategy_dict['liquidity_indicator_combinations'].append([str(indicator.coeff), str(indicator.indicator1), str(indicator.operator), str(indicator.indicator2)])            
                elif str(indicator.polymorphic_ctype) == "ppo":
                    strategy_dict['liquidity_indicators'].append([indicator.__class__.__name__,str([indicator.period1]),str([indicator.period2]),str([indicator.period3]),str(indicator.input_data),str(indicator.coeff),str(indicator.lag)])                    
                else:
                    strategy_dict['liquidity_indicators'].append([indicator.__class__.__name__,str([indicator.period]),str(indicator.input_data),str(indicator.coeff),str(indicator.lag)])
            for rule in liquidity_rules:
                strategy_dict['liquidity_rules'].append([str(rule.title),str(rule.technical1),str(rule.operator),str(rule.technical2)])
            for rulecombination in liquidity_rule_combs:
                strategy_dict['liquidity_rulecombinations'].append([str(rulecombination.title),str(rulecombination.rule1),str(rulecombination.operator),str(rulecombination.rule2)])
            for liquidityrule in liquidity_liquidity_rules:
                strategy_dict['liquidity_liquidity_rules'].append([str(liquidityrule.min_amount),str(liquidityrule.max_amount),str(liquidityrule.rule),str(liquidityrule.name)])
        if period_strategy.strategy.rank_system:
            strategy_dict['is_rank_system'] = 1
            strategy_dict['rank_name'] = period_strategy.strategy.rank_system.name
            strategy_dict['rank_indicators'] = []
            strategy_dict['rank_indicator_combinations'] = []
            rank_indicators = Indicator.objects.filter(rank_system_id=period_strategy.strategy.rank_system.id)
            strategy_dict['rank_rules'] = []
            rank_rules = period_strategy.strategy.rank_system.rule.all()
            for indicator in rank_indicators:
                if str(indicator.polymorphic_ctype) == "indicators_ combination":
                    strategy_dict['rank_indicator_combinations'].append([str(indicator.coeff), str(indicator.indicator1), str(indicator.operator), str(indicator.indicator2)])
                elif str(indicator.polymorphic_ctype) == "ppo":
                    strategy_dict['rank_indicators'].append([indicator.__class__.__name__,str([indicator.period1]),str([indicator.period2]),str([indicator.period3]),str(indicator.input_data),str(indicator.coeff),str(indicator.lag)])                    
                else:
                    strategy_dict['rank_indicators'].append([indicator.__class__.__name__,str([indicator.period]),str(indicator.input_data),str(indicator.coeff),str(indicator.lag)])
            for rank_rule in rank_rules:
                strategy_dict['rank_rules'].append([str(rank_rule.weight),str(rank_rule.name),str(rank_rule.indicator),str(rank_rule.direction)])   
        for technical in technicals:
            if str(technical.polymorphic_ctype) == "indicators_ combination":
                strategy_dict['indicator_combinations'].append([str(technical.coeff), str(technical.indicator1), str(technical.operator), str(technical.indicator2)])
            elif str(technical.polymorphic_ctype) == "ppo":
                    strategy_dict['technicals'].append([technical.__class__.__name__,str([technical.period1]),str([technical.period2]),str([technical.period3]),str(technical.input_data),str(technical.coeff),str(technical.lag)])                        
            else:
                strategy_dict['technicals'].append([technical.__class__.__name__,str([technical.period]),str(technical.input_data),str(technical.coeff),str(technical.lag)])
        for BR in buyrules:
            strategy_dict['buyrules'].append([str(BR.buyrules.title),str(BR.output()),str(BR.active)])
        for SR in sellrules:
            strategy_dict['sellrules'].append([str(SR.sellrules.title),str(SR.output()),str(SR.active)])
        for rule in rules:
            strategy_dict['rules'].append([str(rule.title),str(rule.technical1),str(rule.operator),str(rule.technical2)])
        for rulecombination in rulecombinations:
            strategy_dict['rulecombinations'].append([str(rulecombination.title),str(rulecombination.rule1),str(rulecombination.operator),str(rulecombination.rule2)])
        period_strategy_dict['strategies'].append(strategy_dict)
    userpath = settings.PERIOD_TEST + str(request.user) + '/export/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    with open(userpath+period_strategy_dict['name']+'.pickle', 'wb') as f:
        pickle.dump(period_strategy_dict, f, protocol=2)
    f.close
    """ Display all strategies """  
    tree_element = get_object_or_404(PeriodTree, child_id=id_strategy, child_type=2)
    parent_id = tree_element.parent_id
    if parent_id == -1:
        return redirect('optimize:period_manage_folder', id_folder=99999999999)
    else:
        return redirect('optimize:period_manage_folder', id_folder=parent_id)

def PeriodLoadStrategy(request):
    userpath = settings.PERIOD_TEST + str(request.user) + '/export/'
    if request.POST:
        file_name = request.POST.get("file_name")
        parent_id = request.POST.get("parent_id")
        with open(userpath + file_name + '.pickle', 'rb') as f:
            period_strategy_dict = pickle.load(f)
        period_strategy = PeriodStrategy()
        period_strategy.name = period_strategy_dict['name']
        period_strategy.offset = period_strategy_dict['offset']
        period_strategy.period = period_strategy_dict['period']
        period_strategy.startdate = period_strategy_dict['startdate']
        period_strategy.enddate = period_strategy_dict['enddate']
        period_strategy.save()
        for strategy_dict in period_strategy_dict['strategies']:
            strategy = Strategy()
            strategy.name = str(strategy_dict['name'])
            strategy.capital = int(strategy_dict['capital'])
            strategy.positions = int(strategy_dict['positions'])
            strategy.commissions = float(strategy_dict['commissions'])
            strategy.transaction_type = str(strategy_dict['transaction_type'])
            strategy.frequency = str(strategy_dict['frequency'])
            strategy.rank_rebalance_type = str(strategy_dict['rank_rebalance_type'])
            universe_id = []
            universe_string = []
            default_universe = Universe_Tree.objects.filter(child_type=2, permission=1)
            for element in default_universe:
                universe_id.append(element.id)
                universe_string.append(str(element))
            user_universe = Universe_Tree.objects.filter(permission=0, child_type=2, user=request.user)
            for element in user_universe:
                universe_id.append(element.id)
                universe_string.append(str(element))
            universe_list = Universe_Tree.objects.filter(id__in=universe_id)
            if strategy_dict['universe'] in universe_string:
                for element in universe_list:
                    if str(element) == strategy_dict['universe']:
                        strategy.universe = element
            else:
                if strategy_dict['universe'] != "None":
                    universe_name = strategy_dict['universe']
                    parent_folder_id = 0
                    new_universe = Universe_Universe()
                    new_universe.name = universe_name
                    new_universe.user = request.user
                    new_universe.parent_id = parent_folder_id
                    new_universe.parent_path = ""
                    new_universe.save()
                    userpath = settings.UNIVERSES +str(request.user) + '/'
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
                    strategy.universe = new_tree

            benchmark_id = []
            benchmark_string = []
            default_benchmark = Benchmarks_Tree.objects.filter(child_type=2, permission=1)
            for element in default_benchmark:
                benchmark_id.append(element.id)
                benchmark_string.append(str(element))
            user_benchmark = Benchmarks_Tree.objects.filter(permission=0, child_type=2, user=request.user)
            for element in user_benchmark:
                benchmark_id.append(element.id)
                benchmark_string.append(str(element))
            benchmark_list = Benchmarks_Tree.objects.filter(id__in=benchmark_id)
            if strategy_dict['benchmark'] in benchmark_string:
                for element in benchmark_list:
                    if str(element) == strategy_dict['benchmark']:
                        strategy.benchmark = element
            else:
                if strategy_dict['benchmark'] != "None":
                    universe_name = strategy_dict['benchmark']
                    parent_folder_id = 0
                    new_universe = Benchmarks_Universe()
                    new_universe.name = universe_name
                    new_universe.user = request.user
                    new_universe.parent_id = parent_folder_id
                    new_universe.parent_path = ""
                    new_universe.save()
                    userpath = settings.BENCHMARKS +str(request.user) + '/'
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
                    strategy.benchmark = new_tree
            strategy.startdate = strategy_dict['startdate']
            strategy.enddate = strategy_dict['enddate']
            strategy.user = request.user
            strategy.save()
            technicals = []
            buy_rules = []
            sell_rules = []
            for technical in strategy_dict['technicals']:
                try:
                    if technical[0] == "Ppo":
                        input_data_id = Input_data.objects.get(input_data=technical[4])
                    else:
                        input_data_id = Input_data.objects.get(input_data=technical[2])
                    try:
                        technicals.append(eval(technical[0])(coeff=technical[3], input_data=input_data_id, lag=technical[4], strategy_id=strategy.id).save())
                    except:
                        if technical[0] == "Ppo":
                            technicals.append(eval(technical[0])(coeff=technical[5], period1=technical[1][1:-1],period2=technical[2][1:-1],period3=technical[3][1:-1], input_data=input_data_id, lag=technical[6],strategy_id=strategy.id).save())    
                        else:
                            technicals.append(eval(technical[0])(coeff=technical[3], period=technical[1][1:-1], input_data=input_data_id, lag=technical[4],strategy_id=strategy.id).save())
                except:
                    technicals.append(eval(technical[0])(coeff=technical[3], strategy_id=strategy.id).save())
            for indicator_comb in strategy_dict['indicator_combinations']:
                indicator_combinations = Indicators_Combination(strategy_id=strategy.id)
                tech_coms = Indicator.objects.filter(strategy_id=strategy.id)
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
            tech_coms = Indicator.objects.filter(strategy_id=strategy.id)
            for rule in strategy_dict['rules']:
                tech1 = ''
                tech2 = ''
                for tech in tech_coms:
                    if rule[1] == str(tech):
                        tech1 = tech
                    if rule[3] == str(tech):
                        tech2 = tech
                strategy.rule.create(title=rule[0], technical1=tech1, operator=rule[2], technical2=tech2,
                                strategy_id=strategy.id)
            for rulecomb in strategy_dict['rulecombinations']:
                rules = PrimaryRule.objects.filter(strategy_id=strategy.id)
                rule1 = ''
                rule2 = ''
                for rule in rules:
                    if rulecomb[1] == str(rule):
                        rule1 = rule 
                    if rulecomb[3] == str(rule):
                        rule2 = rule    
                strategy.rulecombination.create(title=rulecomb[0], rule1=rule1, operator=rulecomb[2], rule2=rule2,
                                strategy_id=strategy.id)    
            rules = PrimaryRule.objects.filter(strategy_id=strategy.id)
            for buyrule in strategy_dict['buyrules']:
                rule_id = ''
                for rule in rules:
                    comparerule = str(rule).replace(' ', '') 
                    if buyrule[1] == comparerule:
                        rule_id = rule.id
                new_buyrule = BuyRule(buyrules=PrimaryRule.objects.get(id=rule_id))
                new_buyrule.active = buyrule[2]
                new_buyrule.save()
                strategy.buyrule.add(new_buyrule)
            for sellrule in strategy_dict['sellrules']:
                rule_id = ''
                for rule in rules:
                    comparerule = str(rule).replace(' ', '') 
                    if sellrule[1] == comparerule:
                        rule_id = rule.id
                new_sellrule = SellRule(sellrules=PrimaryRule.objects.get(id=rule_id))
                new_sellrule.active = sellrule[2]
                new_sellrule.save()
                strategy.sellrule.add(new_sellrule)
        #liquidity_system import
            if strategy_dict['is_liquidity_system']:
                liquidity_system = Liquidity_System()
                liquidity_system.name = strategy_dict['liquidity_name']
                liquidity_system.save()
                last_liquidity_system = Liquidity_System.objects.last()
                technicals = []
                for technical in strategy_dict['liquidity_indicators']:
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
                for indicator_comb in strategy_dict['liquidity_indicator_combinations']:
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
                for rule in strategy_dict['liquidity_rules']:
                    tech1 = ''
                    tech2 = ''
                    for tech in tech_coms:
                        if rule[1] == str(tech):
                            tech1 = tech
                        if rule[3] == str(tech):
                            tech2 = tech
                    liquidity_system.rule.create(title=rule[0], technical1=tech1, operator=rule[2], technical2=tech2, strategy_id=0, liquidity_system_id=last_liquidity_system.id)
                for rulecomb in strategy_dict['liquidity_rulecombinations']:
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
                for liquidity_rule in strategy_dict['liquidity_liquidity_rules']:
                    rule1 = ''
                    for rule in rules:
                        if liquidity_rule[2] == str(rule):
                            rule1 = rule
                    liquidity_system.liquidity_rule.create(min_amount=liquidity_rule[0], max_amount=liquidity_rule[1], name=liquidity_rule[3],rule=rule1,)
                liquidity_system.user = request.user
                liquidity_system.save()
                new_tree = Liquidity_Tree()
                new_tree.child_id = liquidity_system.id
                new_tree.child_name = liquidity_system.name
                new_tree.child_type = 2
                new_tree.parent_id = 0
                new_tree.user = request.user
                new_tree.save()
                strategy.liquidity_system = liquidity_system
                strategy.save()
        # end liquidiy_system import    
        # rank_system import
            if strategy_dict['is_rank_system']:
                ranking_system = Ranking_System()
                ranking_system.name = strategy_dict['rank_name']      
                ranking_system.save()
                last_ranking_system = Ranking_System.objects.last()
                technicals = []
                for technical in strategy_dict['rank_indicators']:
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
                for indicator_comb in strategy_dict['rank_indicator_combinations']:
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
                for rank_rule in strategy_dict['rank_rules']:
                    tech1 = ''
                    for tech in tech_coms:
                        if rank_rule[2] == str(tech):
                            tech1 = tech
                    ranking_system.rule.create(weight=rank_rule[0], name=rank_rule[1], indicator=tech1, direction=rank_rule[3], rank_id=last_ranking_system.id)
                ranking_system.user = request.user
                ranking_system.save()           
                new_tree = Ranking_Tree()
                new_tree.child_id = ranking_system.id
                new_tree.child_name = ranking_system.name
                new_tree.child_type = 2
                new_tree.parent_id = 0
                new_tree.user = request.user
                new_tree.save() 
                strategy.rank_system = ranking_system
                strategy.save() 
        # end rank_system    
            new_tree = Tree()
            new_tree.child_id =strategy.id
            new_tree.child_name = strategy.name
            new_tree.child_type = 2
            new_tree.parent_id = 0
            new_tree.user = request.user
            new_tree.save()        
            period_strategy.strategy = strategy
            period_strategy.save()
        if parent_id == "d":
            if not PeriodTree.objects.filter(permission=1).exists():
                default_folder = PeriodTree()
                default_folder.child_id = -1
                default_folder.child_type = 1
                default_folder.child_name = "Default Folder"
                default_folder.parent_id = 0
                default_folder.user = request.user
                default_folder.permission = 1
                default_folder.save()
            else:
                default_folder = get_object_or_404(PeriodTree, permission=1, child_type=1)
            new_tree = PeriodTree()
            new_tree.child_id =period_strategy.id
            new_tree.child_name = period_strategy.name
            new_tree.child_type = 2
            new_tree.parent_id = default_folder.child_id
            new_tree.permission = 1
            new_tree.user = request.user
            new_tree.save()
            return redirect('optimize:period_manage_strategy', id_strategy=period_strategy.id)
        new_tree = PeriodTree()
        new_tree.child_id =period_strategy.id
        new_tree.child_name = period_strategy.name
        new_tree.child_type = 2
        new_tree.parent_id = parent_id
        new_tree.user = request.user
        new_tree.save()  
        return redirect('optimize:period_manage_strategy', id_strategy=period_strategy.id)    
    load_file_list = []
    with os.scandir(userpath) as entries:
        for entry in entries:
            if not entry.is_file():
                continue
            filename, file_extension = os.path.splitext(entry.name)
            if file_extension.lower() != ".pickle":
                continue
            load_file_list.append(filename)      
    folders = PeriodFolder.objects.all().filter(user_id=request.user)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'load_list': load_file_list,
        'folders': folders,
        'tree_structure':tree_structure,
    }            
    return render(request, 'optimize/period_test/load_file_list.html', ctx)      

def PeriodResults(request):
    period_tree = PeriodTree.objects.all().filter(child_type=2, user=request.user).last()
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)    
    if period_tree:
        period_strategy = get_object_or_404(PeriodStrategy, id=period_tree.child_id)
        relative_path = get_path(period_strategy.id)
        userpath = settings.USERS_DIRECTORY + str(request.user) + "/period_bias_test/" + relative_path + str(period_strategy.name)
        if os.path.exists(userpath + '/Results.pickle'):
            with open(userpath+'/Results.pickle', 'rb') as f:
                Results = pickle.load(f)
            ctx = {
                'strategy': period_strategy,
                'Results': Results,
                'tree_structure': tree_structure,
                'relative_path': relative_path,
            }
            return render(request, 'optimize/period_test/display_strategy_results.html',ctx)            
        else:
            ctx = {
                'noavaliable': 'No Results',
                'tree_structure': tree_structure,
            }      
            return render(request, 'optimize/period_test/display_strategy_results.html',ctx)                  
    else:
        ctx = {
            'nostrategy': 'No Period Strategy',
            'tree_structure': tree_structure,            
        }      
        return render(request, 'optimize/period_test/display_strategy_results.html',ctx)         