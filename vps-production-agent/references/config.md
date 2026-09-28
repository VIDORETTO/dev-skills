# Alteração de Configuração

## Quando usar
Alterar `.env`, arquivos de config, Nginx, variáveis de ambiente, certificados SSL, cron jobs.

---

## Protocolo Geral

### SEMPRE antes de alterar qualquer config:
```bash
# 1. Fazer backup do arquivo original
cp /caminho/do/arquivo /caminho/do/arquivo.backup_$(date +%Y%m%d_%H%M%S)

# 2. Ver conteúdo atual
cat /caminho/do/arquivo

# 3. Aplicar alteração
# 4. Validar sintaxe (quando possível)
# 5. Aplicar/reiniciar somente após validação
```

---

## .env / Variáveis de Ambiente

```bash
# Backup obrigatório
cp .env .env.backup_$(date +%Y%m%d_%H%M%S)

# Ver conteúdo atual (cuidado ao exibir — pode ter secrets)
cat .env

# Editar
nano .env   # ou usar echo/sed para alterar valores específicos

# Alterar valor específico sem abrir o arquivo
sed -i 's/^VARIAVEL=.*/VARIAVEL=novo_valor/' .env

# Adicionar nova variável
echo "NOVA_VAR=valor" >> .env

# Verificar
grep "VARIAVEL" .env
```

⚠️ Após alterar `.env`, o serviço precisa ser reiniciado para aplicar. Ver `references/restart.md`.

---

## Nginx

```bash
# Backup da config
cp /etc/nginx/sites-available/nome-do-site /etc/nginx/sites-available/nome-do-site.backup_$(date +%Y%m%d_%H%M%S)

# Editar
nano /etc/nginx/sites-available/nome-do-site

# VALIDAR ANTES DE APLICAR (obrigatório)
nginx -t

# Se OK — reload sem downtime
systemctl reload nginx

# Verificar
systemctl status nginx
curl -I http://dominio.com
```

Nunca faça `systemctl restart nginx` sem antes rodar `nginx -t`. Uma config inválida derruba TODOS os sites.

---

## Certificado SSL (Certbot / Let's Encrypt)

```bash
# Ver certificados atuais
certbot certificates

# Renovar manualmente
certbot renew --dry-run   # testar antes
certbot renew             # renovar de verdade

# Emitir novo certificado
certbot --nginx -d dominio.com -d www.dominio.com

# Verificar validade
echo | openssl s_client -servername dominio.com -connect dominio.com:443 2>/dev/null | openssl x509 -noout -dates
```

---

## Cron Jobs

```bash
# Ver crons atuais
crontab -l

# Backup antes de editar
crontab -l > /backups/crontab_backup_$(date +%Y%m%d_%H%M%S).txt

# Editar
crontab -e

# Testar o comando antes de adicionar ao cron
# Execute o comando manualmente e verifique o resultado
```

---

## Rollback de Configuração

```bash
# Restaurar backup
cp /caminho/arquivo.backup_DATA /caminho/arquivo

# Para Nginx, validar antes
nginx -t && systemctl reload nginx
```