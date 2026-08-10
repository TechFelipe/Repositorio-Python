# Painel de Controle de Tarefas — Flask

Projeto baseado na atividade do livro, com:

- Flask e templates Jinja2
- SQLite
- Cadastro, login e logout
- Hash de senha com Werkzeug
- CRUD de tarefas
- Dashboard
- Filtro de tarefas por status via JSON + fetch()
- Cards coloridos por status
- Modo escuro com localStorage
- Bootstrap 5 e Bootstrap Icons
- Frase motivacional pela Advice Slip API
- Gráfico de progresso com Chart.js
- API REST para tarefas

## 1. Criar ambiente virtual

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Instalar dependências

```bash
pip install -r requirements.txt
```

## 3. Configurar SECRET_KEY

Copie `.env.example` para `.env` e coloque uma chave forte.

Para executar de forma simples no Windows PowerShell:

```powershell
$env:SECRET_KEY="uma-chave-secreta-forte"
```

Linux/macOS:

```bash
export SECRET_KEY="uma-chave-secreta-forte"
```

## 4. Executar

```bash
python app.py
```

Abra no navegador:

```text
http://127.0.0.1:5000
```

O banco `tarefas.db` é criado automaticamente na primeira execução.

## Rotas principais

- `/login` — login
- `/registro` — cadastro
- `/logout` — logout
- `/dashboard` — painel e progresso
- `/nova_tarefa` — criação
- `/editar/<id>` — edição
- `/excluir/<id>` — remoção
- `/api/tarefas` — lista JSON / criação POST
- `/api/tarefas/<id>` — PUT / DELETE
- `/api/progresso` — dados do gráfico

## Observação

A atividade menciona `/dashboard` tanto para a lista de tarefas quanto para o dashboard de progresso. Neste projeto, os dois requisitos foram integrados na mesma página `/dashboard`.
