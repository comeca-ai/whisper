# 🚂 Railway Quick Start - Whisper Enhanced

## ⚡ Deploy em 3 Passos

### 1️⃣ **GitHub Integration (MAIS FÁCIL)**
```bash
# 1. Push este código para seu GitHub
git add .
git commit -m "Railway ready Whisper Enhanced API"
git push origin main

# 2. Vá para Railway.app
# 3. Clique "Deploy from GitHub repo"
# 4. Selecione este repositório
# 5. ✅ Deploy automático!
```

### 2️⃣ **CLI Deploy (RÁPIDO)**
```bash
# Execute o script automático
./deploy-railway.sh
```

### 3️⃣ **Manual CLI**
```bash
# Instala Railway CLI se não tiver
curl -fsSL https://railway.app/install.sh | sh

# Login e deploy
railway login
railway deploy --dockerfile Dockerfile.railway
```

## 🎯 Sua API Ficará Disponível Em

- **Health Check**: `GET https://seu-app.railway.app/health`
- **Transcrição**: `POST https://seu-app.railway.app/transcribe`
- **Modelos**: `GET https://seu-app.railway.app/models`

## 🔥 Teste Rápido

```bash
# Assim que o deploy terminar:
curl -X POST "https://seu-app.railway.app/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "clean_repetitions=true"
```

## 📊 Configurações Otimizadas (Já Definidas)

✅ **Modelo**: base (melhor custo-benefício)  
✅ **Anti-repetição**: 1.8 threshold  
✅ **Limpeza automática**: habilitada  
✅ **Correções**: glossário ativado  
✅ **Health check**: configurado  
✅ **Port**: 8000 (Railway padrão)  

## 💰 Custo Estimado

- **Starter**: $5/mês (suficiente para testes)
- **Developer**: $10/mês (recomendado para produção)
- **Processamento**: ~6s por áudio de 15s

## 🚨 Problemas Comuns

### Build Falhou?
- Verifique se `Dockerfile.railway` existe
- Logs: `railway logs --deployment`

### API Não Responde?
- Aguarde ~2min para build completo  
- Verifique: `railway status`

### Out of Memory?
- Considere upgrade para Developer plan ($10)

---

**🏆 RESULTADO**: Sua API Whisper otimizada rodando em produção!

**📚 Documentação completa**: [RAILWAY_DEPLOY.md](docs/RAILWAY_DEPLOY.md)