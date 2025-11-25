from pathlib import Path

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# 🔐 Chave secreta (local, então não tem problema)
SECRET_KEY = 'django-insecure-1p77607760!=v&nmcw#usw2e%^i7w^yxf^57d%&&xyq4irs-8@'

# 🚧 Debug ligado no ambiente local
DEBUG = True

# Hosts permitidos (local)
ALLOWED_HOSTS = ['*']


# ---------------------------------------
# 🔌 APPS INSTALADOS
# ---------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Seu app
    'sala.apps.SalaConfig',
]


# ---------------------------------------
# 🔐 MIDDLEWARE
# ---------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ---------------------------------------
# 🌐 URLS
# ---------------------------------------

ROOT_URLCONF = 'gestao_salas.urls'


# ---------------------------------------
# 🎨 TEMPLATES
# ---------------------------------------

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'gestao_salas' / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'gestao_salas.wsgi.application'


# ---------------------------------------
# 🗄️ DATABASE (SQLite LOCAL)
# ---------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ---------------------------------------
# 🔒 VALIDAÇÃO DE SENHAS
# ---------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------
# 🌍 CONFIGURAÇÃO DE IDIOMA E TEMPO
# ---------------------------------------

LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True


# ---------------------------------------
# 🧩 ARQUIVOS ESTÁTICOS (CSS / JS)
# ---------------------------------------

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    BASE_DIR / 'gestao_salas' / 'static',  # sua pasta de arquivos estáticos
]

STATIC_ROOT = BASE_DIR / 'staticfiles'  # onde o collectstatic junta (não usado localmente)


# ---------------------------------------
# 🔑 ID PADRÃO
# ---------------------------------------

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
