from django.urls import path
from . import views

app_name = 'optimize'

urlpatterns = [
    path('', views.Index, name="index"),

    path('manage/create_folder/', views.PeriodCreateFolder, name="period_create_folder"),
    path('manage/delete_folder/', views.PeriodDeleteFolder, name="period_delete_folder"),

    path('manage/manage_folder/<int:id_folder>/', views.PeriodManageFolder, name="period_manage_folder"),
    path('manage/ajax_get_tree_element/', views.period_ajax_get_tree_element, name="period_get_tree_element"),

    path('manage/strategy/', views.PeriodManageIndex, name="period_manage_index"),
    path('manage/create_strategy/', views.PeriodCreateStrategy, name="period_create_strategy"),
    path('manage/delete_strategy/<int:id_strategy>/', views.PeriodDeleteStrategy, name="period_delete_strategy"),
    path('manage/strategy/manage_strategy/<int:id_strategy>/', views.PeriodManageStrategy, name="period_manage_strategy"),
    path('manage/strategy/modify_general/<int:id_strategy>/', views.PeriodModifyGeneral, name="period_modify_general"),
    path('manage/export_strategy/<int:id_strategy>/', views.PeriodExportStrategy, name="period_export_strategy"),
    path('manage/load_strategy/', views.PeriodLoadStrategy, name="period_load_strategy"),

    path('manage/manage_result/', views.PeriodResults, name="period_result"),
    path('manage/launch_strategy/<int:id_strategy>/',views.PeriodLaunchStrategy, name="period_launch_strategy"),
    path('manage/launch_state/', views.PeriodLaunchState, name="period_launch_state"),
    path('manage/manage_result/<int:id_strategy>/',views.PeriodLaunchResult, name="period_launch_result"),    

    path('manage/add_strategy/<int:id_strategy>/', views.PeriodAddStrategy, name="period_add_strategy"),
    path('manage/change_strategy/<int:id_strategy>/', views.PeriodChangeStrategy, name="period_change_strategy"),
    path('manage/remove_strategy/<int:id_strategy>/', views.PeriodRemoveStrategy, name="period_remove_strategy"),

    path('manage/', views.PeriodManage, name="period_manage"),
]
