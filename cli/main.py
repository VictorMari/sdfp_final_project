import json
from pathlib import Path


class Strategy:
    def add_stage(self):
        pass

    def add_output(self):
        pass

    def add_processing(self):
        pass


class DockerCompose(Strategy):
    def __init__(self):
        pass

    def add_stage(self):
        pass

    def add_output(self):
        pass

    def add_processing(self):
        pass


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


if __name__ == '__main__':
    pipeline_descriptor = load_pipeline_descriptor()
    deployment_type = pipeline_descriptor["deployment-type"]
    deployment_generator = deployments[deployment_type]
    deployment_pipeline = deployment_generator()
    print(deployment_pipeline)