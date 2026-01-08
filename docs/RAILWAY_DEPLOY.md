# 🚂 Railway Deployment Guide - Whisper Enhanced

## 🚀 Deploy Rápido (Recomendado)

### Método 1: Script Automático
```bash
# Torna o script executável e roda
chmod +x deploy-railway.sh
./deploy-railway.sh
```

### Método 2: Manual Railway CLI
```bash
# Instala Railway CLI
curl -fsSL https://railway.app/install.sh | sh

# Login no Railway
railway login

# Cria projeto (primeira vez)
railway project create whisper-enhanced

# Deploy
railway deploy --dockerfile Dockerfile.railway
```

### Método 3: GitHub Integration (Mais Fácil)
1. 📤 **Push para GitHub**: Faça push deste repositório
2. 🌐 **Acesse Railway.app**: Entre no painel
3. ➕ **New Project**: Clique em "Deploy from GitHub repo"
4. 🔗 **Conecte o repo**: Selecione este repositório
5. ✅ **Deploy automático**: Railway detecta e deploya automaticamente!

## ⚙️ Configurações de Produção

### Variáveis de Ambiente (já configuradas)
```bash
PORT=8000                           # Porta padrão Railway
WHISPER_MODEL=base                  # Modelo otimizado
COMPRESSION_RATIO_THRESHOLD=1.8     # Anti-repetição
CONDITION_ON_PREVIOUS_TEXT=false    # Anti-erro
CLEAN_REPETITIONS=true              # Limpeza automática
APPLY_CORRECTIONS=true              # Correções automáticas
MAX_FILE_SIZE=26214400             # 25MB limite
```

### Health Check
- ✅ **Endpoint**: `GET /health`
- ✅ **Intervalo**: 30s
- ✅ **Timeout**: 30s
- ✅ **Retries**: 3

## 📊 Monitoramento

### Verificar Status
```bash
railway status
```

### Ver Logs em Tempo Real
```bash
railway logs --tail
```

### Abrir App no Browser
```bash
railway open
```

## 🎯 Endpoints Disponíveis

### Transcrição Principal
```bash
POST https://your-app.railway.app/transcribe
```

### Health Check
```bash
GET https://your-app.railway.app/health
```

### Modelos Disponíveis
```bash
GET https://your-app.railway.app/models
```

## 📱 Exemplo de Uso

### Curl
```bash
curl -X POST "https://your-app.railway.app/transcribe" \
  -F "file=@audio.mp3" \
  -F "model=base" \
  -F "clean_repetitions=true" \
  -F "compression_ratio_threshold=1.8"
```

### JavaScript
```javascript
const formData = new FormData();
formData.append('file', audioFile);
formData.append('model', 'base');
formData.append('clean_repetitions', 'true');

const response = await fetch('https://your-app.railway.app/transcribe', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result.text);
```

### Python
```python
import requests

url = "https://your-app.railway.app/transcribe"
files = {'file': open('audio.mp3', 'rb')}
data = {
    'model': 'base',
    'clean_repetitions': 'true',
    'compression_ratio_threshold': '1.8'
}

response = requests.post(url, files=files, data=data)
result = response.json()
print(result['text'])
```

## 🔧 Customização

### Alterar Modelo
```bash
railway variables set WHISPER_MODEL=tiny  # Mais rápido
railway variables set WHISPER_MODEL=small # Mais preciso
```

### Ajustar Limite de Arquivo
```bash
railway variables set MAX_FILE_SIZE=52428800  # 50MB
```

### Configurar CORS
```bash
railway variables set CORS_ORIGINS="https://meusite.com,https://app.exemplo.com"
```

## 📊 Custos Estimados

### Railway Pricing
- **Starter Plan**: $5/mês (512MB RAM, suficiente para modelo base)
- **Developer Plan**: $10/mês (1GB RAM, recomendado)
- **Team Plan**: $20/mês (2GB RAM, para modelo large)

### Uso Estimado
- **Modelo Base**: ~500MB RAM por instância
- **Processamento**: ~5-10s por áudio (15s)
- **Transferência**: Incluída no plano

## 🚨 Troubleshooting

### Deploy Falha
```bash
# Verifica logs de build
railway logs --deployment

# Força rebuild
railway deploy --dockerfile Dockerfile.railway --force
```

### API Lenta
```bash
# Monitora recursos
railway metrics

# Considera upgrade de plano se RAM < 1GB
```

### Limite de Arquivo
```bash
# Railway tem limite de 25MB por request por padrão
# Configurado em MAX_FILE_SIZE
```

## ✅ Checklist de Deploy

- [ ] 📤 Código no GitHub
- [ ] 🔧 railway.toml configurado
- [ ] 🐳 Dockerfile.railway testado
- [ ] ⚙️ Variáveis de ambiente definidas
- [ ] 🚀 Deploy realizado
- [ ] ✅ Health check funcionando
- [ ] 📊 Teste de transcrição OK
- [ ] 📋 Logs sem erros
- [ ] 🎯 Performance aceitável

## 🎯 Próximos Passos

### Após Deploy
1. **Teste a API** com áudios reais
2. **Configure domínio customizado** (se necessário)
3. **Monitore logs** nas primeiras horas
4. **Ajuste variáveis** conforme performance
5. **Configure alertas** para downtime

### Otimizações
- **CDN**: Para cache de respostas
- **Load Balancer**: Para múltiplas instâncias
- **Database**: Para logs de transcrições
- **Webhooks**: Para notificações

## 📚 Recursos Úteis

- 🌐 **Railway Docs**: https://docs.railway.app
- 📊 **Dashboard**: https://railway.app/dashboard
- 💬 **Support**: https://help.railway.app
- 📱 **Status**: https://status.railway.app

---

**🏆 Status**: ✅ Ready for Production
**🚀 Recommended Plan**: Developer ($10/mês)
**📊 Performance**: Base model ~6s avg response