# SSL / HTTPS / Certificados

## Quando usar
Emitir certificado novo, renovar SSL, erro de certificado expirado, configurar HTTPS, redirecionar HTTP → HTTPS, domínio novo.

---

## Diagnóstico Rápido de SSL

```bash
# Ver se o certificado está válido e quando expira
echo | openssl s_client -servername dominio.com -connect dominio.com:443 2>/dev/null | openssl x509 -noout -dates

# Ver todos os certificados gerenciados pelo Certbot
certbot certificates

# Testar renovação sem aplicar
certbot renew --dry-run
```

---

## Emitir Novo Certificado (Certbot + Nginx)

### Pré-requisitos
```bash
# DNS do domínio deve apontar para o IP da VPS
dig +short dominio.com
curl -4 ifconfig.me   # seu IP da VPS

# Porta 80 deve estar aberta (Certbot valida via HTTP)
ufw status | grep 80
```

### Emitir certificado
```bash
# Com plugin Nginx (mais fácil — configura automaticamente)
certbot --nginx -d dominio.com -d www.dominio.com

# Com plugin standalone (Nginx deve estar parado)
systemctl stop nginx
certbot certonly --standalone -d dominio.com
systemctl start nginx

# Verificar se foi emitido
certbot certificates
ls /etc/letsencrypt/live/dominio.com/
```

### Após emissão, verificar Nginx
```bash
nginx -t
systemctl reload nginx
curl -I https://dominio.com
```

---

## Renovação de Certificado

```bash
# Renovar todos os certificados próximos do vencimento
certbot renew

# Forçar renovação de um domínio específico
certbot renew --force-renewal --cert-name dominio.com

# Verificar se o cron de renovação automática existe
systemctl list-timers | grep certbot
crontab -l | grep certbot

# Se não existir renovação automática, adicionar:
crontab -e
# Adicionar linha:
0 3 * * * certbot renew --quiet && systemctl reload nginx
```

---

## Configuração Nginx para HTTPS

Template seguro de config Nginx com HTTPS:

```nginx
server {
    listen 80;
    server_name dominio.com www.dominio.com;
    return 301 https://$host$request_uri;  # Redirecionar HTTP → HTTPS
}

server {
    listen 443 ssl;
    server_name dominio.com www.dominio.com;

    ssl_certificate /etc/letsencrypt/live/dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/dominio.com/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    location / {
        proxy_pass http://localhost:PORTA;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Após editar, sempre validar antes de aplicar
nginx -t && systemctl reload nginx
```

---

## Erros Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| `Certificate has expired` | Renovação automática falhou | `certbot renew --force-renewal` |
| `Connection refused` na porta 443 | Nginx parado ou não escutando 443 | `systemctl status nginx`, checar config |
| `Too many redirects` | Redirect loop HTTP↔HTTPS | Checar config Nginx, remover redirect duplo |
| `ERR_CERT_COMMON_NAME_INVALID` | Certificado não cobre o domínio | `certbot certificates`, emitir novo |
| Certbot falha na validação | Porta 80 bloqueada ou DNS errado | `ufw allow 80`, verificar DNS |

---

## Wildcard Certificate (subdomínios)

```bash
# Requer validação via DNS (não HTTP)
certbot certonly --manual --preferred-challenges dns \
  -d dominio.com -d "*.dominio.com"

# Certbot vai pedir para adicionar um registro TXT no DNS
# Após adicionar, confirmar e aguardar propagação (pode demorar alguns minutos)
```