# Instalação de Novo Projeto

## Quando usar
"quero subir um projeto novo", "como configuro esse repositório na VPS", "instalar um novo app", configurar um serviço do zero.

---

## FASE 0 — Reconhecimento da VPS

```bash
# Recursos disponíveis
free -m && df -h && nproc

# O que já está instalado
node --version 2>/dev/null || echo "Node: não instalado"
python3 --version 2>/dev/null || echo "Python: não instalado"
php --version 2>/dev/null || echo "PHP: não instalado"
docker --version 2>/dev/null || echo "Docker: não instalado"
pm2 --version 2>/dev/null || echo "PM2: não instalado"
nginx -v 2>/dev/null || echo "Nginx: não instalado"

# Projetos já rodando
pm2 list 2>/dev/null
docker ps 2>/dev/null
ls /var/www/ 2>/dev/null
```

---

## FASE 1 — Perguntas Necessárias

Pergunte em uma mensagem:
- Qual o repositório (link do GitHub)?
- Qual a tecnologia? (Node, Python, PHP, etc.)
- Qual porta o app vai usar?
- Tem banco de dados? Qual? (PostgreSQL, MySQL, Redis, etc.)
- Tem domínio? Precisa de SSL?
- Precisa de variáveis de ambiente (.env)?

---

## FASE 2 — Preparação do Ambiente

### Diretório do projeto
```bash
# Padrão recomendado
mkdir -p /var/www/nome-do-projeto
cd /var/www/nome-do-projeto

# Ou na home do usuário
mkdir -p /home/usuario/apps/nome-do-projeto
```

### Clonar repositório
```bash
git clone https://github.com/usuario/repo.git /var/www/nome-do-projeto
cd /var/www/nome-do-projeto
git log --oneline -3   # confirmar que veio certo
```

---

## FASE 3 — Instalação por Tecnologia

### Node.js
```bash
# Verificar versão necessária (package.json)
cat package.json | grep '"node"'

# Instalar versão correta (com nvm se necessário)
nvm use 20   # ou a versão correta
node --version

# Instalar dependências
npm ci

# Criar .env a partir do exemplo
cp .env.example .env
nano .env   # editar com os valores corretos

# Testar antes de colocar no PM2
node index.js   # ou npm start
# Ctrl+C após confirmar que funciona
```

### Python
```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar .env
cp .env.example .env
nano .env

# Testar
python app.py   # ou uvicorn main:app etc.
# Ctrl+C após confirmar
```

### PHP (Laravel)
```bash
composer install --no-dev --optimize-autoloader
cp .env.example .env
php artisan key:generate
nano .env   # configurar banco etc.
php artisan migrate
php artisan config:cache
php artisan route:cache
```

---

## FASE 4 — Banco de Dados

### PostgreSQL — criar banco e usuário
```bash
sudo -u postgres psql << EOF
CREATE USER nome_usuario WITH PASSWORD 'senha_segura';
CREATE DATABASE nome_banco OWNER nome_usuario;
GRANT ALL PRIVILEGES ON DATABASE nome_banco TO nome_usuario;
EOF

# Testar conexão
psql -U nome_usuario -d nome_banco -h localhost -c "\\l"
```

### MySQL
```bash
mysql -u root -p << EOF
CREATE DATABASE nome_banco CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'nome_usuario'@'localhost' IDENTIFIED BY 'senha_segura';
GRANT ALL PRIVILEGES ON nome_banco.* TO 'nome_usuario'@'localhost';
FLUSH PRIVILEGES;
EOF
```

### Redis
```bash
# Verificar se está rodando
systemctl status redis
redis-cli ping   # deve retornar PONG
```

---

## FASE 5 — Configurar Gerenciador de Processo

### PM2 (Node.js / Python)
```bash
# Iniciar com PM2
pm2 start index.js --name "nome-do-app"

# Ou com ecosystem file (recomendado)
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'nome-do-app',
    script: './index.js',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
}
EOF

pm2 start ecosystem.config.js
pm2 save                        # salvar para persistir no reboot
pm2 startup                     # configurar para iniciar no boot (seguir as instruções impressas)
```

### Systemd (Python / outros)
```bash
cat > /etc/systemd/system/nome-do-app.service << EOF
[Unit]
Description=Nome do App
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/nome-do-projeto
ExecStart=/var/www/nome-do-projeto/venv/bin/python app.py
Restart=always
RestartSec=10
EnvironmentFile=/var/www/nome-do-projeto/.env

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable nome-do-app
systemctl start nome-do-app
systemctl status nome-do-app
```

---

## FASE 6 — Configurar Nginx

```bash
# Criar config
nano /etc/nginx/sites-available/nome-do-projeto

# Conteúdo base (HTTP primeiro, SSL depois com certbot)
cat > /etc/nginx/sites-available/nome-do-projeto << 'EOF'
server {
    listen 80;
    server_name dominio.com www.dominio.com;

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
EOF

# Ativar
ln -s /etc/nginx/sites-available/nome-do-projeto /etc/nginx/sites-enabled/

# Validar e aplicar
nginx -t && systemctl reload nginx

# Adicionar SSL
certbot --nginx -d dominio.com -d www.dominio.com
```

---

## FASE 7 — Validação Final

```bash
# Processo rodando?
pm2 status || systemctl status nome-do-app

# Porta respondendo?
curl -I http://localhost:PORTA

# Domínio respondendo?
curl -I http://dominio.com
curl -I https://dominio.com

# Logs limpos (sem erros)?
pm2 logs nome-do-app --lines 30
```

---

## Checklist de Novo Projeto

- [ ] Repositório clonado e verificado
- [ ] Dependências instaladas
- [ ] .env criado e configurado
- [ ] Banco criado e migrations aplicadas
- [ ] App testado manualmente antes do PM2/systemd
- [ ] Gerenciador de processo configurado e salvo
- [ ] PM2 startup / systemd enable configurado (vai subir no reboot)
- [ ] Nginx configurado e validado
- [ ] SSL emitido
- [ ] Domínio respondendo em HTTPS
- [ ] Logs sem erros