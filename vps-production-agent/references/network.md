# Rede e DNS

## Quando usar
Problemas de conectividade, configurar domínio novo, verificar DNS, checar latência, problema de proxy, IP bloqueado, configurar subdomínio.

---

## Diagnóstico de Rede

```bash
# IP público da VPS
curl -4 ifconfig.me
curl -6 ifconfig.me 2>/dev/null   # IPv6

# IP interno
ip addr show
hostname -I

# Conectividade externa
ping -c 4 8.8.8.8
ping -c 4 google.com

# Rotas
ip route

# Portas abertas e o que está escutando
ss -tlnp       # TCP
ss -ulnp       # UDP
netstat -tlnp  # alternativa

# Verificar se porta específica está acessível externamente
# (executar de fora da VPS ou usar ferramenta online)
nc -zv dominio.com 443
```

---

## DNS

```bash
# Verificar para onde um domínio aponta
dig dominio.com
dig +short dominio.com A          # só o IP
dig +short dominio.com AAAA       # IPv6
dig +short dominio.com MX         # e-mail
dig +short dominio.com TXT        # registros TXT (SPF, DKIM, etc.)
dig +short www.dominio.com CNAME  # alias

# Verificar propagação (usar servidor DNS externo)
dig @8.8.8.8 dominio.com A        # Google DNS
dig @1.1.1.1 dominio.com A        # Cloudflare DNS

# Resolver DNS reverso (IP → domínio)
dig -x IP_DA_VPS

# Ver qual DNS server a VPS usa
cat /etc/resolv.conf
```

### Tempo de Propagação
DNS pode levar de minutos a 48h para propagar. Para verificar propagação global:
- `dig @8.8.8.8 dominio.com` (Google)
- `dig @1.1.1.1 dominio.com` (Cloudflare)
- Ferramentas online: whatsmydns.net, dnschecker.org

---

## Nginx — Diagnóstico de Proxy

```bash
# Ver configurações ativas
nginx -T 2>/dev/null | head -100   # toda config compilada
ls /etc/nginx/sites-enabled/       # sites ativos

# Logs de acesso (ver requests chegando)
tail -f /var/log/nginx/access.log

# Logs de erro
tail -f /var/log/nginx/error.log

# Testar se app interno está respondendo (sem passar pelo Nginx)
curl -I http://localhost:PORTA_DO_APP

# Testar via Nginx
curl -I http://dominio.com
curl -I https://dominio.com
```

### Erros comuns de proxy
```bash
# 502 Bad Gateway — app não está rodando na porta esperada
# Verificar:
pm2 list                           # PM2 rodando?
lsof -i :PORTA_DO_APP              # algo na porta?
curl http://localhost:PORTA_DO_APP  # app responde localmente?

# 504 Gateway Timeout — app demora demais para responder
# Aumentar timeout no Nginx:
# proxy_connect_timeout 60s;
# proxy_send_timeout 60s;
# proxy_read_timeout 60s;

# 413 Request Entity Too Large — arquivo enviado muito grande
# Aumentar no Nginx:
# client_max_body_size 50M;
```

---

## Cloudflare (se usar)

```bash
# Se o site usa Cloudflare, o IP do dig será o IP da Cloudflare
# Para ver o IP real da VPS atrás da CF:
dig origem.dominio.com  # se tiver subdomínio de origem configurado

# Verificar se Cloudflare está no modo proxy (nuvem laranja)
# ou DNS only (nuvem cinza) — via painel da Cloudflare

# Teste passando direto pelo IP da VPS (bypassando CF)
curl -H "Host: dominio.com" http://IP_DA_VPS

# Configuração Nginx para Cloudflare (pegar IP real do visitante)
# Adicionar no bloco server ou location:
# set_real_ip_from 173.245.48.0/20;  # ranges da CF
# real_ip_header CF-Connecting-IP;
```

---

## Conectividade entre Serviços

```bash
# Testar conexão com banco de dados
# PostgreSQL
psql -h localhost -U usuario -d banco -c "SELECT 1"
nc -zv localhost 5432

# MySQL
mysql -h localhost -u usuario -p -e "SELECT 1"
nc -zv localhost 3306

# Redis
redis-cli ping
nc -zv localhost 6379

# Testar conexão com serviço externo da VPS
curl -v https://api.servico-externo.com
```

---

## Traceroute e Latência

```bash
# Traceroute (ver caminho até um destino)
traceroute google.com
mtr --report google.com   # mais detalhado (instalar: apt install mtr)

# Latência para domínio
ping -c 10 dominio.com | tail -2

# Velocidade de download da VPS
curl -s https://raw.githubusercontent.com/sivel/speedtest-cli/master/speedtest.py | python3 -
```