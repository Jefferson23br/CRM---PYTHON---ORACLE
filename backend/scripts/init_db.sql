-- ============================================================
-- CRM Piloto - Criação das tabelas no Oracle XEPDB1
-- Execute conectado como crm_user (NAO como SYSTEM)
--
-- Exemplo:
--   sqlplus crm_user/sua_senha@//IP_DA_VPS:1521/XEPDB1
--   @init_db.sql
--
-- Antes disso, execute 01_criar_usuario_crm.sql como SYSTEM
-- ============================================================

-- ============================================================
-- TABELAS
-- ============================================================

CREATE TABLE empresas (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    razao_social    VARCHAR2(200) NOT NULL,
    nome_fantasia   VARCHAR2(200),
    cnpj            VARCHAR2(18) NOT NULL,
    email           VARCHAR2(150),
    telefone        VARCHAR2(20),
    endereco        VARCHAR2(300),
    cidade          VARCHAR2(100),
    estado          VARCHAR2(2),
    cep             VARCHAR2(10),
    status          VARCHAR2(20) DEFAULT 'ativa' NOT NULL,
    criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    atualizado_em   TIMESTAMP,
    CONSTRAINT uk_empresas_cnpj UNIQUE (cnpj),
    CONSTRAINT ck_empresas_status CHECK (status IN ('ativa', 'inativa', 'suspensa'))
);

CREATE TABLE usuarios (
    id                NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    empresa_id        NUMBER,
    nome              VARCHAR2(150) NOT NULL,
    email             VARCHAR2(150) NOT NULL,
    senha_hash        VARCHAR2(255) NOT NULL,
    tipo              VARCHAR2(30) DEFAULT 'vendedor' NOT NULL,
    telefone          VARCHAR2(20),
    cargo             VARCHAR2(100),
    ativo             NUMBER(1) DEFAULT 1 NOT NULL,
    email_verificado  NUMBER(1) DEFAULT 0 NOT NULL,
    ultimo_acesso     TIMESTAMP,
    criado_em         TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    atualizado_em     TIMESTAMP,
    CONSTRAINT uk_usuarios_email UNIQUE (email),
    CONSTRAINT fk_usuarios_empresa FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    CONSTRAINT ck_usuarios_tipo CHECK (tipo IN (
        'super_admin', 'admin_empresa', 'gerente', 'vendedor', 'atendente', 'visualizador'
    )),
    CONSTRAINT ck_usuarios_ativo CHECK (ativo IN (0, 1)),
    CONSTRAINT ck_usuarios_email_verificado CHECK (email_verificado IN (0, 1))
);

CREATE TABLE clientes (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    empresa_id      NUMBER NOT NULL,
    nome            VARCHAR2(200) NOT NULL,
    email           VARCHAR2(150),
    telefone        VARCHAR2(20),
    celular         VARCHAR2(20),
    cpf_cnpj        VARCHAR2(18),
    tipo_pessoa     VARCHAR2(10),
    endereco        VARCHAR2(300),
    cidade          VARCHAR2(100),
    estado          VARCHAR2(2),
    cep             VARCHAR2(10),
    observacoes     CLOB,
    status          VARCHAR2(20) DEFAULT 'prospecto' NOT NULL,
    origem          VARCHAR2(100),
    criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    atualizado_em   TIMESTAMP,
    CONSTRAINT fk_clientes_empresa FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    CONSTRAINT ck_clientes_status CHECK (status IN ('ativo', 'inativo', 'prospecto', 'lead')),
    CONSTRAINT ck_clientes_tipo_pessoa CHECK (tipo_pessoa IN ('PF', 'PJ') OR tipo_pessoa IS NULL)
);

CREATE TABLE topicos_crm (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    empresa_id      NUMBER NOT NULL,
    cliente_id      NUMBER,
    responsavel_id  NUMBER,
    titulo          VARCHAR2(200) NOT NULL,
    descricao       CLOB,
    categoria       VARCHAR2(100),
    status          VARCHAR2(20) DEFAULT 'aberto' NOT NULL,
    prioridade      VARCHAR2(20) DEFAULT 'media' NOT NULL,
    criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    atualizado_em   TIMESTAMP,
    fechado_em      TIMESTAMP,
    CONSTRAINT fk_topicos_empresa FOREIGN KEY (empresa_id) REFERENCES empresas(id),
    CONSTRAINT fk_topicos_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    CONSTRAINT fk_topicos_responsavel FOREIGN KEY (responsavel_id) REFERENCES usuarios(id),
    CONSTRAINT ck_topicos_status CHECK (status IN ('aberto', 'em_andamento', 'resolvido', 'fechado')),
    CONSTRAINT ck_topicos_prioridade CHECK (prioridade IN ('baixa', 'media', 'alta', 'urgente'))
);

CREATE TABLE mensagens (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    topico_id       NUMBER NOT NULL,
    autor_id        NUMBER NOT NULL,
    conteudo        CLOB NOT NULL,
    tipo            VARCHAR2(50) DEFAULT 'texto' NOT NULL,
    criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    atualizado_em   TIMESTAMP,
    CONSTRAINT fk_mensagens_topico FOREIGN KEY (topico_id) REFERENCES topicos_crm(id) ON DELETE CASCADE,
    CONSTRAINT fk_mensagens_autor FOREIGN KEY (autor_id) REFERENCES usuarios(id)
);

CREATE TABLE tokens_recuperacao_senha (
    id              NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    usuario_id      NUMBER NOT NULL,
    token           VARCHAR2(255) NOT NULL,
    expira_em       TIMESTAMP NOT NULL,
    usado           NUMBER(1) DEFAULT 0 NOT NULL,
    criado_em       TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT uk_tokens_token UNIQUE (token),
    CONSTRAINT fk_tokens_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
    CONSTRAINT ck_tokens_usado CHECK (usado IN (0, 1))
);

-- ============================================================
-- ÍNDICES
-- ============================================================

CREATE INDEX idx_usuarios_empresa ON usuarios(empresa_id);
CREATE INDEX idx_clientes_empresa ON clientes(empresa_id);
CREATE INDEX idx_clientes_nome ON clientes(nome);
CREATE INDEX idx_clientes_status ON clientes(status);
CREATE INDEX idx_topicos_empresa ON topicos_crm(empresa_id);
CREATE INDEX idx_topicos_cliente ON topicos_crm(cliente_id);
CREATE INDEX idx_topicos_status ON topicos_crm(status);
CREATE INDEX idx_mensagens_topico ON mensagens(topico_id);
CREATE INDEX idx_tokens_usuario ON tokens_recuperacao_senha(usuario_id);

-- ============================================================
-- COMENTÁRIOS
-- ============================================================

COMMENT ON TABLE empresas IS 'Cadastro de empresas (multi-tenant)';
COMMENT ON TABLE usuarios IS 'Usuários do sistema com tipos e permissões';
COMMENT ON TABLE clientes IS 'Clientes/leads vinculados por empresa';
COMMENT ON TABLE topicos_crm IS 'Tópicos padrão de CRM (atendimentos, negociações)';
COMMENT ON TABLE mensagens IS 'Mensagens e notas dentro dos tópicos';
COMMENT ON TABLE tokens_recuperacao_senha IS 'Tokens para recuperação de senha';

COMMIT;
