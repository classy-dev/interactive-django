from django.urls import path
from . import views
from django.views.generic import ListView
from .models import Rule, Strategy
app_name = 'backtest'
urlpatterns = [
    path('',views.Index, name="index"),  
    path('backtest/strategies/load_list', views.LoadStrategyList, name='load_strategy_list'),
    path('backtest/strategies/add_strategy/', views.AddStrategy, name='add_strategy'),
    path('backtest/strategies/delete/<int:id_strategy>', views.DeleteStrategy, name='delete_strategy'),
    path('backtest/strategies/move/<int:id_strategy>', views.MoveStrategy, name='move_strategy'),
    path('backtest/strategies/managestrategy/<int:id>', views.DisplayStrategy, name='display'),
    path('strategy/<int:id_strategy>/export', views.ExportStrategy, name='export_strategy'),   
    path('backtest/strategies/managestrategy/modifygeneral/<int:id_strategy>', views.ModifyGeneralStrategy, name='modify_generalstrategy'),
    path('strategystate/<int:id_strategy>', views.Strategystate, name='strategystate'),
    path('get_strategy', views.ajax_get_strategy, name='get_strategy'),

    path('backtest/strategies/managestrategy/add_rule/<int:id_strategy>', views.AddRule, name='add_rule'),
    path('backtest/strategies/managestrategy/modify_rule/<int:id_rule>/<int:id_strategy>', views.ModifyRule, name='modify_rule'),
    path('rulestatus/<int:id_strategy>', views.Rulestatus, name='rulestatus'),
    path('ajax_get_rule/<int:id_strategy>', views.ajax_get_rules, name='get_rules'),
    path('getrule/<int:id_rulecombination>/<int:id_strategy>', views.ajax_get_rule, name='get_rule'),

    path('backtest/strategies/managestrategy/add_rulecombination/<int:id_strategy>', views.AddRuleCombination, name='add_rulecombination'),
    path('backtest/strategies/managestrategy/modify_rulecombination/<int:id_rulecombination>/<int:id_strategy>', views.ModifyRuleCombination, name='modify_rulecombination'),
    path('ajax_get_combination/<int:id_strategy>', views.ajax_get_combination_add, name='get_rule_combination_add'),
    path('ajax_get_combination/<int:id_rulecombination>/<int:id_strategy>', views.ajax_get_combination_modify, name='get_rule_combination_modify'),

    path('backtest/strategies/managestrategy/add_buyrule/<int:id_strategy>', views.AddBuyRule, name='add_buyrule'),
    path('backtest/strategies/managestrategy/add_sellrule/<int:id_strategy>', views.AddSellRule, name='add_sellrule'),   
    
    path('backtest/strategies/managestrategy/technical/<str:source>/<slug:indicator>$/add/<int:id_rule>/<int:id_strategy>', views.AddIndicator, name='add_indicator'),
    path('modifytechnical/<str:indicator>/<int:tech_id>/<int:id_strategy>/<str:requestfrom>/<int:requestrule>', views.ModifyIndicator, name='modifytechnical'),
    path('deletetechnical/<int:tech_id>/<int:id_strategy>/<str:requestfrom>/<int:requestrule>', views.DeleteIndicator, name='deletetechnical'),
    path('gettechnical', views.GetIndicator, name='gettechnical'),
    path('gettech/<int:id_rule>/<int:id_strategy>', views.ajax_get_tech, name='get_techs'),
    path('backtest/strategies/managestrategy/add_indicator_combination/<int:id_strategy>', views.AddIndicatorCombination, name="add_indicator_combination"),
    path('backtest/strategies/managestrategy/modify_indicator_combination/<int:id_comb>/<int:id_strategy>', views.ModifyIndicatorCombination, name="modify_combination"),
    path('backtest/get_techs/<int:id_comb>', views.GetTechs, name="get_techs_comb"),
    path('backtest/get_indicator_basic/<int:id_strategy>', views.GetIndicatorBasic, name="get_indicators_basic"),

    path('backtest/strategies/managestrategy/launchbacktest/<int:id_strategy>', views.LaunchBacktest, name='launchbacktest'),    
    path('launch_state', views.launch_state, name='launch_state'),
    path('backtest/strategies/displaystrategyresult/launchresult/<int:id_strategy>', views.launch_result, name='launch_result'),
    path('backtest/strategies/displaystrategyresult/<int:id_strategy>', views.ShowResult, name='showresult'),    
    
    path('delete/', views.Delete, name='delete'),

    path('backtest/', views.ManageBacktest, name="backtest"),
    path('backtest/strategies/',views.ManageStrategies, name="managestrategies"),
    path('backtest/strategies/managestrategy',views.ManageStrategy, name="managestrategy"),  
    path('backtest/strategies/displaystrategyresult',views.DisplayStrategyResult, name="displaystrategyresult"),

    path('backtest/strategies/add_category', views.AddCategory, name="add_category") ,
    path('backtest/strategies/rename_category', views.RenameCategory, name="rename_category") ,
    path('backtest/strategies/delete_category', views.DeleteCategory, name="delete_category") ,
    path('backtest/strategies/<int:id>',views.ManageCategory, name="managecategory"),
    path('backtest/strategies/default/', views.ManageDefaultStrategies, name="manage_default_strategies"),
    #Manage Combination Strategy
    path('backtest/comb_strategies/', views.ManageCombinationStrategies, name="manage_comb_strategies"),

    path('backtest/comb_strategies/<int:id_folder>/', views.CombManageStrategies, name="comb_manage_strategies"),
    path('backtest/comb_strategies/delete_strategy/<int:id_strategy>/', views.CombDeleteStrategy, name="comb_delete_strategy"),
    path('backtest/comb_get_tree_element/', views.ajax_comb_get_tree_element, name="comb_get_tree_element"),

    path('backtest/comb_strategies/manage/<int:id_strategy>/', views.CombManageStrategy, name="comb_manage_strategy"),
    path('backtest/comb_strategies/create_combination_strategy/', views.CombCreateCombStrategy, name="comb_create_comb_strategy"),
    path('backtest/comb_strategies/manage/modify_general/<int:id_comb_strategy>/',views.CombModifyGeneral, name="comb_modify_general"),
    path('backtest/comb_strategies/launch_strategy/<int:id_strategy>/',views.CombLaunchStrategy, name="comb_launch_strategy"),
    path('backtest/comb_strategies/launch_state/', views.CombLaunchState, name="comb_launch_state"),
    path('backtest/comb_strategies/manage_result/<int:id_strategy>/',views.CombLaunchResult, name="comb_launch_result"),
    path('backtest/comb_strategies/manage_result/', views.CombResults, name="comb_results"),
    path('backtest/comb_strategies/export_strategy/<int:id_folder>/<int:id_strategy>/', views.CombExportStrategy, name="comb_export_strategy"),
    path('backtest/comb_strategies/load_strategy/',views.CombLoadStrategy ,name="comb_load_strategy"),
    path('backtest/comb_strategies/manage/', views.CombManage, name="comb_strategy"),

    path('backtest/comb_strategies/create_folder/', views.CombCreateFolder, name="comb_create_folder"),
    path('backtest/comb_strategies/delete_folder/', views.CombDeleteFolder, name="comb_delete_folder"),

    path('backtest/comb_strategies/manage/add_strategy/<int:id_comb_strategy>/', views.CombAddStrategy, name="comb_add_strategy"),
    path('backtest/comb_strategies/manage/remove_strategy/', views.CombRemoveStrategy, name="comb_remove_strategy"),

    path('strategy_status/<int:id_comb>', views.CombStrategyStatus, name='strategy_status'),
]