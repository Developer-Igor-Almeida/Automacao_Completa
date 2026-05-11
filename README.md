## 🚀 Como rodar o projeto

### Pré-requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado

### Passos

```bash
# 1. Clone o repositório
git clone <url-do-repo>
cd Automacao_Completa

# 2. Suba o projeto
docker-compose up --build

# 3. Acesse no navegador
http://localhost:8501
```

### Comandos úteis

```bash
# Rodar em background
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar
docker-compose down

# Rebuildar após mudar requirements.txt
docker-compose build --no-cache
```