# backend/agents/qa_agent/tools/continuous_tester.py
"""
Continuous testing with file watching
"""
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Callable, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

logger = logging.getLogger(__name__)


class FileChangeHandler(FileSystemEventHandler):
    """Handle file changes and trigger tests"""
    
    def __init__(self, callback: Callable):
        self.callback = callback
        
    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)
    
    def on_created(self, event):
        if not event.is_directory:
            self.callback(event.src_path)


class ContinuousTester:
    """Run tests continuously on file changes"""
    
    def __init__(self):
        self.observers = {}
        self.test_processes = {}
        
    async def watch_and_test(self, job_id: str, code_dir: str, language: str) -> Dict[str, Any]:
        """
        Watch directory and run tests on changes
        
        Args:
            job_id: Job identifier
            code_dir: Directory to watch
            language: Programming language
            
        Returns:
            Status of the watch process
        """
        path = Path(code_dir)
        if not path.exists():
            return {"error": f"Directory not found: {code_dir}"}
        
        # Create event handler
        handler = FileChangeHandler(
            lambda file: asyncio.create_task(self._run_tests(job_id, code_dir, language, file))
        )
        
        # Start observer
        observer = Observer()
        observer.schedule(handler, str(path), recursive=True)
        observer.start()
        
        self.observers[job_id] = observer
        
        # Initial test run
        await self._run_tests(job_id, code_dir, language, "initial")
        
        return {
            "status": "watching",
            "job_id": job_id,
            "directory": str(path),
            "message": f"Watching {path} for changes"
        }
    
    async def _run_tests(self, job_id: str, code_dir: str, language: str, changed_file: str):
        """Run tests when files change"""
        logger.info(f"File changed: {changed_file}, running tests for {job_id}")
        
        try:
            if language == "python":
                result = await self._run_python_tests(code_dir)
            elif language == "javascript":
                result = await self._run_javascript_tests(code_dir)
            else:
                result = {"error": f"Unsupported language: {language}"}
            
            # Store results
            self.test_processes[job_id] = result
            
            # Log results
            if result.get("passed", True):
                logger.info(f"Tests passed for {job_id}")
            else:
                logger.warning(f"Tests failed for {job_id}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"Test execution failed: {e}")
    
    async def _run_python_tests(self, code_dir: str) -> Dict[str, Any]:
        """Run Python tests with pytest-watch"""
        try:
            # Run tests with coverage
            process = await asyncio.create_subprocess_exec(
                "pytest", "--cov=.", "-v",
                cwd=code_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "passed": process.returncode == 0,
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    async def _run_javascript_tests(self, code_dir: str) -> Dict[str, Any]:
        """Run JavaScript tests with Jest watch mode"""
        try:
            process = await asyncio.create_subprocess_exec(
                "npx", "jest", "--watch", "--notify",
                cwd=code_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            return {
                "passed": process.returncode == 0,
                "output": stdout.decode(),
                "error": stderr.decode() if stderr else None,
                "timestamp": asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": str(e)
            }
    
    async def stop_watching(self, job_id: str) -> Dict[str, Any]:
        """Stop watching directory"""
        if job_id in self.observers:
            self.observers[job_id].stop()
            self.observers[job_id].join()
            del self.observers[job_id]
            return {"status": "stopped", "job_id": job_id}
        
        return {"error": f"No watcher found for job: {job_id}"}
    
    async def get_test_results(self, job_id: str) -> Dict[str, Any]:
        """Get latest test results"""
        return self.test_processes.get(job_id, {})
