# backend/agents/infra_agent/utils/cost_calculator.py
"""
Cost estimation for infrastructure resources
"""
import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CostCalculator:
    """Calculate infrastructure costs for various cloud providers"""
    
    def __init__(self):
        self.cache = {}
        self.azure_pricing_api = "https://prices.azure.com/api/retail/prices"
        self.aws_pricing_api = "https://api.pricing.us-east-1.amazonaws.com"
        
    async def calculate_cost(self, templates: Dict[str, str], cloud: str, services: List[str]) -> Dict[str, Any]:
        """Calculate cost estimate for infrastructure"""
        
        if cloud == "azure":
            return await self._calculate_azure_cost(templates, services)
        elif cloud == "aws":
            return await self._calculate_aws_cost(templates, services)
        elif cloud == "gcp":
            return await self._calculate_gcp_cost(templates, services)
        else:
            return {"error": f"Unsupported cloud provider: {cloud}"}
    
    async def _calculate_azure_cost(self, templates: Dict[str, str], services: List[str]) -> Dict[str, Any]:
        """Calculate Azure costs"""
        cost_breakdown = {}
        total_monthly = 0
        
        for service in services:
            if service == "compute" or service == "app_service":
                cost = await self._get_azure_app_service_cost()
                cost_breakdown["App Service"] = cost
                total_monthly += cost
                
            elif service == "database":
                cost = await self._get_azure_database_cost()
                cost_breakdown["Database"] = cost
                total_monthly += cost
                
            elif service == "storage":
                cost = await self._get_azure_storage_cost()
                cost_breakdown["Storage"] = cost
                total_monthly += cost
                
            elif service == "monitoring":
                cost = await self._get_azure_monitoring_cost()
                cost_breakdown["Monitoring"] = cost
                total_monthly += cost
                
            elif service == "networking":
                cost = await self._get_azure_networking_cost()
                cost_breakdown["Networking"] = cost
                total_monthly += cost
        
        return {
            "cloud_provider": "azure",
            "total_monthly": round(total_monthly, 2),
            "total_yearly": round(total_monthly * 12, 2),
            "breakdown": cost_breakdown,
            "currency": "USD",
            "calculated_at": datetime.utcnow().isoformat(),
            "notes": [
                "Costs are estimates based on standard pricing",
                "Actual costs may vary based on usage and region",
                "Consider using reserved instances for production workloads"
            ]
        }
    
    async def _get_azure_app_service_cost(self) -> float:
        """Get App Service cost estimate"""
        # B1 tier: ~$13/month
        return 13.00
    
    async def _get_azure_database_cost(self) -> float:
        """Get Database cost estimate"""
        # Cosmos DB: ~$25/month for standard tier
        return 25.00
    
    async def _get_azure_storage_cost(self) -> float:
        """Get Storage cost estimate"""
        # Standard LRS: ~$0.021/GB/month * 100GB
        return 2.10
    
    async def _get_azure_monitoring_cost(self) -> float:
        """Get Monitoring cost estimate"""
        # Application Insights: ~$2.50/month
        return 2.50
    
    async def _get_azure_networking_cost(self) -> float:
        """Get Networking cost estimate"""
        # Basic VNet: ~$1.50/month
        return 1.50
    
    async def _calculate_aws_cost(self, templates: Dict[str, str], services: List[str]) -> Dict[str, Any]:
        """Calculate AWS costs"""
        cost_breakdown = {}
        total_monthly = 0
        
        for service in services:
            if service == "compute":
                cost = 15.00  # t3.micro: ~$15/month
                cost_breakdown["ECS/Fargate"] = cost
                total_monthly += cost
                
            elif service == "database":
                cost = 18.00  # db.t3.micro: ~$18/month
                cost_breakdown["RDS"] = cost
                total_monthly += cost
                
            elif service == "storage":
                cost = 2.50  # S3: ~$0.023/GB * 100GB
                cost_breakdown["S3"] = cost
                total_monthly += cost
                
            elif service == "networking":
                cost = 3.00  # VPC + NAT Gateway
                cost_breakdown["VPC"] = cost
                total_monthly += cost
        
        return {
            "cloud_provider": "aws",
            "total_monthly": round(total_monthly, 2),
            "total_yearly": round(total_monthly * 12, 2),
            "breakdown": cost_breakdown,
            "currency": "USD",
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    async def _calculate_gcp_cost(self, templates: Dict[str, str], services: List[str]) -> Dict[str, Any]:
        """Calculate GCP costs"""
        cost_breakdown = {}
        total_monthly = 0
        
        for service in services:
            if service == "compute":
                cost = 12.00  # Cloud Run: ~$12/month
                cost_breakdown["Cloud Run"] = cost
                total_monthly += cost
                
            elif service == "database":
                cost = 20.00  # Cloud SQL: ~$20/month
                cost_breakdown["Cloud SQL"] = cost
                total_monthly += cost
                
            elif service == "storage":
                cost = 2.50  # Cloud Storage: ~$0.02/GB * 100GB
                cost_breakdown["Cloud Storage"] = cost
                total_monthly += cost
        
        return {
            "cloud_provider": "gcp",
            "total_monthly": round(total_monthly, 2),
            "total_yearly": round(total_monthly * 12, 2),
            "breakdown": cost_breakdown,
            "currency": "USD",
            "calculated_at": datetime.utcnow().isoformat()
        }
    
    async def get_cost_comparison(self, services: List[str]) -> Dict[str, Any]:
        """Compare costs across cloud providers"""
        comparison = {}
        
        for cloud in ["azure", "aws", "gcp"]:
            cost = await self.calculate_cost({}, cloud, services)
            comparison[cloud] = {
                "total_monthly": cost["total_monthly"],
                "breakdown": cost["breakdown"]
            }
        
        return {
            "services": services,
            "comparison": comparison,
            "recommendation": min(comparison.items(), key=lambda x: x[1]["total_monthly"])[0],
            "calculated_at": datetime.utcnow().isoformat()
        }
