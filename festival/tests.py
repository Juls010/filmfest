from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import datetime

from .models import Pelicula, Festival, Proyeccion
from .forms import PeliculaForm, FestivalForm, ProyeccionForm


def crear_pelicula(**kwargs):
    defaults = {
        'titulo': 'Película de prueba',
        'director': 'Director Test',
        'anio': 2020,
        'duracion_minutos': 120,
        'genero': 'drama',
        'sinopsis': 'Una sinopsis de prueba para el test.',
        'puntuacion': Decimal('7.5'),
    }
    defaults.update(kwargs)
    return Pelicula.objects.create(**defaults)


def crear_festival(**kwargs):
    defaults = {
        'nombre': 'Festival de prueba',
        'ciudad': 'Sevilla',
        'pais': 'España',
        'fecha_inicio': datetime.date(2025, 6, 1),
        'fecha_fin': datetime.date(2025, 6, 10),
        'tematica': 'Cine independiente',
        'aforo_maximo': 500,
    }
    defaults.update(kwargs)
    return Festival.objects.create(**defaults)


def crear_proyeccion(pelicula, festival, **kwargs):
    defaults = {
        'pelicula': pelicula,
        'festival': festival,
        'fecha_hora': timezone.make_aware(datetime.datetime(2025, 6, 3, 18, 0)),
        'sala': 'sala_principal',
        'entradas_disponibles': 100,
        'precio_entrada': Decimal('8.00'),
    }
    defaults.update(kwargs)
    return Proyeccion.objects.create(**defaults)


#  Tests de modelos

class PeliculaModelTest(TestCase):

    def test_str_representacion(self):
        p = crear_pelicula(titulo='Casablanca', anio=1942)
        self.assertEqual(str(p), 'Casablanca (1942)')

    def test_validador_anio_demasiado_antiguo(self):
        p = Pelicula(titulo='Vieja', director='Alguien', anio=1800,
                     duracion_minutos=90, genero='drama', sinopsis='Sinopsis.')
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_validador_anio_futuro_lejano(self):
        p = Pelicula(titulo='Futura', director='Alguien', anio=2099,
                     duracion_minutos=90, genero='drama', sinopsis='Sinopsis.')
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_validador_puntuacion_negativa(self):
        p = Pelicula(titulo='Test', director='Dir', anio=2020,
                     duracion_minutos=90, genero='drama', sinopsis='Sinopsis.',
                     puntuacion=Decimal('-1'))
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_validador_puntuacion_mayor_diez(self):
        p = Pelicula(titulo='Test', director='Dir', anio=2020,
                     duracion_minutos=90, genero='drama', sinopsis='Sinopsis.',
                     puntuacion=Decimal('11'))
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_pelicula_valida_no_lanza_error(self):
        p = Pelicula(titulo='Buena película', director='Director', anio=2020,
                     duracion_minutos=100, genero='drama', sinopsis='Sinopsis.',
                     puntuacion=Decimal('8.0'))
        try:
            p.full_clean()
        except ValidationError:
            self.fail('Una película válida no debería lanzar ValidationError')

    def test_titulo_demasiado_corto(self):
        p = Pelicula(titulo='A', director='Director', anio=2020,
                     duracion_minutos=100, genero='drama', sinopsis='Sinopsis.')
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_ordering_por_defecto(self):
        crear_pelicula(titulo='B', anio=2019)
        crear_pelicula(titulo='A', anio=2022)
        peliculas = list(Pelicula.objects.values_list('anio', flat=True))
        self.assertEqual(peliculas, sorted(peliculas, reverse=True))


class FestivalModelTest(TestCase):

    def test_str_representacion(self):
        f = crear_festival(nombre='Cannes', ciudad='Cannes', fecha_inicio=datetime.date(2025, 5, 1))
        self.assertIn('Cannes', str(f))

    def test_fechas_invertidas_lanza_error(self):
        f = Festival(nombre='Test', ciudad='Test', pais='España',
                     fecha_inicio=datetime.date(2025, 6, 10),
                     fecha_fin=datetime.date(2025, 6, 1),
                     tematica='Test', aforo_maximo=100)
        with self.assertRaises(ValidationError):
            f.full_clean()

    def test_festival_mas_de_30_dias(self):
        f = Festival(nombre='Test', ciudad='Test', pais='España',
                     fecha_inicio=datetime.date(2025, 1, 1),
                     fecha_fin=datetime.date(2025, 3, 1),
                     tematica='Test', aforo_maximo=100)
        with self.assertRaises(ValidationError):
            f.full_clean()

    def test_aforo_minimo(self):
        f = Festival(nombre='Test', ciudad='Test', pais='España',
                     fecha_inicio=datetime.date(2025, 6, 1),
                     fecha_fin=datetime.date(2025, 6, 5),
                     tematica='Test', aforo_maximo=5)
        with self.assertRaises(ValidationError):
            f.full_clean()

    def test_nombre_demasiado_corto(self):
        f = Festival(nombre='AB', ciudad='Test', pais='España',
                     fecha_inicio=datetime.date(2025, 6, 1),
                     fecha_fin=datetime.date(2025, 6, 5),
                     tematica='Test', aforo_maximo=100)
        with self.assertRaises(ValidationError):
            f.full_clean()

    def test_duracion_dias_property(self):
        f = crear_festival(
            fecha_inicio=datetime.date(2025, 6, 1),
            fecha_fin=datetime.date(2025, 6, 5)
        )
        self.assertEqual(f.duracion_dias, 5)

    def test_festival_valido(self):
        f = Festival(nombre='Festival válido', ciudad='Madrid', pais='España',
                     fecha_inicio=datetime.date(2025, 6, 1),
                     fecha_fin=datetime.date(2025, 6, 10),
                     tematica='Drama', aforo_maximo=200)
        try:
            f.full_clean()
        except ValidationError:
            self.fail('Un festival válido no debería lanzar ValidationError')


class ProyeccionModelTest(TestCase):

    def setUp(self):
        self.pelicula = crear_pelicula()
        self.festival = crear_festival()

    def test_str_contiene_titulo_pelicula(self):
        p = crear_proyeccion(self.pelicula, self.festival)
        self.assertIn(self.pelicula.titulo, str(p))

    def test_proyeccion_fuera_de_fechas_festival(self):
        p = Proyeccion(
            pelicula=self.pelicula, festival=self.festival,
            fecha_hora=timezone.make_aware(datetime.datetime(2025, 12, 1, 18, 0)),
            sala='sala_principal', entradas_disponibles=100, precio_entrada=Decimal('5.00'),
        )
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_entradas_superan_aforo(self):
        p = Proyeccion(
            pelicula=self.pelicula, festival=self.festival,
            fecha_hora=timezone.make_aware(datetime.datetime(2025, 6, 3, 18, 0)),
            sala='sala_a', entradas_disponibles=9999, precio_entrada=Decimal('5.00'),
        )
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_precio_negativo(self):
        p = Proyeccion(
            pelicula=self.pelicula, festival=self.festival,
            fecha_hora=timezone.make_aware(datetime.datetime(2025, 6, 3, 20, 0)),
            sala='sala_b', entradas_disponibles=50, precio_entrada=Decimal('-1.00'),
        )
        with self.assertRaises(ValidationError):
            p.full_clean()

    def test_proyeccion_valida(self):
        p = Proyeccion(
            pelicula=self.pelicula, festival=self.festival,
            fecha_hora=timezone.make_aware(datetime.datetime(2025, 6, 4, 18, 0)),
            sala='sala_c', entradas_disponibles=100, precio_entrada=Decimal('8.00'),
        )
        try:
            p.full_clean()
        except ValidationError as e:
            self.fail(f'Proyección válida no debería fallar: {e}')

    def test_es_preestreno_por_defecto_false(self):
        p = crear_proyeccion(self.pelicula, self.festival)
        self.assertFalse(p.es_preestreno)


#  Tests de formularios

class PeliculaFormTest(TestCase):

    def datos_validos(self):
        return {
            'titulo': 'Mi película',
            'director': 'Ana García',
            'anio': 2021,
            'duracion_minutos': 110,
            'genero': 'drama',
            'sinopsis': 'Una sinopsis de prueba suficientemente larga.',
            'puntuacion': '7.5',
            'poster_url': '',
        }

    def test_form_valido(self):
        form = PeliculaForm(data=self.datos_validos())
        self.assertTrue(form.is_valid(), form.errors)

    def test_titulo_requerido(self):
        datos = self.datos_validos()
        datos['titulo'] = ''
        form = PeliculaForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('titulo', form.errors)

    def test_titulo_muy_corto(self):
        datos = self.datos_validos()
        datos['titulo'] = 'A'
        form = PeliculaForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('titulo', form.errors)

    def test_director_con_numeros(self):
        datos = self.datos_validos()
        datos['director'] = 'Director123'
        form = PeliculaForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('director', form.errors)

    def test_duracion_cero(self):
        datos = self.datos_validos()
        datos['duracion_minutos'] = 0
        form = PeliculaForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_duracion_excesiva(self):
        datos = self.datos_validos()
        datos['duracion_minutos'] = 700
        form = PeliculaForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_mensaje_error_titulo_requerido(self):
        datos = self.datos_validos()
        datos['titulo'] = ''
        form = PeliculaForm(data=datos)
        self.assertIn('obligatorio', str(form.errors['titulo']))

    def test_mensaje_error_director_requerido(self):
        datos = self.datos_validos()
        datos['director'] = ''
        form = PeliculaForm(data=datos)
        self.assertIn('director', form.errors)

    def test_puntuacion_invalida(self):
        datos = self.datos_validos()
        datos['puntuacion'] = '15'
        form = PeliculaForm(data=datos)
        self.assertFalse(form.is_valid())


class FestivalFormTest(TestCase):

    def datos_validos(self):
        return {
            'nombre': 'FestivalTest',
            'ciudad': 'Sevilla',
            'pais': 'España',
            'fecha_inicio': '2025-06-01',
            'fecha_fin': '2025-06-10',
            'tematica': 'Cine independiente',
            'aforo_maximo': 300,
            'descripcion': '',
            'activo': True,
        }

    def test_form_valido(self):
        form = FestivalForm(data=self.datos_validos())
        self.assertTrue(form.is_valid(), form.errors)

    def test_fechas_invertidas(self):
        datos = self.datos_validos()
        datos['fecha_inicio'] = '2025-06-10'
        datos['fecha_fin'] = '2025-06-01'
        form = FestivalForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_fin', form.errors)

    def test_aforo_minimo(self):
        datos = self.datos_validos()
        datos['aforo_maximo'] = 5
        form = FestivalForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('aforo_maximo', form.errors)

    def test_nombre_muy_corto(self):
        datos = self.datos_validos()
        datos['nombre'] = 'AB'
        form = FestivalForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_festival_mayor_30_dias(self):
        datos = self.datos_validos()
        datos['fecha_inicio'] = '2025-01-01'
        datos['fecha_fin'] = '2025-03-01'
        form = FestivalForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_mensaje_nombre_requerido(self):
        datos = self.datos_validos()
        datos['nombre'] = ''
        form = FestivalForm(data=datos)
        self.assertIn('obligatorio', str(form.errors['nombre']))

    def test_mensaje_fecha_invalida(self):
        datos = self.datos_validos()
        datos['fecha_inicio'] = ''
        form = FestivalForm(data=datos)
        self.assertIn('fecha_inicio', form.errors)

    def test_ciudad_requerida(self):
        datos = self.datos_validos()
        datos['ciudad'] = ''
        form = FestivalForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_tematica_requerida(self):
        datos = self.datos_validos()
        datos['tematica'] = ''
        form = FestivalForm(data=datos)
        self.assertFalse(form.is_valid())


class ProyeccionFormTest(TestCase):

    def setUp(self):
        self.pelicula = crear_pelicula()
        self.festival = crear_festival()

    def datos_validos(self):
        return {
            'pelicula': self.pelicula.pk,
            'festival': self.festival.pk,
            'fecha_hora': '2025-06-03T18:00',
            'sala': 'sala_principal',
            'entradas_disponibles': 100,
            'precio_entrada': '8.00',
            'es_preestreno': False,
        }

    def test_form_valido(self):
        form = ProyeccionForm(data=self.datos_validos())
        self.assertTrue(form.is_valid(), form.errors)

    def test_pelicula_requerida(self):
        datos = self.datos_validos()
        datos['pelicula'] = ''
        form = ProyeccionForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('pelicula', form.errors)

    def test_festival_requerido(self):
        datos = self.datos_validos()
        datos['festival'] = ''
        form = ProyeccionForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_precio_negativo(self):
        datos = self.datos_validos()
        datos['precio_entrada'] = '-5'
        form = ProyeccionForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('precio_entrada', form.errors)

    def test_precio_excesivo(self):
        datos = self.datos_validos()
        datos['precio_entrada'] = '600'
        form = ProyeccionForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_entradas_superan_aforo(self):
        datos = self.datos_validos()
        datos['entradas_disponibles'] = 9999
        form = ProyeccionForm(data=datos)
        self.assertFalse(form.is_valid())

    def test_fecha_fuera_del_festival(self):
        datos = self.datos_validos()
        datos['fecha_hora'] = '2025-12-01T18:00'
        form = ProyeccionForm(data=datos)
        self.assertFalse(form.is_valid())
        self.assertIn('fecha_hora', form.errors)

    def test_mensaje_pelicula_requerida(self):
        datos = self.datos_validos()
        datos['pelicula'] = ''
        form = ProyeccionForm(data=datos)
        self.assertIn('seleccionar', str(form.errors['pelicula']))

    def test_sala_requerida(self):
        datos = self.datos_validos()
        datos['sala'] = ''
        form = ProyeccionForm(data=datos)
        self.assertFalse(form.is_valid())


#  Tests de vistas

class VistasPublicasTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='normal', password='pass1234')
        self.pelicula = crear_pelicula()
        self.festival = crear_festival()
        self.proyeccion = crear_proyeccion(self.pelicula, self.festival)

    def test_home_sin_login(self):
        r = self.client.get(reverse('home'))
        self.assertEqual(r.status_code, 200)

    def test_home_con_login(self):
        self.client.login(username='normal', password='pass1234')
        r = self.client.get(reverse('home'))
        self.assertEqual(r.status_code, 200)

    def test_lista_peliculas_sin_login(self):
        r = self.client.get(reverse('lista_peliculas'))
        self.assertEqual(r.status_code, 200)

    def test_lista_peliculas_con_login(self):
        self.client.login(username='normal', password='pass1234')
        r = self.client.get(reverse('lista_peliculas'))
        self.assertEqual(r.status_code, 200)

    def test_detalle_pelicula_sin_login(self):
        r = self.client.get(reverse('detalle_pelicula', args=[self.pelicula.pk]))
        self.assertEqual(r.status_code, 200)

    def test_detalle_pelicula_con_login(self):
        self.client.login(username='normal', password='pass1234')
        r = self.client.get(reverse('detalle_pelicula', args=[self.pelicula.pk]))
        self.assertEqual(r.status_code, 200)

    def test_lista_festivales_sin_login(self):
        r = self.client.get(reverse('lista_festivales'))
        self.assertEqual(r.status_code, 200)

    def test_lista_festivales_con_login(self):
        self.client.login(username='normal', password='pass1234')
        r = self.client.get(reverse('lista_festivales'))
        self.assertEqual(r.status_code, 200)

    def test_detalle_festival_sin_login(self):
        r = self.client.get(reverse('detalle_festival', args=[self.festival.pk]))
        self.assertEqual(r.status_code, 200)

    def test_detalle_festival_con_login(self):
        self.client.login(username='normal', password='pass1234')
        r = self.client.get(reverse('detalle_festival', args=[self.festival.pk]))
        self.assertEqual(r.status_code, 200)

    def test_lista_proyecciones_sin_login(self):
        r = self.client.get(reverse('lista_proyecciones'))
        self.assertEqual(r.status_code, 200)

    def test_lista_proyecciones_con_login(self):
        self.client.login(username='normal', password='pass1234')
        r = self.client.get(reverse('lista_proyecciones'))
        self.assertEqual(r.status_code, 200)

    def test_detalle_proyeccion_sin_login(self):
        r = self.client.get(reverse('detalle_proyeccion', args=[self.proyeccion.pk]))
        self.assertEqual(r.status_code, 200)

    def test_detalle_proyeccion_con_login(self):
        self.client.login(username='normal', password='pass1234')
        r = self.client.get(reverse('detalle_proyeccion', args=[self.proyeccion.pk]))
        self.assertEqual(r.status_code, 200)


class VistasLoginRequeridoTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='normal', password='pass1234')
        self.pelicula = crear_pelicula()
        self.festival = crear_festival()
        self.proyeccion = crear_proyeccion(self.pelicula, self.festival)

    def test_crear_pelicula_sin_login_redirige(self):
        r = self.client.get(reverse('crear_pelicula'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    def test_crear_pelicula_con_login(self):
        self.client.login(username='normal', password='pass1234')
        r = self.client.get(reverse('crear_pelicula'))
        self.assertEqual(r.status_code, 200)

    def test_estadisticas_sin_login_redirige(self):
        r = self.client.get(reverse('estadisticas'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    def test_estadisticas_con_login(self):
        self.client.login(username='normal', password='pass1234')
        r = self.client.get(reverse('estadisticas'))
        self.assertEqual(r.status_code, 200)


class VistasStaffRequeridoTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username='staff', password='pass1234', is_staff=True
        )
        self.pelicula = crear_pelicula()
        self.festival = crear_festival()
        self.proyeccion = crear_proyeccion(self.pelicula, self.festival)

    def test_editar_pelicula_sin_login_redirige(self):
        r = self.client.get(reverse('editar_pelicula', args=[self.pelicula.pk]))
        self.assertEqual(r.status_code, 302)

    def test_editar_pelicula_con_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.client.get(reverse('editar_pelicula', args=[self.pelicula.pk]))
        self.assertEqual(r.status_code, 200)

    def test_eliminar_pelicula_sin_login_redirige(self):
        r = self.client.get(reverse('eliminar_pelicula', args=[self.pelicula.pk]))
        self.assertEqual(r.status_code, 302)

    def test_eliminar_pelicula_con_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.client.get(reverse('eliminar_pelicula', args=[self.pelicula.pk]))
        self.assertEqual(r.status_code, 200)

    def test_crear_festival_sin_login_redirige(self):
        r = self.client.get(reverse('crear_festival'))
        self.assertEqual(r.status_code, 302)

    def test_crear_festival_con_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.client.get(reverse('crear_festival'))
        self.assertEqual(r.status_code, 200)

    def test_editar_festival_sin_login_redirige(self):
        r = self.client.get(reverse('editar_festival', args=[self.festival.pk]))
        self.assertEqual(r.status_code, 302)

    def test_editar_festival_con_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.client.get(reverse('editar_festival', args=[self.festival.pk]))
        self.assertEqual(r.status_code, 200)

    def test_eliminar_festival_sin_login_redirige(self):
        r = self.client.get(reverse('eliminar_festival', args=[self.festival.pk]))
        self.assertEqual(r.status_code, 302)

    def test_eliminar_festival_con_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.client.get(reverse('eliminar_festival', args=[self.festival.pk]))
        self.assertEqual(r.status_code, 200)

    def test_crear_proyeccion_sin_login_redirige(self):
        r = self.client.get(reverse('crear_proyeccion'))
        self.assertEqual(r.status_code, 302)

    def test_crear_proyeccion_con_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.client.get(reverse('crear_proyeccion'))
        self.assertEqual(r.status_code, 200)

    def test_editar_proyeccion_sin_login_redirige(self):
        r = self.client.get(reverse('editar_proyeccion', args=[self.proyeccion.pk]))
        self.assertEqual(r.status_code, 302)

    def test_editar_proyeccion_con_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.client.get(reverse('editar_proyeccion', args=[self.proyeccion.pk]))
        self.assertEqual(r.status_code, 200)

    def test_eliminar_proyeccion_sin_login_redirige(self):
        r = self.client.get(reverse('eliminar_proyeccion', args=[self.proyeccion.pk]))
        self.assertEqual(r.status_code, 302)

    def test_eliminar_proyeccion_con_staff(self):
        self.client.login(username='staff', password='pass1234')
        r = self.client.get(reverse('eliminar_proyeccion', args=[self.proyeccion.pk]))
        self.assertEqual(r.status_code, 200)