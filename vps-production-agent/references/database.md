# Banco de Dados

## Quando usar
Migrations, queries diretas, backup de banco, alteração de schema, restauração, limpeza de dados.

---

## ⚠️ Regra de Ouro
**Nunca execute nenhuma operação de escrita no banco sem backup recente.**
Queries de leitura (SELECT) são seguras. Tudo que modifica dados (INSERT, UPDATE, DELETE, DROP, ALTER) exige backup primeiro.

---

## Backup de Banco (SEMPRE antes de migrations ou alterações)

### PostgreSQL
```bash
# Backup completo
pg_dump -U usuario -h localhost nome_do_banco > /backups/db_$(date +%Y%m%d_%H%M%S).sql

# Comprimido (economiza espaço)
pg_dump -U usuario nome_do_banco | gzip > /backups/db_$(date +%Y%m%d_%H%M%S).sql.gz

# Verificar se o backup foi gerado
ls -lh /backups/db_*.sql* | tail -3
```

### MySQL / MariaDB
```bash
mysqldump -u usuario -p nome_do_banco > /backups/db_$(date +%Y%m%d_%H%M%S).sql

# Comprimido
mysqldump -u usuario -p nome_do_banco | gzip > /backups/db_$(date +%Y%m%d_%H%M%S).sql.gz
```

### SQLite
```bash
cp /caminho/do/banco.db /backups/banco_$(date +%Y%m%d_%H%M%S).db
```

---

## Migrations

### Protocolo
1. Fazer backup do banco (acima)
2. Executar migration em modo dry-run/check se disponível
3. Aplicar migration
4. Validar resultado
5. Reiniciar serviço se necessário

```bash
# Prisma
npx prisma migrate deploy

# Django
python manage.py showmigrations   # ver pendentes
python manage.py migrate --check   # checar sem aplicar
python manage.py migrate           # aplicar

# Laravel
php artisan migrate:status
php artisan migrate --force

# Verificar resultado (sempre)
# Conectar ao banco e verificar estrutura da tabela alterada
```

---

## Queries Diretas (Cuidado)

```bash
# PostgreSQL — sempre com transação para alterações
psql -U usuario -d nome_do_banco

# DENTRO DO PSQL:
BEGIN;
-- sua query aqui
-- verificar resultado antes de confirmar
SELECT * FROM tabela WHERE ... LIMIT 10;
COMMIT;    -- confirmar
-- ou ROLLBACK; para desfazer
```

⚠️ Para queries destrutivas (DELETE sem WHERE, DROP TABLE, TRUNCATE), mostrar o plano ao usuário e aguardar confirmação explícita.

---

## Restore de Backup

### PostgreSQL
```bash
# Dropar e recriar o banco (cuidado!)
psql -U postgres -c "DROP DATABASE IF EXISTS nome_do_banco;"
psql -U postgres -c "CREATE DATABASE nome_do_banco;"
psql -U usuario -d nome_do_banco < /backups/db_TIMESTAMP.sql
```

### MySQL
```bash
mysql -u usuario -p nome_do_banco < /backups/db_TIMESTAMP.sql
```

---

## Verificações Úteis

```bash
# Ver tamanho do banco
# PostgreSQL
psql -U usuario -c "SELECT pg_size_pretty(pg_database_size('nome_do_banco'));"

# Ver tabelas e tamanhos
psql -U usuario -d nome_do_banco -c "\\dt+"

# Conexões ativas
psql -U usuario -c "SELECT count(*) FROM pg_stat_activity;"
```