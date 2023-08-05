from celery import task


@task(serializer='json')
def start_new_controller(project_id):
    from mc2.controllers.base.models import Controller

    controller = Controller.objects.get(pk=project_id)
    controller.get_builder().build()
