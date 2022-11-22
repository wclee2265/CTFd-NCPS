import json
import random
import traceback
import uuid
from collections import OrderedDict
import docker


class DockerUtils:
    @staticmethod
    def create_docker_service(docker_image, challenge_id, challenge_name, team_id, team_name, user_passwd):
        uuid_code = uuid.uuid4()
        dns = []

        nodes = ["linux-1"]

        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
        client.services.create(
            image=docker_image,
            name=f"{challenge_id}-{challenge_name}-{team_id}-{team_name}-{uuid_code}",
            env={"FLAG": r"FLAG{thisisflag}"},
            dns_config=docker.types.DNSConfig(nameservers=dns),
            networks=["swarmtest"],
            resources=docker.types.Resources(
                mem_limit=DockerUtils.convert_readable_text("128m"), cpu_limit=int(0.5 * 1e9)
            ),
            # constraints=["node.labels.name==" + node],
            endpoint_spec=docker.types.EndpointSpec(ports={2225: (22, "tcp", "host")}),
        )
        client.close()

    def list_docker_container():
        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
        container_list = client.containers.list()
        client.close()
        return container_list

    def list_docker_service():
        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
        service_list = client.services.list()
        client.close()
        return service_list

    def remove_docker_service():
        pass

    @staticmethod
    def convert_readable_text(text):
        lower_text = text.lower()

        if lower_text.endswith("k"):
            return int(text[:-1]) * 1024

        if lower_text.endswith("m"):
            return int(text[:-1]) * 1024 * 1024

        if lower_text.endswith("g"):
            return int(text[:-1]) * 1024 * 1024 * 1024

        return 0

    @staticmethod
    def remove_docker_service(name: str):
        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
        services = client.services.list(filters={"name": name})

        for s in services:
            s.remove()

        client.close()

    """
    @staticmethod
    def remove_current_docker_container(app, user_id, is_retry=False):
        configs = DBUtils.get_all_configs()
        container = DBUtils.get_current_containers(user_id=user_id)

        auto_containers = configs.get("docker_auto_connect_containers", "").split(",")

        if container is None:
            return False

        try:
            client = docker.DockerClient(base_url=configs.get("docker_api_url"))
            networks = client.networks.list(names=[str(user_id) + '-' + container.uuid])

            if len(networks) == 0:
                services = client.services.list(filters={'name': str(user_id) + '-' + container.uuid})
                for s in services:
                    s.remove()
            else:
                redis_util = RedisUtils(app)
                services = client.services.list(filters={'label': str(user_id) + '-' + container.uuid})
                for s in services:
                    s.remove()

                for n in networks:
                    for ac in auto_containers:
                        try:
                            n.disconnect(ac, force=True)
                        except:
                            pass
                    n.remove()
                    redis_util.add_available_network_range(n.attrs['Labels']['prefix'])
        except:
            traceback.print_exc()
            if not is_retry:
                DockerUtils.remove_current_docker_container(app, user_id, True)

        return True
    """


if __name__ == "__main__":
    # DockerUtils.create_docker_service("scada:latest", 1, "test_chal", 1, "test_team", "password")
    print(DockerUtils.list_docker_container())
    service_list = DockerUtils.list_docker_service()
    for service in service_list:
        print(service.attrs)

    DockerUtils.remove_docker_service(name=service_list[-1].attrs["Spec"]["Name"])
