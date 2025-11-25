# Sistema de Gestão de Salas - Faculdade Insted

Sistema web desenvolvido em Django para gerenciamento de salas, cursos e ocupação de espaços da Faculdade Insted.

## 🚀 Funcionalidades

- **Gestão de Andares**: Organize salas por andares
- **Gestão de Cursos**: Cadastre cursos com semestre, turma e quantidade de alunos
- **Gestão de Salas**: Controle de lugares disponíveis por sala
- **Sistema de Semestres**: Organize dados por período acadêmico (ex: 2025.1, 2025.2)
- **Filtros Avançados**: 
  - Por semestre acadêmico
  - Por curso
  - Por andar
  - Por disponibilidade de lugares
- **Tema Escuro/Claro**: Interface com suporte a tema escuro
- **Exportação para Excel**: Exporte relatórios filtrados para Excel

## 🛠️ Tecnologias

- **Django 5.2.6**: Framework web Python
- **Tailwind CSS**: Framework CSS para estilização
- **SQLite**: Banco de dados
- **openpyxl**: Geração de arquivos Excel

## 📋 Pré-requisitos

- Python 3.8+
- pip

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/VitorAngelozi/gestao_insted.git
cd gestao_insted
```

2. Instale as dependências:
```bash
pip install django openpyxl
```

3. Execute as migrações:
```bash
python manage.py migrate
```

4. Crie um superusuário (opcional):
```bash
python manage.py createsuperuser
```

5. Execute o servidor:
```bash
python manage.py runserver
```

6. Acesse no navegador:
```
http://127.0.0.1:8000
```

## 📁 Estrutura do Projeto

```
gestao_espacos/
├── gestao_salas/          # Configurações do projeto Django
│   ├── settings.py        # Configurações
│   ├── urls.py           # URLs principais
│   └── templates/        # Templates base
├── sala/                  # App principal
│   ├── models.py         # Modelos (Andar, Curso, Sala, SemestrePeriodo)
│   ├── views.py          # Views (homepage, exportar_excel)
│   ├── admin.py          # Configuração do admin
│   └── templates/        # Templates do app
└── manage.py             # Script de gerenciamento Django
```

## 📊 Modelos

### SemestrePeriodo
- Ano e período (1 ou 2)
- Data de início e fim
- Status ativo

### Andar
- Número do andar
- Nome opcional

### Curso
- Nome
- Semestre do curso (1° a 12°)
- Turma
- Quantidade de alunos
- Semestre período (vinculado)

### Sala
- Nome
- Quantidade de lugares
- Curso vinculado
- Andar

## 🎨 Interface

- Design moderno e minimalista
- Responsivo (mobile-friendly)
- Tema escuro/claro
- Cards organizados por andar
- Indicadores visuais de disponibilidade

## 📤 Exportação

O sistema permite exportar os dados filtrados para Excel com:
- Informações completas das salas
- Formatação condicional (verde/vermelho)
- Cabeçalhos estilizados
- Data e hora da exportação

## 👤 Admin

Acesse `/admin` para gerenciar:
- Semestres Períodos
- Andares
- Cursos
- Salas

## 📝 Licença

Este projeto é de uso interno da Faculdade Insted.

## 👨‍💻 Desenvolvedor

Desenvolvido para a Faculdade Insted

