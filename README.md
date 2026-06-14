# CRM Piloto

**Projeto piloto de CRM (Customer Relationship Management)** desenvolvido para atender empresas que precisam de um controle centralizado de relacionamento com clientes, gestão de leads, atendimentos e funil de vendas.

Este é um sistema **multi-empresa (multi-tenant)**, onde cada empresa possui seus próprios usuários, clientes e dados isolados. O backend é hospedado em **VPS** e o frontend será hospedado em **hospedagem web**, comunicando-se via API REST.

---

## Visão Geral

O CRM Piloto foi concebido como uma solução enxuta e escalável para pequenas e médias empresas que:

- Precisam organizar contatos e clientes em um único lugar
- Querem registrar interações, negociações e atendimentos (tópicos CRM)
- Desejam controlar equipes com diferentes níveis de acesso
- Planejam integrar canais de marketing digital no funil de vendas

### Roadmap de Integrações (planejado)

| Integração | Finalidade |
|------------|------------|
| **Facebook (Meta)** | Captura de leads via formulários e anúncios, rastreamento de origem |
| **Google Ads** | Conversões, campanhas e atribuição de leads ao funil |
| **Funil de vendas** | Etapas configuráveis: lead → prospecto → negociação → fechamento |

> As integrações com Meta e Google Ads serão implementadas em fases futuras, consumindo as APIs oficiais e vinculando a origem dos clientes ao campo `origem` no cadastro.

---

## Arquitetura

```
┌─────────────────────┐         HTTPS/API          ┌─────────────────────┐
│   Frontend (Vue.js) │  ◄────────────────────────► │  Backend (FastAPI)  │
│   Hospedagem Web    │         JWT + CORS           │       VPS           │
└─────────────────────┘                              └──────────┬──────────┘
                                                                │
                                                                │ oracledb
                                                                ▼
                                                     ┌─────────────────────┐
                                                     │   Oracle Database   │
                                                     │   (Multi-tenant)    │
                                                     └─────────────────────┘
```

### Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy |
| **Banco de dados** | Oracle Database |
| **Autenticação** | JWT (access + refresh tokens) |
| **Frontend** *(futuro)* | Vue.js 3 + Vite |
| **Hospedagem Backend** | VPS (Linux) |
| **Hospedagem Frontend** | Hospedagem web (ex.: estático/CDN) |
| **E-mail** | SMTP do seu domínio (recuperação de senha) |

---

## Estrutura do Projeto

```
CRM - PYTHON - ORACLE/
├── backend/
│   ├── app/
│   │   ├── main.py              # Aplicação FastAPI
│   │   ├── config.py            # Configurações (.env)
│   │   ├── database.py          # Conexão Oracle + SQLAlchemy
│   │   ├── models/              # Modelos do banco (ORM)
│   │   ├── schemas/             # Validação Pydantic (request/response)
│   │   ├── routers/             # Rotas da API REST
│   │   ├── services/            # Serviços (e-mail, etc.)
│   │   └── utils/               # Segurança, dependências
│   ├── scripts/
│   │   ├── init_db.sql          # Script SQL Oracle
│   │   └── criar_tabelas.py     # Criação via SQLAlchemy (dev)
│   ├── requirements.txt
│   └── .env.example
├── frontend/                    # Vue.js 3 + Vite
│   ├── src/
│   │   ├── views/               # Telas (auth, clientes, tópicos...)
│   │   ├── components/          # Layout e componentes
│   │   ├── stores/              # Pinia (autenticação)
│   │   ├── services/            # Cliente HTTP (axios)
│   │   └── router/              # Rotas Vue Router
│   ├── package.json
│   └── .env.example
└── README.md
```

---

## Multi-Empresa (Multi-Tenant)

Cada **empresa** é um tenant isolado. Todos os dados de clientes, tópicos e mensagens são vinculados ao `empresa_id`. Usuários só acessam dados da própria empresa, exceto o `super_admin` que gerencia todas.

### Tipos de Usuário

| Tipo | Descrição | Permissões |
|------|-----------|------------|
| `super_admin` | Administrador do sistema | Gerencia todas as empresas |
| `admin_empresa` | Administrador da empresa | CRUD completo na própria empresa |
| `gerente` | Gerente de equipe | Gerencia usuários, clientes e tópicos |
| `vendedor` | Vendedor | Clientes e tópicos (criar/editar) |
| `atendente` | Atendimento | Tópicos e mensagens |
| `visualizador` | Somente leitura | Consulta dados |

---

## Módulos e Funcionalidades

### Autenticação (`/api/v1/auth`)

| Método | Rota | Descrição |
|--------|------|-----------|
| `POST` | `/registro` | Registro de nova empresa + admin |
| `POST` | `/login` | Login com e-mail e senha |
| `GET` | `/me` | Dados do usuário autenticado |
| `POST` | `/recuperar-senha` | Solicita recuperação por e-mail |
| `POST` | `/redefinir-senha` | Redefine senha com token |

### Empresas (`/api/v1/empresas`)

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Listar empresas (super_admin) |
| `GET` | `/{id}` | Obter empresa |
| `POST` | `/` | Criar empresa (super_admin) |
| `PUT` | `/{id}` | Atualizar empresa |
| `DELETE` | `/{id}` | Excluir empresa (super_admin) |

### Usuários (`/api/v1/usuarios`)

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Listar usuários da empresa |
| `GET` | `/{id}` | Obter usuário |
| `POST` | `/` | Criar usuário |
| `PUT` | `/{id}` | Atualizar usuário |
| `DELETE` | `/{id}` | Excluir usuário |

### Clientes (`/api/v1/clientes`)

Cadastro completo com: nome, e-mail, telefone, celular, CPF/CNPJ, endereço, status (lead/prospecto/ativo), origem (facebook, google_ads, etc.) e observações.

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Listar clientes (com busca e paginação) |
| `GET` | `/{id}` | Obter cliente |
| `POST` | `/` | Criar cliente |
| `PUT` | `/{id}` | Atualizar cliente |
| `DELETE` | `/{id}` | Excluir cliente |

### Tópicos CRM (`/api/v1/topicos`)

Tópicos padrão de CRM para atendimentos, negociações e acompanhamentos.

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Listar tópicos (filtro por status/cliente) |
| `GET` | `/{id}` | Obter tópico |
| `POST` | `/` | Criar tópico |
| `PUT` | `/{id}` | Atualizar tópico |
| `DELETE` | `/{id}` | Excluir tópico |

**Status:** `aberto`, `em_andamento`, `resolvido`, `fechado`  
**Prioridade:** `baixa`, `media`, `alta`, `urgente`

### Mensagens (`/api/v1/topicos/{topico_id}/mensagens`)

Mensagens, notas e registros dentro de cada tópico.

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Listar mensagens do tópico |
| `POST` | `/` | Criar mensagem |
| `PUT` | `/{id}` | Editar mensagem (autor) |
| `DELETE` | `/{id}` | Excluir mensagem (autor) |

---

## Banco de Dados Oracle

### Tabelas

| Tabela | Descrição |
|--------|-----------|
| `empresas` | Cadastro multi-empresa |
| `usuarios` | Usuários com tipos e permissões |
| `clientes` | Clientes/leads por empresa |
| `topicos_crm` | Tópicos de atendimento e vendas |
| `mensagens` | Mensagens dentro dos tópicos |
| `tokens_recuperacao_senha` | Tokens de recuperação de senha |

### Criar o banco

**Opção 1 — Script SQL (produção):**

```bash
sqlplus crm_user/senha@ORCL @backend/scripts/init_db.sql
```

**Opção 2 — SQLAlchemy (desenvolvimento):**

```bash
cd backend
python -m scripts.criar_tabelas
```

---

## Instalação e Execução Local

### Pré-requisitos

- Python 3.11 ou superior
- Oracle Database (local ou remoto)
- Oracle Instant Client (necessário para `oracledb`)

### Passo a passo

```bash
# 1. Clonar/acessar o projeto
cd "CRM - PYTHON - ORACLE/backend"

# 2. Criar ambiente virtual
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar variáveis de ambiente
copy .env.example .env   # Windows
# cp .env.example .env   # Linux

# Edite o .env com suas credenciais Oracle e SMTP

# 5. Criar tabelas
python -m scripts.criar_tabelas

# 6. Iniciar o servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

A documentação interativa estará em: **http://localhost:8000/docs**

### Frontend (Vue.js)

```bash
cd frontend
npm install
copy .env.example .env   # Windows — configure VITE_API_URL
npm run dev
```

Painel em: **http://localhost:5173**

---

## Deploy em Produção

### Backend (VPS)

1. Instale Python 3.11+, Oracle Instant Client e dependências do sistema
2. Clone o repositório na VPS
3. Configure o `.env` com credenciais de produção
4. Execute o script SQL `init_db.sql` no Oracle
5. Use um process manager (systemd, supervisor ou PM2) com Gunicorn/Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

6. Configure **Nginx** como reverse proxy com HTTPS (Let's Encrypt)
7. Libere a porta 8000 apenas internamente; exponha 443 via Nginx

**Exemplo de bloco Nginx:**

```nginx
server {
    listen 443 ssl;
    server_name api.seudominio.com.br;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Frontend (hospedagem web)

1. Acesse a pasta `frontend/`
2. Configure a URL da API no `.env`: `VITE_API_URL=https://api.seudominio.com.br/api/v1`
3. Faça build: `npm run build`
4. Publique a pasta `dist/` no painel da sua hospedagem
5. Adicione a URL do site em `CORS_ORIGINS` no `.env` do backend

### Variáveis de ambiente importantes

| Variável | Descrição |
|----------|-----------|
| `SECRET_KEY` | Chave JWT (mín. 32 caracteres, única em produção) |
| `ORACLE_*` | Credenciais do banco Oracle |
| `CORS_ORIGINS` | URLs do frontend na hospedagem web |
| `SMTP_*` | E-mail para recuperação de senha |
| `FRONTEND_URL` | URL base do frontend (links no e-mail) |

---

## Segurança

- Senhas armazenadas com **bcrypt**
- Autenticação via **JWT** (access token + refresh token)
- Isolamento de dados por **empresa_id** (multi-tenant)
- Controle de permissões por **tipo de usuário**
- Tokens de recuperação de senha com **expiração de 2 horas**
- CORS configurável para domínios do frontend
- HTTPS obrigatório em produção

---

## Exemplo de Fluxo — Registro e Uso

### 1. Registrar empresa e administrador

```http
POST /api/v1/auth/registro
Content-Type: application/json

{
  "empresa": {
    "razao_social": "Minha Empresa LTDA",
    "nome_fantasia": "Minha Empresa",
    "cnpj": "12.345.678/0001-90",
    "email": "contato@minhaempresa.com.br"
  },
  "usuario": {
    "nome": "João Admin",
    "email": "joao@minhaempresa.com.br",
    "senha": "SenhaSegura123!",
    "telefone": "11999999999"
  }
}
```

### 2. Criar cliente (com origem Facebook)

```http
POST /api/v1/clientes
Authorization: Bearer {access_token}

{
  "nome": "Maria Silva",
  "email": "maria@email.com",
  "telefone": "11988887777",
  "status": "lead",
  "origem": "facebook"
}
```

### 3. Abrir tópico de negociação

```http
POST /api/v1/topicos
Authorization: Bearer {access_token}

{
  "titulo": "Proposta comercial - Maria Silva",
  "descricao": "Cliente interessado no plano premium",
  "cliente_id": 1,
  "categoria": "vendas",
  "prioridade": "alta"
}
```

---

## Próximos Passos

- [x] Frontend Vue.js com painel administrativo
- [ ] Dashboard com métricas de funil de vendas
- [ ] Integração Facebook (Meta) Lead Ads API
- [ ] Integração Google Ads Conversion API
- [ ] Etapas configuráveis do funil de vendas
- [ ] Notificações em tempo real (WebSocket)
- [ ] Relatórios e exportação (PDF/Excel)
- [ ] API de webhooks para integrações externas

---

## Licença

Projeto piloto — uso interno e comercial conforme definido pelo proprietário.

---

## Contato e Suporte

Para dúvidas sobre implantação, integrações ou customizações, entre em contato com o responsável pelo projeto.
