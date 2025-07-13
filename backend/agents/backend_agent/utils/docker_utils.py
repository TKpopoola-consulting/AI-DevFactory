import docker
from typing import Optional

class DockerValidator:
    def __init__(self):
        self.client = docker.from_env()
    
    def validate_container(self, image: str, command: str) -> Optional[str]:
        try:
            container = self.client.containers.run(
                image,
                command,
                detach=True,
                remove=True
            )
            container.wait(timeout=30)
            logs = container.logs().decode('utf-8')
            return logs
        except Exception as e:
            return f"Validation failed: {str(e)}"