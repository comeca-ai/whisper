// Exemplo de uso da API Whisper com JavaScript/Node.js
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

const API_URL = 'https://laughing-eureka-pj9j5j55x6vwh6797-8000.app.github.dev';

// ========================================
// Exemplo 1: Transcrição simples
// ========================================
async function transcricaoSimples(caminhoArquivo) {
    const form = new FormData();
    form.append('file', fs.createReadStream(caminhoArquivo));

    try {
        const response = await axios.post(`${API_URL}/transcribe-simple`, form, {
            headers: form.getHeaders()
        });

        console.log('✅ Transcrição concluída!');
        console.log('Texto:', response.data.text);
        console.log('Idioma:', response.data.language);
        return response.data;
    } catch (error) {
        console.error('❌ Erro:', error.response?.data || error.message);
    }
}

// ========================================
// Exemplo 2: Transcrição com opções
// ========================================
async function transcricaoCompleta(caminhoArquivo, opcoes = {}) {
    const form = new FormData();
    form.append('file', fs.createReadStream(caminhoArquivo));
    form.append('model', opcoes.model || 'base');
    form.append('language', opcoes.language || 'pt');
    form.append('task', opcoes.task || 'transcribe');

    try {
        const response = await axios.post(`${API_URL}/transcribe`, form, {
            headers: form.getHeaders()
        });

        console.log('✅ Transcrição concluída!');
        console.log('Texto:', response.data.text);
        console.log('\nSegmentos:');
        response.data.segments.forEach(seg => {
            console.log(`  [${seg.start.toFixed(1)}s - ${seg.end.toFixed(1)}s] ${seg.text}`);
        });
        return response.data;
    } catch (error) {
        console.error('❌ Erro:', error.response?.data || error.message);
    }
}

// ========================================
// Uso
// ========================================
if (require.main === module) {
    const arquivo = process.argv[2];
    
    if (!arquivo) {
        console.log('Uso: node exemplo_uso_api.js <arquivo_audio>');
        process.exit(1);
    }

    transcricaoSimples(arquivo);
}

module.exports = { transcricaoSimples, transcricaoCompleta };
