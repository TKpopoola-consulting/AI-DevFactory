# backend/agents/qa_agent/tools/benchmark_tracker.py
"""
Performance benchmarking and regression tracking
"""
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BenchmarkTracker:
    """Track performance benchmarks and detect regressions"""
    
    def __init__(self):
        self.benchmark_db = {}  # In production, this would be a database
        
    async def compare_to_baseline(self, current_results: Dict, baseline: Dict = None) -> Dict[str, Any]:
        """
        Compare current performance to baseline
        
        Args:
            current_results: Current performance results
            baseline: Baseline results (if None, use last run)
            
        Returns:
            Comparison results with regressions
        """
        if baseline is None:
            baseline = await self._get_last_benchmark()
        
        if not baseline:
            return {
                "status": "no_baseline",
                "message": "No baseline found, saving current results as baseline",
                "current": current_results
            }
        
        comparison = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {},
            "regressions": [],
            "improvements": [],
            "overall": "stable"
        }
        
        # Compare metrics
        for metric, current_value in current_results.items():
            if metric in baseline:
                baseline_value = baseline[metric]
                percent_change = ((current_value - baseline_value) / baseline_value) * 100
                
                comparison["metrics"][metric] = {
                    "current": current_value,
                    "baseline": baseline_value,
                    "change": current_value - baseline_value,
                    "percent_change": round(percent_change, 2)
                }
                
                # Detect regressions
                if percent_change > 10:  # More than 10% worse
                    comparison["regressions"].append({
                        "metric": metric,
                        "current": current_value,
                        "baseline": baseline_value,
                        "change": f"+{percent_change:.1f}%",
                        "severity": "HIGH" if percent_change > 20 else "MEDIUM"
                    })
                elif percent_change < -10:  # More than 10% better
                    comparison["improvements"].append({
                        "metric": metric,
                        "current": current_value,
                        "baseline": baseline_value,
                        "change": f"{percent_change:.1f}%",
                        "severity": "GOOD"
                    })
        
        # Determine overall status
        if len(comparison["regressions"]) > 0:
            comparison["overall"] = "regression"
        elif len(comparison["improvements"]) > 0:
            comparison["overall"] = "improved"
        
        return comparison
    
    async def _get_last_benchmark(self) -> Optional[Dict]:
        """Get last benchmark results"""
        # In production, this would query a database
        return None
    
    async def save_benchmark(self, job_id: str, results: Dict) -> Dict[str, Any]:
        """Save benchmark results"""
        benchmark = {
            "job_id": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "results": results
        }
        
        # Save to database
        self.benchmark_db[job_id] = benchmark
        
        return {"status": "saved", "job_id": job_id}
    
    async def generate_trend_graph(self, job_id: str, metric: str, days: int = 30) -> Dict[str, Any]:
        """Generate trend data for graph"""
        # In production, this would fetch historical data
        historical_data = []
        
        # Mock historical data
        for i in range(days):
            historical_data.append({
                "date": (datetime.now() - timedelta(days=days - i)).isoformat(),
                "value": random.uniform(50, 150)  # Mock value
            })
        
        return {
            "job_id": job_id,
            "metric": metric,
            "data": historical_data,
            "trend": "stable"  # Could be "improving", "declining", "stable"
        }
    
    async def detect_anomalies(self, current_results: Dict) -> List[Dict]:
        """Detect anomalies in performance metrics"""
        anomalies = []
        
        # Define typical ranges (in production, these would be learned)
        typical_ranges = {
            "response_time_ms": (50, 500),
            "throughput_rps": (100, 10000),
            "error_rate": (0, 5),
            "memory_usage_mb": (50, 500),
            "cpu_usage": (10, 80)
        }
        
        for metric, value in current_results.items():
            if metric in typical_ranges:
                min_val, max_val = typical_ranges[metric]
                if value < min_val:
                    anomalies.append({
                        "metric": metric,
                        "value": value,
                        "expected_range": (min_val, max_val),
                        "severity": "LOW",
                        "message": f"{metric} is below expected range"
                    })
                elif value > max_val:
                    anomalies.append({
                        "metric": metric,
                        "value": value,
                        "expected_range": (min_val, max_val),
                        "severity": "HIGH",
                        "message": f"{metric} is above expected range"
                    })
        
        return anomalies
