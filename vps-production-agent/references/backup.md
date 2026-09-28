# Backup e Restore

## Quando usar
Backup manual antes de operações de risco, restore de versão anterior, recuperação de desastre.

---

## Estrutura de Backup Recomendada

```
/backups/
├── YYYYMMDD_HHMMSS_nome-do-projeto/
│   ├── codigo/          # cópia do projeto
│   ├── .env.backup      # variáveis de ambiente
│   ├── db_TIMESTAMP.sql # dump do banco
│   └── commit_anterior.txt  # hash do commit
└── cron/               # backups automáticos
```

---

## Backup Completo de Projeto

```bash
PROJECT="nome-do-projeto"
PROJECT_PATH="/var/www/$PROJECT"
BACKUP_BASE="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_BASE/${TIMESTAMP}_${PROJECT}"

mkdir -p $BACKUP_DIR

# Código
cp -r $PROJECT_PATH $BACKUP_DIR/codigo
echo "✅ Código copiado"

# .env
cp $PROJECT_PATH/.env $BACKUP_DIR/.env.backup 2>/dev/null || echo "⚠️ .env não encontrado"

# Commit atual
cd $PROJECT_PATH && git rev-parse HEAD > $BACKUP_DIR/commit_anterior.txt 2>/dev/null
echo "✅ Commit registrado: $(cat $BACKUP_DIR/commit_anterior.txt)"

# Banco de dados (editar conforme o banco usado)
# PostgreSQL:
# pg_dump -U usuario nome_do_banco > $BACKUP_DIR/banco.sql
# MySQL:
# mysqldump -u usuario -p nome_do_banco > $BACKUP_DIR/banco.sql

echo ""
echo "📦 Backup completo em: $BACKUP_DIR"
echo "📁 Tamanho: $(du -sh $BACKUP_DIR | cut -f1)"
ls -la $BACKUP_DIR
```

---

## Restore Completo

```bash
# Listar backups disponíveis
ls -lt /backups/ | head -20

# Escolher o backup correto
BACKUP_DIR="/backups/TIMESTAMP_nome-do-projeto"
PROJECT_PATH="/var/www/nome-do-projeto"

# Parar o serviço antes de restaurar
pm2 stop nome-do-app || docker stop nome || systemctl stop nome

# Restaurar código
rm -rf $PROJECT_PATH
cp -r $BACKUP_DIR/codigo $PROJECT_PATH

# Restaurar .env
cp $BACKUP_DIR/.env.backup $PROJECT_PATH/.env

# Restaurar banco (se tiver backup)
# PostgreSQL:
# psql -U usuario nome_do_banco < $BACKUP_DIR/banco.sql

# Reinstalar dependências (por segurança)
cd $PROJECT_PATH
npm ci --production    # ou pip install -r requirements.txt

# Reiniciar serviço
pm2 start nome-do-app || docker start nome || systemctl start nome

# Verificar
pm2 status
curl -I http://localhost:PORTA
```

---

## Backup Automático via Cron

Adicionar ao crontab para backup diário automático:

```bash
# Ver crontab atual
crontab -l

# Adicionar (editar crontab)
crontab -e

# Linha para adicionar — backup todo dia às 3h da manhã:
0 3 * * * /bin/bash /backups/scripts/backup_diario.sh >> /var/log/backup.log 2>&1
```

Script `/backups/scripts/backup_diario.sh`:
```bash
#!/bin/bash
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Adicionar seus projetos aqui
for PROJECT in projeto1 projeto2; do
  pg_dump -U postgres $PROJECT | gzip > /backups/cron/${TIMESTAMP}_${PROJECT}.sql.gz
done

# Limpar backups com mais de 7 dias
find /backups/cron -name "*.sql.gz" -mtime +7 -delete

echo "[$TIMESTAMP] Backup automático concluído"
```

---

## Verificar Integridade do Backup

```bash
# Ver tamanho (um backup vazio indica problema)
du -sh /backups/TIMESTAMP_projeto/

# Verificar que o código foi copiado
ls /backups/TIMESTAMP_projeto/codigo/

# Verificar .env
cat /backups/TIMESTAMP_projeto/.env.backup | head -5

# Para banco comprimido, testar descompressão
gzip -t /backups/TIMESTAMP.sql.gz && echo "✅ Backup íntegro"
```

---

## Limpeza de Backups Antigos

```bash
# Ver todos os backups e tamanhos
du -sh /backups/*/ | sort -h

# Remover backups com mais de 30 dias
find /backups -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \;

# Ver espaço liberado
df -h /backups
```