from django.urls import path
from . import views
app_name = 'chart'
urlpatterns = [
    path('', views.view_chart, name="view_chart"),
    path('addChart', views.add_chart, name="add_chart"),
    path('removeChartList', views.remove_chart_list, name="remove_chart_list"),
    path('removeChart/<int:chart_id>', views.remove_chart, name="remove_chart"),
    path('addList/<int:chart_id>', views.add_list, name="add_list"),
    path('addList/<int:chart_id>/<int:list_id>/<str:f_name>', views.add_universe, name="add_universe"),
    path('addInstrument/<int:chart_id>/<int:list_id>/<str:f_name>', views.add_instrument, name="add_instrument"),
    path('getInstrument/', views.get_instrument, name="get_instrument"),
    path('viewInstrument/', views.view_instrument, name="view_instrument"),
    path('getModifyList/<int:chart_id>', views.get_modify_list, name="get_modify_list"),
    path('modifyChangeName/<int:list_id>/<int:chart_id>', views.modify_change_name, name="m_change_name"),
    path('modifyAddInstrument/<int:list_id>/<int:chart_id>', views.modify_add_instrument, name="m_add_instrument"),
    path('getDeleteInstruments/<int:list_id>/<int:chart_id>', views.get_delete_instruments, name="get_delete_instruments"),
    path('modifyDeleteInstruments/<int:instrument_id>/<int:chart_id>/<int:list_id>', views.m_delete_instrument, name="m_delete_instrument"),
    path('selectModifyMode/<int:list_id>/<int:chart_id>', views.select_modify_mode, name="select_modify_mode"),
    path('getDeleteList/<int:chart_id>', views.get_delete_list, name="get_delete_list"),
    path('DeleteList/<int:list_id>/<int:chart_id>', views.delete_list, name="delete_list"),
    path('writeJson', views.write_json, name="write_json"),
    path('update_chart_settings', views.update_chart_settings),
    path('update_overlay', views.update_overlay),
    path('update_indicator', views.update_indicator),
    path('delete_overlay/<int:chart_id>/<int:overlay_id>', views.delete_overlay),
    path('delete_indicator/<int:chart_id>/<int:indicator_id>', views.delete_indicator)
]
