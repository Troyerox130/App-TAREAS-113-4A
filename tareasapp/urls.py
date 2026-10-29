
from django.urls import path
from . import views

urlpatterns = [
    # Página de inicio de sesión
    path('', views.login_pagina, name='login_pagina'),

    # Gestión de tareas mediante páginas HTML
    path('tareas/', views.inicio, name='inicio'),
    path('crear/', views.crear_tarea, name='crear_tarea'),
    path('detalle/<int:id>/', views.detalle_tarea, name='detalle_tarea'),
    path('editar/<int:id>/', views.editar_tarea, name='editar_tarea'),
    path('eliminar/<int:id>/', views.eliminar_tarea, name='eliminar_tarea'),

    # API REST: autenticación
    path('api/login/', views.LoginAPIView.as_view(), name='login_api'),

    # API REST: listar tareas
    path('api/tareas/', views.Tareasapiview.as_view(), name='api_tareas'),

    # API REST: consultar y eliminar una tarea individual
    path(
        'api/tareas/<int:id>/',
        views.TareaDetalleAPIView.as_view(),
        name='api_tarea_detalle'
    ),
]
