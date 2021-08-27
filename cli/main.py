import json
import yaml
from pathlib import Path


class Strategy:
    def add_ingestion_stage(self, stage_info):
        pass

    def add_output_stage(self, stage_info):
        pass

    def add_processing_stage(self, stage_info):
        pass


class DockerCompose(Strategy):
    def __init__(self):
        self.default_configs = {
            "grafana_provisioning": "./cli/configs/grafana/provisioning:/etc/grafana/provisioning:z",
            "grafana_dashboard": "./cli/configs/grafana/dashboards:/var/lib/grafana/dashboards:z"
        }
        self.docker_compose = {
            "version": "2",
            "services": {}
        }

    def add_ingestion_stage(self, stage_info):
        def generate_prometheus_binding():
            self.docker_compose["services"]["prometheus"] = {
                "image": "prom/prometheus",
                "network_mode": "host",
                "volumes": [
                    f"{stage_info['custom-config']}:/etc/prometheus/prometheus.yml:z",
                ]
            }

        def generate_grafana_binding():
            self.docker_compose["services"]["grafana"] = {
                "image": "grafana/grafana:latest",
                "network_mode": "host",
                "user": "104",
                "volumes": [
                    self.default_configs['grafana_provisioning'],
                    self.default_configs['grafana_dashboard'],
                    f"{stage_info['custom-config']}:/etc/grafana/grafana.ini:z"
                ]
            }

        implementation_strategy = {
            "Prometheus": generate_prometheus_binding,
            "Grafana": generate_grafana_binding
        }

        implementation_type = stage_info["implementation"]
        stage_implementation = implementation_strategy[implementation_type]
        stage_implementation()

    def add_output_stage(self, stage_info):
        pass

    def add_processing_stage(self, stage_info):
        pass

    def generate_artifact(self):
        with Path("docker-compose.yaml").open("w") as file:
            yaml.safe_dump(self.docker_compose, file)


deployments = {
    "docker-compose": DockerCompose
}


def load_pipeline_descriptor():
    descriptor_file = Path("cli/services/pipeline-descriptor.json")
    with descriptor_file.open("r") as file:
        return json.load(file)


def load_deployment_strategy():
    pass


def start_ui():
    pass


def start_back_end():
    pass


if __name__ == '__main__':
    pipeline_descriptor = load_pipeline_descriptor()

    deployment_type = pipeline_descriptor["deployment-type"]
    deployment_generator = deployments[deployment_type]
    deployment_pipeline = deployment_generator()

    ingestion_stages = pipeline_descriptor["stages"]["ingestion"]
    processing_stages = pipeline_descriptor["stages"]["processing"]
    output_stages = pipeline_descriptor["stages"]["output"]

    for stage in ingestion_stages:
        deployment_pipeline.add_ingestion_stage(stage)

    for stage in processing_stages:
        deployment_pipeline.add_processing_stage(stage)

    for stage in output_stages:
        deployment_pipeline.add_output_stage(stage)

    deployment_pipeline.generate_artifact()
