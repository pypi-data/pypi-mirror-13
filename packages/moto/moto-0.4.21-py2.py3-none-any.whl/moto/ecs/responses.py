from __future__ import unicode_literals
import json
import uuid

from moto.core.responses import BaseResponse
from .models import ecs_backends


class EC2ContainerServiceResponse(BaseResponse):
    @property
    def ecs_backend(self):
        return ecs_backends[self.region]

    @property
    def request_params(self):
        try:
            return json.loads(self.body.decode())
        except ValueError:
            return {}

    def _get_param(self, param):
        return self.request_params.get(param, None)

    def create_cluster(self):
        cluster_name = self._get_param('clusterName')
        cluster = self.ecs_backend.create_cluster(cluster_name)
        return json.dumps({
            'cluster': cluster.response_object
        })

    def list_clusters(self):
        cluster_arns = self.ecs_backend.list_clusters()
        return json.dumps({
            'clusterArns': cluster_arns,
            'nextToken': str(uuid.uuid1())
        })

    def delete_cluster(self):
        cluster_str = self._get_param('cluster')
        cluster = self.ecs_backend.delete_cluster(cluster_str)
        return json.dumps({
            'cluster': cluster.response_object
        })

    def register_task_definition(self):
        family = self._get_param('family')
        container_definitions = self._get_param('containerDefinitions')
        volumes = self._get_param('volumes')
        task_definition = self.ecs_backend.register_task_definition(family, container_definitions, volumes)
        return json.dumps({
            'taskDefinition': task_definition.response_object
        })

    def list_task_definitions(self):
        task_definition_arns = self.ecs_backend.list_task_definitions()
        return json.dumps({
            'taskDefinitionArns': task_definition_arns,
            'nextToken': str(uuid.uuid1())
        })

    def deregister_task_definition(self):
        task_definition_str = self._get_param('taskDefinition')
        task_definition = self.ecs_backend.deregister_task_definition(task_definition_str)
        return json.dumps({
            'taskDefinition': task_definition.response_object
        })

    def create_service(self):
        cluster_str = self._get_param('cluster')
        service_name = self._get_param('serviceName')
        task_definition_str = self._get_param('taskDefinition')
        desired_count = self._get_int_param('desiredCount')
        service = self.ecs_backend.create_service(cluster_str, service_name, task_definition_str, desired_count)
        return json.dumps({
            'service': service.response_object
        })

    def list_services(self):
        cluster_str = self._get_param('cluster')
        service_arns = self.ecs_backend.list_services(cluster_str)
        return json.dumps({
            'serviceArns': service_arns,
            'nextToken': str(uuid.uuid1())
        })

    def update_service(self):
        cluster_str = self._get_param('cluster')
        service_name = self._get_param('service')
        task_definition = self._get_param('taskDefinition')
        desired_count = self._get_int_param('desiredCount')
        service = self.ecs_backend.update_service(cluster_str, service_name, task_definition, desired_count)
        return json.dumps({
            'service': service.response_object
        })

    def delete_service(self):
        service_name = self._get_param('service')
        cluster_name = self._get_param('cluster')
        service = self.ecs_backend.delete_service(cluster_name, service_name)
        return json.dumps({
            'service': service.response_object
        })
