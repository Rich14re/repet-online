from django.urls import path
from .views import register, login_view, course_view, task_view, account_view, logout_view, payment_success, add_explanation, explanation_detail
from . import views

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.task_detail, name='task_detail'),
    path('add/', views.add_task, name='add_task'),
    path('account/', account_view, name='account'),
    path('logout/', logout_view, name='logout'),
    path('add_explanation/', views.add_explanation, name='add_explanation'),
    path('explanation/<int:explain_id>/', views.explanation_detail, name='explanation_detail'),
    path('computer_science_tasks/', views.computer_science_tasks, name='computer_science_tasks'),
    path('computer_science_tasks/add/', views.add_computer_science_task, name='add_computer_science_task'),
    path('computer_science_tasks/<int:pk>/', views.computer_science_task_detail, name='computer_science_task_detail'),
    path('payment_success/<str:status_name>/', views.payment_success, name='payment_success'),
]