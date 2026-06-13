-- ============================================================
-- CRM Piloto - Criar usuário/schema no Oracle XEPDB1
-- Execute conectado como SYSTEM no PDB XEPDB1
--
-- Exemplo de conexão na VPS:
--   sqlplus system/sua_senha@//IP_DA_VPS:1521/XEPDB1
-- ============================================================

-- Troque a senha abaixo antes de executar!
-- Use aspas duplas se a senha tiver caracteres especiais.

CREATE USER crm_user IDENTIFIED BY "uma senha segura"
  DEFAULT TABLESPACE USERS
  TEMPORARY TABLESPACE TEMP
  QUOTA UNLIMITED ON USERS;

GRANT CONNECT, RESOURCE TO crm_user;
GRANT CREATE VIEW TO crm_user;
GRANT CREATE SEQUENCE TO crm_user;

-- Permissões extras (opcional, recomendado)
GRANT CREATE SESSION TO crm_user;
GRANT CREATE TABLE TO crm_user;
GRANT CREATE PROCEDURE TO crm_user;
GRANT CREATE TRIGGER TO crm_user;

COMMIT;

PROMPT Usuario crm_user criado com sucesso no seu banco de dados..
PROMPT Proximo passo: conectar como crm_user e executar init_db.sql
