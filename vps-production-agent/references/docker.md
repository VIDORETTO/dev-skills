# Docker

## Quando usar
Gerenciar containers, Docker Compose, imagens, volumes, redes. "sobe o docker", "container caiu", "rebuild da imagem", "limpar docker", atualizar imagem.

---

## Diagnóstico Rápido

```bash
# Ver containers rodando
docker ps

# Ver TODOS os containers (incluindo parados)
docker ps -a

# Ver imagens
docker images

# Ver uso de disco pelo Docker
docker system df

# Ver logs de um container
docker logs nome-do-container --tail 100
docker logs nome-do-container --tail 100 -f   # follow (tempo real)
```

---

## Docker Compose — Operações Comuns

### Subir / parar
```bash
cd /caminho/do/projeto  # onde está o docker-compose.yml

# Subir em background
docker-compose up -d

# Ver status
docker-compose ps

# Ver logs de todos os serviços
docker-compose logs --tail 50

# Ver logs de um serviço específico
docker-compose logs --tail 50 nome-do-servico

# Parar tudo (não remove containers)
docker-compose stop

# Parar e remover containers (mantém volumes)
docker-compose down

# Parar e remover TUDO incluindo volumes (⚠️ PERDA DE DADOS)
docker-compose down -v
```

### Atualizar imagem (deploy com Docker)
```bash
# Backup antes
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)_docker-compose"
mkdir -p $BACKUP_DIR
cp docker-compose.yml $BACKUP_DIR/
cp .env $BACKUP_DIR/ 2>/dev/null

# Baixar novas imagens
docker-compose pull

# Ver o que vai mudar (diff de imagens)
docker-compose images

# Recriar containers com novas imagens
docker-compose up -d --build

# Verificar
docker-compose ps
docker-compose logs --tail 30
```

### Rebuild forçado (quando há alteração no Dockerfile)
```bash
# Sem cache (garante build limpo)
docker-compose build --no-cache nome-do-servico
docker-compose up -d nome-do-servico

# Ou tudo de uma vez
docker-compose up -d --build --force-recreate
```

---

## Gerenciar Containers Individuais

```bash
# Reiniciar container
docker restart nome-do-container

# Parar
docker stop nome-do-container

# Iniciar container parado
docker start nome-do-container

# Entrar no container (shell interativo)
docker exec -it nome-do-container bash
docker exec -it nome-do-container sh   # se não tiver bash

# Executar comando dentro do container
docker exec nome-do-container comando

# Copiar arquivo para dentro do container
docker cp arquivo.txt nome-do-container:/caminho/destino

# Copiar arquivo do container para fora
docker cp nome-do-container:/caminho/arquivo.txt ./destino
```

---

## Volumes (dados persistentes)

```bash
# Listar volumes
docker volume ls

# Inspecionar volume (ver onde está montado)
docker volume inspect nome-do-volume

# Backup de volume
docker run --rm \
  -v nome-do-volume:/data \
  -v /backups:/backup \
  alpine tar czf /backup/volume_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restore de volume
docker run --rm \
  -v nome-do-volume:/data \
  -v /backups:/backup \
  alpine tar xzf /backup/volume_TIMESTAMP.tar.gz -C /data
```

---

## Limpeza (liberar espaço)

```bash
# Ver espaço usado pelo Docker
docker system df

# Remover containers parados, imagens sem uso, cache de build
docker system prune

# Com volumes não usados (⚠️ confirmar que volumes não têm dados importantes)
docker system prune -a --volumes

# Remover imagens não usadas (mantém as em uso)
docker image prune -a

# Remover volumes não usados
docker volume prune
```

---

## Rede Docker

```bash
# Listar redes
docker network ls

# Inspecionar rede (ver quais containers estão conectados)
docker network inspect nome-da-rede

# Criar rede
docker network create nome-da-rede

# Conectar container a uma rede
docker network connect nome-da-rede nome-do-container
```

---

## Rollback de Container

```bash
# Ver histórico de imagens de um container
docker images nome-da-imagem --format "table {{.Repository}}\t{{.Tag}}\t{{.ID}}\t{{.CreatedAt}}"

# Voltar para versão anterior
docker-compose stop nome-do-servico

# Editar docker-compose.yml para versão anterior
# image: nome-da-imagem:v1.2.3  ← tag anterior

docker-compose up -d nome-do-servico
docker-compose logs nome-do-servico --tail 30
```

---

## Problemas Comuns

| Problema | Diagnóstico | Solução |
|----------|-------------|---------|
| Container sai imediatamente | `docker logs nome` | Ver erro nos logs, corrigir config |
| Porta já em uso | `lsof -i :PORTA` | Parar processo na porta ou mudar porta |
| Sem espaço em disco | `docker system df` | `docker system prune` |
| Container não consegue conectar ao banco | `docker network ls` | Verificar se estão na mesma rede |
| Imagem não atualiza | Build com cache | `docker-compose build --no-cache` |