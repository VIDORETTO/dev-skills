# Deploy de Nova Versão

## Quando usar
Link do GitHub recebido, "nova versão pronta", "faz o deploy", "atualiza o projeto", novo tag/release.

---

## Protocolo Completo de Deploy

### FASE 0 — Coleta de Informações
Pergunte (em uma mensagem só) se não souber:
- Qual o nome do projeto e onde está hospedado na VPS? (ex: `/var/www/meuapp`)
- Qual o gerenciador de processo? (PM2, Docker, systemd, outro)
- Tem banco de dados com migrations pendentes?
- Horário de menor uso (para minimizar impacto)?

### FASE 1 — Reconhecimento (sempre executar)
```bash
# Identificar o projeto
ls /var/www/ || ls /home/ || ls /opt/

# Ver processo atual
pm2 list           # se usar PM2
docker ps          # se usar Docker
systemctl list-units --type=service --state=running  # se usar systemd

# Ver versão atual em produção
cd /caminho/do/projeto
git log --oneline -5
git status

# Ver uso de recursos
df -h              # espaço em disco
free -m            # memória disponível
```

### FASE 2 — Backup Obrigatório (nunca pular)
```bash
# Backup do código atual
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)_nome-do-projeto"
mkdir -p $BACKUP_DIR
cp -r /caminho/do/projeto $BACKUP_DIR/codigo

# Backup do .env (CRÍTICO)
cp /caminho/do/projeto/.env $BACKUP_DIR/.env.backup

# Backup do banco (se aplicável) — ver references/database.md

# Registrar versão atual
cd /caminho/do/projeto
git rev-parse HEAD > $BACKUP_DIR/commit_anterior.txt
echo "Backup criado em: $BACKUP_DIR"
```

### FASE 3 — Download da Nova Versão

**Opção A — Git Pull (repositório já clonado)**
```bash
cd /caminho/do/projeto
git fetch origin
git diff HEAD origin/main --stat   # ver o que vai mudar
git pull origin main               # ou a branch correta
```

**Opção B — Novo clone (repositório novo ou troca de branch)**
```bash
cd /tmp
git clone https://github.com/usuario/repo.git projeto-novo
# Verificar se veio certo
ls projeto-novo/
```

**Opção C — Release/tag específico**
```bash
cd /caminho/do/projeto
git fetch --tags
git checkout tags/v1.2.3
```

### FASE 4 — Instalação de Dependências
```bash
cd /caminho/do/projeto

# Node.js
npm ci --production          # preferível ao npm install em produção

# Python
pip install -r requirements.txt --break-system-packages

# PHP
composer install --no-dev --optimize-autoloader
```

### FASE 5 — Migrations de Banco (se houver)
⚠️ Ver `references/database.md` para protocolo completo de migrations.

```bash
# Exemplo Node/Prisma
npx prisma migrate deploy

# Exemplo Django
python manage.py migrate --check   # checar primeiro
python manage.py migrate           # aplicar

# Exemplo Laravel
php artisan migrate --force
```

### FASE 6 — Build (se necessário)
```bash
# Node.js
npm run build

# Verificar se o build foi gerado
ls -la dist/ || ls -la build/ || ls -la .next/
```

### FASE 7 — Variáveis de Ambiente
```bash
# Comparar .env com .env.example para ver se faltou algo
diff .env .env.example || diff .env .env.sample
# Se houver variáveis novas, adicionar antes de reiniciar
```

### FASE 8 — Reinicialização do Serviço

**PM2:**
```bash
pm2 reload nome-do-app     # zero-downtime (preferível)
# ou
pm2 restart nome-do-app   # downtime curto
pm2 save                  # salvar estado
```

**Docker:**
```bash
docker-compose pull
docker-compose up -d --build
docker-compose ps   # verificar se subiu
```

**Systemd:**
```bash
systemctl restart nome-do-servico
systemctl status nome-do-servico
```

### FASE 9 — Validação Pós-Deploy (OBRIGATÓRIO)
```bash
# Verificar se processo está rodando
pm2 status || docker ps || systemctl status nome

# Ver últimos logs (procurar erros)
pm2 logs nome-do-app --lines 50
docker logs nome-do-container --tail 50
journalctl -u nome-do-servico -n 50

# Testar endpoint (se for web)
curl -I http://localhost:PORTA
curl -I https://dominio.com

# Checar uso de memória/CPU
pm2 monit    # interativo
htop         # visão geral
```

### FASE 10 — Registro
Informe ao usuário:
- Commit anterior → Commit novo
- Tempo total de deploy
- Se houve downtime e por quanto tempo
- Localização do backup criado

---

## Rollback

Se algo der errado após o deploy:

```bash
# Voltar para o commit anterior
cd /caminho/do/projeto
git checkout COMMIT_ANTERIOR

# Ou restaurar do backup
cp -r $BACKUP_DIR/codigo/. /caminho/do/projeto/
cp $BACKUP_DIR/.env.backup /caminho/do/projeto/.env

# Reinstalar dependências da versão anterior
npm ci --production

# Reiniciar
pm2 restart nome-do-app
```

---

## Checklist Rápido

- [ ] Backup do código feito?
- [ ] Backup do .env feito?
- [ ] Backup do banco feito (se migration)?
- [ ] Código baixado e verificado?
- [ ] Dependências instaladas?
- [ ] Migrations aplicadas?
- [ ] Build gerado?
- [ ] Serviço reiniciado?
- [ ] Logs verificados (sem erros)?
- [ ] Endpoint respondendo?