from docker.client import Client
from docker.utils import kwargs_from_env


def get_cli(assert_hostname=True):
    kwargs = kwargs_from_env()

    if not assert_hostname:
        kwargs['tls'].assert_hostname = False

    cli = Client(**kwargs)

    return cli


def inspect_config(cli, image, param):
    return cli.inspect_image(image)['Config'].get(param)
