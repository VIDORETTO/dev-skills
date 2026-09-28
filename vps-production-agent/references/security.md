# Segurança

## Quando usar
Alterar firewall, configurar SSH, criar/remover usuários, definir permissões de arquivos, checar acessos suspeitos, hardening da VPS.

---

## ⚠️ Classificação Padrão: 🔴 Alto / ⚫ Crítico
Erros de segurança podem bloquear acesso à VPS permanentemente ou abrir brechas. Sempre confirme antes de executar.

---

## Firewall (UFW)

```bash
# Ver regras atuais ANTES de qualquer alteração
ufw status verbose

# NUNCA feche a porta SSH antes de confirmar que ela está liberada
# Verificar porta SSH atual
ss -tlnp | grep sshd
cat /etc/ssh/sshd_config | grep Port

# Liberar porta (sempre confirme a porta SSH antes)
ufw allow 22/tcp      # SSH
ufw allow 80/tcp      # HTTP
ufw allow 443/tcp     # HTTPS
ufw allow PORTA/tcp   # App específico

# Bloquear porta
ufw deny PORTA/tcp

# Remover regra
ufw delete allow PORTA/tcp

# Ativar (só após verificar que SSH está liberado)
ufw enable

# Ver regras numeradas (para deletar por número)
ufw status numbered
ufw delete NUMERO
```

⚫ **CRÍTICO**: Nunca execute `ufw deny 22` ou `ufw reset` sem confirmar que acesso alternativo existe. Bloquear SSH pode tornar a VPS inacessível.

---

## SSH

```bash
# Ver configuração atual
cat /etc/ssh/sshd_config

# Backup antes de qualquer alteração
cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup_$(date +%Y%m%d_%H%M%S)

# Testar configuração ANTES de reiniciar SSH
sshd -t

# Reiniciar SSH (só após sshd -t retornar OK)
systemctl restart sshd

# Ver tentativas de login (detectar ataques)
journalctl -u sshd | grep "Failed password" | tail -20
grep "Failed password" /var/log/auth.log | tail -20

# Ver IPs bloqueados pelo fail2ban (se instalado)
fail2ban-client status sshd
```

⚫ **CRÍTICO**: Nunca altere a porta SSH sem ter uma sessão paralela aberta para testar. Se a config ficar inválida e você reiniciar, perde acesso.

---

## Usuários e Permissões

```bash
# Listar usuários com shell (usuários reais)
cat /etc/passwd | grep -v nologin | grep -v false

# Criar usuário com home
useradd -m -s /bin/bash nome-do-usuario

# Definir senha
passwd nome-do-usuario

# Adicionar ao sudo
usermod -aG sudo nome-do-usuario

# Ver grupos do usuário
groups nome-do-usuario

# Remover usuário (com cuidado — não remova usuários de serviços ativos)
# Primeiro verificar se tem processos rodando com esse usuário
ps aux | grep nome-do-usuario
# Só então remover
userdel -r nome-do-usuario   # -r remove o home também
```

---

## Permissões de Arquivos

```bash
# Ver permissões atuais
ls -la /caminho/do/projeto/

# Permissões seguras para projeto web
chmod 755 /var/www/projeto          # diretório
chmod 644 /var/www/projeto/*.js     # arquivos de código
chmod 600 /var/www/projeto/.env     # .env nunca deve ser público

# Dono correto
chown -R www-data:www-data /var/www/projeto    # Nginx/Apache
chown -R node:node /var/www/projeto            # se rodar como usuário node

# Verificar .env (não deve ter leitura por outros)
stat /var/www/projeto/.env
```

---

## Auditoria de Acesso

```bash
# Últimos logins
last -n 20

# Logins falhos recentes
lastb -n 20

# Comandos sudo executados
grep sudo /var/log/auth.log | tail -30

# Processos rodando e por quem
ps aux

# Conexões abertas
ss -tlnp
netstat -tlnp

# Ver se tem algo escutando em portas incomuns
ss -tlnp | grep -v -E ":(22|80|443|3000|8080|5432|3306)\\s"
```

---

## Fail2ban (proteção contra bruteforce)

```bash
# Ver status
fail2ban-client status

# Ver IPs banidos para SSH
fail2ban-client status sshd

# Desbanir IP específico
fail2ban-client set sshd unbanip IP_DO_SEU_USUARIO

# Ver log do fail2ban
tail -50 /var/log/fail2ban.log
```