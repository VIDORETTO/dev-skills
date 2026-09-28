# Diagnóstico e Debugging

## Quando usar
"não funciona", "deu erro", "tá lento", "caiu", "retornando 500", "timeout", qualquer falha de funcionamento.

---

## Protocolo de Diagnóstico (ordem a seguir)

### PASSO 1 — Verificar se o processo está rodando
```bash
pm2 list
docker ps -a
systemctl status nome-do-servico

# Verificar porta
lsof -i :PORTA
netstat -tlnp | grep PORTA
```

### PASSO 2 — Ver logs recentes
```bash
# PM2
pm2 logs nome-do-app --lines 100 --nostream

# Docker
docker logs nome-do-container --tail 100

# Systemd
journalctl -u nome-do-servico -n 100 --no-pager

# Nginx
tail -100 /var/log/nginx/error.log
tail -100 /var/log/nginx/access.log

# App logs customizados
tail -100 /var/log/nome-do-app/*.log
find /var/log -name "*.log" -newer /tmp -mmin -60  # logs modificados na última hora
```

### PASSO 3 — Recursos do sistema
```bash
# Memória
free -m
# Se memória esgotada: processos podem estar sendo mortos pelo OOM killer
dmesg | grep -i "killed process" | tail -10

# CPU
top -bn1 | head -20
# Ou ver processo específico
ps aux --sort=-%cpu | head -20

# Disco
df -h
du -sh /var/www/* | sort -h  # ver qual pasta está consumindo mais

# Inodes (pode causar "no space left" mesmo com espaço livre)
df -i
```

### PASSO 4 — Testar endpoint diretamente
```bash
# HTTP simples
curl -v http://localhost:PORTA
curl -v https://dominio.com

# Com timeout
curl --max-time 10 -v http://localhost:PORTA

# Ver headers
curl -I http://localhost:PORTA

# POST com JSON
curl -X POST http://localhost:PORTA/rota \
  -H "Content-Type: application/json" \
  -d '{"teste": "valor"}' -v
```

### PASSO 5 — Verificar configuração
```bash
# .env existe e tem as variáveis corretas?
cat /caminho/do/projeto/.env

# Permissões corretas?
ls -la /caminho/do/projeto/

# Versões corretas?
node --version
python --version
php --version
```

---

## Erros Comuns e Soluções

| Sintoma | Causa Provável | Verificar |
|---------|---------------|-----------|
| App não responde na porta | Processo não iniciou ou porta errada | `lsof -i :PORTA` |
| 502 Bad Gateway (Nginx) | App interno não está rodando | `pm2 list`, logs do app |
| Erro de memória / OOM | Leak ou pico de tráfego | `free -m`, `dmesg | grep killed` |
| "No space left on device" | Disco cheio | `df -h`, `du -sh /*` |
| Erro de permissão | Arquivo/pasta sem permissão correta | `ls -la`, `whoami` |
| "Cannot connect to database" | Banco não está rodando ou credenciais erradas | `systemctl status postgresql`, checar `.env` |
| SSL expirado | Certificado vencido | `certbot certificates` |

---

## Coleta de Evidências (antes de qualquer mudança)

Sempre salve os logs e estado antes de intervir:

```bash
DIAG_DIR="/tmp/diagnostico_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DIAG_DIR

pm2 list > $DIAG_DIR/pm2_list.txt 2>&1
pm2 logs nome-do-app --lines 200 --nostream > $DIAG_DIR/pm2_logs.txt 2>&1
free -m > $DIAG_DIR/memoria.txt
df -h > $DIAG_DIR/disco.txt
top -bn1 > $DIAG_DIR/cpu.txt

echo "Diagnóstico salvo em $DIAG_DIR"
ls $DIAG_DIR
```