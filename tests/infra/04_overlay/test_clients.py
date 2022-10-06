import pytest

try:
    import docker
    from tests.framework import DockerContainer
except (ImportError, ModuleNotFoundError):
    pytestmark = pytest.mark.skip(reason="Requires Docker")


HOSTS = [
    "clab-avdirb-client1",
    "clab-avdirb-client2",
    "clab-avdirb-client3",
    "clab-avdirb-client4",
]


@pytest.mark.parametrize(
    "client_ip",
    [
        ('10.1.10.101'),
        ('10.1.11.102'),
        ('10.1.12.103'),
        ('10.1.13.104')
    ]
)
@pytest.mark.docker_hosts(*(HOSTS))
def test_clients(docker_host, client_ip):
    """
    Arrange/Act: Attach to client container and test across the overlay
    Assert: The clients can ping each other
    """
    with DockerContainer(container_name=docker_host) as container:
        output = container.exec_run(f'ping {client_ip} -c 1 -w 2').output
        assert '1 packets received' in output.decode('utf-8')
