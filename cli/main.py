import json
import yaml
import sys
from flask import Flask, send_from_directory, request, Response, session, redirect, url_for, make_response, send_file, abort
from pathlib import Path



class Server:
    def __init__(self, pipeline_generator) -> None:
        self.app = Flask(__name__)
        @self.app.route('/', methods=["POST"])
        def parse_specifications():
            body_data = request.get_json()
            if not "output" in body_data["stages"]:
                body_data["stages"]["output"] = ""
            if not "processing" in body_data["stages"]:
                body_data["stages"]["processing"] = []

            if body_data:
                try:
                    pipeline_generator(body_data)
                except Exception as e:
                    print(json.dumps(body_data, indent=4))
                    print(e)
                    return Response(json.dumps({
                        "error": "Error while executing the configuration"
                    }), status=400, mimetype='application/json') 
                return body_data
            else:
                return Response(json.dumps({
                    "error": "No body provided"
                }), status=400, mimetype='application/json') 
                
        
        @self.app.route('/', methods=["GET"])
        def load_main_page():
            return send_from_directory("static","index.html")


    def listen(self):
        self.app.run(host="127.0.0.1", port=8082, debug=True)



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

        def generate_node_exporter_binding():
            self.docker_compose["services"]["node-exporter"] = {
                "image": "prom/node-exporter",
                "ports": ["9100:9100"]
            }

        implementation_strategy = {
            "Prometheus": generate_prometheus_binding,
            "Grafana": generate_grafana_binding,
            "node-exporter": generate_node_exporter_binding
        }

        implementation_type = stage_info["implementation"]
        stage_implementation = implementation_strategy[implementation_type]
        stage_implementation()


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





def generate_pipeline(specifications=None):
    # extract this to a method
    # call the method from the http rquest of the ui without creating the pipeline descriptor
    if not specifications:
        pipeline_descriptor = load_pipeline_descriptor()
    else:
        pipeline_descriptor = specifications

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



if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == "server=True":
        test_server = Server(generate_pipeline)
        test_server.listen()
    else:
        generate_pipeline()
