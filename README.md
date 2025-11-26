# 🏫 Sistema de Gestão de Espaços - Faculdade Insted

Sistema web para gerenciamento de salas e espaços acadêmicos com backup automático.

## 🌐 Servidor de Rede Local

Este sistema está configurado para funcionar em **rede local**, permitindo acesso de qualquer dispositivo na rede.

### 🚀 Iniciar Servidor

```bash
# Opção 1: Script otimizado (RECOMENDADO)
python iniciar_servidor.py

# Opção 2: Script completo
python runserver_com_backup.py

# Opção 3: Django básico (sem backup)
python manage.py runserver 0.0.0.0:8000
```

### 📱 Como Acessar

**No computador servidor:**
- http://localhost:8000

**De outros dispositivos na rede:**
- http://IP_DO_SERVIDOR:8000
- Exemplo: http://192.168.1.100:8000

> O IP será mostrado ao iniciar o servidor

## ✨ Funcionalidades

### 📚 Gestão de Salas
- Visualização por andar
- Filtros por curso, metodologia, disponibilidade
- Informações em tempo real de ocupação

### 🎯 Metodologias de Ensino
- **Metodologia Ativa** - Salas com ensino interativo
- **Metodologia Tradicional** - Salas com ensino convencional

### 📊 Sistema de Filtros
- Semestre/Período
- Curso específico
- Andar do prédio
- Tipo de metodologia
- Disponibilidade de lugares

### 📦 Backup Automático
- Backup do banco SQLite a cada 1 hora
- Rotação automática (mantém 24 backups)
- Logs detalhados em `logs/backup_sqlite.log`
- Backups salvos em `backups_sqlite/`

## 🛠️ Configuração

### Requisitos
- Python 3.8+
- Django 5.2+
- SQLite (incluído no Python)

### Instalação
```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar migrações
python manage.py migrate

# 3. Iniciar servidor
python iniciar_servidor.py
```

## 📋 Comandos de Backup

```bash
# Ver status do backup
python manage.py backup_automatico --status

# Fazer backup manual
python manage.py backup_automatico --backup-now

# Iniciar backup automático
python manage.py backup_automatico --start

# Parar backup automático
python manage.py backup_automatico --stop
```

## 🔧 Administração

### Acessar Admin
- URL: http://localhost:8000/admin/
- Usuário: admin
- Senha: admin123

### Gerenciar Dados
- **Andares:** Definir pisos do prédio
- **Cursos:** Cadastrar cursos e turmas
- **Salas:** Adicionar salas com metodologia
- **Períodos:** Configurar semestres letivos

## 📁 Estrutura de Arquivos

```
gestao_espacos/
├── gestao_salas/           # Configurações Django
├── sala/                   # App principal
│   ├── models.py          # Modelos (Sala, Curso, etc.)
│   ├── views.py           # Lógica de negócio
│   └── templates/         # Templates HTML
├── db.sqlite3             # Banco de dados
├── backups_sqlite/        # Backups automáticos
├── logs/                  # Logs do sistema
├── iniciar_servidor.py    # Script de inicialização
└── runserver_com_backup.py # Servidor com backup
```

## 🌙 Tema Escuro/Claro

O sistema possui **alternância automática** entre tema claro e escuro:
- Botão de alternância no cabeçalho
- Preferência salva automaticamente
- Detecta preferência do sistema

## 🎨 Design

- **Minimalista e moderno**
- **Totalmente responsivo** (funciona em celulares)
- **Cores neutras** com ícone de graduação animado
- **Interface limpa** focada na funcionalidade

## 📊 Dados Incluídos

O sistema já vem com dados de exemplo:
- Andares configurados
- Salas com diferentes metodologias
- Cursos de exemplo
- Períodos letivos

## 🔒 Segurança

- Backup automático para proteção de dados
- Logs detalhados de todas as operações
- Configurações seguras para rede local
- Acesso administrativo protegido

---

## 🆘 Suporte

### Problemas Comuns

**Erro de porta ocupada:**
```bash
python iniciar_servidor.py --port 8080
```

**Backup não funciona:**
```bash
python manage.py backup_automatico --status
```

**Não consegue acessar da rede:**
- Verificar firewall do Windows
- Confirmar que o IP está correto
- Testar com: `python runserver_com_backup.py`

### Logs Importantes
- **Servidor:** Console onde executou o comando
- **Backup:** `logs/backup_sqlite.log`
- **Django:** Logs no console durante execução

---

**🎓 Desenvolvido para a Faculdade Insted**  
*Sistema de Gestão de Espaços Acadêmicos*

Última atualização: Janeiro 2025