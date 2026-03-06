# FilmFest — Plataforma de Gestión de Festivales de Cine

## 1. Descripción del Proyecto

FilmFest es una aplicación web desarrollada con Django que permite gestionar festivales de cine, las películas que participan en ellos y las proyecciones programadas. Incluye registro y autenticación de usuarios, gestión de contenido con control de permisos por roles, estadísticas con gráficos y un diseño oscuro responsive con Bootstrap 5.

---
## 2. Estructura del Proyecto

```
filmfest/
├── filmfest/                  # Configuración principal
│   ├── settings.py
│   └── urls.py
├── festival/                  # Aplicación principal
│   ├── models.py              # Modelos: Pelicula, Festival, Proyeccion
│   ├── forms.py               # Formularios con validaciones
│   ├── views.py               # 15 vistas
│   ├── urls.py                # Rutas de la app
│   ├── auth_views.py          # Vista de registro
│   └── tests.py               # Tests de modelos, forms y vistas
├── templates/
│   ├── base.html
│   ├── festival/              # Templates de cada modelo
│   └── registration/          # Login, registro, logout
├── cargar_peliculas.py
└── cargar_festivales_proyecciones.py
```


## 3. Instalación y Puesta en Marcha

### Requisitos previos
- Python 3.10 o superior
- pip (gestor de paquetes de Python)

### Pasos

**1. Crear y activar el entorno virtual:**
```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux / macOS
```

**2. Instalar Django:**
```bash
pip install django
```

**3. Crear las tablas en la base de datos:**
```bash
python manage.py makemigrations festival
python manage.py migrate
```

**4. Crear un superusuario (perfil staff/admin):**
```bash
python manage.py createsuperuser
```

**5. Cargar datos de ejemplo (opcional pero recomendado):**
```bash
python cargar_peliculas.py
python cargar_festivales_proyecciones.py
```

**6. Arrancar el servidor de desarrollo:**
```bash
python manage.py runserver
```

La aplicación estará disponible en: **http://127.0.0.1:8000/**
---

**Proyecto 2º Trimestre Servidor· DAW2 · Django + Python**
