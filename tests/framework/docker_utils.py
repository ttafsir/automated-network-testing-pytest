import docker

client = docker.from_env()


class DockerContainer:
    def __init__(
        self, image_name: str = None, container_name: str = None, detach: bool = True
    ):
        self._image_name = image_name
        self._container_id = container_name
        self._container = None
        self.detach = detach

    def __enter__(self):
        if self._container_id is not None:
            self._container = next(
                (c for c in client.containers.list() if c.name == self._container_id),
                None,
            )
            if self._container is None:
                raise ValueError(f"Container {self._container_id} not found")
        else:
            self._container = client.containers.run(
                image=self._image_name, detach=self.detach
            )
        return self._container

    def __exit__(self, *args):
        pass
