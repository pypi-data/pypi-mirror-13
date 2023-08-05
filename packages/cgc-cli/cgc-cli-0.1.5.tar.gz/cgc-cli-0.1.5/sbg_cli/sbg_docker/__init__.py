__author__ = 'Sinisa'


from sbg_cli.context import Context
from sbg_cli.config import Config, load_config
from sbg_cli.sbg_docker.docker_client.client import Docker


__utility__ = 'sbg_cli.sbg_docker.main'
__description__ = 'Seven Bridges Genomics utility for building and managing docker images'


def docker_client(cfg):
    client = Docker.create_docker_client(cfg)
    return client


def production(binder):
    cfg = load_config('SBG')
    binder.bind(Config, cfg)
    client = docker_client(cfg)
    binder.bind(Docker, client)
    ctx = Context()
    binder.bind(Context, ctx)


def cgc(binder):
    cfg = load_config('CGC')
    binder.bind(Config, cfg)
    client = docker_client(cfg)

    binder.bind(Docker, client)
    ctx = Context()
    binder.bind(Context, ctx)
