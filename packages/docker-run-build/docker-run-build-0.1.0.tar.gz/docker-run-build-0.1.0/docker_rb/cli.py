import click
import dockerapi
import warnings

import utils as u


@click.command()
@click.argument('image')
@click.option('--output', help='output image')
@click.option('--no-assert-hostname', is_flag=True,
              help='Disable hostname validation')
def main(image, output, no_assert_hostname):
    click.secho('\nUpdating image {} (to: {})'.format(
        image, output if output else 'same image'), fg='green')

    if not output:
        output = image

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        cli = dockerapi.get_cli(assert_hostname=not no_assert_hostname)

        # cache old options
        options = u.get_old_options(cli, image)

        # read code from stdin
        code = u.get_code()

        # execute code inside a container
        click.secho('Running code..., output:', fg='green')
        container_id = u.run_code_in_container(
            cli, image, code, entrypoint=options['entrypoint'])

        # get logs
        logs, abort = u.get_logs(cli, container_id)

        if logs:
            click.echo(logs)
        else:
            click.secho('Nothing', bold=True)

        # commit running container to image
        if not abort:
            cli.commit(container=container_id, repository=output)
            cli.stop(container=container_id)

        cli.wait(container=container_id)
        cli.remove_container(container=container_id)

        # restore container's entrypoint and cmd
        if not abort:
            u.restore_image_options(cli, output, options)
