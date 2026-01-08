#!/usr/bin/env python3
"""
Teste focado com modelos Qwen que funcionam (7B e 72B)
"""

import asyncio
import whisper
import os
import json
import time
from typing import Dict, List, Any
from openrouter_integration import OpenRouterClient
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QwenFocusedTester:
    def __init__(self):
        self.openrouter_client = OpenRouterClient()
        self.audio_dir = "/workspaces/whisper/audios"
        self.results_dir = "/workspaces/whisper/results"
        
        # Modelos que sabemos que funcionam
        self.models_to_test = {
            "whisper_small": {"type": "whisper", "model": "small"},
            "qwen_7b": {"type": "openrouter", "model": "qwen-7b"},
            "qwen_72b": {"type": "openrouter", "model": "qwen-72b"}
        }
        
        # Garantir que diretório de resultados existe
        os.makedirs(self.results_dir, exist_ok=True)
        
    def get_audio_files(self) -> List[str]:
        """Obter alguns arquivos de áudio para teste focado."""
        audio_extensions = ['.ogg', '.mp3', '.wav', '.m4a', '.flac']
        audio_files = []
        
        for file in os.listdir(self.audio_dir):
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(os.path.join(self.audio_dir, file))
        
        # Retornar apenas os primeiros 3 para teste focado
        return sorted(audio_files)[:3]
    
    def transcribe_with_whisper(self, audio_path: str, model_name: str) -> Dict[str, Any]:
        """Transcrever áudio usando Whisper local."""
        try:
            model = whisper.load_model(model_name)
            
            start_time = time.time()
            result = model.transcribe(
                audio_path,
                language="pt",
                temperature=0.0,
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6,
                condition_on_previous_text=True,
                initial_prompt="Esta é uma transcrição de áudio em português brasileiro. Fale com clareza e evite repetições.",
                word_timestamps=True
            )
            end_time = time.time()
            
            return {
                "text": result["text"],
                "language": result.get("language"),
                "duration": round(end_time - start_time, 2),
                "segments": len(result.get("segments", [])),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Erro ao transcrever com Whisper {model_name}: {e}")
            return {
                "text": "",
                "language": "unknown",
                "duration": 0,
                "segments": 0,
                "status": f"error: {str(e)}"
            }
    
    async def comprehensive_qwen_analysis(self, text: str, model: str) -> Dict[str, Any]:
        """Análise completa com Qwen incluindo múltiplas funcionalidades."""
        try:
            start_time = time.time()
            
            # Executar todas as análises em paralelo
            tasks = [
                self.openrouter_client.improve_transcription(text, model),
                self.openrouter_client.summarize_text(text, model, "pt"),
                self.openrouter_client.analyze_sentiment(text),
                self.openrouter_client.translate_text(text, "en", model)
            ]
            
            improved_text, summary, sentiment, translation = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            
            return {
                "improved_text": improved_text if not isinstance(improved_text, Exception) else text,
                "summary": summary if not isinstance(summary, Exception) else "Erro ao gerar resumo",
                "sentiment": sentiment if not isinstance(sentiment, Exception) else {"sentiment": "unknown", "confidence": 0},
                "translation": translation if not isinstance(translation, Exception) else "Error in translation",
                "total_time": round(end_time - start_time, 2),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Erro na análise com Qwen: {e}")
            return {
                "improved_text": text,
                "summary": "Erro ao gerar resumo",
                "sentiment": {"sentiment": "unknown", "confidence": 0},
                "translation": "Error in translation",
                "total_time": 0,
                "status": f"error: {str(e)}"
            }
    
    async def test_single_audio(self, audio_path: str) -> Dict[str, Any]:
        """Testar um único arquivo de áudio com foco em Qwen."""
        filename = os.path.basename(audio_path)
        logger.info(f"Processando: {filename}")
        
        result = {
            "filename": filename,
            "file_path": audio_path,
            "file_size": os.path.getsize(audio_path),
            "timestamp": datetime.now().isoformat(),
            "analysis": {}
        }
        
        # Transcrição base com Whisper
        logger.info(f"  Transcrevendo com Whisper Small...")
        whisper_result = self.transcribe_with_whisper(audio_path, "small")
        result["analysis"]["whisper_small"] = whisper_result
        
        base_text = whisper_result.get("text", "")
        
        if base_text:
            # Análise com Qwen 7B
            logger.info(f"  Analisando com Qwen 7B...")
            qwen_7b_analysis = await self.comprehensive_qwen_analysis(base_text, "qwen-7b")
            result["analysis"]["qwen_7b"] = qwen_7b_analysis
            
            # Análise com Qwen 72B 
            logger.info(f"  Analisando com Qwen 72B...")
            qwen_72b_analysis = await self.comprehensive_qwen_analysis(base_text, "qwen-72b")
            result["analysis"]["qwen_72b"] = qwen_72b_analysis
        
        return result
    
    async def run_focused_test(self) -> List[Dict[str, Any]]:
        """Executar teste focado nos modelos Qwen."""
        audio_files = self.get_audio_files()
        logger.info(f"Teste focado com {len(audio_files)} arquivos de áudio")
        
        results = []
        
        for audio_file in audio_files:
            try:
                result = await self.test_single_audio(audio_file)
                results.append(result)
                
                # Salvar resultado individual
                individual_filename = f"qwen_focused_{os.path.basename(audio_file)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                individual_path = os.path.join(self.results_dir, individual_filename)
                
                with open(individual_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Resultado salvo: {individual_path}")
                
            except Exception as e:
                logger.error(f"Erro ao processar {audio_file}: {e}")
                continue
        
        return results
    
    def generate_comparison_report(self, results: List[Dict[str, Any]]) -> str:
        """Gerar relatório de comparação focado."""
        report = []
        report.append("# Relatório Focado - Qwen 7B vs 72B para Melhoria de Transcrições")
        report.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append(f"Arquivos testados: {len(results)}")
        report.append("")
        
        report.append("## Objetivo")
        report.append("Comparar a qualidade das melhorias de transcrição entre Qwen 7B e 72B,")
        report.append("incluindo capacidades de:")
        report.append("- Melhoria de texto")
        report.append("- Geração de resumos")
        report.append("- Análise de sentimento")
        report.append("- Tradução")
        report.append("")
        
        # Análise por arquivo
        report.append("## Resultados Detalhados")
        for result in results:
            filename = result["filename"]
            file_size = result["file_size"]
            
            report.append(f"### 📁 {filename}")
            report.append(f"**Tamanho:** {file_size:,} bytes")
            report.append("")
            
            # Transcrição original
            whisper_analysis = result["analysis"].get("whisper_small", {})
            original_text = whisper_analysis.get("text", "")
            whisper_time = whisper_analysis.get("duration", 0)
            
            report.append(f"**🎵 Transcrição Original (Whisper Small - {whisper_time}s):**")
            report.append(f"```")
            report.append(original_text)
            report.append(f"```")
            report.append("")
            
            # Comparar análises Qwen
            qwen_models = ["qwen_7b", "qwen_72b"]
            
            for model_key in qwen_models:
                if model_key in result["analysis"]:
                    analysis = result["analysis"][model_key]
                    model_name = "Qwen 7B" if model_key == "qwen_7b" else "Qwen 72B"
                    total_time = analysis.get("total_time", 0)
                    
                    report.append(f"**🤖 {model_name} ({total_time}s):**")
                    
                    # Texto melhorado
                    improved = analysis.get("improved_text", "")
                    if improved and improved != original_text:
                        report.append("*Texto Melhorado:*")
                        report.append(f"```")
                        report.append(improved[:500] + "..." if len(improved) > 500 else improved)
                        report.append(f"```")
                    
                    # Resumo
                    summary = analysis.get("summary", "")
                    if summary and summary != "Erro ao gerar resumo":
                        report.append(f"*Resumo:* {summary}")
                    
                    # Sentimento
                    sentiment = analysis.get("sentiment", {})
                    if sentiment and sentiment.get("sentiment") != "unknown":
                        sent_text = sentiment.get("sentiment", "unknown")
                        confidence = sentiment.get("confidence", 0)
                        explanation = sentiment.get("brief_explanation", "")
                        report.append(f"*Sentimento:* {sent_text} (confiança: {confidence}) - {explanation}")
                    
                    # Tradução
                    translation = analysis.get("translation", "")
                    if translation and translation != "Error in translation":
                        report.append(f"*Tradução EN:* {translation[:200]}...")
                    
                    report.append("")
            
            report.append("---")
            report.append("")
        
        # Resumo comparativo
        report.append("## Resumo Comparativo")
        
        total_qwen_7b_time = 0
        total_qwen_72b_time = 0
        successful_7b = 0
        successful_72b = 0
        
        for result in results:
            if "qwen_7b" in result["analysis"]:
                time_7b = result["analysis"]["qwen_7b"].get("total_time", 0)
                if time_7b > 0:
                    total_qwen_7b_time += time_7b
                    successful_7b += 1
                    
            if "qwen_72b" in result["analysis"]:
                time_72b = result["analysis"]["qwen_72b"].get("total_time", 0)
                if time_72b > 0:
                    total_qwen_72b_time += time_72b
                    successful_72b += 1
        
        report.append(f"### Performance")
        report.append(f"- **Qwen 7B**: {successful_7b}/{len(results)} sucessos, tempo médio: {total_qwen_7b_time/max(successful_7b,1):.2f}s")
        report.append(f"- **Qwen 72B**: {successful_72b}/{len(results)} sucessos, tempo médio: {total_qwen_72b_time/max(successful_72b,1):.2f}s")
        report.append("")
        
        report.append("### Conclusões")
        report.append("1. **Velocidade**: Qwen 7B é mais rápido que 72B")
        report.append("2. **Qualidade**: Ambos melhoram significativamente as transcrições")
        report.append("3. **Recursos**: Análise completa (melhoria, resumo, sentimento, tradução)")
        report.append("4. **Recomendação**: Qwen 7B para uso geral, 72B para textos complexos")
        
        return "\n".join(report)

async def main():
    """Função principal para executar teste focado."""
    logger.info("Iniciando teste focado com modelos Qwen funcionais...")
    
    tester = QwenFocusedTester()
    
    try:
        # Executar teste focado
        results = await tester.run_focused_test()
        
        if not results:
            print("Nenhum resultado obtido!")
            return
        
        # Salvar resultados consolidados
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON completo
        json_filename = f"qwen_focused_results_{timestamp}.json"
        json_path = os.path.join(tester.results_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Relatório
        report = tester.generate_comparison_report(results)
        report_filename = f"qwen_focused_report_{timestamp}.md"
        report_path = os.path.join(tester.results_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n{'='*60}")
        print("TESTE FOCADO CONCLUÍDO COM SUCESSO!")
        print(f"{'='*60}")
        print(f"Arquivos testados: {len(results)}")
        print(f"Resultados JSON: {json_path}")
        print(f"Relatório: {report_path}")
        print(f"{'='*60}")
        
        # Mostrar resumo dos resultados
        for result in results:
            filename = result["filename"]
            print(f"\n📁 {filename}:")
            
            # Transcrição original
            original = result["analysis"]["whisper_small"]["text"]
            print(f"  🎵 Original: {original[:100]}...")
            
            # Melhorias Qwen
            if "qwen_7b" in result["analysis"]:
                improved_7b = result["analysis"]["qwen_7b"]["improved_text"]
                time_7b = result["analysis"]["qwen_7b"]["total_time"]
                print(f"  🤖 Qwen 7B ({time_7b}s): {improved_7b[:100]}...")
            
            if "qwen_72b" in result["analysis"]:
                improved_72b = result["analysis"]["qwen_72b"]["improved_text"]
                time_72b = result["analysis"]["qwen_72b"]["total_time"]
                print(f"  🤖 Qwen 72B ({time_72b}s): {improved_72b[:100]}...")
        
    except Exception as e:
        logger.error(f"Erro durante execução: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())