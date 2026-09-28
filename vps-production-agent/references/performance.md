# Performance e Otimização

## Quando usar
"tá lento", "alta latência", "CPU alta", "memória estourando", "muitos usuários simultâneos", "quero otimizar", queries lentas, alto tempo de resposta.

---

## FASE 0 — Medir Antes de Otimizar

Nunca otimize no chute. Sempre meça primeiro.

```bash
# Tempo de resposta do endpoint
time curl -s http://localhost:PORTA/rota > /dev/null

# Múltiplas medições
for i in {1..10}; do time curl -s http://localhost:PORTA/ > /dev/null; done 2>&1 | grep real

# Recursos atuais
top -bn1 | head -20
free -m
iostat -x 1 3   # I/O de disco (instalar: apt install sysstat)
```

---

## Node.js / PM2

```bash
# Ver uso de memória e CPU por processo
pm2 monit

# Ver detalhes de um app específico
pm2 show nome-do-app

# Aumentar instâncias (cluster mode) — usar múltiplos cores
pm2 delete nome-do-app
pm2 start index.js --name nome-do-app -i max  # -i max = um por core
# Ou no ecosystem.config.js:
# instances: 'max'  # ou um número específico
pm2 save

# Limitar uso de memória (auto-restart se ultrapassar)
pm2 start index.js --name nome-do-app --max-memory-restart 500M

# Ver logs de performance
pm2 logs nome-do-app --lines 50
```

---

## Nginx — Otimizações

```bash
# Backup antes de alterar
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup_$(date +%Y%m%d_%H%M%S)
```

Configurações recomendadas em `/etc/nginx/nginx.conf`:

```nginx
worker_processes auto;              # um worker por core
worker_connections 1024;            # conexões por worker

# Compressão gzip
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;

# Cache de arquivos estáticos
location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2)$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}

# Timeouts
proxy_connect_timeout 30s;
proxy_send_timeout 30s;
proxy_read_timeout 30s;
```

```bash
# Após editar
nginx -t && systemctl reload nginx
```

---

## Banco de Dados — Queries Lentas

### PostgreSQL
```bash
# Ativar log de queries lentas (> 1 segundo)
psql -U postgres -c "ALTER SYSTEM SET log_min_duration_statement = 1000;"
psql -U postgres -c "SELECT pg_reload_conf();"

# Ver queries ativas agora
psql -U postgres -c "SELECT pid, now()-query_start AS duracao, query FROM pg_stat_activity WHERE state = 'active' ORDER BY duracao DESC;"

# Matar query travada
psql -U postgres -c "SELECT pg_cancel_backend(PID);"

# Queries mais lentas (requer pg_stat_statements)
psql -U postgres -d nome_banco -c "SELECT query, mean_exec_time, calls FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;"

# Ver conexões abertas
psql -U postgres -c "SELECT count(*) FROM pg_stat_activity;"

# Índices não usados (candidatos a remover)
psql -U postgres -d nome_banco -c "SELECT schemaname, tablename, indexname FROM pg_stat_user_indexes WHERE idx_scan = 0;"
```

### MySQL
```bash
# Ver queries em execução
mysql -u root -p -e "SHOW PROCESSLIST;"

# Ver queries lentas
mysql -u root -p -e "SHOW VARIABLES LIKE 'slow_query_log%';"
mysql -u root -p -e "SET GLOBAL slow_query_log = 'ON'; SET GLOBAL long_query_time = 1;"

# Matar query
mysql -u root -p -e "KILL QUERY ID_DA_QUERY;"
```

---

## Memória — Diagnóstico e Solução

```bash
# Ver o que mais consome
ps aux --sort=-%mem | head -15

# Ver se tem leak (memória crescendo continuamente)
watch -n 5 'ps aux --sort=-%mem | head -5'

# Se memória esgotando — criar/aumentar swap
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
# Para persistir no reboot:
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Verificar
free -m
swapon --show
```

---

## Disco — I/O Lento

```bash
# Ver operações de I/O por processo
iotop -ao   # instalar: apt install iotop

# Ver estatísticas de disco
iostat -x 1 5

# Ver arquivos abertos por um processo
lsof -p PID | head -20

# Identificar arquivos grandes criados recentemente
find / -size +100M -newer /tmp -not -path "/proc/*" 2>/dev/null
```

---

## Benchmark Simples de Endpoint

```bash
# ab (Apache Benchmark) — instalar: apt install apache2-utils
ab -n 100 -c 10 http://localhost:PORTA/
# -n = total de requests
# -c = concorrência

# wrk (mais moderno) — instalar: apt install wrk
wrk -t4 -c100 -d30s http://localhost:PORTA/
# -t = threads, -c = conexões, -d = duração
```