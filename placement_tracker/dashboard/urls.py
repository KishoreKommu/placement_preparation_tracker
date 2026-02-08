from django.urls import path
from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete-goal/<int:goal_id>/', views.delete_goal, name='delete_goal'),

    path('skills/', views.skills, name='skills'),
    path('skills/add-progress/<int:skill_id>/', views.add_skill_progress, name='add_skill_progress'),
    path('skills/add-goal/<int:skill_id>/', views.add_skill_goal, name='add_skill_goal'),

    path('goal/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),

    path('mock-tests/', views.mock_tests, name='mock_tests'),
    path('mock-tests/<int:test_id>/', views.take_mock_test, name='take_mock_test'),
    path('resume/', views.resume_upload, name='resume_upload'),

    path('analytics/', views.analytics_page, name='analytics_page'),

    path('companies/', views.target_companies, name='target_companies'),
    path('companies/<int:company_id>/', views.company_detail, name='company_detail'),


]
