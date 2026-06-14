# CRM Piloto

**Projeto piloto de CRM (Customer Relationship Management)** desenvolvido para atender empresas que precisam de um controle centralizado de relacionamento com clientes, gestão de leads, atendimentos e funil de vendas.

Este é um sistema **multi-empresa (multi-tenant)**, onde cada empresa possui seus próprios usuários, clientes e dados isolados. O **backend** roda em **VPS** (Python/FastAPI) e o **frontend** em **hospedagem web estática** (Vue.js), comunicando-se via API REST com HTTPS.

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
                                                     │   XEPDB1 (PDB)      │
                                                     └─────────────────────┘
```

### Stack Tecnológica

| Camada | Tecnologia |
|--------|------------|
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, Uvicorn |
| **Banco de dados** | Oracle Database (XEPDB1) |
| **Autenticação** | JWT (access + refresh tokens) |
| **Frontend** | Vue.js 3, Vite, Pinia, Vue Router, Axios |
| **Hospedagem Backend** | VPS Linux + Nginx + Certbot (HTTPS) |
| **Hospedagem Frontend** | Hospedagem estática (ex.: Hostinger) |
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
│   │   ├── 01_criar_usuario_crm.sql   # Criar schema Oracle (SYSTEM)
│   │   ├── init_db.sql                # Criar tabelas (crm_user)
│   │   ├── 02_verificar_instalacao.sql
│   │   └── criar_tabelas.py           # Alternativa via SQLAlchemy (dev)
│   ├── deploy/
│   │   └── nginx-crm-api.conf   # Template Nginx (configurar na VPS)
│   ├── ecosystem.config.js      # Template PM2 (opcional)
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── public/
│   │   └── .htaccess            # Fallback SPA para Apache
│   ├── src/
│   │   ├── views/               # Telas do painel
│   │   ├── components/layout/   # Sidebar e layout
│   │   ├── stores/              # Pinia (autenticação)
│   │   ├── services/            # Cliente HTTP (axios)
│   │   └── router/              # Rotas Vue Router (hash mode)
│   ├── package.json
│   └── .env.example
└── README.md
```

---

## Frontend — Telas do Painel

| Tela | Rota | Funcionalidade |
|------|------|----------------|
| Login | `/#/login` | Autenticação |
| Registro | `/#/registro` | Criar empresa + administrador |
| Recuperar senha | `/#/recuperar-senha` | Solicitar e-mail de recuperação |
| Dashboard | `/#/` | Resumo (clientes, tópicos, usuários) |
| Clientes | `/#/clientes` | CRUD de leads e clientes |
| Usuários | `/#/usuarios` | Gerenciar equipe |
| Tópicos CRM | `/#/topicos` | Atendimentos e negociações |
| Detalhe do tópico | `/#/topicos/:id` | Mensagens e status |
| Empresa | `/#/empresa` | Dados da organização |

> O frontend usa **hash router** (`/#/rota`) para funcionar em hospedagem estática sem configuração extra de servidor.

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

## API — Módulos e Rotas

Documentação interativa: `https://api.seudominio.com.br/docs`

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
| `PUT` | `/{id}` | Atualizar empresa |

### Usuários (`/api/v1/usuarios`)

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Listar usuários da empresa |
| `POST` | `/` | Criar usuário |
| `PUT` | `/{id}` | Atualizar usuário |
| `DELETE` | `/{id}` | Excluir usuário |

### Clientes (`/api/v1/clientes`)

Cadastro com: nome, e-mail, telefone, status (lead/prospecto/ativo), origem (facebook, google_ads, etc.) e observações.

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Listar clientes (busca + paginação) |
| `POST` | `/` | Criar cliente |
| `PUT` | `/{id}` | Atualizar cliente |
| `DELETE` | `/{id}` | Excluir cliente |

### Tópicos CRM (`/api/v1/topicos`)

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Listar tópicos |
| `POST` | `/` | Criar tópico |
| `PUT` | `/{id}` | Atualizar tópico |
| `DELETE` | `/{id}` | Excluir tópico |

**Status:** `aberto`, `em_andamento`, `resolvido`, `fechado`  
**Prioridade:** `baixa`, `media`, `alta`, `urgente`

### Mensagens (`/api/v1/topicos/{topico_id}/mensagens`)

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/` | Listar mensagens |
| `POST` | `/` | Criar mensagem |
| `PUT` | `/{id}` | Editar mensagem |
| `DELETE` | `/{id}` | Excluir mensagem |

### Health checks

| Rota | Descrição |
|------|-----------|
| `GET /health` | API online |
| `GET /health/db` | Conexão com Oracle |

---

## Banco de Dados Oracle (XEPDB1)

### Tabelas

| Tabela | Descrição |
|--------|-----------|
| `empresas` | Cadastro multi-empresa |
| `usuarios` | Usuários com tipos e permissões |
| `clientes` | Clientes/leads por empresa |
| `topicos_crm` | Tópicos de atendimento e vendas |
| `mensagens` | Mensagens dentro dos tópicos |
| `tokens_recuperacao_senha` | Tokens de recuperação de senha |

### Criar o banco (produção)

**1. Como SYSTEM no XEPDB1** — criar usuário:

```bash
sqlplus system/senha@//IP_DA_VPS:1521/XEPDB1 @backend/scripts/01_criar_usuario_crm.sql
```

**2. Como crm_user no XEPDB1** — criar tabelas:

```bash
sqlplus crm_user/senha@//IP_DA_VPS:1521/XEPDB1 @backend/scripts/init_db.sql
```

**3. Verificar:**

```bash
sqlplus crm_user/senha@//IP_DA_VPS:1521/XEPDB1 @backend/scripts/02_verificar_instalacao.sql
```

> Também é possível usar o **DBeaver**: conecte como SYSTEM, crie o usuário, depois conecte como `crm_user` e execute `init_db.sql`.

---

## Instalação Local

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux
source venv/bin/activate

pip install -r requirements.txt
copy .env.example .env    # Windows
# cp .env.example .env    # Linux

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API: http://localhost:8000
- Docs: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
copy .env.example .env    # Configure VITE_API_URL
npm run dev
```

- Painel: http://localhost:5173

**`.env` do frontend:**

```env
VITE_API_URL=http://localhost:8000/api/v1
```

---

## Deploy em Produção

### Visão geral do deploy

```
[Usuário] → https://seu-site.com (Hostinger / estático)
                ↓ API calls
            https://api.seudominio.com.br (VPS + Nginx + Uvicorn)
                ↓
            Oracle XEPDB1 (mesma VPS ou remoto)
```

### Backend (VPS)

1. Envie os arquivos via **SCP** ou Git para a VPS
2. Crie o `.env` **somente na VPS** (nunca no GitHub)
3. Instale dependências e configure **systemd**

```bash
cd /caminho/para/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nano .env
```

**Serviço systemd** (`/etc/systemd/system/crm-api.service`):

```ini
[Unit]
Description=CRM API Python
After=network.target

[Service]
WorkingDirectory=/caminho/para/backend
EnvironmentFile=/caminho/para/backend/.env
ExecStart=/caminho/para/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable crm-api
systemctl start crm-api
```

4. Configure **Nginx** como reverse proxy (template em `backend/deploy/nginx-crm-api.conf`)
5. Ative **HTTPS** com Certbot:

```bash
certbot --nginx -d api.seudominio.com.br
```

### Frontend (hospedagem estática)

1. Configure o `.env` do frontend:

```env
VITE_API_URL=https://api.seudominio.com.br/api/v1
```

2. Gere o build:

```bash
cd frontend
npm install
npm run build
```

3. Publique **todo o conteúdo** de `frontend/dist/` na hospedagem:

```
dist/
├── .htaccess       ← necessário para Apache
├── index.html
├── favicon.svg
└── assets/
```

4. Acesse pelo domínio raiz: `https://seu-site.com/`

### CORS — obrigatório no backend

No `.env` da VPS, adicione a URL exata do frontend:

```env
CORS_ORIGINS=https://seu-site.com,http://localhost:5173
CORS_ORIGIN_REGEX=https://.*\.hostingersite\.com
FRONTEND_URL=https://seu-site.com
```

```bash
systemctl restart crm-api
```

> `CORS_ORIGIN_REGEX` é útil para subdomínios temporários de hospedagem estática.

---

## Variáveis de Ambiente

### Backend (`.env` — somente na VPS)

| Variável | Descrição |
|----------|-----------|
| `SECRET_KEY` | Chave JWT (mín. 32 caracteres, única em produção) |
| `ORACLE_USER` | Usuário Oracle (`crm_user`) |
| `ORACLE_PASSWORD` | Senha do Oracle |
| `ORACLE_HOST` | `localhost` se Oracle está na mesma VPS |
| `ORACLE_SERVICE` | `XEPDB1` |
| `CORS_ORIGINS` | URLs do frontend (separadas por vírgula) |
| `CORS_ORIGIN_REGEX` | Regex opcional para subdomínios |
| `FRONTEND_URL` | URL do frontend (links de e-mail) |
| `SMTP_*` | Configuração de e-mail |

### Frontend (`.env` — build local)

| Variável | Descrição |
|----------|-----------|
| `VITE_API_URL` | URL completa da API com `/api/v1` |

---

## Segurança e Boas Práticas

- **Nunca** commite arquivos `.env` (já estão no `.gitignore`)
- Senhas armazenadas com **bcrypt**
- Autenticação via **JWT**
- Isolamento de dados por **empresa_id** (multi-tenant)
- **HTTPS** obrigatório em produção
- Use placeholders genéricos no repositório público
- Configure configs reais (Nginx, domínios) **apenas na VPS/hospedagem**

---

## Solução de Problemas

### Erro CORS no navegador

```
blocked by CORS policy: No 'Access-Control-Allow-Origin'
```

→ Adicione a URL do frontend em `CORS_ORIGINS` no `.env` do backend e reinicie:

```bash
systemctl restart crm-api
```

### Login salva mas não navega / Sair não funciona

→ Atualize o frontend para a versão com autenticação reativa (Pinia) e faça novo `npm run build`.

### 404 em rotas do frontend (`/login`)

→ Use hash router (`/#/login`) e publique o `.htaccess` junto com o `dist/`.

### ORA-02290 check constraint violated (status ATIVA)

→ Enums Oracle devem usar valores em minúsculo (`ativa`, não `ATIVA`). Já corrigido nos modelos.

---

## Status do Projeto

- [x] Backend Python/FastAPI
- [x] Oracle XEPDB1 + tabelas multi-tenant
- [x] API REST completa (auth, clientes, usuários, tópicos, mensagens)
- [x] Deploy VPS + Nginx + HTTPS
- [x] Frontend Vue.js com painel administrativo
- [x] Autenticação JWT integrada
- [x] CORS configurável
- [ ] Dashboard com métricas de funil de vendas
- [ ] Integração Facebook (Meta) Lead Ads API
- [ ] Integração Google Ads Conversion API
- [ ] Etapas configuráveis do funil de vendas
- [ ] Notificações em tempo real (WebSocket)
- [ ] Relatórios e exportação (PDF/Excel)

---

## Licença

Projeto piloto — uso interno e comercial conforme definido pelo proprietário.

---

## Contato

Para dúvidas sobre implantação, integrações ou customizações, entre em contato com o responsável pelo projeto.
