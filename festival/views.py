from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count, Sum, Max, Min
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Pelicula, Festival, Proyeccion
from .forms import PeliculaForm, FestivalForm, ProyeccionForm


# ──────────────────────────────────────────────
#  HOME
# ──────────────────────────────────────────────

def home(request):
    ultimas_peliculas = Pelicula.objects.all()[:6]
    proximos_festivales = Festival.objects.filter(activo=True)[:4]
    return render(request, 'festival/home.html', {
        'ultimas_peliculas': ultimas_peliculas,
        'proximos_festivales': proximos_festivales,
    })


# ──────────────────────────────────────────────
#  PELÍCULAS
# ──────────────────────────────────────────────

def lista_peliculas(request):
    """Lista con paginación, filtrado y ordenado."""
    peliculas = Pelicula.objects.all()

    # Filtrado
    q = request.GET.get('q', '')
    genero = request.GET.get('genero', '')
    anio_desde = request.GET.get('anio_desde', '')
    anio_hasta = request.GET.get('anio_hasta', '')

    if q:
        peliculas = peliculas.filter(
            Q(titulo__icontains=q) | Q(director__icontains=q)
        )
    if genero:
        peliculas = peliculas.filter(genero=genero)
    if anio_desde:
        peliculas = peliculas.filter(anio__gte=anio_desde)
    if anio_hasta:
        peliculas = peliculas.filter(anio__lte=anio_hasta)

    # Ordenado
    orden = request.GET.get('orden', '-anio')
    opciones_orden = ['-anio', 'anio', 'titulo', '-titulo', '-puntuacion', 'puntuacion']
    if orden in opciones_orden:
        peliculas = peliculas.order_by(orden)

    # Paginación
    paginator = Paginator(peliculas, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    from .models import GENEROS
    return render(request, 'festival/pelicula_list.html', {
        'page_obj': page_obj,
        'generos': GENEROS,
        'q': q,
        'genero': genero,
        'orden': orden,
    })


def detalle_pelicula(request, pk):
    pelicula = get_object_or_404(Pelicula, pk=pk)
    proyecciones = pelicula.proyecciones.select_related('festival').order_by('fecha_hora')
    return render(request, 'festival/pelicula_detail.html', {
        'pelicula': pelicula,
        'proyecciones': proyecciones,
    })


@login_required
def crear_pelicula(request):
    if request.method == 'POST':
        form = PeliculaForm(request.POST)
        if form.is_valid():
            pelicula = form.save(commit=False)
            pelicula.creada_por = request.user
            pelicula.save()
            messages.success(request, f'Película "{pelicula.titulo}" creada correctamente.')
            return redirect('detalle_pelicula', pk=pelicula.pk)
    else:
        form = PeliculaForm()
    return render(request, 'festival/pelicula_form.html', {'form': form, 'titulo': 'Nueva película'})


@login_required
def editar_pelicula(request, pk):
    pelicula = get_object_or_404(Pelicula, pk=pk)
    if not request.user.is_staff and pelicula.creada_por != request.user:
        messages.error(request, 'No tienes permiso para editar esta película.')
        return redirect('detalle_pelicula', pk=pk)
    if request.method == 'POST':
        form = PeliculaForm(request.POST, instance=pelicula)
        if form.is_valid():
            form.save()
            messages.success(request, f'Película "{pelicula.titulo}" actualizada.')
            return redirect('detalle_pelicula', pk=pk)
    else:
        form = PeliculaForm(instance=pelicula)
    return render(request, 'festival/pelicula_form.html', {'form': form, 'titulo': 'Editar película', 'pelicula': pelicula})


@staff_member_required
def eliminar_pelicula(request, pk):
    pelicula = get_object_or_404(Pelicula, pk=pk)
    if request.method == 'POST':
        titulo = pelicula.titulo
        pelicula.delete()
        messages.success(request, f'Película "{titulo}" eliminada.')
        return redirect('lista_peliculas')
    return render(request, 'festival/confirmar_eliminar.html', {'objeto': pelicula, 'tipo': 'película'})


# ──────────────────────────────────────────────
#  FESTIVALES
# ──────────────────────────────────────────────

def lista_festivales(request):
    """Lista con paginación."""
    festivales = Festival.objects.all()

    # Filtrado
    q = request.GET.get('q', '')
    activo = request.GET.get('activo', '')
    if q:
        festivales = festivales.filter(
            Q(nombre__icontains=q) | Q(ciudad__icontains=q) | Q(tematica__icontains=q)
        )
    if activo == '1':
        festivales = festivales.filter(activo=True)
    elif activo == '0':
        festivales = festivales.filter(activo=False)

    orden = request.GET.get('orden', '-fecha_inicio')
    festivales = festivales.order_by(orden)

    paginator = Paginator(festivales, 8)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'festival/festival_list.html', {
        'page_obj': page_obj,
        'q': q,
        'activo': activo,
    })


def detalle_festival(request, pk):
    festival = get_object_or_404(Festival, pk=pk)
    proyecciones = festival.proyecciones.select_related('pelicula').order_by('fecha_hora')
    return render(request, 'festival/festival_detail.html', {
        'festival': festival,
        'proyecciones': proyecciones,
    })


@login_required
def crear_festival(request):
    if request.method == 'POST':
        form = FestivalForm(request.POST)
        if form.is_valid():
            festival = form.save(commit=False)
            festival.creado_por = request.user
            festival.save()
            messages.success(request, f'Festival "{festival.nombre}" creado correctamente.')
            return redirect('detalle_festival', pk=festival.pk)
    else:
        form = FestivalForm()
    return render(request, 'festival/festival_form.html', {'form': form, 'titulo': 'Nuevo festival'})


@login_required
def editar_festival(request, pk):
    festival = get_object_or_404(Festival, pk=pk)
    if not request.user.is_staff and festival.creado_por != request.user:
        messages.error(request, 'No tienes permiso para editar este festival.')
        return redirect('detalle_festival', pk=pk)
    if request.method == 'POST':
        form = FestivalForm(request.POST, instance=festival)
        if form.is_valid():
            form.save()
            messages.success(request, f'Festival "{festival.nombre}" actualizado.')
            return redirect('detalle_festival', pk=pk)
    else:
        form = FestivalForm(instance=festival)
    return render(request, 'festival/festival_form.html', {'form': form, 'titulo': 'Editar festival', 'festival': festival})


@staff_member_required
def eliminar_festival(request, pk):
    festival = get_object_or_404(Festival, pk=pk)
    if request.method == 'POST':
        nombre = festival.nombre
        festival.delete()
        messages.success(request, f'Festival "{nombre}" eliminado.')
        return redirect('lista_festivales')
    return render(request, 'festival/confirmar_eliminar.html', {'objeto': festival, 'tipo': 'festival'})


# ──────────────────────────────────────────────
#  PROYECCIONES
# ──────────────────────────────────────────────

def lista_proyecciones(request):
    proyecciones = Proyeccion.objects.select_related('pelicula', 'festival').all()

    festival_id = request.GET.get('festival', '')
    if festival_id:
        proyecciones = proyecciones.filter(festival_id=festival_id)

    orden = request.GET.get('orden', 'fecha_hora')
    proyecciones = proyecciones.order_by(orden)

    paginator = Paginator(proyecciones, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    festivales = Festival.objects.all()
    return render(request, 'festival/proyeccion_list.html', {
        'page_obj': page_obj,
        'festivales': festivales,
        'festival_id': festival_id,
    })


def detalle_proyeccion(request, pk):
    proyeccion = get_object_or_404(Proyeccion.objects.select_related('pelicula', 'festival'), pk=pk)
    return render(request, 'festival/proyeccion_detail.html', {'proyeccion': proyeccion})


@login_required
def crear_proyeccion(request):
    if request.method == 'POST':
        form = ProyeccionForm(request.POST)
        if form.is_valid():
            proyeccion = form.save()
            messages.success(request, 'Proyección creada correctamente.')
            return redirect('detalle_proyeccion', pk=proyeccion.pk)
    else:
        form = ProyeccionForm()
    return render(request, 'festival/proyeccion_form.html', {'form': form, 'titulo': 'Nueva proyección'})


@login_required
def editar_proyeccion(request, pk):
    proyeccion = get_object_or_404(Proyeccion, pk=pk)
    if request.method == 'POST':
        form = ProyeccionForm(request.POST, instance=proyeccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proyección actualizada.')
            return redirect('detalle_proyeccion', pk=pk)
    else:
        form = ProyeccionForm(instance=proyeccion)
    return render(request, 'festival/proyeccion_form.html', {'form': form, 'titulo': 'Editar proyección', 'proyeccion': proyeccion})


@staff_member_required
def eliminar_proyeccion(request, pk):
    proyeccion = get_object_or_404(Proyeccion, pk=pk)
    if request.method == 'POST':
        proyeccion.delete()
        messages.success(request, 'Proyección eliminada.')
        return redirect('lista_proyecciones')
    return render(request, 'festival/confirmar_eliminar.html', {'objeto': proyeccion, 'tipo': 'proyección'})


# ──────────────────────────────────────────────
#  ESTADÍSTICAS
# ──────────────────────────────────────────────

@login_required
def estadisticas(request):
    # 1. Puntuación media por género
    puntuacion_por_genero = (
        Pelicula.objects.values('genero')
        .annotate(media=Avg('puntuacion'))
        .order_by('-media')
    )

    # 2. Número de proyecciones por festival
    proyecciones_por_festival = (
        Festival.objects.annotate(num_proyecciones=Count('proyecciones'))
        .order_by('-num_proyecciones')[:10]
    )

    # 3. Películas más proyectadas
    peliculas_mas_proyectadas = (
        Pelicula.objects.annotate(num_proyecciones=Count('proyecciones'))
        .order_by('-num_proyecciones')[:10]
    )

    # 4. Distribución por género
    peliculas_por_genero = (
        Pelicula.objects.values('genero')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    # 5. Entradas totales por festival
    entradas_por_festival = (
        Festival.objects.annotate(
            total_entradas=Sum('proyecciones__entradas_disponibles')
        ).order_by('-total_entradas')[:10]
    )

    # 6. Directores con más películas
    directores = (
        Pelicula.objects.values('director')
        .annotate(total=Count('id'))
        .order_by('-total')[:10]
    )

    totales = {
        'peliculas': Pelicula.objects.count(),
        'festivales': Festival.objects.count(),
        'proyecciones': Proyeccion.objects.count(),
        'puntuacion_media': Pelicula.objects.aggregate(m=Avg('puntuacion'))['m'],
    }

    return render(request, 'festival/estadisticas.html', {
        'puntuacion_por_genero': puntuacion_por_genero,
        'proyecciones_por_festival': proyecciones_por_festival,
        'peliculas_mas_proyectadas': peliculas_mas_proyectadas,
        'peliculas_por_genero': peliculas_por_genero,
        'entradas_por_festival': entradas_por_festival,
        'directores': directores,
        'totales': totales,
    })
