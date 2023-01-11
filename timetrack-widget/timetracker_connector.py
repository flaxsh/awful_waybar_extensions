import abc
from dataclasses import dataclass
from typing import List


@dataclass
class Project:
    id : str
    name: str
@dataclass
class TrackedTask:
    id : str
    name : str
    project : Project
    is_active : bool
    start_time_epoch_secs : int

class TimetrackConnector(abc.ABC):

    def list_projects(self) -> List[Project]:
        raise NotImplementedError

    def list_tasks(self) -> List[TrackedTask]:
        raise NotImplementedError
    def get_current_task(self) -> TrackedTask:
        raise NotImplementedError

    def create_task(self) -> TrackedTask:
        raise NotImplementedError

    def stop_task(self, task_id : str):
        raise NotImplementedError

    def start_task(self, task_id :str):
        raise NotImplementedError