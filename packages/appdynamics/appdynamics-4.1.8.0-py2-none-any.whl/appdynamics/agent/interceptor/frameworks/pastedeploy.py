import appdynamics.agent
from appdynamics.agent.interceptor.frameworks.wsgi import WSGIMiddleware


def composite_factory(loader, global_conf, target, **local_conf):
    target = loader.get_app(target, global_conf=global_conf)

    try:
        appdynamics.agent.configure(local_conf)
        return WSGIMiddleware(application=target)
    except:
        return target
