#!/usr/bin/env bash
# ==============================================================================
# Script de Deploy e Inicialização da Plataforma no Cloud (Docker Compose)
# ==============================================================================
set -e

echo "🚀 Iniciando Deploy da Plataforma de Rastreio IoT no Cloud..."

# 1. Verifica se o Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não encontrado! Instale o Docker antes de continuar:"
    echo "   curl -fsSL https://get.docker.com | sh"
    exit 1
fi

# 2. Cria o arquivo .env.cloud se não existir
if [ ! -f .env.cloud ]; then
    echo "📝 Criando .env.cloud a partir de .env.cloud.example..."
    cp .env.cloud.example .env.cloud
    echo "⚠️ Por favor, edite o arquivo .env.cloud com seu DOMAIN e senhas seguras."
fi

# 3. Faz o build e sobe os containers em segundo plano
echo "📦 Construindo imagens e subindo os serviços no Docker..."
docker compose -f docker-compose.cloud.yml up -d --build

echo "✅ Deploy concluído com sucesso!"
echo "🌐 Verifique o status com: docker compose -f docker-compose.cloud.yml ps"
echo "📜 Visualize os logs com:  docker compose -f docker-compose.cloud.yml logs -f"

