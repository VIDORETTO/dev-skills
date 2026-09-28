# Monitoramento e Alertas

## Quando usar
"disco cheio", "memória esgotada", "CPU a 100%", "app caindo sozinho", "quero saber se o site cair", verificar saúde geral da VPS, configurar alertas.

---

## Health Check Geral da VPS

Execute isso primeiro quando algo parece errado ou para uma visão geral:

```bash
echo "=== DISCO ===" && df -h
echo "=== MEMÓRIA ===" && free -m
echo "=== CPU/LOAD ===" && uptime && top -bn1 | head -5
echo "=== PROCESSOS PM2 ===" && pm2 list 2>/dev/null || echo "PM2 não instalado"
echo "=== DOCKER ===" && docker ps 2>/dev/null || echo "Docker não instalado"
echo "=== NGINX ===" && systemctl is-active nginx
echo "=== ÚLTIMOS ERROS NGINX ===" && tail -20 /var/log/nginx/error.log 2>/dev/null
```

---

## Disco

```bash
# Uso geral
df -h

# O que está consumindo mais espaço
du -sh /* 2>/dev/null | sort -h | tail -15

# Dentro de /var (logs, banco, etc.)
du -sh /var/* 2>/dev/null | sort -h | tail -10

# Logs grandes
find /var/log -name "*.log" -size +100M 2>/dev/null

# Inodes (pode estar "cheio" mesmo com espaço em disco)
df -i

# Arquivos temporários grandes
find /tmp -size +50M 2>/dev/null
```

### Liberar espaço com segurança
```bash
# Limpar logs antigos do PM2
pm2 flush

# Limpar logs do sistema (com cuidado)
journalctl --vacuum-time=7d    # manter só 7 dias
journalctl --vacuum-size=500M  # ou limitar por tamanho

# Limpar imagens Docker não usadas
docker system prune -a         # remove containers parados, imagens sem uso, cache
docker volume prune            # remove volumes não usados (cuidado com dados!)

# Limpar cache de pacotes
apt-get clean
apt-get autoremove

# Logs de apps (verificar antes de deletar)
ls -lh /var/log/
# Só deletar se tiver certeza que não precisa
```

---

## Memória

```bash
# Visão geral
free -m

# Processos que mais consomem memória
ps aux --sort=-%mem | head -15

# Ver se tem swap
swapon --show
free -m | grep Swap

# Criar swap (se não existir e memória for crítica)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
```

---

## CPU

```bash
# Load atual e histórico
uptime
# Load average: 1min, 5min, 15min — ideal < número de cores
nproc   # ver quantos cores tem

# Processos que mais consomem CPU
ps aux --sort=-%cpu | head -15
top -bn1 | head -20

# Ver histórico de carga (se sar instalado)
sar -u 1 5
```

---

## Configurar Monitoramento Simples com Cron

### Script de health check com alerta por e-mail
```bash
# Criar script
cat > /usr/local/bin/healthcheck.sh << 'EOF'
#!/bin/bash
ALERT_EMAIL="seu@email.com"
HOSTNAME=$(hostname)

# Verificar disco
DISCO=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
if [ $DISCO -gt 85 ]; then
  echo "⚠️ ALERTA: Disco em ${DISCO}% em $HOSTNAME" | mail -s "Disco cheio - $HOSTNAME" $ALERT_EMAIL
fi

# Verificar memória
MEM_LIVRE=$(free -m | awk 'NR==2{printf "%s", $7}')
if [ $MEM_LIVRE -lt 200 ]; then
  echo "⚠️ ALERTA: Memória livre: ${MEM_LIVRE}MB em $HOSTNAME" | mail -s "Memória baixa - $HOSTNAME" $ALERT_EMAIL
fi

# Verificar se Nginx está rodando
if ! systemctl is-active --quiet nginx; then
  echo "⚠️ ALERTA: Nginx PARADO em $HOSTNAME" | mail -s "Nginx down - $HOSTNAME" $ALERT_EMAIL
fi
EOF

chmod +x /usr/local/bin/healthcheck.sh

# Adicionar ao cron (a cada 10 minutos)
(crontab -l 2>/dev/null; echo "*/10 * * * * /usr/local/bin/healthcheck.sh") | crontab -
```

---

## Uptime e Disponibilidade

```bash
# Tempo que a VPS está no ar
uptime -p

# Histórico de reboots
last reboot | head -10

# Ver se houve OOM killer (processo morto por falta de memória)
dmesg | grep -i "out of memory" | tail -10
journalctl -k | grep -i "killed process" | tail -10
```

---

## Ferramentas de Monitoramento em Tempo Real

```bash
# htop (interativo — instalar se não tiver)
apt-get install -y htop
htop

# ncdu (uso de disco interativo)
apt-get install -y ncdu
ncdu /

# nethogs (uso de rede por processo)
apt-get install -y nethogs
nethogs

# PM2 monit (só para apps Node)
pm2 monit
```

---

## Rotação de Logs

```bash
# Ver configuração do logrotate
cat /etc/logrotate.conf
ls /etc/logrotate.d/

# Criar config de rotação para app específico
cat > /etc/logrotate.d/meu-app << 'EOF'
/var/log/meu-app/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    sharedscripts
    postrotate
        pm2 reloadLogs 2>/dev/null || true
    endscript
}
EOF

# Testar rotação (sem aplicar)
logrotate --debug /etc/logrotate.d/meu-app

# Forçar rotação agora
logrotate --force /etc/logrotate.d/meu-app
```