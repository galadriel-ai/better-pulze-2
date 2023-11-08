from dataclasses import dataclass
from googleapiclient.discovery import build
from google.auth import default
from router.singleton import Singleton

@dataclass(frozen=True)
class InstanceGroupStatus:
    target_size: int
    actions: dict

@Singleton
class GoogleComputeRepository:
    def __init__(self):
        credentials, _ = default()
        self.compute_service = build("compute", "v1", credentials=credentials)
        self.project = "sidekik-ai"
        self.zone = "us-west1-b"
        self.instance_group = "llm-gpu-instance-group"

    def get_instance_group_status(self) -> InstanceGroupStatus:
        response = (
            self.compute_service.instanceGroupManagers()
            .get(
                project=self.project,
                zone=self.zone,
                instanceGroupManager=self.instance_group,
            )
            .execute()
        )

        target_size = response.get("targetSize", 0)
        actions = response.get("currentActions", {})

        return InstanceGroupStatus(target_size=target_size, actions=actions)
