#!/usr/bin/env python3
"""
Teste do modelo Qwen pelo OpenRouter para transcrever todos os áudios
e comparar com resultados anteriores.
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

class QwenAudioTester:
    def __init__(self):
        self.openrouter_client = OpenRouterClient()
        self.audio_dir = "/workspaces/whisper/audios"
        self.results_dir = "/workspaces/whisper/results"
        self.models_to_test = {
            "whisper_base": {"type": "whisper", "model": "base"},
            "whisper_small": {"type": "whisper", "model": "small"},
            "qwen_7b": {"type": "openrouter", "model": "qwen-7b"},
            "qwen_32b": {"type": "openrouter", "model": "qwen3-32b"}
        }
        
        # Garantir que diretório de resultados existe
        os.makedirs(self.results_dir, exist_ok=True)
        
    def get_audio_files(self) -> List[str]:
        """Obter todos os arquivos de áudio disponíveis."""
        audio_extensions = ['.ogg', '.mp3', '.wav', '.m4a', '.flac']
        audio_files = []
        
        for file in os.listdir(self.audio_dir):
            if any(file.lower().endswith(ext) for ext in audio_extensions):
                audio_files.append(os.path.join(self.audio_dir, file))
        
        return sorted(audio_files)
    
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
                "confidence": "N/A",
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Erro ao transcrever com Whisper {model_name}: {e}")
            return {
                "text": "",
                "language": "unknown",
                "duration": 0,
                "segments": 0,
                "confidence": 0,
                "status": f"error: {str(e)}"
            }
    
    async def improve_with_qwen(self, text: str, model: str = "qwen3-32b") -> Dict[str, Any]:
        """Melhorar transcrição usando Qwen via OpenRouter."""
        try:
            start_time = time.time()
            improved_text = await self.openrouter_client.improve_transcription(text, model)
            end_time = time.time()
            
            return {
                "improved_text": improved_text,
                "improvement_time": round(end_time - start_time, 2),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Erro ao melhorar com Qwen: {e}")
            return {
                "improved_text": text,
                "improvement_time": 0,
                "status": f"error: {str(e)}"
            }
    
    async def analyze_with_qwen(self, text: str, model: str = "qwen3-32b") -> Dict[str, Any]:
        """Análise completa do texto com Qwen."""
        try:
            # Executar análises em paralelo quando possível
            tasks = [
                self.openrouter_client.summarize_text(text, model),
                self.openrouter_client.analyze_sentiment(text),
                self.improve_with_qwen(text, model)
            ]
            
            summary, sentiment, improvement = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                "summary": summary if not isinstance(summary, Exception) else "Erro ao gerar resumo",
                "sentiment": sentiment if not isinstance(sentiment, Exception) else {"sentiment": "unknown", "confidence": 0},
                "improvement": improvement if not isinstance(improvement, Exception) else {"improved_text": text, "status": "error"}
            }
        except Exception as e:
            logger.error(f"Erro na análise com Qwen: {e}")
            return {
                "summary": "Erro ao gerar resumo",
                "sentiment": {"sentiment": "unknown", "confidence": 0},
                "improvement": {"improved_text": text, "status": "error"}
            }
    
    async def test_single_audio(self, audio_path: str) -> Dict[str, Any]:
        """Testar um único arquivo de áudio com todos os modelos."""
        filename = os.path.basename(audio_path)
        logger.info(f"Processando: {filename}")
        
        result = {
            "filename": filename,
            "file_path": audio_path,
            "file_size": os.path.getsize(audio_path),
            "timestamp": datetime.now().isoformat(),
            "transcriptions": {}
        }
        
        # Testar com Whisper local
        for model_key, model_config in self.models_to_test.items():
            if model_config["type"] == "whisper":
                logger.info(f"  Transcrevendo com {model_key}...")
                transcription = self.transcribe_with_whisper(audio_path, model_config["model"])
                result["transcriptions"][model_key] = transcription
        
        # Melhorar transcrições existentes com Qwen
        for model_key, model_config in self.models_to_test.items():
            if model_config["type"] == "openrouter":
                logger.info(f"  Melhorando transcrições com {model_key}...")
                
                # Usar a melhor transcrição disponível como base
                base_text = ""
                if "whisper_small" in result["transcriptions"]:
                    base_text = result["transcriptions"]["whisper_small"]["text"]
                elif "whisper_base" in result["transcriptions"]:
                    base_text = result["transcriptions"]["whisper_base"]["text"]
                
                if base_text:
                    # Análise completa com Qwen
                    analysis = await self.analyze_with_qwen(base_text, model_config["model"])
                    
                    result["transcriptions"][model_key] = {
                        "base_text": base_text,
                        "improved_text": analysis["improvement"]["improved_text"],
                        "summary": analysis["summary"],
                        "sentiment": analysis["sentiment"],
                        "improvement_time": analysis["improvement"].get("improvement_time", 0),
                        "status": analysis["improvement"]["status"]
                    }
        
        return result
    
    async def test_all_audios(self) -> List[Dict[str, Any]]:
        """Testar todos os arquivos de áudio disponíveis."""
        audio_files = self.get_audio_files()
        logger.info(f"Encontrados {len(audio_files)} arquivos de áudio para testar")
        
        results = []
        
        for audio_file in audio_files:
            try:
                result = await self.test_single_audio(audio_file)
                results.append(result)
                
                # Salvar resultado individual
                individual_filename = f"qwen_test_{os.path.basename(audio_file)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                individual_path = os.path.join(self.results_dir, individual_filename)
                
                with open(individual_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Resultado salvo: {individual_path}")
                
            except Exception as e:
                logger.error(f"Erro ao processar {audio_file}: {e}")
                continue
        
        return results
    
    def save_consolidated_results(self, results: List[Dict[str, Any]]):
        """Salvar resultados consolidados."""
        # Salvar JSON completo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f"qwen_complete_results_{timestamp}.json"
        json_path = os.path.join(self.results_dir, json_filename)
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados JSON salvos: {json_path}")
        
        # Criar CSV para análise
        csv_data = []
        for result in results:
            base_row = {
                "filename": result["filename"],
                "file_size": result["file_size"],
                "timestamp": result["timestamp"]
            }
            
            for model_key, transcription in result["transcriptions"].items():
                row = base_row.copy()
                row["model"] = model_key
                
                if model_key.startswith("whisper"):
                    row["text"] = transcription.get("text", "")
                    row["language"] = transcription.get("language", "")
                    row["duration"] = transcription.get("duration", 0)
                    row["segments"] = transcription.get("segments", 0)
                    row["status"] = transcription.get("status", "")
                    row["type"] = "whisper_original"
                elif model_key.startswith("qwen"):
                    row["text"] = transcription.get("improved_text", "")
                    row["base_text"] = transcription.get("base_text", "")
                    row["summary"] = transcription.get("summary", "")
                    row["sentiment"] = json.dumps(transcription.get("sentiment", {}))
                    row["improvement_time"] = transcription.get("improvement_time", 0)
                    row["status"] = transcription.get("status", "")
                    row["type"] = "qwen_improved"
                
                csv_data.append(row)
        
        # Salvar CSV
        csv_filename = f"qwen_results_analysis_{timestamp}.csv"
        csv_path = os.path.join(self.results_dir, csv_filename)
        
        df = pd.DataFrame(csv_data)
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        logger.info(f"Análise CSV salva: {csv_path}")
        
        return json_path, csv_path
    
    def generate_comparison_report(self, results: List[Dict[str, Any]]) -> str:
        """Gerar relatório de comparação."""
        report = []
        report.append("# Relatório de Teste - Qwen vs Whisper")
        report.append(f"Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report.append(f"Arquivos testados: {len(results)}")
        report.append("")
        
        # Estatísticas gerais
        whisper_models = [k for k in self.models_to_test.keys() if k.startswith("whisper")]
        qwen_models = [k for k in self.models_to_test.keys() if k.startswith("qwen")]
        
        report.append("## Modelos Testados")
        report.append("### Whisper (Transcrição Original)")
        for model in whisper_models:
            report.append(f"- {model}")
        
        report.append("### Qwen (Melhoria via OpenRouter)")
        for model in qwen_models:
            model_info = self.models_to_test[model]
            report.append(f"- {model} ({model_info['model']})")
        
        report.append("")
        
        # Análise por arquivo
        report.append("## Resultados por Arquivo")
        for result in results:
            filename = result["filename"]
            report.append(f"### {filename}")
            report.append(f"Tamanho: {result['file_size']:,} bytes")
            
            # Comparar transcrições
            for model_key, transcription in result["transcriptions"].items():
                if model_key.startswith("whisper"):
                    text = transcription.get("text", "")[:100] + "..." if len(transcription.get("text", "")) > 100 else transcription.get("text", "")
                    duration = transcription.get("duration", 0)
                    report.append(f"**{model_key}** ({duration}s): {text}")
                
                elif model_key.startswith("qwen"):
                    improved = transcription.get("improved_text", "")[:100] + "..." if len(transcription.get("improved_text", "")) > 100 else transcription.get("improved_text", "")
                    summary = transcription.get("summary", "")[:100] + "..." if len(transcription.get("summary", "")) > 100 else transcription.get("summary", "")
                    sentiment = transcription.get("sentiment", {})
                    improvement_time = transcription.get("improvement_time", 0)
                    
                    report.append(f"**{model_key}** ({improvement_time}s):")
                    report.append(f"  - Texto melhorado: {improved}")
                    report.append(f"  - Resumo: {summary}")
                    report.append(f"  - Sentimento: {sentiment.get('sentiment', 'unknown')} (conf: {sentiment.get('confidence', 0)})")
            
            report.append("")
        
        return "\n".join(report)

async def main():
    """Função principal para executar todos os testes."""
    logger.info("Iniciando teste completo com modelo Qwen...")
    
    tester = QwenAudioTester()
    
    try:
        # Executar testes
        results = await tester.test_all_audios()
        
        # Salvar resultados
        json_path, csv_path = tester.save_consolidated_results(results)
        
        # Gerar relatório
        report = tester.generate_comparison_report(results)
        report_filename = f"qwen_comparison_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path = os.path.join(tester.results_dir, report_filename)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        logger.info(f"Relatório salvo: {report_path}")
        
        # Resumo final
        print(f"\n{'='*60}")
        print("TESTE CONCLUÍDO COM SUCESSO!")
        print(f"{'='*60}")
        print(f"Arquivos testados: {len(results)}")
        print(f"Resultados JSON: {json_path}")
        print(f"Análise CSV: {csv_path}")
        print(f"Relatório: {report_path}")
        print(f"{'='*60}")
        
        # Mostrar resumo dos resultados
        for result in results[:3]:  # Mostrar apenas os 3 primeiros
            filename = result["filename"]
            print(f"\n📁 {filename}:")
            
            for model_key, transcription in result["transcriptions"].items():
                if model_key.startswith("whisper"):
                    text = transcription.get("text", "")[:80] + "..." if len(transcription.get("text", "")) > 80 else transcription.get("text", "")
                    print(f"  🎵 {model_key}: {text}")
                elif model_key.startswith("qwen"):
                    improved = transcription.get("improved_text", "")[:80] + "..." if len(transcription.get("improved_text", "")) > 80 else transcription.get("improved_text", "")
                    print(f"  🤖 {model_key}: {improved}")
        
        if len(results) > 3:
            print(f"\n... e mais {len(results) - 3} arquivos processados.")
        
    except Exception as e:
        logger.error(f"Erro durante execução: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())