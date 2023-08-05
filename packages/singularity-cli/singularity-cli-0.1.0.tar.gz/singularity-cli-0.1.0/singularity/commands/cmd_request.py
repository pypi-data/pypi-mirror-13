import click
from json import dumps, load
import os
from tabulate import tabulate

@click.group('request')
@click.pass_context
def cli(ctx):
    pass

@cli.command(name='unpause')
@click.argument('request-id')
@click.pass_context
def request_unpause(ctx, request_id):
    res = ctx.obj['client'].unpause_request(request_id)
    if 'error' in res:
        click.echo('error during unpause request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('unpaused request {0}'.format(request_id))

@cli.command(name='run')
@click.argument('request-id')
@click.pass_context
def request_run(ctx, request_id):
    res = ctx.obj['client'].run_request(request_id)
    if 'error' in res:
        click.echo('error during running request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('running request {0}'.format(request_id))

@cli.command(name='pause')
@click.option('--kill-tasks', '-k', is_flag=True, default=False, help='Kill tasks when paused')
@click.argument('request-id')
@click.pass_context
def request_pause(ctx, request_id, kill_tasks):
    res = ctx.obj['client'].pause_request(request_id, kill_tasks)
    if 'error' in res:
        click.echo('error during pause request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('paused request {0} with killTasks={1}'.format(request_id, kill_tasks))

@cli.command(name='instances')
@click.argument('request-id')
@click.argument('instances', '-i', type=click.INT)
@click.pass_context
def request_instances(ctx, request_id, instances):
    res = ctx.obj['client'].set_instances_request(request_id, instances)
    if 'error' in res:
        click.echo('error during set instances for request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('setting instances to {0} for request {1}'.format(instances, request_id))

@cli.command(name='bounce')
@click.argument('request-id')
@click.pass_context
def request_bounce(ctx, request_id):
    res = ctx.obj['client'].bounce_request(request_id)
    if 'error' in res:
        click.echo('error during set instances for request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('bounced request {0}'.format(request_id))

@cli.command(name='get')
@click.argument('request-id')
@click.option('--json', '-j', is_flag=True, help='Enable json output')
@click.pass_context
def request_get(ctx, request_id, json):
    if request_id:
        res = ctx.obj['client'].get_request(request_id)
        if json:
            click.echo(dumps(res, indent=2))
        else:
            output_request(res)

@cli.command(name='delete')
@click.argument('request-id')
@click.pass_context
def request_delete(ctx, request_id):
    res = ctx.obj['client'].delete_request(request_id)
    if 'error' in res:
        click.echo('error during delete request {0}: {1}'.format(request_id, res['error']))
    else:
        click.echo('deleted request {0} to {1}'.format(request_id, instances))

@cli.command(name='list')
@click.option('--type', '-t', default='all', type=click.Choice(['pending', 'cleanup', 'paused', 'finished', 'cooldown', 'active', 'all']), help='Request type to get')
@click.option('--json', '-j', is_flag=True, help='Enable json output')
@click.pass_context
def request_list(ctx, type, json):
    res = ctx.obj['client'].get_requests(type)
    if json:
        click.echo(dumps(res, indent=2))
    else:
        output_requests(res)

@cli.command(name='sync')
@click.option('--file', '-f', type=click.File('r'), help='JSON request/deploy file to sync')
@click.option('--dir',  '-d', type=click.Path(), help='Directory of JSON request/deploy files to sync')
@click.pass_context
def request_sync(ctx, file, dir):
    client = ctx.obj['client']
    if file:
        file_request = load(file)
        sync_request(client, file_request)
    elif dir:
        for filename in os.listdir(dir):
            if filename.endswith('json'):
                with open(os.path.join(dir, filename)) as file:
                    sync_request(client, load(file))
    else:
        click.echo('Either --file or --dir is required')

def sync_request(client, request):
    singularity_request = client.upsert_request(request['request'])
    if 'error' in singularity_request:
        click.echo('error during sync request: {0}'.format(singularity_request['error']))
    else:
        click.echo('syncronized request {0}'.format(request['request']['id']))
    if 'deploy' in request:
        file_deploy_id = request['deploy'].get('id', None)
        if 'activeDeploy' in singularity_request:
            singularity_deploy_id = singularity_request['activeDeploy'].get('id', None)
            if file_deploy_id != singularity_deploy_id:
                sync_deploy(client, request['deploy'])
        else:
            sync_deploy(client, request['deploy'])

def sync_deploy(client, deploy):
    res = client.create_deploy(deploy)
    if 'error' in res:
        click.echo('error during sync deploy: {0}'.format(res['error']))
    else:
        click.echo('syncronized deploy {0} for request {1}'.format(deploy['id'], deploy['requestId']))
    return res

def output_request(request):
    request_output = [
        ['Id', request.get('request', {}).get('id', 'unknown')],
        ['State', request.get('state')],
        ['Type', request.get('request', {}).get('requestType', 'unknown')],
        ['Instances', request.get('request', {}).get('instances', 1)],
        ['Rack Sensitive', request.get('request', {}).get('rackSensitive', 'unknown')],
        ['Load Balanced', request.get('request', {}).get('loadBalanced', 'unknown')],
        ['Owners', request.get('request', {}).get('owners', 'unknown')],
        ['Deploy Id', request.get('activeDeploy', {}).get('id', 'unknown')],
    ]
    click.echo(tabulate(request_output))

def output_requests(requests):
    requests_output = [['Id', 'State', 'Type', 'Instances', 'Deploy Id']]
    for request in requests:
        requests_output.append([
            request.get('request', {}).get('id', 'unknown'),
            request.get('state', 'unknown'),
            request.get('request', {}).get('requestType', 'unknown'),
            request.get('request', {}).get('instances', 1),
            request.get('requestDeployState', {}).get('activeDeploy', {}).get('deployId', 'none')
        ])
    click.echo(tabulate(requests_output, headers="firstrow"))
