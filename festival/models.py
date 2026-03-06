from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User


def validar_anio(value):
    if value < 1888 or value > timezone.now().year + 2:
        raise ValidationError(
            f'El año debe estar entre 1888 y {timezone.now().year + 2}. '
            f'Has introducido %(value)s.',
            params={'value': value}
        )


def validar_puntuacion(value):
    if value < 0 or value > 10:
        raise ValidationError(
            'La puntuación debe estar entre 0 y 10. Has introducido %(value)s.',
            params={'value': value}
        )


GENEROS = [
    ('drama', 'Drama'),
    ('comedia', 'Comedia'),
    ('terror', 'Terror'),
    ('ciencia_ficcion', 'Ciencia Ficción'),
    ('documental', 'Documental'),
    ('animacion', 'Animación'),
    ('thriller', 'Thriller'),
    ('romance', 'Romance'),
    ('accion', 'Acción'),
    ('fantasia', 'Fantasía'),
]


class Pelicula(models.Model):
    titulo = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    director = models.CharField(
        max_length=150,
        verbose_name='Director/a'
    )
    anio = models.IntegerField(
        verbose_name='Año de estreno',
        validators=[validar_anio]
    )
    duracion_minutos = models.PositiveIntegerField(
        verbose_name='Duración (minutos)'
    )
    genero = models.CharField(
        max_length=30,
        choices=GENEROS,
        verbose_name='Género'
    )
    sinopsis = models.TextField(
        max_length=1000,
        verbose_name='Sinopsis'
    )
    puntuacion = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='Puntuación (0-10)',
        validators=[validar_puntuacion]
    )
    poster_url = models.URLField(
        blank=True,
        verbose_name='URL del póster'
    )
    creada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='peliculas'
    )

    class Meta:
        verbose_name = 'Película'
        verbose_name_plural = 'Películas'
        ordering = ['-anio', 'titulo']

    def __str__(self):
        return f'{self.titulo} ({self.anio})'

    def clean(self):
        if self.duracion_minutos and self.duracion_minutos < 1:
            raise ValidationError({'duracion_minutos': 'La duración debe ser al menos 1 minuto.'})
        if self.titulo and len(self.titulo.strip()) < 2:
            raise ValidationError({'titulo': 'El título debe tener al menos 2 caracteres.'})


class Festival(models.Model):
    nombre = models.CharField(
        max_length=200,
        verbose_name='Nombre del festival'
    )
    ciudad = models.CharField(
        max_length=100,
        verbose_name='Ciudad'
    )
    pais = models.CharField(
        max_length=100,
        default='España',
        verbose_name='País'
    )
    fecha_inicio = models.DateField(
        verbose_name='Fecha de inicio'
    )
    fecha_fin = models.DateField(
        verbose_name='Fecha de fin'
    )
    tematica = models.CharField(
        max_length=200,
        verbose_name='Temática'
    )
    aforo_maximo = models.PositiveIntegerField(
        verbose_name='Aforo máximo'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    activo = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    creado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='festivales'
    )

    class Meta:
        verbose_name = 'Festival'
        verbose_name_plural = 'Festivales'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.nombre} ({self.ciudad}, {self.fecha_inicio.year})'

    def clean(self):
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_fin < self.fecha_inicio:
                raise ValidationError({
                    'fecha_fin': 'La fecha de fin no puede ser anterior a la fecha de inicio.'
                })
            duracion = (self.fecha_fin - self.fecha_inicio).days
            if duracion > 30:
                raise ValidationError({
                    'fecha_fin': 'Un festival no puede durar más de 30 días.'
                })
        if self.aforo_maximo and self.aforo_maximo < 10:
            raise ValidationError({
                'aforo_maximo': 'El aforo mínimo permitido es de 10 personas.'
            })
        if self.nombre and len(self.nombre.strip()) < 3:
            raise ValidationError({
                'nombre': 'El nombre del festival debe tener al menos 3 caracteres.'
            })

    @property
    def duracion_dias(self):
        return (self.fecha_fin - self.fecha_inicio).days + 1


SALAS = [
    ('sala_principal', 'Sala Principal'),
    ('sala_a', 'Sala A'),
    ('sala_b', 'Sala B'),
    ('sala_c', 'Sala C'),
    ('auditorio', 'Auditorio'),
    ('al_aire_libre', 'Al aire libre'),
]


class Proyeccion(models.Model):
    pelicula = models.ForeignKey(
        Pelicula,
        on_delete=models.CASCADE,
        related_name='proyecciones',
        verbose_name='Película'
    )
    festival = models.ForeignKey(
        Festival,
        on_delete=models.CASCADE,
        related_name='proyecciones',
        verbose_name='Festival'
    )
    fecha_hora = models.DateTimeField(
        verbose_name='Fecha y hora'
    )
    sala = models.CharField(
        max_length=30,
        choices=SALAS,
        verbose_name='Sala'
    )
    entradas_disponibles = models.PositiveIntegerField(
        verbose_name='Entradas disponibles'
    )
    precio_entrada = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.00,
        verbose_name='Precio de entrada (€)'
    )
    es_preestreno = models.BooleanField(
        default=False,
        verbose_name='Es preestreno'
    )

    class Meta:
        verbose_name = 'Proyección'
        verbose_name_plural = 'Proyecciones'
        ordering = ['fecha_hora']
        unique_together = [['festival', 'sala', 'fecha_hora']]

    def __str__(self):
        return f'{self.pelicula.titulo} — {self.festival.nombre} ({self.fecha_hora.strftime("%d/%m/%Y %H:%M")})'

    def clean(self):
        # La proyección debe estar dentro del período del festival
        if self.fecha_hora and self.festival_id:
            fecha = self.fecha_hora.date()
            if fecha < self.festival.fecha_inicio or fecha > self.festival.fecha_fin:
                raise ValidationError({
                    'fecha_hora': 'La proyección debe realizarse durante el período del festival.'
                })
        if self.entradas_disponibles and self.festival_id:
            if self.entradas_disponibles > self.festival.aforo_maximo:
                raise ValidationError({
                    'entradas_disponibles': 'Las entradas disponibles no pueden superar el aforo máximo del festival.'
                })
        if self.precio_entrada is not None and self.precio_entrada < 0:
            raise ValidationError({
                'precio_entrada': 'El precio no puede ser negativo.'
            })
