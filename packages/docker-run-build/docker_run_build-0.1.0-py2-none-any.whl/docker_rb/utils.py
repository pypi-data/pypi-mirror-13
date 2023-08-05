import io
import json
import click
import dockerapi

try:
    from shlex import quote
except ImportError:
    from pipes import quote


def get_old_options(cli, image):
    """ Returns Dockerfile values for CMD and Entrypoint
    """
    return {
        'cmd': dockerapi.inspect_config(cli, image, 'Cmd'),
        'entrypoint': dockerapi.inspect_config(cli, image, 'Entrypoint'),
    }


def get_code():
    """ Reads code from STDIN
    """
    code = ''
    with click.open_file('-', 'r') as f:
        code += f.read()
    return code


def restore_image_options(cli, image, options):
    """ Restores CMD and ENTRYPOINT values of the image

    This is needed because we force the overwrite of ENTRYPOINT and CMD in the
    `run_code_in_container` function, to be able to run the code in the
    container, through /bin/bash.
    """
    dockerfile = io.StringIO()

    dockerfile.write(u'FROM {image}\nCMD {cmd}'.format(
        image=image, cmd=json.dumps(options['cmd'])))

    if options['entrypoint']:
        dockerfile.write(
            '\nENTRYPOINT {}'.format(json.dumps(options['entrypoint'])))

    cli.build(tag=image, fileobj=dockerfile)


def run_code_in_container(cli, image, code, entrypoint):
    """ Run `code` in a container, returning its ID
    """
    if entrypoint:
        container = cli.create_container(image=image, entrypoint='/bin/bash',
                                         command='-c {}'.format(quote(code)))
    else:
        container = cli.create_container(
            image=image, command='/bin/bash -c {}'.format(quote(code)))

    container_id = container['Id']

    cli.start(container=container_id)

    return container_id


def get_logs(cli, container_id):
    """ Returns logs and whether an error occurred
    """
    logs = cli.logs(container_id, stdout=True, stderr=True)
    stderr = cli.logs(container_id, stdout=False, stderr=True)
    return logs, bool(stderr)
