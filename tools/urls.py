from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [

    path('', views.Index, name="index"),

    #UNIVERSES url
    path('universes/', views.ManageUniverses_default, name="manage_universes_default"),
    path('universes/create_folder/', views.CreateFolder, name="create_folder"),
    path('universes/delete_folder/', views.DeleteFolder, name="delete_folder"),
    path('universes/<int:id>', views.ManageUniverses, name="manage_universes"),

    path('universes/universe/', views.ManageUniverse_default, name="manage_universe_default"),
    path('universes/upload_universe/', views.UploadUniverse, name="upload_universe"),
    path('universe/delete_universe_default/', views.DeleteUniverse_default, name="delete_universe_default"),
    path('universe/add_instrument_default/<int:id>', views.AddInstrument_default, name="add_instrument_default"),
    path('universe/add_instrument_to_universe', views.AddInstrumenttoUniverse, name="add_instrument_to_universe"),
    path('universe/delete_instrument_default/<int:id>', views.DeleteInstrument_default, name="delete_instrument_default"),

    path('universes/create_universe/', views.CreateUniverse, name="create_universe"),
    path('universes/delete_universe/', views.DeleteUniverse, name="delete_universe"),
    path('universes/universe/<int:id>', views.ManageUniverse, name="manage_universe"),
    path('universes/universe/default/<int:id>', views.ManageDefaultUniverse, name="manage_default_universe"),

    path('universes/universe/add_instrument/<int:id>', views.AddInstrument, name="add_instrument"),
    # path('universes/universe/insert_instrument/', views.InsertInstrument, name="insert_instrument"),
    # path('universes/universe/update_instrument/', views.UpdateInstrument, name="update_instrument"),
    path('universes/universe/delete_instrument/', views.DeleteInstrument, name="delete_instrument"),

    path('universes/boolean_operation/', views.BooleanOperation, name="manage_boolean_operation"),

    path('universe/ajax_get_treeelement/', views.ajax_get_treeelement, name='ajax_get_treeelement'),
    path('universe/get_instrument_of_universe', views.ajax_get_instrument_of_universe, name="get_instrument_of_universe"), 


    #LISTS url
    path('lists/', views.LManageUniverses_default, name="lists_manage_universes_default"),
    path('lists/create_folder/', views.LCreateFolder, name="lists_create_folder"),
    path('lists/delete_folder/', views.LDeleteFolder, name="lists_delete_folder"),
    path('lists/<int:id>', views.LManageUniverses, name="lists_manage_universes"),

    path('lists/list/', views.LManageUniverse_default, name="lists_manage_universe_default"),
    path('lists/upload_universe/', views.LUploadUniverse, name="lists_upload_universe"),
    path('list/delete_universe_default/', views.LDeleteUniverse_default, name="lists_delete_universe_default"),
    path('list/add_instrument_default/<int:id>', views.LAddInstrument_default, name="lists_add_instrument_default"),
    path('list/add_instrument_to_universe', views.LAddInstrumenttoUniverse, name="lists_add_instrument_to_universe"),
    path('list/delete_instrument_default/<int:id>', views.LDeleteInstrument_default, name="lists_delete_instrument_default"),

    path('lists/create_universe/', views.LCreateUniverse, name="lists_create_universe"),
    path('lists/delete_universe/', views.LDeleteUniverse, name="lists_delete_universe"),
    path('lists/list/<int:id>', views.LManageUniverse, name="lists_manage_universe"),
    path('lists/list/default/<int:id>', views.LManageDefaultUniverse, name="lists_manage_default_universe"),

    path('lists/list/add_instrument/<int:id>', views.LAddInstrument, name="lists_add_instrument"),
    # path('universes/universe/insert_instrument/', views.InsertInstrument, name="lists_insert_instrument"),
    # path('universes/universe/update_instrument/', views.UpdateInstrument, name="lists_update_instrument"),
    path('lists/list/delete_instrument/', views.LDeleteInstrument, name="lists_delete_instrument"),

    path('lists/boolean_operation/', views.LBooleanOperation, name="lists_manage_boolean_operation"),

    path('list/ajax_get_treeelement/', views.Lajax_get_treeelement, name='lists_ajax_get_treeelement'),
    path('list/get_instrument_of_universe', views.Lajax_get_instrument_of_universe, name="lists_get_instrument_of_universe"),

    #BENCHMARKS url
    path('benchmarks/', views.BManageUniverses_default, name="benchmarks_manage_universes_default"),
    path('benchmarks/create_folder/', views.BCreateFolder, name="benchmarks_create_folder"),
    path('benchmarks/delete_folder/', views.BDeleteFolder, name="benchmarks_delete_folder"),
    path('benchmarks/<int:id>', views.BManageUniverses, name="benchmarks_manage_universes"),

    path('benchmarks/benchmark/', views.BManageUniverse_default, name="benchmarks_manage_universe_default"),
    path('benchmarks/upload_universe/', views.BUploadUniverse, name="benchmarks_upload_universe"),
    path('benchmark/delete_universe_default/', views.BDeleteUniverse_default, name="benchmarks_delete_universe_default"),
    path('benchmark/add_instrument_default/<int:id>', views.BAddInstrument_default, name="benchmarks_add_instrument_default"),
    path('benchmark/add_instrument_to_universe', views.BAddInstrumenttoUniverse, name="benchmarks_add_instrument_to_universe"),
    path('benchmark/delete_instrument_default/<int:id>', views.BDeleteInstrument_default, name="benchmarks_delete_instrument_default"),

    path('benchmarks/create_universe/', views.BCreateUniverse, name="benchmarks_create_universe"),
    path('benchmarks/delete_universe/', views.BDeleteUniverse, name="benchmarks_delete_universe"),
    path('benchmarks/benchmark/<int:id>', views.BManageUniverse, name="benchmarks_manage_universe"),
    path('benchmarks/benchmark/default/<int:id>', views.BManageDefaultUniverse, name="benchmarks_manage_default_universe"),

    path('benchmarks/benchmark/add_instrument/<int:id>', views.BAddInstrument, name="benchmarks_add_instrument"),
    # path('universes/universe/insert_instrument/', views.InsertInstrument, name="benchmarks_insert_instrument"),
    # path('universes/universe/update_instrument/', views.UpdateInstrument, name="benchmarks_update_instrument"),
    path('benchmarks/benchmark/delete_instrument/', views.BDeleteInstrument, name="benchmarks_delete_instrument"),

    path('benchmark/ajax_get_treeelement/', views.Bajax_get_treeelement, name='benchmarks_ajax_get_treeelement'),
    path('benchmark/get_instrument_of_universe', views.Bajax_get_instrument_of_universe, name="benchmarks_get_instrument_of_universe"),

    #RANKING URL
    path('ranksystems/', views.RManageRankSystems, name="rank_manage_rank_systems"),
    path('ranksystems/<int:parent_id>', views.RManageRankSystems_folder, name="rank_manage_rank_systems_folder"),
    path('ranksystems/add_ranking_system/', views.RAddRankSystem, name="rank_add_ranking_system"),
    path('ranksystems/delete_ranking_system/<int:id>',views.RDeleteRankingSystem, name="rank_delete_ranking_system"),
    path('ranksystems/export/<int:id_rank_system>/<int:id_parent>', views.RExportRankingSystem, name="rank_export_ranking_system"),
    path('ranksystems/load_ranking_system/', views.RLoadRankingSystem, name="rank_load_ranking_system"),
    path('ranksystems/manage_ranking_system/<int:id>',views.RManageRankingSystem, name="rank_manage_ranking_system"),
    path('ranksystems/manage_rank_get_data/', views.RGetRankData, name="rank_get_data"),

    path('ranksystems/add_ranking_rule/<int:id>',views.RAddRankingRule, name="rank_add_ranking_rule"),
    path('ranksystems/modify_ranking_rule/<int:id_rank>/<int:id_rule>', views.RModifyRule, name="rank_modify_rule"),
    path('ranksystem/get_indicator/<int:id_rule>/<int:id_rank>', views.ajax_get_tech, name='rank_get_tech'),
    path('ranksystem/delete_rule/', views.RDeleteRule, name="rank_delete_rule"),

    path('ranksystems/add_indicator/<str:source>/<slug:indicator>$/add/<int:id_rank>', views.RAddIndicator, name='rank_add_indicator'),
    path('ranksystems/rank_get_indicator/<int:id_rank>', views.RGetIndicator, name="rank_get_indicator"),
    path('ranksystems/rank_get_indicator_add', views.RGetIndicatorAdd, name="rank_get_indicator_add"),
    path('ranksystems/modifytechnical/<str:indicator>/<int:tech_id>/<int:id_rank>/<str:requestfrom>/<int:requestrule>', views.RModifyIndicator, name='rank_modifytechnical'),
    path('ranksystems/deletetechnical/<int:tech_id>/<int:id_rank>/<str:requestfrom>/<int:requestrule>', views.RDeleteIndicator, name='rank_deletetechnical'),

    path('ranksystems/add_indicator_combination/<int:id>', views.RAddIndicatorCombination, name="rank_add_indicator_combination"),
    path('ranksystems/modify_indicator_combination/<int:id_comb>/<int:id_system>', views.RModifyIndicatorCombination, name="rank_modify_combination"),
    path('ranksystems/get_techs_comb/<int:id_comb>', views.RGetTechs, name="rank_get_techs_comb"),
    path('ranksystems/get_indicator_basic/<int:id_system>', views.RGetIndicatorBasic, name="rank_get_indicators_basic"),

    path('ranksystems/createfolder/', views.RCreateFolder, name="rank_create_folder"),
    path('ranksystems/deletefolder/', views.RDeleteFolder, name='rank_delete_folder'),

    path('ranksystems/default/', views.RManageDefaultSystems, name="rank_manage_default_systems"),

    #LIQUIDITY URL
    path('liquiditysystems/', views.LSManageLiquiditySystems, name="liqudity_manage_liquidity_systems"),
    path('liquiditysystems/<int:parent_id>', views.LSManageLiquiditySystems_folder, name="liquidity_manage_liquidity_system_folder"),
    path('liquiditysystems/add_liquidity_system/', views.LSAddLiquiditySystem, name="liquidity_add_liquidity_system"),
    path('liquiditysystems/export/<int:id_system>/<int:id_parent>', views.LSExportLiquiditySystem, name="liquidity_export_liquidity_system"),
    path('liquiditysystems/load_liquidity_system/', views.LSLoadLiquiditySystem, name="liquidity_load_liquidity_system"),
    path('liquiditysystems/createfolder/', views.LSCreateFolder, name="liquidity_create_folder"),
    path('liquiditysystems/deletefolder/', views.LSDeleteFolder, name="liquidity_delete_folder"),

    path('liquiditysystems/manage_liquidity_get_data/', views.LSGetLiquidityData, name="liquidity_get_data"),

    path('liquiditysystems/manage_liquidity_system/<int:id>',views.LSManageLiquiditySystem, name="liquidity_manage_liquidity_system"),
    path('liquiditysystems/delete_liquidity_system/<int:id_system>', views.LSDeleteLiquiditySystem, name="liquidity_delete_liquidity_system"),

    path('liquiditysystems/add_rule/<int:id_system>', views.LSAddRule, name="liquidity_add_rule"),
    path('liquiditysystems/modify_rule/<int:id_rule>/<int:id_system>', views.LSModifyRule, name="liquidity_modify_rule"),
    path('liquiditysystems/get_rule_modify/<int:id_rule>/<int:id_system>', views.LSajax_get_rule_modify, name="liquidity_get_rule_modify"),

    path('liquiditysystems/add_rule_combination/<int:id_system>', views.LSAddRuleCombination, name="liquidity_add_rule_combination"),
    path('liquiditysystems/modify_rulecombination/<int:id_rule>/<int:id_system>', views.LSModifyRuleCombination, name="liquidity_modify_rulecombination"),
    path('liquiditysystems/get_rule_combination_add/<int:id_system>', views.LSajax_get_rule_combination, name="liquidity_get_rule_combination_add"),
    path('liquiditysystems/get_rule_combination_modify/<int:id_system>', views.LSajax_get_rule_combination_modify, name="liquidity_get_rule_combination_modify"),

    path('liquiditysystems/add_liquidity_rule/<int:id_system>',views.LSAddLiquidityRule, name="liquidity_add_liquidity_rule"),
    path('liquiditysystems/add_liquidity_rule/<int:id_rule>/<int:id_system>',views.LSModifyLiquidityRule, name="liquidity_modify_liquidity_rule"),

    path('liquiditysystems/add_indicator/<str:source>/<slug:indicator>$/add/<int:id_system>', views.LSAddIndicator, name='liquidity_add_indicator'),
    path('liquiditysystems/liquidity_get_indicator/<int:id_system>', views.LSGetIndicator, name="liquidity_get_indicator"),
    path('liquiditysystems/<str:indicator>/<int:tech_id>/<int:id_system>/<str:requestfrom>/<int:requestrule>', views.LSModifyIndicator, name='liquidity_modifytechnical'),
    path('liquiditysystems/liquidity_get_indicator_form/', views.LSGetIndicatorForm, name="liquidity_get_indicator_form"),
    path('liquiditysystems/<int:tech_id>/<int:id_system>/<str:requestfrom>/<int:requestrule>', views.LSDeleteIndicator, name='liquidity_deletetechnical'),

    path('liquiditysystems/add_indicator_combination/<int:id_system>', views.LSAddIndicatorCombination, name="liquidity_add_indicator_combination"),
    path('liquiditysystems/modify_indicator_combination/<int:id_comb>/<int:id_system>', views.LSModifyIndicatorCombination, name="liquidity_modify_combination"),
    path('liquiditysystems/get_techs_comb/<int:id_comb>', views.LSGetTechs, name="liquidity_get_techs_comb"),
    path('liquiditysystems/get_indicator_basic/<int:id_system>', views.LSGetIndicatorBasic, name="liquidity_get_indicators_basic"),

    path('liquiditysystems/delete/', views.LSDelete, name="liquidity_delete"),
    path('liquiditysystems/default/', views.LSManageDefaultSystems, name="liquidity_manage_default_systems"),
]
