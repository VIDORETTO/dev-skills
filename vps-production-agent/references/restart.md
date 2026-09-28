# Reinicialização de Serviço

## Quando usar
"reinicia o app", "tá travado", "não responde", "deu crash", processo consumindo muita memória, serviço parado.

---

## FASE 0 — Diagnóstico Antes de Reiniciar
Nunca reinicie sem antes entender o porquê do problema.

```bash
# Ver status atual de todos os processos
pm2 list
docker ps -a
systemctl list-units --type=service --state=failed

# Ver logs recentes (ANTES de reiniciar — logs podem ser perdidos)
pm2 logs nome-do-app --lines 100
docker logs nome-do-container --tail 100 2>&1
journalctl -u nome-do-servico -n 100

# Recursos do sistema
top -bn1 | head -20
free -m
df -h
```

Salve os logs antes de reiniciar:
```bash
pm2 logs nome --lines 200 > /tmp/logs_antes_restart_$(date +%Y%m%d_%H%M%S).txt
```

---

## Reinicialização por Gerenciador

### PM2
```bash
# Zero-downtime (preferível para web apps)
pm2 reload nome-do-app

# Reinício completo (quando reload não resolve)
pm2 restart nome-do-app

# Verificar depois
pm2 status
pm2 logs nome-do-app --lines 30
```

### Docker
```bash
# Reiniciar container
docker restart nome-do-container

# Se container parou (não está em docker ps)
docker start nome-do-container

# Se precisa recriar
docker-compose down && docker-compose up -d

# Verificar
docker ps
docker logs nome-do-container --tail 30
```

### Systemd
```bash
# Reiniciar
systemctl restart nome-do-servico

# Verificar
systemctl status nome-do-servico
journalctl -u nome-do-servico -n 30 --no-pager
```

### Nginx
```bash
# Testar configuração ANTES de reiniciar (OBRIGATÓRIO)
nginx -t

# Se OK, reload (sem downtime)
systemctl reload nginx

# Se reload não funcionar
systemctl restart nginx

# Verificar
systemctl status nginx
curl -I http://localhost
```

---

## Validação Pós-Restart
```bash
# Processo está rodando?
pm2 status || docker ps || systemctl status nome

# Tem erros nos logs?
pm2 logs nome --lines 20
docker logs nome --tail 20

# Endpoint responde?
curl -I http://localhost:PORTA
```

---

## Se o Serviço Não Sobe

1. Ver logs de erro completos
2. Verificar se porta está em uso: `lsof -i :PORTA`
3. Verificar permissões: `ls -la /caminho/do/projeto`
4. Verificar variáveis de ambiente: `cat .env`
5. Tentar subir manualmente para ver output: `node index.js` ou `python app.py`