# backend/agents/backend_agent/agent_logic_async.py
"""
Async version of BackendAgent with improved concurrency
"""
import asyncio
import aiohttp
import aiofiles
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from utils.cache_manager import TemplateCache
from utils.rate_limiter import AsyncRateLimiter

class AsyncBackendAgent:
    """Async backend agent for better concurrency"""
    
    def __init__(self):
        self.configure_gemini()
        self.cache = TemplateCache()
        self.rate_limiter = AsyncRateLimiter()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent operations
    
    def configure_gemini(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel(
            'gemini-pro',
            generation_config={
                "temperature": 0.5,
                "top_p": 0.95,
                "max_output_tokens": 4096
            }
        )
    
    async def generate_backend_async(self, description: str, framework: str, 
                                     requirements: List[str], user_id: str = None) -> Dict:
        """
        Async version of generate_backend with rate limiting and concurrency control
        """
        async with self.semaphore:
            # Rate limiting
            if user_id:
                await self.rate_limiter.acquire(f"user_{user_id}")
            
            # Build prompt (non-blocking)
            prompt = await self._build_prompt_async(description, framework, requirements)
            
            # Run Gemini in thread pool (blocking operation)
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                self.executor,
                lambda: self.model.generate_content(prompt)
            )
            
            # Parse response
            result = await self._parse_response_async(response.text)
            
            # Validate in parallel
            validation_tasks = [
                self._validate_syntax_async(result),
                self._validate_dependencies_async(result),
                self._validate_security_async(result)
            ]
            validation_results = await asyncio.gather(*validation_tasks)
            
            return {
                **result,
                'validation': validation_results
            }
    
    async def _build_prompt_async(self, description: str, framework: str, 
                                  requirements: List[str]) -> str:
        """Async prompt building with template loading"""
        # Load templates asynchronously
        templates = await self._load_templates_async(framework)
        
        # Build prompt (CPU bound, but fast)
        return f"""
        Generate production-ready {framework} backend code for:
        {description}
        
        Additional Requirements:
        {', '.join(requirements) if requirements else 'None'}
        
        Base Template:
        {json.dumps(templates['base'], indent=2)}
        """
    
    async def _load_templates_async(self, framework: str) -> Dict:
        """Async template loading with caching"""
        loop = asyncio.get_event_loop()
        
        # Check cache first (non-blocking)
        cached = self.cache.get(f"template_{framework}")
        if cached:
            return cached['data']
        
        # Load from disk in thread pool
        templates = await loop.run_in_executor(
            self.executor,
            self._load_framework_templates,
            framework
        )
        
        # Store in cache
        self.cache.set(f"template_{framework}", templates)
        
        return templates
    
    async def _parse_response_async(self, response_text: str) -> Dict:
        """Async JSON parsing"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            json.loads,
            response_text.strip().removeprefix("```json").removesuffix("```").strip()
        )
    
    async def _validate_syntax_async(self, project: Dict) -> Dict:
        """Async syntax validation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor,
            self._validate_syntax,
            project
        )
    
    async def batch_generate(self, requests: List[Dict]) -> List[Dict]:
        """
        Batch generate multiple projects concurrently
        """
        tasks = []
        for req in requests:
            task = self.generate_backend_async(
                description=req['description'],
                framework=req.get('framework', 'fastapi'),
                requirements=req.get('requirements', []),
                user_id=req.get('user_id')
            )
            tasks.append(task)
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append({
                    'error': str(result),
                    'request': requests[i]
                })
            else:
                final_results.append(result)
        
        return final_results
    
    async def stream_generate(self, description: str, framework: str):
        """
        Stream generation results token by token
        """
        prompt = await self._build_prompt_async(description, framework, [])
        
        # Use streaming response
        response = await self.model.generate_content_async(prompt, stream=True)
        
        async for chunk in response:
            yield chunk.text


# Updated main.py with async endpoints
from fastapi import FastAPI, BackgroundTasks
import asyncio

app = FastAPI()
agent = AsyncBackendAgent()

@app.post('/generate')
async def generate(data: dict, background_tasks: BackgroundTasks):
    """Async endpoint with background processing"""
    job_id = data.get('job_id')
    
    # Start async generation
    background_tasks.add_task(
        agent.generate_backend_async,
        description=data['description'],
        framework=data.get('framework', 'fastapi'),
        requirements=data.get('requirements', [])
    )
    
    return {
        "job_id": job_id,
        "status": "processing"
    }

@app.post('/generate-batch')
async def generate_batch(data: dict):
    """Batch generation endpoint"""
    results = await agent.batch_generate(data['requests'])
    return {"results": results}
