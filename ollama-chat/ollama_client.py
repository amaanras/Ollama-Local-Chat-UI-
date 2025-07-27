import requests
import json
import time
from typing import List, Dict, Generator, Optional, Tuple
from datetime import datetime
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", timeout: int = 300):
        self.base_url = base_url
        self.timeout = timeout
        self._session = None
        
    def list_models(self) -> List[str]:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        except requests.RequestException:
            return []
    
    def chat_stream(self, model: str, messages: List[Dict], **kwargs) -> Generator[str, None, None]:
        """Stream chat responses from Ollama"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                stream=True,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode('utf-8'))
                    if chunk.get("message", {}).get("content"):
                        yield chunk["message"]["content"]
                        
        except requests.RequestException as e:
            yield f"Error: {str(e)}"
    
    def chat(self, model: str, messages: List[Dict], **kwargs) -> str:
        """Non-streaming chat (for simple cases)"""
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat", 
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except requests.RequestException as e:
            return f"Error: {str(e)}"
    
    def chat_with_metrics(self, model: str, messages: List[Dict], **kwargs) -> Tuple[str, Dict]:
        """Chat with performance metrics"""
        start_time = time.time()
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/chat", 
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            end_time = time.time()
            response_data = response.json()
            
            content = response_data["message"]["content"]
            
            metrics = {
                "response_time": end_time - start_time,
                "model": model,
                "prompt_eval_count": response_data.get("prompt_eval_count", 0),
                "eval_count": response_data.get("eval_count", 0),
                "total_duration": response_data.get("total_duration", 0) / 1e9,  # Convert to seconds
                "load_duration": response_data.get("load_duration", 0) / 1e9,
                "prompt_eval_duration": response_data.get("prompt_eval_duration", 0) / 1e9,
                "eval_duration": response_data.get("eval_duration", 0) / 1e9,
                "tokens_per_second": response_data.get("eval_count", 0) / (response_data.get("eval_duration", 1) / 1e9) if response_data.get("eval_duration", 0) > 0 else 0
            }
            
            return content, metrics
            
        except requests.RequestException as e:
            return f"Error: {str(e)}", {"error": str(e)}
    
    async def chat_async(self, model: str, messages: List[Dict], **kwargs) -> str:
        """Async chat for concurrent requests"""
        if not self._session:
            self._session = aiohttp.ClientSession()
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs
        }
        
        try:
            async with self._session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["message"]["content"]
        except Exception as e:
            return f"Error: {str(e)}"
    
    def compare_models(self, models: List[str], messages: List[Dict], **kwargs) -> Dict[str, str]:
        """Compare responses from multiple models"""
        responses = {}
        
        with ThreadPoolExecutor(max_workers=len(models)) as executor:
            futures = {
                executor.submit(self.chat, model, messages, **kwargs): model 
                for model in models
            }
            
            for future in futures:
                model = futures[future]
                try:
                    response = future.result()
                    responses[model] = response
                except Exception as e:
                    responses[model] = f"Error: {str(e)}"
        
        return responses
    
    def benchmark_model(self, model: str, test_prompt: str = "Hello, how are you?", 
                       iterations: int = 3) -> Dict[str, float]:
        """Benchmark a model's performance"""
        messages = [{"role": "user", "content": test_prompt}]
        metrics_list = []
        
        for _ in range(iterations):
            _, metrics = self.chat_with_metrics(
                model=model,
                messages=messages,
                options={"temperature": 0.7, "num_predict": 100}
            )
            if "error" not in metrics:
                metrics_list.append(metrics)
        
        if not metrics_list:
            return {"error": "All benchmark attempts failed"}
        
        # Calculate averages
        avg_metrics = {
            "model": model,
            "iterations": len(metrics_list),
            "avg_response_time": sum(m["response_time"] for m in metrics_list) / len(metrics_list),
            "avg_tokens_per_second": sum(m["tokens_per_second"] for m in metrics_list) / len(metrics_list),
            "avg_total_duration": sum(m["total_duration"] for m in metrics_list) / len(metrics_list),
            "avg_eval_duration": sum(m["eval_duration"] for m in metrics_list) / len(metrics_list),
        }
        
        return avg_metrics
    
    def get_model_info(self, model_name: str) -> Dict:
        """Get detailed information about a specific model"""
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model_name},
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return {}
    
    def get_model_details(self, model_name: str) -> Dict:
        """Get enhanced model details including size and parameters"""
        info = self.get_model_info(model_name)
        
        if info:
            details = {
                "name": model_name,
                "size": info.get("size", "Unknown"),
                "format": info.get("details", {}).get("format", "Unknown"),
                "family": info.get("details", {}).get("family", "Unknown"),
                "parameter_size": info.get("details", {}).get("parameter_size", "Unknown"),
                "quantization_level": info.get("details", {}).get("quantization_level", "Unknown"),
                "modified_at": info.get("modified_at", "Unknown")
            }
            
            # Extract template if available
            if "template" in info:
                details["template"] = info["template"]
            
            # Extract modelfile if available
            if "modelfile" in info:
                details["modelfile"] = info["modelfile"]
            
            return details
        
        return {"name": model_name, "error": "Could not retrieve model details"}
    
    def unload_model(self, model: str) -> bool:
        """Unload model from memory to free up resources"""
        try:
            requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "keep_alive": 0},
                timeout=30
            )
            return True
        except requests.RequestException:
            return False
    
    def keep_model_loaded(self, model: str, duration: int = 3600) -> bool:
        """Keep a model loaded in memory for specified duration (seconds)"""
        try:
            requests.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "keep_alive": duration},
                timeout=30
            )
            return True
        except requests.RequestException:
            return False
    
    def generate_embeddings(self, model: str, prompt: str) -> Optional[List[float]]:
        """Generate embeddings for a given prompt"""
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={"model": model, "prompt": prompt},
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("embedding")
        except requests.RequestException:
            return None
    
    def is_available(self) -> bool:
        """Check if Ollama server is running"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_server_version(self) -> Optional[str]:
        """Get Ollama server version"""
        try:
            response = requests.get(f"{self.base_url}/api/version", timeout=5)
            response.raise_for_status()
            return response.json().get("version")
        except:
            return None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._session:
            await self._session.close()
            self._session = None