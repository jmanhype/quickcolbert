import logging
import os
import httpx
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class RunpodClient:
    def __init__(self):
        self.api_key = os.environ.get("RUNPOD_API_KEY")
        self.api_url = "https://api.runpod.io/v1"
        
    async def create_pod(self, gpu_type: str, docker_image: str, environment_variables: Optional[Dict[str, str]] = None):
        """Create a new pod with the specified GPU and Docker image"""
        if not self.api_key:
            logger.error("RUNPOD_API_KEY environment variable not set")
            raise ValueError("RUNPOD_API_KEY environment variable not set")
            
        logger.info(f"Creating pod with GPU {gpu_type} and image {docker_image}")
        
        payload = {
            "name": f"colbertv2-{int(time.time())}",
            "imageName": docker_image,
            "gpuCount": 1,
            "gpuType": gpu_type,
            "containerDiskSizeGB": 10,
            "env": environment_variables or {}
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.api_url}/pods",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to create pod: {response.text}")
                raise Exception(f"Failed to create pod: {response.text}")
                
            pod_data = response.json()
            logger.info(f"Created pod with ID {pod_data['id']}")
            
            return pod_data
            
    async def list_pods(self):
        """List all pods"""
        if not self.api_key:
            logger.error("RUNPOD_API_KEY environment variable not set")
            raise ValueError("RUNPOD_API_KEY environment variable not set")
            
        logger.info("Listing pods")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.api_url}/pods",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to list pods: {response.text}")
                raise Exception(f"Failed to list pods: {response.text}")
                
            pods_data = response.json()
            logger.info(f"Found {len(pods_data['pods'])} pods")
            
            return pods_data['pods']
            
    async def terminate_pod(self, pod_id: str):
        """Terminate a pod"""
        if not self.api_key:
            logger.error("RUNPOD_API_KEY environment variable not set")
            raise ValueError("RUNPOD_API_KEY environment variable not set")
            
        logger.info(f"Terminating pod {pod_id}")
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.api_url}/pods/{pod_id}",
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to terminate pod: {response.text}")
                raise Exception(f"Failed to terminate pod: {response.text}")
                
            logger.info(f"Pod {pod_id} terminated")
            
            return True
