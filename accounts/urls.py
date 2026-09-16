from django.urls import path

from .views import (
    home,
    register,
    login,
    dashboard,
    logout,
    set_target,
    add_jap,
    jap_history,
    achievements,
    naam_jap_info,
    profile,
    daily_goal,
    settings_view,
    level_1,
    level_2,
    level_3
)


urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout, name='logout'),

    path('set-target/', set_target, name='set_target'),
    path('add-jap/', add_jap, name='add_jap'),
    path('jap-history/', jap_history, name='jap_history'),

    path('achievements/', achievements, name='achievements'),
    path('naam-jap-info/', naam_jap_info, name='naam_jap_info'),
    path('profile/', profile, name='profile'),
    path('daily-goal/', daily_goal, name='daily_goal'),
    path('settings/', settings_view, name='settings'),
    path('level-1/', level_1, name='level_1'),
    path('level-2/', level_2, name='level_2'),
    path('level-3/', level_3, name='level_3'),
]