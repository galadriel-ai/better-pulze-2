from dataclasses import dataclass

from google.cloud import compute_v1
from google.oauth2 import service_account

import settings
from router.singleton import Singleton


@dataclass(frozen=True)
class InstanceGroupStatus:
    target_size: int
    actions: dict


@Singleton
class GoogleComputeRepository:
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(
            'sidekik-ai-9b5fe8b95c6c.json')
        self.client = compute_v1.InstanceGroupManagersClient(credentials=credentials)

    def get_instance_group_status(self) -> InstanceGroupStatus:
        response = self.client.get(
            project=settings.GCP_PROJECT_ID,
            zone=settings.GCP_ZONE,
            instance_group_manager=settings.GCP_INSTANCE_GROUP_NAME
        )
        target_size = response.target_size
        actions = _map_actions(response.current_actions)
        return InstanceGroupStatus(target_size=target_size, actions=actions)


def _map_actions(actions) -> dict:
    return {
        "abandoning": actions.abandoning,
        "creating": actions.creating,
        "creating_without_retries": actions.creating_without_retries,
        "deleting": actions.deleting,
        "none": actions.none,
        "recreating": actions.recreating,
        "refreshing": actions.refreshing,
        "restarting": actions.restarting,
        "resuming": actions.resuming,
        "starting": actions.starting,
        "stopping": actions.stopping,
        "suspending": actions.suspending,
        "verifying": actions.verifying,
    }


if __name__ == '__main__':
    repository = GoogleComputeRepository.instance()
    print(repository.get_instance_group_status())
