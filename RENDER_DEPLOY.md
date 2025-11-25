# Deploy no Render

## Configurações necessárias no Render

### 1. Variáveis de Ambiente

Configure as seguintes variáveis de ambiente no painel do Render:

- `SECRET_KEY`: Chave secreta do Django (gere uma nova para produção)
- `DEBUG`: `False` (para produção)
- `ALLOWED_HOSTS`: Seu domínio do Render (ex: `gestao-insted.onrender.com`)
- `DATABASE_URL`: URL do banco de dados PostgreSQL (Render fornece automaticamente se você criar um banco)

### 2. Build Command

```
./build.sh
```

### 3. Start Command

```
gunicorn gestao_salas.wsgi:application
```

### 4. Dependências adicionais

Adicione `gunicorn` ao requirements.txt se ainda não estiver:

```
gunicorn==21.2.0
```

### 5. Banco de Dados

1. Crie um banco PostgreSQL no Render
2. Copie a Internal Database URL
3. Configure como variável de ambiente `DATABASE_URL`

### 6. Migrações

As migrações serão executadas automaticamente pelo `build.sh`.

### 7. Superusuário

Após o deploy, você precisará criar um superusuário:

1. Acesse o Shell do Render
2. Execute: `python manage.py createsuperuser`

## Checklist de Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados PostgreSQL criado
- [ ] Build command configurado
- [ ] Start command configurado
- [ ] Migrações executadas
- [ ] Superusuário criado
- [ ] Static files coletados (automático via build.sh)

