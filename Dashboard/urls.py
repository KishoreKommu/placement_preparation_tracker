from django.urls import path
from . import views

urlpatterns = [

    # AUTH
    path('', views.welcome, name='welcome'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # DASHBOARD
    path('dashboard/', views.dashboard, name='dashboard'),

    # SKILLS
    path('skills/', views.skills, name='skills'),
    path('skills/add-progress/<int:skill_id>/', views.add_skill_progress, name='add_skill_progress'),
    path('skills/add-goal/<int:skill_id>/', views.add_skill_goal, name='add_skill_goal'),

    path('goal/delete/<int:goal_id>/', views.delete_goal, name='delete_goal'),

    # MOCK TESTS
    path('mock-tests/', views.mock_tests, name='mock_tests'),
    path('mock-tests/<int:test_id>/', views.take_mock_test, name='take_mock_test'),

    # RESUME AI
    path('resume/', views.resume_upload, name='resume_upload'),

    # ANALYTICS
    path('analytics/', views.analytics_page, name='analytics_page'),

    # COMPANY HUB
    path('companies/', views.target_companies, name='target_companies'),
    path('companies/<int:company_id>/', views.company_detail, name='company_detail'),

    # PROFILE
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # ROADMAPS
    path('roadmaps/', views.roadmap_page, name='roadmaps'),
    path('roadmap/', views.roadmap_page, name='roadmap'),
    path('roadmap/<slug:slug>/', views.roadmap_detail, name='roadmap_detail'),

    # CHATBOT
    path('chatbot/', views.chatbot, name='chatbot'),
    path('chatbot-response/', views.chatbot_response, name='chatbot_response'),

    # DAILY PLANNER
    path('daily-planner/', views.daily_planner, name='daily_planner'),

    # PDF DOWNLOAD
    path('download-analysis-pdf/', views.download_analysis_pdf, name='download_analysis_pdf'),

    # JOB NOTIFICATIONS
    path('jobs/', views.job_notifications, name='job_notifications'),

    # GAMES HUB
    path("games/", views.games, name="games"),

    # GAME PAGES
    path("games/reaction/", views.reaction_game, name="reaction_game"),
    path("games/memory/", views.memory_game, name="memory_game"),
    path("games/math/", views.math_game, name="math_game"),
    path("games/color/", views.color_game, name="color_game"),
    path("games/snake/", views.snake_game, name="snake_game"),
    path("games/tictactoe/", views.tictactoe_game, name="tictactoe_game"),
    path("games/2048/", views.game_2048, name="game_2048"),


    # path('result/<int:test_id>/', views.result, name='result'),
    # path('test-result/<int:test_id>/', views.test_result, name='test_result'),
    
#     path('test/<int:test_id>/result/', views.result_view, name='result'),
#     path('test/<int:test_id>/', views.test_view, name='test'),  
# ]
]