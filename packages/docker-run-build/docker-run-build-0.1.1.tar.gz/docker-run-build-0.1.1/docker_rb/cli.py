import click
import dockerapi
import warnings

import utils as u


@click.command()
@click.argument('image')
@click.option('--output', help='output image')
@click.option('--no-assert-hostname', is_flag=True,
              help='Disable hostname validation')
@click.option('--mount', multiple=True,
              help='Mount volume (format: "src:target[:rw,:ro]")')
def main(image, output, no_assert_hostname, mount):
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
            cli, image, code, mount, entrypoint=options['entrypoint'])

        # get logs
        exitcode = cli.wait(container=container_id)

        logs = cli.logs(container_id, stdout=True, stderr=True)

        if logs:
            if exitcode < 1:
                click.echo(logs)
            else:
                click.secho(logs, fg='red')
        else:
            click.secho('Nothing', bold=True)

        # commit running container to image
        if exitcode < 1:
            cli.commit(container=container_id, repository=output)
            cli.stop(container=container_id)

        cli.remove_container(container=container_id)

        # restore container's entrypoint and cmd
        if exitcode < 1:
            u.restore_image_options(cli, output, options)
