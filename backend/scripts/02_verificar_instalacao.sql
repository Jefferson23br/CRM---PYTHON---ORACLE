-- ============================================================
-- CRM Piloto - Verificar instalação
-- Execute conectado como crm_user no XEPDB1
-- ============================================================

SELECT table_name
FROM user_tables
ORDER BY table_name;

SELECT index_name, table_name
FROM user_indexes
WHERE table_name IN (
    'EMPRESAS', 'USUARIOS', 'CLIENTES',
    'TOPICOS_CRM', 'MENSAGENS', 'TOKENS_RECUPERACAO_SENHA'
)
ORDER BY table_name, index_name;

PROMPT Se aparecerem 6 tabelas, a instalacao esta correta.
