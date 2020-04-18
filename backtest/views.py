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

from backtest.models import (Adx, Atrn, BarSinceEntry, Benchmark, BuyRule,
                             Constant, Ema, HighDS, LowDS, OpenDS, Ppo,
                             PriceDS, PrimaryRule, Result, Roc, Rsi, Rule,
                             RuleCombination, SellRule,  Slope, Sma, Universe,
                             Strategy, Indicator, Input_data, Category, Tree, IndicatorProperty, 
                             Indicators_Combination, CombFolder, CombTree, CombinationStrategy,
                             BuyStrategy)

from .forms import ( BuyRuleForm, DeleteRuleForm, GeneralStrategyForm,
                     ModifyRuleForm, ResultForm, RuleCombinationForm, 
                     RuleForm, SellRuleForm,  StrategyForm, IndicatorCombinationForm, 
                     CombinationStrategyForm, GeneralCombStrategyForm)

from tools.models import (Ranking_System, Ranking_Tree, Liquidity_System , Liquidity_Tree,
                        Universe_Universe, Universe_Tree, Benchmarks_Tree, Benchmarks_Universe)
                            # Indicators_Combination_System

from .Script import interactive_process
from django.conf import settings
from django.views import View

def compare(temp):
        strtemp = str(temp)
        if strtemp == "":
            strtemp = 100
            return strtemp
        if strtemp == "None":
            strtemp = 100
            return strtemp
        else: 
            return strtemp

def get_tree_list(user_id):
    tree_list = []
    list_item = {}
    get_default_trees = Tree.objects.all().filter(permission=1)
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
    get_tree_lists = Tree.objects.all().filter(user_id=user_id, permission=0)
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

# def getIndicatorComb(user_id):
#     element_tree = []
#     indicator_system = Indicators_Combination_System.objects.filter(Q(user_id=user_id) | Q(user_id__isnull=True))
#     for elment in indicator_system:
#         element_tree.append({
#             "id": -elment.id,
#             "icon": "fa fa-plus",
#             "text": str(elment),
#             "state": {
#                 "opened": 1
#             },
#             "children": []
#         })
#     return element_tree

def getIndicatorTree(user_id):
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
    # indicator_tree.append({
    #     "id": 20000,
    #     "text": "Indicator Combination",
    #     "state": {
    #         "opened": 1
    #     },
    #     "children": getIndicatorComb(user_id)
    # })
    return  indicator_tree      

def get_path(strategy_id):
    tree_element = get_object_or_404(Tree, child_id=strategy_id, child_type=2, permission=0)
    if tree_element.parent_id == 0:
        return ""
    else:
        category_element = get_object_or_404(Category, id=tree_element.parent_id)
        return category_element.path

@login_required
def Index(request):
    return render(request, 'base.html')

@login_required
def LoadStrategyList(request):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    userpath = settings.STRATEGIES + str(request.user) + '/export/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)    
    if request.POST:
        file_name = request.POST.get("file_name")
        parent_id = request.POST.get("parent_id")
        strategy = Strategy()
        name = file_name
        strategy.name = name   
        with open(userpath+name+'.pickle', 'rb') as f:
            strategy_dict = pickle.load(f)
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
        strategy = Strategy.objects.last()
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
                        technicals.append(eval(technical[0])(coeff=technical[5], period1=technical[1][1:-1],period2=technical[2][1:-1],period3=technical[3][1:-1], input_data=input_data_id, lag=technical[6],strategy_id=0, liquidity_system_id=last_liquidity_system.id).save())    
                    except:
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
        if parent_id == "d":
            if not Tree.objects.filter(permission=1).exists():
                default_folder = Tree()
                default_folder.child_id = -1
                default_folder.child_type = 1
                default_folder.child_name = "Default Folder"
                default_folder.parent_id = 0
                default_folder.user = request.user
                default_folder.permission = 1
                default_folder.save()
            else:
                default_folder = get_object_or_404(Tree, permission=1, child_type=1)
            new_tree = Tree()
            new_tree.child_id =strategy.id
            new_tree.child_name = strategy.name
            new_tree.child_type = 2
            new_tree.parent_id = default_folder.child_id
            new_tree.permission = 1
            new_tree.user = request.user
            new_tree.save()
            return redirect('backtest:manage_default_strategies')
        new_tree = Tree()
        new_tree.child_id =strategy.id
        new_tree.child_name = strategy.name
        new_tree.child_type = 2
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('backtest:display', id=strategy.id)
    load_file_list = []
    with os.scandir(userpath) as entries:
        for entry in entries:
            if not entry.is_file():
                continue
            filename, file_extension = os.path.splitext(entry.name)
            if file_extension.lower() != ".pickle":
                continue
            load_file_list.append(filename)
    categories = Category.objects.all().filter(user_id = request.user)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'strategies': strategies,
        'load_list': load_file_list,
        'tree_structure': tree_structure,
        'categories': categories
    }
    return render(request, 'backtest/load_file_list.html', ctx)

@login_required
def AddStrategy(request):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    form = StrategyForm(request.POST or None)
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if form.is_valid():
        new_strategy = form.save()
        new_strategy.user = request.user
        new_strategy.save()
        new_tree = Tree()
        new_tree.child_id =new_strategy.id
        new_tree.child_name = new_strategy.name
        new_tree.child_type = 2
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('backtest:display', id=new_strategy.id)
    categories = Category.objects.all().filter(user_id = request.user)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'form': form,
        'strategies': strategies,
        'categories': categories,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/add_strategy.html', ctx)

@login_required
def DeleteStrategy(request, id_strategy):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    strategy = get_object_or_404(Strategy, id=id_strategy)
    form = StrategyForm(request.POST or None, instance=strategy)
    strategies = Strategy.objects.all().filter(user_id=request.user) # get all strategies
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if form.is_valid():
        rules = strategy.rule.all()
        for rule in rules:
            strategy.rule.remove(rule)
            rule.delete()        
        strategy_tree = Tree.objects.filter(child_id = id_strategy, child_type=2)
        strategy_tree.delete()
        technicals = Indicator.objects.filter(strategy_id = id_strategy).order_by('-id')
        for technical in technicals:
            technical.delete()
        strategy.delete()      
        return redirect('backtest:managestrategies')
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'strategies': strategies,
        'strategy': strategy,
        'form': form,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/delete_strategy.html', ctx)

@login_required
def MoveStrategy(request, id_strategy):
    if request.POST:
        new_parent_id = request.POST.get("parent_id")
        old_parent = get_object_or_404(Tree, child_type=2, child_id=id_strategy)
        old_parent.parent_id = new_parent_id
        old_parent.save()
        return redirect('backtest:managestrategies')
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    categories = Category.objects.all().filter(user_id = request.user)
    ctx = {
        'categories': categories,
        'tree_structure': tree_structure,
        'id_strategy': id_strategy,
    }
    return render(request, 'backtest/move_strategy.html', ctx)

@login_required
def DisplayStrategy(request, id):
    strategy = get_object_or_404(Strategy, id=id)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    if Tree.objects.filter(child_id=id, child_type=2, parent_id=-1).exists():
        relative_path = "Default Folder/"
    else:
        relative_path = get_path(id)
    indicator_combinations = Indicators_Combination.objects.filter(strategy_id=id)
    ctx = {
        'strategy': strategy,
        'tree_structure': tree_structure,
        'indicator_combinations': indicator_combinations,
        'relative_path': relative_path,
    }
    return render(request, 'backtest/strategies/manage_strategy.html', ctx)

@login_required
def ExportStrategy(request, id_strategy):
    strategy = get_object_or_404(Strategy, id=id_strategy)
    strategy_dict = {} #model_to_dict(strategy)
    technicals = Indicator.objects.filter(strategy_id = id_strategy)   #.exclude(rule_id = 999999999)
    buyrules = strategy.buyrule.all()
    sellrules = strategy.sellrule.all()
    rules = strategy.rule.all()
    rulecombinations = strategy.rulecombination.all()
    strategy_dict['name'] = str(strategy.name)
    strategy_dict['capital'] = str(strategy.capital)
    strategy_dict['positions'] = str(strategy.positions)
    strategy_dict['commissions'] = str(strategy.commissions)
    strategy_dict['benchmark'] = str(strategy.benchmark)
    strategy_dict['transaction_type'] = str(strategy.transaction_type)
    strategy_dict['frequency'] = str(strategy.frequency)
    # strategy_dict['slippage'] = str(strategy.slippage)
    strategy_dict['universe'] = str(strategy.universe)
    strategy_dict['rank_rebalance_type'] = str(strategy.rank_rebalance_type)
    strategy_dict['startdate'] = str(strategy.startdate)
    strategy_dict['enddate'] = str(strategy.enddate)
    strategy_dict['technicals'] = []
    strategy_dict['buyrules'] = []
    strategy_dict['sellrules'] = []
    strategy_dict['rules'] = []
    strategy_dict['rulecombinations'] = []
    strategy_dict['is_liquidity_system'] = 0
    strategy_dict['is_rank_system'] = 0
    strategy_dict['indicator_combinations'] = []
    if strategy.liquidity_system:
        strategy_dict['is_liquidity_system'] = 1
        strategy_dict['liquidity_name'] = strategy.liquidity_system.name
        liquidity_indicators = Indicator.objects.filter(liquidity_system_id=strategy.liquidity_system.id)
        liquidity_rules = strategy.liquidity_system.rule.all()
        liquidity_rule_combs = strategy.liquidity_system.rulecombination.all()
        liquidity_liquidity_rules = strategy.liquidity_system.liquidity_rule.all()
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
    if strategy.rank_system:
        strategy_dict['is_rank_system'] = 1
        strategy_dict['rank_name'] = strategy.rank_system.name
        strategy_dict['rank_indicators'] = []
        strategy_dict['rank_indicator_combinations'] = []
        rank_indicators = Indicator.objects.filter(rank_system_id=strategy.rank_system.id)
        strategy_dict['rank_rules'] = []
        rank_rules = strategy.rank_system.rule.all()
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
    userpath = settings.STRATEGIES + str(request.user) + '/export/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    with open(userpath+strategy_dict['name']+'.pickle', 'wb') as f:
        pickle.dump(strategy_dict, f, protocol=2)
    f.close
    """ Display all strategies """
    return redirect('backtest:managestrategies')

@login_required
def ModifyGeneralStrategy(request,id_strategy):
    flag = 0
    strategies = Strategy.objects.all().filter(user_id=request.user)
    strategy = get_object_or_404(Strategy, id=id_strategy)
    form = GeneralStrategyForm(request.POST or None, instance=strategy)

    liquidity_system_id = []
    default_liquidity_system = Liquidity_Tree.objects.filter(parent_id=-1, permission=1)
    for element in default_liquidity_system:
        liquidity_system_id.append(element.child_id)
    user_liquidity_system = Liquidity_Tree.objects.filter(permission=0, user=request.user, child_type=2)
    for element in user_liquidity_system:
        liquidity_system_id.append(element.child_id)
    form.fields["liquidity_system"].queryset= Liquidity_System.objects.filter(id__in=liquidity_system_id)

    rank_system_id = []
    default_rank_system = Ranking_Tree.objects.filter(parent_id=-1, permission=1)
    for element in default_rank_system:
        rank_system_id.append(element.child_id)
    user_rank_system = Ranking_Tree.objects.filter(permission=0, user=request.user, child_type=2)
    for element in user_rank_system:
        rank_system_id.append(element.child_id)    
    form.fields["rank_system"].queryset = Ranking_System.objects.filter(id__in=rank_system_id)

    universe_id = []
    default_universe = Universe_Tree.objects.filter(child_type=2, permission=1)
    for element in default_universe:
        universe_id.append(element.id)
    user_universe = Universe_Tree.objects.filter(permission=0, child_type=2, user=request.user)
    for element in user_universe:
        universe_id.append(element.id)
    form.fields["universe"].queryset = Universe_Tree.objects.filter(id__in=universe_id)

    benchmark_id = []
    default_benchmark = Benchmarks_Tree.objects.filter(child_type=2, permission=1)
    for element in default_benchmark:
        benchmark_id.append(element.id)
    user_benchmark = Benchmarks_Tree.objects.filter(permission=0, child_type=2, user=request.user)
    for element in user_benchmark:
        benchmark_id.append(element.id)
    form.fields["benchmark"].queryset = Benchmarks_Tree.objects.filter(id__in=benchmark_id)    
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if str(strategy.capital) != str(request.POST.get('capital')) : 
        flag=1
    if str(strategy.commissions) != str(request.POST.get('commissions')) : 
        flag=1
    if str(strategy.positions) != str(request.POST.get('positions')) : 
        flag=1
    if str(strategy.startdate) != str(request.POST.get('startdate')) : 
        flag=1
    if str(strategy.enddate) != str(request.POST.get('enddate')) : 
        flag=1
    if compare(strategy.benchmark_id) != compare(request.POST.get('benchmark')) : 
        flag=1
    if compare(strategy.universe_id) != compare(request.POST.get('universe')) : 
        flag=1
    if form.is_valid():  
        if flag == 1:
            if strategy.state != "red":
                strategy.state = "yellow"
                strategy.save()
        form.save()
        return redirect("backtest:display", id=id_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'strategies': strategies,
        'strategy': strategy,
        'form': form,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/modify_generalstrategy.html', ctx)

@login_required
def Strategystate(request, id_strategy):
    strategy = get_object_or_404(Strategy, id=id_strategy)
    if Tree.objects.filter(child_id=id_strategy, child_type=2, parent_id=-1).exists():
        relative_path = "default/"
    else:
        relative_path = get_path(id_strategy)
    userpath = settings.USERS_DIRECTORY+str(request.user)+"/Strategies/"+relative_path + str(strategy.name) +'/Results.pickle'   
    if os.path.exists(userpath):
        if strategy.state == "yellow":
            msg = strategy.state
            json_data = json.dumps(msg)
            return HttpResponse(json_data, content_type='application/json')  
        else: 
            strategy.state = "green"
            strategy.save()
            msg = strategy.state
            json_data = json.dumps(msg)
            return HttpResponse(json_data, content_type='application/json')    
    else:
        strategy.state = "red"
        strategy.save()
        msg =  strategy.state
        json_data = json.dumps(msg)
        return HttpResponse(json_data, content_type='application/json')

def ajax_get_strategy(request):
    tree_id = request.GET.get("id")
    tree_element = get_object_or_404(Tree, id=tree_id)
    msg = {
        "child_type": tree_element.child_type,
        "child_id": tree_element.child_id,
        "permission": tree_element.permission,
    }
    json_data = json.dumps(msg)
    return HttpResponse(json_data, content_type='application/json')

@login_required
def AddRule(request, id_strategy):
    instantiate = Rule(strategy_id=id_strategy)
    if request.POST:
        post = request.POST.copy() # to make it mutable
        technical_1 = post['technical1']
        technical_2 = post['technical2']
        tech_coms  = Indicator.objects.filter(strategy_id=id_strategy)
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
    form = RuleForm(id_strategy,999999999, request.POST or None, instance=instantiate)
    strategy = get_object_or_404(Strategy, id=id_strategy)
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if form.is_valid():
        new_rule = form.save()
        strategy.rule.add(new_rule)        
        return redirect("backtest:display", id=id_strategy)
    indicator_tree = []
    indicator_tree = getIndicatorTree(request.user.id)
    ctx = {
        'strategy': strategy,
        'form': form,
        'id_strategy': id_strategy,
        'indicator_tree': indicator_tree
    }
    return render(request, 'backtest/add_rule.html', ctx)

@login_required
def ModifyRule(request, id_rule, id_strategy):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    rule = get_object_or_404(Rule, id=id_rule)
    if request.POST:
        post = request.POST.copy() # to make it mutable
        technical_1 = post['technical1']
        technical_2 = post['technical2']
        tech_coms  = Indicator.objects.filter(strategy_id=id_strategy)
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
    form = ModifyRuleForm(id_strategy,id_rule, request.POST or None, instance=rule)
    strategy = get_object_or_404(Strategy, id=id_strategy)
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if form.is_valid():
        new_rule = form.save()
        strategy.rule.add(new_rule)
        return redirect("backtest:display", id=id_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'strategies': strategies,
        'strategy': strategy,
        'rule': rule,
        'form': form,
        'id_rule': id_rule,
        'id_strategy': id_strategy, 
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/modify_rule.html', ctx)

@login_required
def Rulestatus(request, id_strategy):
    if request.POST:
        msg = "success"
        rulestatus = json.loads(request.POST['rule_status'])
        buyrule_checked = rulestatus['buyrule_checked']
        buyrule_unchecked = rulestatus['buyrule_unchecked']
        sellrule_checked = rulestatus['sellrule_checked']
        sellrule_unchecked = rulestatus['sellrule_unchecked']
        for col in buyrule_checked:
            buyrule = get_object_or_404(BuyRule, id=col)
            buyrule.active = 1
            buyrule.save()
        for col in buyrule_unchecked:
            buyrule = get_object_or_404(BuyRule, id=col)
            buyrule.active = 0
            buyrule.save()
        for col in sellrule_checked:
            sellrule = get_object_or_404(SellRule, id=col)
            sellrule.active = 1
            sellrule.save()
        for col in sellrule_unchecked:
            sellrule = get_object_or_404(SellRule, id=col)
            sellrule.active = 0
            sellrule.save()
        json_data = json.dumps(msg)
    return HttpResponse(json_data, content_type='application/json')

@login_required
def ajax_get_rules(request, id_strategy):
    technical_1 = Indicator.objects.filter(strategy_id=id_strategy)
    rule_str = ''
    for technical in technical_1:
        rule_str = rule_str + str(technical) + '#'
    return HttpResponse(rule_str)

@login_required
def ajax_get_rule(request, id_rulecombination, id_strategy):
    rule = ''
    rulecombination = get_object_or_404(RuleCombination, primaryrule_ptr_id=id_rulecombination)
    rule1 = get_object_or_404(PrimaryRule, id=rulecombination.rule1_id)
    rule2 = get_object_or_404(PrimaryRule, id=rulecombination.rule2_id)
    rule = str(rule1) + '#' + str(rule2)
    return HttpResponse(rule)

@login_required
def AddRuleCombination(request, id_strategy):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    instantiate = RuleCombination(strategy_id=id_strategy)
    if request.POST:
        post = request.POST.copy() # to make it mutable
        rule_coms = PrimaryRule.objects.filter(strategy_id=id_strategy)
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
    form = RuleCombinationForm(id_strategy,request.POST or None, instance=instantiate)
    strategy = get_object_or_404(Strategy, id=id_strategy)
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if form.is_valid():
        new_rulecombination = form.save()
        strategy.rulecombination.add(new_rulecombination)        
        return redirect("backtest:display", id=id_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'strategies': strategies,
        'strategy': strategy,
        'form': form,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/add_rulecombination.html', ctx)

@login_required
def ModifyRuleCombination(request, id_rulecombination, id_strategy):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    rulecombination = get_object_or_404(RuleCombination, id=id_rulecombination)
    if request.POST:
        post = request.POST.copy() # to make it mutable
        rule_coms = PrimaryRule.objects.filter(strategy_id=id_strategy)
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
    form = RuleCombinationForm(id_strategy,request.POST or None, instance=rulecombination)
    strategy = get_object_or_404(Strategy, id=id_strategy) 
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if form.is_valid():
        new_rulecombination = form.save()
        strategy.rulecombination.add(new_rulecombination)
        return redirect("backtest:display", id=id_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'strategies': strategies,
        'strategy': strategy,
        'form': form,
        'id_rulecombination': id_rulecombination,
        'id_strategy': id_strategy,
        'rulecombination': rulecombination,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/modify_rulecombination.html', ctx)

@login_required
def ajax_get_combination_add(request, id_strategy):
    technical_1 = PrimaryRule.objects.filter(strategy_id=id_strategy)
    rule_str = ''
    for technical in technical_1:
        rule_str = rule_str + str(technical) + '#'
    return HttpResponse(rule_str)

@login_required
def ajax_get_combination_modify(request, id_strategy, id_rulecombination):
    technical_1 = Rule.objects.filter(strategy_id=id_strategy)
    rule_str = ''
    for technical in technical_1:
        rule_str = rule_str + str(technical) + '#'
    return HttpResponse(rule_str)

@login_required
def AddBuyRule(request, id_strategy):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    strategy = get_object_or_404(Strategy, id=id_strategy)
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if request.POST:
        buy_rule = request.POST.get('buy_rule')  
        flag = buy_rule.count(',')
        rule_coms = PrimaryRule.objects.filter(strategy_id=id_strategy)
        if flag == 0 :
            pr_id = ''
            for rule_com in rule_coms:
                if  buy_rule == str(rule_com).lower():
                    pr_id = rule_com.id
            new_buyrule = BuyRule(buyrules=PrimaryRule.objects.get(id=pr_id))
            new_buyrule.save()
            strategy.buyrule.add(new_buyrule)
            if strategy.state != "red":
                strategy.state = "yellow"
                strategy.save()
            return redirect("backtest:display", id=id_strategy)
        else :
            buy_rule = buy_rule.rsplit(',')
            for buy in buy_rule:
                pr_id = ''
                for rule_com in rule_coms:
                    if  buy == str(rule_com).lower():
                        pr_id = rule_com.id
                new_buyrule = BuyRule(buyrules=PrimaryRule.objects.get(id=pr_id))
                new_buyrule.save()
                strategy.buyrule.add(new_buyrule)
                if strategy.state != "red":
                    strategy.state = "yellow"
                    strategy.save()
            return redirect("backtest:display", id=id_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'strategies': strategies,
        'strategy': strategy,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/add_buyrule.html', ctx)

@login_required
def AddSellRule(request, id_strategy):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    strategy = get_object_or_404(Strategy, id=id_strategy)
    # Quoiqu'il arrive, on affiche la page du formulaire.
    if request.POST:
        sell_rule = request.POST.get('sell_rule') 
        flag = sell_rule.count(',')
        rule_coms = PrimaryRule.objects.filter(strategy_id=id_strategy)
        if flag == 0 :
            pr_id = ''
            for rule_com in rule_coms:
                if request.POST.get('sell_rule') == str(rule_com).lower():
                    pr_id = rule_com.id
            new_sellrule = SellRule(sellrules=PrimaryRule.objects.get(id=pr_id))
            new_sellrule.save()
            strategy.sellrule.add(new_sellrule)
            if strategy.state != "red":
                strategy.state = "yellow"
                strategy.save()
            return redirect("backtest:display", id=id_strategy)
        else :
            sell_rule = sell_rule.rsplit(',')
            for sell in sell_rule:
                pr_id = ''
                for rule_com in rule_coms:
                    if  sell == str(rule_com).lower():
                        pr_id = rule_com.id
                new_sellrule = SellRule(sellrules=PrimaryRule.objects.get(id=pr_id))
                new_sellrule.save()
                strategy.sellrule.add(new_sellrule)
            if strategy.state != "red":
                strategy.state = "yellow"
                strategy.save()
            return redirect("backtest:display", id=id_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'strategy': strategy,
        'strategies': strategies,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/add_sellrule.html', ctx)

@login_required
def AddIndicator(request, source, indicator, id_rule, id_strategy):
    instantiate = eval(indicator+"(strategy_id=id_strategy)")
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
        if id_rule == 999999999:
            if source == 'comb':
                return redirect('backtest:add_indicator_combination', id_strategy=id_strategy)
            elif source == 'add':
                form = RuleForm(id_strategy,id_rule,None)
                return redirect("backtest:add_rule", id_strategy=id_strategy)
        else:
            rule = get_object_or_404(Rule, id=id_rule)
            form = RuleForm(id_strategy,id_rule,None, instance=rule) 
            return redirect("backtest:modify_rule", id_rule=id_rule, id_strategy=id_strategy)
    indicator_property = get_object_or_404(IndicatorProperty, indicator=indicator)
    ctx = {
        'source': source,
        'indicator': indicator,
        'id_rule': id_rule,
        'id_strategy': id_strategy,
        'form': form,
        'indicator_property': indicator_property,
    }
    return render(request, 'backtest/add_indicator.html', ctx)

@login_required
def ModifyIndicator(request, indicator, tech_id, id_strategy, requestfrom, requestrule):
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
            return redirect("backtest:add_rule", id_strategy=id_strategy)
        elif requestfrom == 'modify':
            return redirect("backtest:modify_rule", id_rule=requestrule, id_strategy=id_strategy)  

@login_required
def DeleteIndicator(request, tech_id, id_strategy, requestfrom, requestrule):
    tech_indicator = get_object_or_404(Indicator, id=tech_id)
    tech_indicator.delete()
    if requestfrom == 'add':
        return redirect("backtest:add_rule", id_strategy=id_strategy)
    elif requestfrom == 'modify':
        return redirect("backtest:modify_rule", id_rule=requestrule, id_strategy=id_strategy)

@login_required
def GetIndicator(request):    
    techindicator = request.GET.get('techindicator')
    id_strategy = request.GET.get('id_strategy')
    requestfrom = request.GET.get('from')
    if requestfrom == 'add':
        requestrule = 0
    elif requestfrom == 'modify':
        requestrule = request.GET.get('ruleid')
    indicator = ''
    tech_coms = Indicator.objects.filter(strategy_id=id_strategy)
    tech_id = ''
    for tech_com in tech_coms:
        if techindicator == str(tech_com).lower():
            tech_id = tech_com.id
    instantiate = get_object_or_404(Indicator, id=tech_id)
    indicator_temp = str(instantiate.polymorphic_ctype).replace(' ', '')
    if indicator_temp == "indicators_combination":
        ctx = {
            'deletetype': 'combination',
            'deleteid': instantiate.id,
            'strategyid': id_strategy,
        }
        return render(request, 'backtest/delete_indicator_combination.html', ctx)
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
        'id_strategy': id_strategy,
        'requestfrom': requestfrom,
        'requestrule': requestrule,
        'form': form,
        'indicator_property': indicator_obj
    }
    return render(request, 'backtest/modify_indicator.html', ctx)

@login_required       
def ajax_get_tech(request, id_rule, id_strategy):
    technical = ''
    rule = get_object_or_404(Rule, primaryrule_ptr_id=id_rule)
    technical_1 = get_object_or_404(Indicator, id=rule.technical1_id) 
    technical_2 = get_object_or_404(Indicator, id=rule.technical2_id) 
    technical = str(technical_1) +',' + str(technical_2)
    return HttpResponse(technical)

@login_required     
def AddIndicatorCombination(request, id_strategy):
    instantiate = Indicators_Combination(strategy_id=id_strategy)
    if request.POST:
        post = request.POST.copy()
        technical_1 = post['indicator1']
        technical_2 = post['indicator2']
        tech_coms = Indicator.objects.filter(strategy_id=id_strategy)
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
        return redirect('backtest:display', id=id_strategy)
    indicator_tree = []
    indicator_tree = getIndicatorTree(request.user.id)
    ctx = {
        'id_strategy': id_strategy,
        'form': form,
        'indicator_tree': indicator_tree,
    }
    return render(request, 'backtest/add_indicator_combination.html', ctx)

@login_required     
def ModifyIndicatorCombination(request, id_strategy, id_comb):
    instantiate = get_object_or_404(Indicators_Combination, id=id_comb)
    if request.POST:
        post = request.POST.copy()
        technical_1 = post['indicator1']
        technical_2 = post['indicator2']
        tech_coms = Indicator.objects.filter(strategy_id=id_strategy)
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
        return redirect("backtest:display", id=id_strategy)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)  
    ctx = {
        'form': form,
        'tree_structure': tree_structure,
        'id_strategy': id_strategy,
        'id_comb': id_comb,
    }    
    return render(request, 'backtest/modify_indicator_combination.html', ctx)

@login_required
def GetIndicatorBasic(request, id_strategy):
    indicators = Indicator.objects.filter(strategy_id=id_strategy)
    rule_str = ''
    for indicator in indicators:
        if not str(indicator.polymorphic_ctype) == "indicators_ combination":
            rule_str = rule_str + str(indicator) + '#'
    return HttpResponse(rule_str)       

# Calling Ajax method when click launch button.
# creating filename.pickle file
# running Script.py file using celery.
# then creating filename_Result.pickle
@login_required
def LaunchBacktest(request, id_strategy):
    strategy = get_object_or_404(Strategy, id=id_strategy)
    strategy.state = "green"
    strategy.save()
    strategy_dict = {}  # model_to_dict(strategy)
    rule_id_active = []
    rule_active = []
    tech_id_active = []
    tech_temp = []
    technicals = []
    buyrules = strategy.buyrule.all().filter(active=1)
    for buyrule in buyrules:
        if buyrule.buyrules_id not in rule_id_active:
            rule_id_active.append(buyrule.buyrules_id) 
    sellrules = strategy.sellrule.all().filter(active=1)
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
    strategy_dict['name'] = str(strategy.name)
    strategy_dict['capital'] = str(strategy.capital)
    strategy_dict['positions'] = str(strategy.positions)
    strategy_dict['commissions'] = str(strategy.commissions)
    strategy_dict['benchmark'] = str(strategy.benchmark)
    strategy_dict['transaction_type'] = str(strategy.transaction_type)
    strategy_dict['frequency'] = str(strategy.frequency)  
    strategy_dict['rank_rebalance_type'] = str(strategy.rank_rebalance_type)  
    # strategy_dict['slippage'] = str(strategy.slippage)
    strategy_dict['universe'] = str(strategy.universe)
    strategy_dict['startdate'] = str(strategy.startdate)
    strategy_dict['enddate'] = str(strategy.enddate)
    strategy_dict['technicals'] = []
    strategy_dict['buyrules'] = []
    strategy_dict['sellrules'] = []
    strategy_dict['indicator_combinations'] = []
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
    # Work in user directory
    if Tree.objects.filter(child_id=id_strategy, child_type=2, parent_id=-1).exists():
        relative_path = "default/"
    else:
        relative_path = get_path(id_strategy)
    userpath = settings.USERS_DIRECTORY+str(request.user)+"/Strategies/"+relative_path + str(strategy.name)
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    with open(userpath+'/inputs.pickle', 'wb') as f:
        pickle.dump(strategy_dict, f, protocol=2)
    f.close
    process_result = interactive_process.delay(userpath)
    return HttpResponse(process_result)

# Get the data to display progress bar
@login_required
def launch_state(request):
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

# Read the filename_Result.pickle file and Display the result
@login_required
def launch_result(request, id_strategy):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    strategy = get_object_or_404(Strategy, id=id_strategy)
    if Tree.objects.filter(child_id=id_strategy, child_type=2, parent_id=-1).exists():
        relative_path = "default/"
    else:
        relative_path = get_path(id_strategy)
    userpath = settings.USERS_DIRECTORY+str(request.user)+"/Strategies/"+relative_path + str(strategy.name)
    with open(userpath+'/Results.pickle', 'rb') as f:
        Results = pickle.load(f)
    if strategy.results == None:
        new_result = Result()
        new_result.Total_return = Results["Total_Return"]
        new_result.Benchmark_return = Results["Benchmark_Return"]
        new_result.Annualized_return = Results["Annualized_Return"]
        new_result.Max_drawdown = Results["Max_Drowdown"]
        new_result.Benchmark_max_drawdown = Results["Benchmark_Max_Drowdown"]
        new_result.pctwinners = Results["Winner_Percentage"]
        new_result.Sharpe_ratio = Results["Sharpe_Ratio"]
        new_result.save() 
        strategy.results = new_result
        strategy.save()
    else:
        strategy.results.Total_return = Results["Total_Return"]
        strategy.results.Benchmark_return = Results["Benchmark_Return"]
        strategy.results.Annualized_return = Results["Annualized_Return"]
        strategy.results.Max_drawdown = Results["Max_Drowdown"]
        strategy.results.Benchmark_max_drawdown = Results["Benchmark_Max_Drowdown"]
        strategy.results.pctwinners = Results["Winner_Percentage"]
        strategy.results.Sharpe_ratio = Results["Sharpe_Ratio"]
        strategy.save()
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'strategies': strategies,
        'strategy': strategy,
        'Results': Results,
        'tree_structure': tree_structure,
        'relative_path': relative_path
    }
    return render(request, 'backtest/display_strategy_results.html', ctx)

@login_required
def ShowResult(request, id_strategy):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    strategy = get_object_or_404(Strategy, id=id_strategy)
    if Tree.objects.filter(child_id=id_strategy, child_type=2, parent_id=-1).exists():
        relative_path = "default/"
    else:
        relative_path = get_path(id_strategy)
    userpath = settings.USERS_DIRECTORY+str(request.user)+"/Strategies/"+relative_path + str(strategy.name)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    if os.path.isfile(userpath+'/Results.pickle'):
        with open(userpath+'/Results.pickle', 'rb') as f:
            Results = pickle.load(f)
        ctx = {
            'strategies': strategies,
            'strategy': strategy,
            'Results': Results,
            'tree_structure': tree_structure,
            'relative_path': relative_path
        }
        return render(request, 'backtest/display_strategy_results.html', ctx)
    else:
        ctx = {
            'strategies': strategies,
            'noexists': 'No Results avaliable',
            'tree_structure': tree_structure,
            'relative_path': relative_path
        }
        return render(request, 'backtest/display_strategy_results.html', ctx)

@login_required
def Delete(request):
    deletetype = request.POST.get('deletetype')
    deleteid = request.POST.get('id')
    strategyid = request.POST.get('strategyid')
    strategy = get_object_or_404(Strategy, id=strategyid)
    if deletetype == "rule":
        rule = get_object_or_404(Rule, id=deleteid)
        buyrule = BuyRule.objects.filter(buyrules_id=deleteid)
        buyrule_str = str(buyrule)
        sellrule = SellRule.objects.filter(sellrules_id=deleteid)
        sellrule_str = str(sellrule)
        if buyrule_str != "<QuerySet []>":
            if strategy.state != "red":
                strategy.state = "yellow"
                strategy.save()
        if sellrule_str != "<QuerySet []>":
            if strategy.state != "red":
                strategy.state = "yellow"
                strategy.save()
        rule.delete()
        return redirect("backtest:display", id=strategyid)
    if deletetype == "rulecombination":
        rulecombination = get_object_or_404(RuleCombination, id=deleteid)
        buyrule = BuyRule.objects.filter(buyrules_id=deleteid)
        buyrule_str = str(buyrule)
        sellrule = SellRule.objects.filter(sellrules_id=deleteid)
        sellrule_str = str(sellrule)
        if buyrule_str != "<QuerySet []>":
            if strategy.state != "red":
                strategy.state = "yellow"
                strategy.save()
        if sellrule_str != "<QuerySet []>":
            if strategy.state != "red":
                strategy.state = "yellow"
                strategy.save()
        rulecombination.delete()
        return redirect("backtest:display", id=strategyid)
    if deletetype == "buyrule":
        buyrule = get_object_or_404(BuyRule, id=deleteid)
        buyrule.delete()
        if strategy.state != "red":
            strategy.state = "yellow"
            strategy.save()
        return redirect("backtest:display", id=strategyid)
    if deletetype == "sellrule":
        sellrule = get_object_or_404(SellRule, id=deleteid)
        sellrule.delete()
        if strategy.state != "red":
            strategy.state = "yellow"
            strategy.save()
        return redirect("backtest:display", id=strategyid)
    if deletetype == "combination":
        indicator_combination =get_object_or_404(Indicators_Combination, indicator_ptr_id=deleteid)
        indicator_combination.delete()
        if strategy.state != "red":
            strategy.state = "yellow"
            strategy.save()
        return redirect("backtest:display", id=strategyid)

@login_required
def ManageBacktest(request):
    return redirect('backtest:manage_default_strategies')

@login_required
def ManageStrategies(request):
    return redirect('backtest:manage_default_strategies')

@login_required
def ManageStrategy(request):
    if Strategy.objects.filter(user_id=request.user).exists():
        strategies = Strategy.objects.all().filter(user_id=request.user)
        selectstrategy = Strategy.objects.filter(user_id=request.user).last()
        if Tree.objects.filter(child_id=selectstrategy.id, child_type=2, permission=0).exists():
            tree_list = get_tree_list(request.user)
            tree_structure = createTree(0,[], tree_list)
            relative_path = get_path(selectstrategy.id)
            indicator_combinations = Indicators_Combination.objects.filter(strategy_id=selectstrategy.id)
            ctx = {
                'strategies': strategies,
                'selectstrategy': selectstrategy,
                'indicator_combinations': indicator_combinations,
                'tree_structure': tree_structure,
                'relative_path': relative_path
            }
            return render(request, "backtest/strategies/manage_strategy.html", ctx)
        else:
            tree_list = get_tree_list(request.user)
            tree_structure = createTree(0,[], tree_list)
            ctx = {
                'tree_structure': tree_structure,
            }
            return render(request, "backtest/strategies/manage_strategy.html", ctx)              
    else:
        tree_list = get_tree_list(request.user)
        tree_structure = createTree(0,[], tree_list)
        ctx = {
            'tree_structure': tree_structure,
        }
        return render(request, "backtest/strategies/manage_strategy.html", ctx)        

@login_required
def DisplayStrategyResult(request):
    strategies = Strategy.objects.all().filter(user_id=request.user)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    selectstrategy = Strategy.objects.filter(user=request.user).first()
    if str(selectstrategy) == "None":
        ctx = {
            'nostrategy': 'No Strategy',
            'tree_structure': tree_structure,
        }
        return render(request, 'backtest/display_strategy_results.html', ctx)
    else:
        if not Tree.objects.filter(child_id=selectstrategy.id, child_type=2, parent_id=-1).exists():
            relative_path = "default/"
        else:     
            relative_path = get_path(selectstrategy.id)
        userpath = settings.USERS_DIRECTORY+str(request.user)+"/Strategies/"+relative_path + str(selectstrategy.name)
        if os.path.isfile(userpath+'/Results.pickle'):
            with open(userpath+'/Results.pickle', 'rb') as f:
                Results = pickle.load(f)
            ctx = {
                'strategies': strategies,
                'selectstrategy': selectstrategy,
                'Results': Results,
                'tree_structure': tree_structure,
                'relative_path': relative_path
            }
            return render(request, 'backtest/display_strategy_results.html', ctx)
        else:
            ctx = {
                'strategies': strategies,
                'noexists': 'No Results avaliable',
                'tree_structure': tree_structure,
                'relative_path': relative_path
            }
            return render(request, 'backtest/display_strategy_results.html', ctx)

def AddCategory(request):
    if request.POST:
        new_category = Category()
        new_category.name = request.POST.get("category_name")        
        new_category.user = request.user
        if request.POST.get("parent_id") == '0':
            new_category.path = request.POST.get("category_name") + '/'  
        else:
            parent_category = get_object_or_404(Category, id=request.POST.get("parent_id"))
            new_category.path = parent_category.path + request.POST.get("category_name") + '/'
        new_category.save()
        new_tree = Tree()
        new_tree.child_id =new_category.id
        new_tree.child_name = new_category.name
        new_tree.child_type = 1
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect("backtest:managestrategies")
    categories = Category.objects.all().filter(user_id = request.user)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'categories': categories,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/strategies/add_category.html', ctx)

def RenameCategory(request):
    categories = Category.objects.all().filter(user_id = request.user)
    if request.POST:
        category_id = request.POST.get("id")
        new_name = request.POST.get("category_name")
        category = get_object_or_404(Category, id=category_id)
        category.name = new_name
        category.save()
        tree_category = get_object_or_404(Tree, child_id=category_id, child_type=1)
        tree_category.child_name = new_name
        tree_category.save()
        return redirect("backtest:managestrategies")
    categories = Category.objects.all().filter(user_id = request.user)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'categories': categories,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/strategies/rename_category.html', ctx)

def DeleteCategory(request):
    categories = Category.objects.all().filter(user_id = request.user)
    if request.POST: 
        category_id = request.POST.get("id")
        if Tree.objects.all().filter(parent_id=category_id).exists():
            strategies = []
            parent_strategies = Tree.objects.all().filter(child_type=2, parent_id=0, permission=0)
            for parent_strategy in parent_strategies:
                strategies.append(get_object_or_404(Strategy, id=parent_strategy.child_id))
            tree_list = get_tree_list(request.user)
            tree_structure = createTree(0,[], tree_list)
            ctx = {
                'title': "top folder",
                'strategies': strategies,
                'tree_structure': tree_structure,
                'error_message': "Not Empty Folder",
                'categories': categories
            }
            return render(request, "backtest/strategies/delete_category.html", ctx)
        else:
            category = get_object_or_404(Category, id=category_id)
            category.delete()
            tree = get_object_or_404(Tree, child_id=category_id, child_type=1, permission=0)
            tree.delete()
            return redirect('backtest:managestrategies')
    categories = Category.objects.all().filter(user_id = request.user)
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'categories': categories,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/strategies/delete_category.html', ctx)

def ManageCategory(request, id):
    strategies = []
    parent_strategies = Tree.objects.all().filter(child_type=2, parent_id=id, user=request.user)
    for parent_strategy in parent_strategies:
        strategies.append(get_object_or_404(Strategy, id=parent_strategy.child_id))
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    if id == 0:
        ctx = {
            'title': 'Top Folder',
            'strategies': strategies,
            'tree_structure': tree_structure
        }
    else:
        category = get_object_or_404(Category, id=id)
        ctx = {
            'title': category.path,
            'strategies': strategies,
            'tree_structure': tree_structure
        }
    return render(request, "backtest/strategies/manage_strategies.html", ctx)   


def ManageDefaultStrategies(request):
    strategies = []
    strategy_trees = Tree.objects.all().filter(child_type=2, parent_id=-1, permission=1)
    for strategy_tree in strategy_trees:
        strategies.append(get_object_or_404(Strategy, id=strategy_tree.child_id))    
    tree_list = get_tree_list(request.user)
    tree_structure = createTree(0,[], tree_list)
    ctx = {
        'title': 'Default Folder',
        'strategies': strategies,
        'tree_structure': tree_structure
    }
    return render(request, 'backtest/strategies/manage_default_strategies.html', ctx)

def GetTechs(request, id_comb):
    technical = ''
    indicator_combination = get_object_or_404(Indicators_Combination, indicator_ptr_id=id_comb)
    technical = str(indicator_combination.indicator1) + ',' + str(indicator_combination.indicator2)
    return HttpResponse(technical)

#Combination Strategies

def comb_get_tree_list(user_id):
    tree_list = []
    list_item = {}
    get_default_trees = CombTree.objects.all().filter(permission=1)
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
    get_tree_lists = CombTree.objects.all().filter(user_id=user_id, permission=0)
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

def comb_createTree(parent_id, PushData, data):
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

def comb_get_path(strategy_id):
    tree_element = get_object_or_404(CombTree, child_id=strategy_id, child_type=2)
    if tree_element.parent_id == 0:
        return ""
    elif tree_element.parent_id == -1:
        return "Default Folder/"
    else:
        category_element = get_object_or_404(CombFolder, id=tree_element.parent_id)
        return category_element.path    

def ManageCombinationStrategies(request):
    return redirect('backtest:comb_manage_strategies', id_folder=99999999999)

def CombManageStrategies(request, id_folder):
    comb_strategies = []
    if id_folder == 99999999999:
        tree_element = CombTree.objects.all().filter(child_type=2, parent_id=-1, user=request.user)    
    else:
        tree_element = CombTree.objects.all().filter(child_type=2, parent_id=id_folder, user=request.user)
    for element in tree_element:
        comb_strategies.append(get_object_or_404(CombinationStrategy, id=element.child_id))
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)
    if id_folder == 0:
        ctx = {
            'id_folder': id_folder,
            'title': 'Top Folder',
            'comb_strategies': comb_strategies,
            'tree_structure': tree_structure,
        }
        return render(request, 'backtest/comb_strategy/manage_strategies.html', ctx)
    else:
        if id_folder == 99999999999:
            ctx = {
                'id_folder': id_folder,
                'title': 'Default Folder/',
                'comb_strategies': comb_strategies,
                'tree_structure': tree_structure,
            }
        else:
            parent_folder = get_object_or_404(CombFolder, id=id_folder)
            ctx = {
                'id_folder': id_folder,
                'title': parent_folder.path,
                'comb_strategies': comb_strategies,
                'tree_structure': tree_structure,
            }
        return render(request, 'backtest/comb_strategy/manage_strategies.html', ctx)

def CombDeleteStrategy(request, id_strategy):
    comb_strategy = get_object_or_404(CombinationStrategy, id=id_strategy)
    form = CombinationStrategyForm(request.POST or None, instance=comb_strategy)
    if form.is_valid():
        tree_element = get_object_or_404(CombTree, child_id=comb_strategy.id, child_type=2)
        tree_element.delete()
        if comb_strategy.results:
            comb_strategy.results.delete()
        for element in comb_strategy.get_strategy():
            element.delete()
        comb_strategy.delete()
        return redirect('backtest:manage_comb_strategies')
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)  
    ctx = {
        'form': form,
        'tree_structure': tree_structure,
        'comb_strategy': comb_strategy,
    }
    return render(request, 'backtest/comb_strategy/delete_strategy.html', ctx)

def ajax_comb_get_tree_element(request):
    tree_id = request.GET.get("id")
    tree_element = get_object_or_404(CombTree, id=tree_id)
    msg = {
        'child_type': tree_element.child_type,
        'child_id': tree_element.child_id,
        'permission': tree_element.permission,
    }
    return HttpResponse(json.dumps(msg), content_type='application/json')

def CombManageStrategy(request, id_strategy):
    comb_strategy = get_object_or_404(CombinationStrategy, id=id_strategy)
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)
    parent_path = comb_get_path(id_strategy)
    userpath = settings.USERS_DIRECTORY + str(request.user) + "/combination_strategies/" + parent_path + str(comb_strategy.name)
    if os.path.exists(userpath + '/Results.pickle'):
        comb_strategy.state = "green"
    else:
        comb_strategy.state = "red"
    comb_strategy.save()
    ctx = {
        'tree_structure': tree_structure,
        'comb_strategy': comb_strategy,
        'parent_path': parent_path,
    }
    return render(request, 'backtest/comb_strategy/manage_strategy.html', ctx)

def CombModifyGeneral(request, id_comb_strategy):
    comb_strategy = get_object_or_404(CombinationStrategy, id=id_comb_strategy)
    form = GeneralCombStrategyForm(request.POST or None, instance=comb_strategy)
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)

    universe_id = []
    default_universe = Universe_Tree.objects.filter(child_type=2, permission=1)
    for element in default_universe:
        universe_id.append(element.id)
    user_universe = Universe_Tree.objects.filter(permission=0, child_type=2, user=request.user)
    for element in user_universe:
        universe_id.append(element.id)
    form.fields["universe"].queryset = Universe_Tree.objects.filter(id__in=universe_id)

    benchmark_id = []
    default_benchmark = Benchmarks_Tree.objects.filter(child_type=2, permission=1)
    for element in default_benchmark:
        benchmark_id.append(element.id)
    user_benchmark = Benchmarks_Tree.objects.filter(permission=0, child_type=2, user=request.user)
    for element in user_benchmark:
        benchmark_id.append(element.id)
    form.fields["benchmark"].queryset = Benchmarks_Tree.objects.filter(id__in=benchmark_id)      

    if form.is_valid():
        form.save()
        return redirect('backtest:comb_manage_strategy', id_strategy=id_comb_strategy)
    ctx = {
        'comb_strategy': comb_strategy,
        'form': form, 
        'tree_structure': tree_structure,
        'id_comb_strategy': id_comb_strategy,
    }
    return render(request, 'backtest/comb_strategy/modify_general.html', ctx)

def CombLaunchStrategy(request, id_strategy):
    strategy_dict = {}
    strategy_dict['technicals'] = []
    strategy_dict['buyrules'] = []
    strategy_dict['sellrules'] = []
    strategy_dict['indicator_combinations'] = []    
    comb_strategy = get_object_or_404(CombinationStrategy, id=id_strategy)
    if comb_strategy.get_strategy().count() < 2:
        return HttpResponse('error')
    else:
        for strategy in comb_strategy.get_strategy():
            if strategy.strategy.buyrule.all().filter(active=1).count() < 1 or strategy.strategy.sellrule.all().filter(active=1).count() < 1:
                return HttpResponse('error1')
        comb_strategy_dict = {}
        comb_strategy_dict['strategies'] = []
        comb_strategy_dict['name'] = str(comb_strategy.name)
        comb_strategy_dict['capital'] = str(comb_strategy.capital)
        comb_strategy_dict['positions'] = str(comb_strategy.positions)
        comb_strategy_dict['commissions'] = str(comb_strategy.commissions)
        comb_strategy_dict['benchmark'] = str(comb_strategy.benchmark)
        comb_strategy_dict['transaction_type'] = str(comb_strategy.transaction_type)
        comb_strategy_dict['frequency'] = str(comb_strategy.frequency)
        comb_strategy_dict['universe'] = str(comb_strategy.universe)
        comb_strategy_dict['startdate'] = str(comb_strategy.startdate)
        comb_strategy_dict['enddate'] = str(comb_strategy.enddate)                 
        for strategy in comb_strategy.get_strategy().filter(active=1):
            strategy_dict['name'] = str(strategy.strategy.name)
            strategy_dict['capital'] = str(strategy.strategy.capital)
            strategy_dict['positions'] = str(strategy.strategy.positions)
            strategy_dict['commissions'] = str(strategy.strategy.commissions)
            strategy_dict['benchmark'] = str(strategy.strategy.benchmark)
            strategy_dict['transaction_type'] = str(strategy.strategy.transaction_type)
            strategy_dict['frequency'] = str(strategy.strategy.frequency)
            strategy_dict['universe'] = str(strategy.strategy.universe)
            strategy_dict['startdate'] = str(strategy.strategy.startdate)
            strategy_dict['enddate'] = str(strategy.strategy.enddate)            
            rule_id_active = []
            rule_active = []
            tech_id_active = []
            tech_temp = []
            technicals = []
            buyrules = strategy.strategy.buyrule.all().filter(active=1)
            for buyrule in buyrules:
                if buyrule.buyrules_id not in rule_id_active:
                    rule_id_active.append(buyrule.buyrules_id) 
            sellrules = strategy.strategy.sellrule.all().filter(active=1)
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
                strategy_dict['buyrules'].append([str(BR.buyrules.title), str(BR.output()), str(strategy.order)])
            for SR in sellrules: #Need to recover only Sell Rules that are active
                strategy_dict['sellrules'].append([str(SR.sellrules.title), str(SR.output()), str(strategy.order)])                                 
            comb_strategy_dict['strategies'].append(strategy_dict)
        relative_path = comb_get_path(id_strategy)
        userpath = settings.USERS_DIRECTORY + str(request.user) + "/combination_strategies/" + relative_path + str(comb_strategy.name)
        if not os.path.exists(userpath):
            os.makedirs(userpath)
        with open(userpath+'/inputs.pickle', 'wb') as f:
            pickle.dump(comb_strategy_dict, f, protocol=2)
        f.close
        process_result = interactive_process.delay(userpath)
        return HttpResponse(process_result)

def CombLaunchState(request):
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

def CombLaunchResult(request, id_strategy):
    comb_strategy = get_object_or_404(CombinationStrategy, id=id_strategy)
    relative_path = comb_get_path(comb_strategy.id)
    userpath = settings.USERS_DIRECTORY + str(request.user) + "/combination_strategies/" + relative_path + str(comb_strategy.name)
    with open(userpath+'/Results.pickle', 'rb') as f:
        Results = pickle.load(f)
    if comb_strategy.results == None:
        new_result = Result()
        new_result.Total_return = Results["Total_Return"]
        new_result.Benchmark_return = Results["Benchmark_Return"]
        new_result.Annualized_return = Results["Annualized_Return"]
        new_result.Max_drawdown = Results["Max_Drowdown"]
        new_result.Benchmark_max_drawdown = Results["Benchmark_Max_Drowdown"]
        new_result.pctwinners = Results["Winner_Percentage"]
        new_result.Sharpe_ratio = Results["Sharpe_Ratio"]
        new_result.save() 
        comb_strategy.results = new_result
        comb_strategy.save()
    else:
        comb_strategy.results.Total_return = Results["Total_Return"]
        comb_strategy.results.Benchmark_return = Results["Benchmark_Return"]
        comb_strategy.results.Annualized_return = Results["Annualized_Return"]
        comb_strategy.results.Max_drawdown = Results["Max_Drowdown"]
        comb_strategy.results.Benchmark_max_drawdown = Results["Benchmark_Max_Drowdown"]
        comb_strategy.results.pctwinners = Results["Winner_Percentage"]
        comb_strategy.results.Sharpe_ratio = Results["Sharpe_Ratio"]
        comb_strategy.save()
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)        
    ctx = {
        'strategy': comb_strategy,
        'Results': Results,
        'tree_structure': tree_structure,
        'relative_path': relative_path,
    }
    return render(request, 'backtest/comb_strategy/display_strategy_results.html',ctx)

def CombResults(request):
    comb_tree = CombTree.objects.all().filter(child_type=2, user=request.user).last()
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)    
    if comb_tree:
        comb_strategy = get_object_or_404(CombinationStrategy, id=comb_tree.child_id)
        relative_path = comb_get_path(comb_strategy.id)
        userpath = settings.USERS_DIRECTORY + str(request.user) + "/combination_strategies/" + relative_path + str(comb_strategy.name)
        if os.path.exists(userpath + '/Results.pickle'):
            with open(userpath+'/Results.pickle', 'rb') as f:
                Results = pickle.load(f)
            ctx = {
                'strategy': comb_strategy,
                'Results': Results,
                'tree_structure': tree_structure,
                'relative_path': relative_path,
            }
            return render(request, 'backtest/comb_strategy/display_strategy_results.html',ctx)            
        else:
            ctx = {
                'noavaliable': 'No Results',
                'tree_structure': tree_structure,
            }      
            return render(request, 'backtest/comb_strategy/display_strategy_results.html',ctx)            
    else:
        ctx = {
            'nostrategy': 'No Combination Strategy',
            'tree_structure': tree_structure,            
        }      
        return render(request, 'backtest/comb_strategy/display_strategy_results.html',ctx)            

def CombExportStrategy(request, id_folder, id_strategy):
    comb_strategy = get_object_or_404(CombinationStrategy, id=id_strategy)
    comb_strategy_dict = {}
    comb_strategy_dict['strategies'] = []
    comb_strategy_dict['name'] = str(comb_strategy.name)
    comb_strategy_dict['capital'] = str(comb_strategy.capital)
    comb_strategy_dict['positions'] = str(comb_strategy.positions)
    comb_strategy_dict['commissions'] = str(comb_strategy.commissions)
    comb_strategy_dict['benchmark'] = str(comb_strategy.benchmark)
    comb_strategy_dict['transaction_type'] = str(comb_strategy.transaction_type)
    comb_strategy_dict['frequency'] = str(comb_strategy.frequency)
    comb_strategy_dict['universe'] = str(comb_strategy.universe)
    comb_strategy_dict['startdate'] = str(comb_strategy.startdate)
    comb_strategy_dict['enddate'] = str(comb_strategy.enddate)    
    for strategy in comb_strategy.get_strategy():
        strategy_dict = {} #model_to_dict(strategy)
        technicals = Indicator.objects.filter(strategy_id = strategy.strategy.id)   #.exclude(rule_id = 999999999)
        buyrules = strategy.strategy.buyrule.all()
        sellrules = strategy.strategy.sellrule.all()
        rules = strategy.strategy.rule.all()
        rulecombinations = strategy.strategy.rulecombination.all()
        strategy_dict['name'] = str(strategy.strategy.name)
        strategy_dict['capital'] = str(strategy.strategy.capital)
        strategy_dict['positions'] = str(strategy.strategy.positions)
        strategy_dict['commissions'] = str(strategy.strategy.commissions)
        strategy_dict['benchmark'] = str(strategy.strategy.benchmark)
        strategy_dict['transaction_type'] = str(strategy.strategy.transaction_type)
        strategy_dict['frequency'] = str(strategy.strategy.frequency)
        # strategy_dict['slippage'] = str(strategy.slippage)
        strategy_dict['universe'] = str(strategy.strategy.universe)
        strategy_dict['rank_rebalance_type'] = str(strategy.strategy.rank_rebalance_type)
        strategy_dict['startdate'] = str(strategy.strategy.startdate)
        strategy_dict['enddate'] = str(strategy.strategy.enddate)
        strategy_dict['technicals'] = []
        strategy_dict['buyrules'] = []
        strategy_dict['sellrules'] = []
        strategy_dict['rules'] = []
        strategy_dict['rulecombinations'] = []
        strategy_dict['is_liquidity_system'] = 0
        strategy_dict['is_rank_system'] = 0
        strategy_dict['indicator_combinations'] = []
        if strategy.strategy.liquidity_system:
            strategy_dict['is_liquidity_system'] = 1
            strategy_dict['liquidity_name'] = strategy.strategy.liquidity_system.name
            liquidity_indicators = Indicator.objects.filter(liquidity_system_id=strategy.strategy.liquidity_system.id)
            liquidity_rules = strategy.strategy.liquidity_system.rule.all()
            liquidity_rule_combs = strategy.strategy.liquidity_system.rulecombination.all()
            liquidity_liquidity_rules = strategy.strategy.liquidity_system.liquidity_rule.all()
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
        if strategy.strategy.rank_system:
            strategy_dict['is_rank_system'] = 1
            strategy_dict['rank_name'] = strategy.strategy.rank_system.name
            strategy_dict['rank_indicators'] = []
            strategy_dict['rank_indicator_combinations'] = []
            rank_indicators = Indicator.objects.filter(rank_system_id=strategy.strategy.rank_system.id)
            strategy_dict['rank_rules'] = []
            rank_rules = strategy.strategy.rank_system.rule.all()
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
        comb_strategy_dict['strategies'].append(strategy_dict)
    userpath = settings.COMBINATION_STRATEGIES + str(request.user) + '/export/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    with open(userpath+comb_strategy_dict['name']+'.pickle', 'wb') as f:
        pickle.dump(comb_strategy_dict, f, protocol=2)
    f.close
    """ Display all strategies """  
    return redirect('backtest:comb_manage_strategies', id_folder=id_folder)

def CombLoadStrategy(request):
    userpath = settings.COMBINATION_STRATEGIES + str(request.user) + '/export/'
    if not os.path.exists(userpath):
        os.makedirs(userpath)
    if request.POST:
        file_name = request.POST.get("file_name")
        parent_id = request.POST.get("parent_id")
        with open(userpath + file_name + '.pickle', 'rb') as f:
            comb_strategy_dict = pickle.load(f)
        comb_strategy = CombinationStrategy()
        comb_strategy.name = comb_strategy_dict['name']
        comb_strategy.capital = comb_strategy_dict['capital']
        comb_strategy.positions = comb_strategy_dict['positions']
        comb_strategy.commissions = comb_strategy_dict['commissions']
        comb_strategy.transaction_type = comb_strategy_dict['transaction_type']
        comb_strategy.frequency = comb_strategy_dict['frequency']
        comb_strategy.startdate = comb_strategy_dict['startdate']
        comb_strategy.enddate = comb_strategy_dict['enddate']

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
        if comb_strategy_dict['universe'] in universe_string:
            for element in universe_list:
                if str(element) == comb_strategy_dict['universe']:
                    comb_strategy.universe = element
        else:
            if comb_strategy_dict['universe'] != "None":
                universe_name = comb_strategy_dict['universe']
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
                comb_strategy.universe = new_tree

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
        if comb_strategy_dict['benchmark'] in benchmark_string:
            for element in benchmark_list:
                if str(element) == comb_strategy_dict['benchmark']:
                    comb_strategy.benchmark = element
        else:
            if comb_strategy_dict['benchmark'] != "None":
                universe_name = comb_strategy_dict['benchmark']
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
                comb_strategy.benchmark = new_tree

        comb_strategy.save()
        for strategy_dict in comb_strategy_dict['strategies']:
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
            buy_strategy = BuyStrategy()
            buy_strategy.strategy = strategy
            buy_strategy.save()
            comb_strategy.buystrategy.add(buy_strategy)
            comb_strategy.save()
        if parent_id == "d":
            if not CombTree.objects.filter(permission=1).exists():
                default_folder = CombTree()
                default_folder.child_id = -1
                default_folder.child_type = 1
                default_folder.child_name = "Default Folder"
                default_folder.parent_id = 0
                default_folder.user = request.user
                default_folder.permission = 1
                default_folder.save()
            else:
                default_folder = get_object_or_404(CombTree, permission=1, child_type=1)
            new_tree = CombTree()
            new_tree.child_id =comb_strategy.id
            new_tree.child_name = comb_strategy.name
            new_tree.child_type = 2
            new_tree.parent_id = default_folder.child_id
            new_tree.permission = 1
            new_tree.user = request.user
            new_tree.save()
            return redirect('backtest:comb_manage_strategy', id_strategy=comb_strategy.id)
        new_tree = CombTree()
        new_tree.child_id =comb_strategy.id
        new_tree.child_name = comb_strategy.name
        new_tree.child_type = 2
        new_tree.parent_id = parent_id
        new_tree.user = request.user
        new_tree.save()  
        return redirect('backtest:comb_manage_strategy', id_strategy=comb_strategy.id)
    load_file_list = []
    with os.scandir(userpath) as entries:
        for entry in entries:
            if not entry.is_file():
                continue
            filename, file_extension = os.path.splitext(entry.name)
            if file_extension.lower() != ".pickle":
                continue
            load_file_list.append(filename)        
    folders = CombFolder.objects.all().filter(user_id=request.user)
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)
    ctx = {
        'load_list': load_file_list,
        'folders': folders,
        'tree_structure':tree_structure,
    }            
    return render(request, 'backtest/comb_strategy/load_file_list.html',ctx)

def CombManage(request):
    comb_tree = CombTree.objects.all().filter(child_type=2, user=request.user).last()
    if comb_tree:
        comb_strategy = get_object_or_404(CombinationStrategy, id=comb_tree.child_id)
        return redirect('backtest:comb_manage_strategy', id_strategy=comb_strategy.id)
    else:
        tree_list = comb_get_tree_list(request.user)
        tree_structure = comb_createTree(0,[], tree_list)        
        ctx = {
            'tree_structure': tree_structure,
            'nostrategy': 'No Combination Strategy!',
        }
        return render(request, 'backtest/comb_strategy/manage_strategy.html', ctx)

def CombCreateFolder(request):
    if request.POST:
        new_folder = CombFolder()
        new_folder.name = request.POST.get("folder_name")
        new_folder.user = request.user
        if request.POST.get("parent_id") == '0':
            new_folder.path = request.POST.get("folder_name") + '/'
        else:
            parent_folder = get_object_or_404(CombFolder, id=request.POST.get("parent_id"))
            new_folder.path = parent_folder.path + request.POST.get("folder_name") + "/"
        new_folder.save()
        new_tree = CombTree()
        new_tree.child_id = new_folder.id
        new_tree.child_name = new_folder.name
        new_tree.child_type = 1
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('backtest:comb_manage_strategies', id_folder=new_folder.id)
    folders = CombFolder.objects.all().filter(user_id=request.user)
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)
    ctx = {
        'folders': folders,
        'tree_structure': tree_structure,
    }
    return render(request, 'backtest/comb_strategy/create_folder.html', ctx)

def CombDeleteFolder(request):
    folders = CombFolder.objects.all().filter(user_id=request.user)
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)    
    if request.POST:
        folder_id = request.POST.get("id")
        if CombTree.objects.all().filter(parent_id=folder_id).exists():
            ctx = {
                'folders': folders,
                'tree_structure': tree_structure,
                'error_message': "Not Empty Folder",
            }
            return render(request, "backtest/comb_strategy/create_folder.html", ctx)
        else:
            folder = get_object_or_404(CombFolder, id=folder_id)
            folder.delete()
            tree = get_object_or_404(CombTree, child_id=folder_id, child_type=1, permission=0)
            tree.delete()
            return redirect('backtest:manage_comb_strategies')
    ctx = {
        'folders': folders,
        'tree_structure': tree_structure,
    }
    return render(request, 'backtest/comb_strategy/delete_folder.html', ctx)

def CombCreateCombStrategy(request):
    folders = CombFolder.objects.all().filter(user_id=request.user)
    form  = CombinationStrategyForm(request.POST or None)
    if form.is_valid():
        new_strategy = form.save()
        new_strategy.user = request.user
        new_strategy.save()
        new_tree = CombTree()
        new_tree.child_id = new_strategy.id
        new_tree.child_name = new_strategy.name
        new_tree.child_type = 2
        new_tree.parent_id = request.POST.get("parent_id")
        new_tree.user = request.user
        new_tree.save()
        return redirect('backtest:comb_manage_strategy', id_strategy=new_strategy.id)
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)
    ctx = {
        'form': form,
        'folders': folders,
        'tree_structure': tree_structure,
    }
    return render(request, 'backtest/comb_strategy/create_combination_strategy.html', ctx)

def CombAddStrategy(request, id_comb_strategy):
    comb_strategy = get_object_or_404(CombinationStrategy, id=id_comb_strategy)
    if request.POST:
        id_strategies = request.POST.getlist('strategy[]')
        for id in id_strategies:
            buy_strategy = BuyStrategy()
            buy_strategy.strategy = get_object_or_404(Strategy, id=id)
            buy_strategy.save()
            comb_strategy.buystrategy.add(buy_strategy)
        return redirect('backtest:comb_manage_strategy', id_strategy=id_comb_strategy)
    tree_list = comb_get_tree_list(request.user)
    tree_structure = comb_createTree(0,[], tree_list)
    strategies = []
    tree_strategy_defaults = Tree.objects.all().filter(permission=1, child_type=2)
    for element in tree_strategy_defaults:
        strategies.append(get_object_or_404(Strategy, id=element.child_id))
    tree_strategy_user = Tree.objects.all().filter(permission=0, child_type=2, user=request.user)
    for element in tree_strategy_user:
        strategies.append(get_object_or_404(Strategy, id=element.child_id))
    if strategies:
        ctx = {
            'strategies': strategies,
            'tree_structure': tree_structure,
            'id_comb_strategy': id_comb_strategy,
        }    
    else:
        ctx = {
            'error_message': 'No strategies. Please add strategies first',
            'tree_structure': tree_structure,
            'id_comb_strategy': id_comb_strategy,
        }           
    return render(request, 'backtest/comb_strategy/add_strategy.html', ctx)
    
def CombRemoveStrategy(request):
    id_strategy = request.POST.get("id_strategy")
    id_combination_strategy = request.POST.get("id_comb")
    combination_strategy = get_object_or_404(CombinationStrategy, id=id_combination_strategy)
    strategy = get_object_or_404(BuyStrategy, id=id_strategy)
    combination_strategy.buystrategy.remove(strategy)
    strategy.delete()
    return redirect('backtest:comb_manage_strategy', id_strategy=id_combination_strategy)

def CombStrategyStatus(request, id_comb):
    if request.POST:
        msg = "success"
        strategy_status = json.loads(request.POST['strategy_status'])
        strategy_checked = strategy_status['strategy_selected']
        strategy_unchecked = strategy_status['strategy_unselected']
        strategy_order = strategy_status['strategy_order']
        strategy_id = strategy_status['strategy_id']
        for col in strategy_checked:
            strategy = get_object_or_404(BuyStrategy, id=col)
            strategy.active = 1
            strategy.save()
        for col in strategy_unchecked:
            strategy = get_object_or_404(BuyStrategy, id=col)
            strategy.active = 0
            strategy.save()     
        for col in strategy_id:
            strategy = get_object_or_404(BuyStrategy, id=col)
            strategy.order = strategy_order[strategy_id.index(col)]
            strategy.save()     
        json_data = json.dumps(msg)
        return HttpResponse(json_data, content_type='application/json')     