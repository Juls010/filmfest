from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Películas
    path('peliculas/', views.lista_peliculas, name='lista_peliculas'),
    path('peliculas/<int:pk>/', views.detalle_pelicula, name='detalle_pelicula'),
    path('peliculas/nueva/', views.crear_pelicula, name='crear_pelicula'),
    path('peliculas/<int:pk>/editar/', views.editar_pelicula, name='editar_pelicula'),
    path('peliculas/<int:pk>/eliminar/', views.eliminar_pelicula, name='eliminar_pelicula'),

    # Festivales
    path('festivales/', views.lista_festivales, name='lista_festivales'),
    path('festivales/<int:pk>/', views.detalle_festival, name='detalle_festival'),
    path('festivales/nuevo/', views.crear_festival, name='crear_festival'),
    path('festivales/<int:pk>/editar/', views.editar_festival, name='editar_festival'),
    path('festivales/<int:pk>/eliminar/', views.eliminar_festival, name='eliminar_festival'),

    # Proyecciones
    path('proyecciones/', views.lista_proyecciones, name='lista_proyecciones'),
    path('proyecciones/<int:pk>/', views.detalle_proyeccion, name='detalle_proyeccion'),
    path('proyecciones/nueva/', views.crear_proyeccion, name='crear_proyeccion'),
    path('proyecciones/<int:pk>/editar/', views.editar_proyeccion, name='editar_proyeccion'),
    path('proyecciones/<int:pk>/eliminar/', views.eliminar_proyeccion, name='eliminar_proyeccion'),

    # Estadísticas
    path('estadisticas/', views.estadisticas, name='estadisticas'),
]
