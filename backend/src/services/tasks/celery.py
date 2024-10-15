from celery.result import AsyncResult

from .base import TASK, TASK_ID, TaskServiceABC


class CeleryTaskService(TaskServiceABC):
    @staticmethod
    async def create_task(function, *args, **kwargs) -> TASK_ID:
        id_task = function.apply_async(args=args, kwargs=kwargs)
        return id_task.task_id

    @staticmethod
    async def get_task(task_id: TASK_ID) -> TASK:
        return AsyncResult(task_id)


celery_task_service = CeleryTaskService()
