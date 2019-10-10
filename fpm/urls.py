from django.urls import path
from . import views
app_name ='fpm'

urlpatterns =[
    path('', views.IndexView.as_view(), name='family_index'), # 家庭绩效首页
    path('login/',views.LoginView.as_view(),name='family_login'), #家庭绩效系统登录页
    path('logout/',views.LogoutView.as_view(),name='family_logout'), #家庭绩效系统登录页
    path('perfitems/',views.PerfItemIndexView.as_view(),name='perfitems_index'), #成员绩效项目
    path('perfitems/<int:pk>/', views.PerfItemView.as_view(), name='member_perfitems'),  # 成员绩效项目
    path('perfitems/<int:pk>/add/', views.PerfItemCreateView.as_view(), name='member_perfitems_add'),  # 成员绩效项目
    path('perfitems/<int:pk>/update/', views.PerfItemUpdateView.as_view(), name='member_perfitems_update'),  # 成员绩效项目编辑
    path('perfitems/<int:pk>/delete/', views.PerfItemDeleteView.as_view(), name='member_perfitems_delete'),  # 成员绩效项目删除

    path('perfrecords/',views.PerfRecordIndexView.as_view(), name='perfrecords_index'),
    path('perfrecords/<int:year>-<int:month>-<int:day>/<int:pk>/', views.PerfRecordView.as_view(),name='member_perfrecords'),
    path('perfrecords/<int:year>-<int:month>-<int:day>/<int:pk>/add', views.PerfRecordCreateView.as_view(),
         name='member_perfrecords_add'),

]