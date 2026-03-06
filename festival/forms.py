from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pelicula, Festival, Proyeccion


class PeliculaForm(forms.ModelForm):
    class Meta:
        model = Pelicula
        fields = ['titulo', 'director', 'anio', 'duracion_minutos', 'genero', 'sinopsis', 'puntuacion', 'poster_url']
        widgets = {
            'sinopsis': forms.Textarea(attrs={'rows': 4}),
            'titulo': forms.TextInput(attrs={'placeholder': 'Título de la película'}),
            'director': forms.TextInput(attrs={'placeholder': 'Nombre del director/a'}),
        }
        error_messages = {
            'titulo': {
                'required': 'El título es obligatorio. No puedes dejar este campo vacío.',
                'max_length': 'El título es demasiado largo. Máximo 200 caracteres.',
            },
            'director': {
                'required': 'Debes indicar el nombre del director o directora.',
                'max_length': 'El nombre del director es demasiado largo. Máximo 150 caracteres.',
            },
            'anio': {
                'required': 'El año de estreno es obligatorio.',
                'invalid': 'Introduce un año válido (número entero).',
            },
            'duracion_minutos': {
                'required': 'La duración de la película es obligatoria.',
                'invalid': 'La duración debe ser un número entero positivo.',
            },
            'genero': {
                'required': 'Debes seleccionar un género para la película.',
            },
            'sinopsis': {
                'required': 'La sinopsis es obligatoria.',
                'max_length': 'La sinopsis es demasiado larga. Máximo 1000 caracteres.',
            },
            'puntuacion': {
                'invalid': 'Introduce una puntuación válida entre 0 y 10.',
            },
            'poster_url': {
                'invalid': 'Introduce una URL válida para el póster.',
            },
        }

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo', '').strip()
        if len(titulo) < 2:
            raise forms.ValidationError('El título debe tener al menos 2 caracteres.')
        return titulo

    def clean_director(self):
        director = self.cleaned_data.get('director', '').strip()
        if len(director) < 3:
            raise forms.ValidationError('El nombre del director debe tener al menos 3 caracteres.')
        if any(char.isdigit() for char in director):
            raise forms.ValidationError('El nombre del director no puede contener números.')
        return director

    def clean_duracion_minutos(self):
        duracion = self.cleaned_data.get('duracion_minutos')
        if duracion is not None and duracion < 1:
            raise forms.ValidationError('La duración debe ser de al menos 1 minuto.')
        if duracion is not None and duracion > 600:
            raise forms.ValidationError('La duración no puede superar las 10 horas (600 minutos).')
        return duracion


class FestivalForm(forms.ModelForm):
    class Meta:
        model = Festival
        fields = ['nombre', 'ciudad', 'pais', 'fecha_inicio', 'fecha_fin', 'tematica', 'aforo_maximo', 'descripcion', 'activo']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
        error_messages = {
            'nombre': {
                'required': 'El nombre del festival es obligatorio.',
                'max_length': 'El nombre del festival es demasiado largo. Máximo 200 caracteres.',
            },
            'ciudad': {
                'required': 'La ciudad es obligatoria.',
                'max_length': 'El nombre de la ciudad es demasiado largo. Máximo 100 caracteres.',
            },
            'fecha_inicio': {
                'required': 'La fecha de inicio es obligatoria.',
                'invalid': 'Introduce una fecha de inicio válida.',
            },
            'fecha_fin': {
                'required': 'La fecha de fin es obligatoria.',
                'invalid': 'Introduce una fecha de fin válida.',
            },
            'aforo_maximo': {
                'required': 'El aforo máximo es obligatorio.',
                'invalid': 'El aforo debe ser un número entero positivo.',
            },
            'tematica': {
                'required': 'La temática del festival es obligatoria.',
            },
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre', '').strip()
        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre

    def clean_aforo_maximo(self):
        aforo = self.cleaned_data.get('aforo_maximo')
        if aforo is not None and aforo < 10:
            raise forms.ValidationError('El aforo mínimo permitido es de 10 personas.')
        return aforo

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        if fecha_inicio and fecha_fin:
            if fecha_fin < fecha_inicio:
                self.add_error('fecha_fin', 'La fecha de fin no puede ser anterior a la de inicio.')
            elif (fecha_fin - fecha_inicio).days > 30:
                self.add_error('fecha_fin', 'Un festival no puede durar más de 30 días.')
        return cleaned_data


class ProyeccionForm(forms.ModelForm):
    class Meta:
        model = Proyeccion
        fields = ['pelicula', 'festival', 'fecha_hora', 'sala', 'entradas_disponibles', 'precio_entrada', 'es_preestreno']
        widgets = {
            'fecha_hora': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
        error_messages = {
            'pelicula': {
                'required': 'Debes seleccionar una película para la proyección.',
            },
            'festival': {
                'required': 'Debes seleccionar el festival donde se proyectará.',
            },
            'fecha_hora': {
                'required': 'La fecha y hora de la proyección son obligatorias.',
                'invalid': 'Introduce una fecha y hora válidas.',
            },
            'sala': {
                'required': 'Debes seleccionar una sala.',
            },
            'entradas_disponibles': {
                'required': 'El número de entradas disponibles es obligatorio.',
                'invalid': 'Introduce un número entero positivo.',
            },
            'precio_entrada': {
                'invalid': 'Introduce un precio válido.',
            },
        }

    def clean_precio_entrada(self):
        precio = self.cleaned_data.get('precio_entrada')
        if precio is not None and precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        if precio is not None and precio > 500:
            raise forms.ValidationError('El precio de una entrada no puede superar los 500€.')
        return precio

    def clean(self):
        cleaned_data = super().clean()
        festival = cleaned_data.get('festival')
        fecha_hora = cleaned_data.get('fecha_hora')
        entradas = cleaned_data.get('entradas_disponibles')

        if festival and fecha_hora:
            fecha = fecha_hora.date()
            if fecha < festival.fecha_inicio or fecha > festival.fecha_fin:
                self.add_error('fecha_hora', 'La proyección debe realizarse durante el período del festival.')

        if festival and entradas:
            if entradas > festival.aforo_maximo:
                self.add_error(
                    'entradas_disponibles',
                    f'Las entradas ({entradas}) no pueden superar el aforo máximo del festival ({festival.aforo_maximo}).'
                )
        return cleaned_data


class RegistroForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        error_messages={
            'required': 'El email es obligatorio.',
            'invalid': 'Introduce un email válido.',
        }
    )
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label='Nombre',
        error_messages={
            'required': 'El nombre es obligatorio.',
        }
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label='Apellidos',
        error_messages={
            'required': 'Los apellidos son obligatorios.',
        }
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con este email.')
        return email
