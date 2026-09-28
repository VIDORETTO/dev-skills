# Atualização do Sistema e Pacotes

## Quando usar
"atualiza o sistema", "tem updates pendentes", instalar pacote novo, atualizar Node/Python/PHP, atualizar Nginx/banco de dados, "quero instalar o X".

---

## ⚠️ Classificação: 🟡 Médio / 🔴 Alto
Atualizações do sistema podem reiniciar serviços ou quebrar compatibilidade. Sempre fazer em horário de baixo uso.

---

## Atualização de Pacotes do Sistema (apt)

```bash
# Ver updates disponíveis SEM instalar
apt-get update
apt list --upgradable 2>/dev/null | head -30

# Instalar updates de segurança apenas (mais seguro)
apt-get upgrade -s | grep "^Inst.*security"  # ver quais são de segurança
unattended-upgrades --dry-run                 # simular

# Atualização completa (mais risco — pode atualizar pacotes críticos)
apt-get update && apt-get upgrade -y

# Checar se reboot é necessário após updates
ls /var/run/reboot-required 2>/dev/null && echo "⚠️ Reboot necessário" || echo "✅ Sem necessidade de reboot"
```

### Antes de atualizar em produção
```bash
# Registrar versões atuais dos serviços críticos
nginx -v
node --version
python3 --version
psql --version

# Fazer backup do banco (por segurança)
# Ver references/database.md

# Verificar se alguma atualização vai afetar serviços críticos
apt-get upgrade -s | grep -E "(nginx|postgresql|mysql|node|python)"
```

---

## Instalar Pacote Novo

```bash
# Verificar se já está instalado
which nome-do-pacote
dpkg -l | grep nome-do-pacote

# Instalar
apt-get update && apt-get install -y nome-do-pacote

# Verificar instalação
nome-do-pacote --version

# Remover pacote (com cuidado)
apt-get remove nome-do-pacote
apt-get purge nome-do-pacote   # remove também arquivos de config
```

---

## Node.js — Atualizar Versão

```bash
# Ver versão atual
node --version
npm --version

# Com nvm (recomendado)
nvm list                    # ver versões instaladas
nvm list-remote | grep LTS  # ver LTS disponíveis
nvm install 20              # instalar versão desejada
nvm use 20
nvm alias default 20        # definir como padrão

# Verificar que PM2 usa a versão correta
pm2 restart all             # reiniciar com a nova versão
pm2 list                    # verificar

# Sem nvm — via NodeSource
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
```

---

## Python — Atualizar / Instalar Versão

```bash
# Ver disponíveis
apt-cache show python3.11 python3.12

# Instalar versão específica
apt-get install -y python3.12 python3.12-venv

# Não alterar o python3 padrão sem necessidade — pode quebrar ferramentas do sistema
# Usar pyenv para múltiplas versões
```

---

## Nginx — Atualizar

```bash
# Ver versão atual e disponível
nginx -v
apt-cache policy nginx

# Backup das configs antes
cp -r /etc/nginx /etc/nginx.backup_$(date +%Y%m%d_%H%M%S)

# Atualizar
apt-get update && apt-get install -y nginx

# Verificar se configs ainda são válidas
nginx -t

# Reiniciar
systemctl restart nginx
systemctl status nginx
```

---

## Reboot da VPS

Às vezes necessário após atualizações de kernel.

```bash
# Verificar se reboot é necessário
cat /var/run/reboot-required 2>/dev/null

# Antes de reiniciar:
# 1. Verificar que PM2 está configurado para subir no boot
pm2 list   # anotar os apps rodando
pm2 startup   # deve mostrar "already" se configurado

# 2. Verificar que systemd services têm 'enable'
systemctl is-enabled nginx
systemctl is-enabled postgresql
systemctl is-enabled docker

# 3. Avisar usuários se possível

# Agendar reboot para daqui a X minutos
shutdown -r +5 "Sistema será reiniciado em 5 minutos para manutenção"

# Reboot imediato
reboot

# Após reboot — verificar que tudo subiu
pm2 list
docker ps
systemctl status nginx
curl -I https://dominio.com
```

---

## Limpeza do Sistema

```bash
# Remover pacotes desnecessários
apt-get autoremove -y
apt-get clean

# Ver logs grandes
journalctl --disk-usage
journalctl --vacuum-time=30d   # manter só 30 dias

# Pacotes que podem ser removidos com segurança
apt-get autoremove --purge
```