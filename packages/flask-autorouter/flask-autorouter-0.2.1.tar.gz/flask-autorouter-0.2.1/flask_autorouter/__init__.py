__author__ = 'dpepper'
__version__ = '0.2.1'


import os
import imp
import json
import urllib

# from bson import json_util
import flask


def generate_urls(app, src_dir, base_url='/', auth_fn=None):
    assert type(app) == flask.Flask
    assert base_url.startswith('/')
    base_url = base_url.rstrip('/')

    if os.path.isdir(src_dir):
        src_dir = os.path.abspath(src_dir)
    else:
        src_dir = os.path.join(app.config['ROOT_PATH'], src_dir)

    assert os.path.isdir(src_dir)
    assert src_dir.startswith(app.config['ROOT_PATH'])

    def generate_view_fn(http_fns):
        def view_fn(*args, **kwargs):
            fn = view_fn.http_fns.get(flask.request.method)

            if fn:
                res = fn(*args, **kwargs)

                if None == res:
                    res = ('', 204)  # Empty Response Code
                elif type(res) in [list, dict, int, float]:
                    # auto-package results into json
                    res = flask.Response(
                        # json.dumps(res, default=json_util.default),
                        json.dumps(res),
                        mimetype='application/json',
                    )
            else:
                res = ('', 405)  # Method Not Allowed

            return res

        view_fn.http_fns = http_fns
        return view_fn


    paths = {}
    for path, subdirs, filenames in os.walk(src_dir):
        filenames = [f for f in filenames if f.endswith('.py')]
        for filename in filenames:
            if filename == '__init__.py':
                continue

            mod_name = '%s/%s' % (path[len(app.config['ROOT_PATH']):], filename[:-3])
            mod_path = os.path.abspath(os.path.join(path, filename))
            module = imp.load_source(mod_name, mod_path)

            public_view = getattr(module, 'PUBLIC', False)

            http_fns = {}
            for method in ['VIEW', 'GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']:
                fn = getattr(module, method, None)

                if fn:
                    if getattr(module, method.lower(), None):
                        raise Exception('endpoint has both %s() and %s(): %s' % (method, method.lower(), mod_path))
                else:
                    fn = getattr(module, method.lower(), None)

                if fn:
                    if not callable(fn):
                        raise Exception('invalid http method function: %s: %s' % (method, mod_path))

                    http_fns[method] = fn


            if not http_fns:
                raise Exception('invalid endpoint, missing http function: ' + mod_path)

            if http_fns.get('VIEW') and (http_fns.get('GET') or http_fns.get('POST')):
                raise Exception('invalid endpoints, use either view() or get()/post() but not both: ' + mod_path)

            # remap VIEW fn to GET / POST
            if http_fns.get('VIEW'):
                http_fns['GET'] = http_fns['POST'] = http_fns['VIEW']
                del http_fns['VIEW']

            view_fn = generate_view_fn(http_fns)

            # add authentication layer
            if not public_view and auth_fn:
                view_fn = auth_fn(view_fn)


            if hasattr(module, 'PATH'):
                url_paths = [getattr(module, 'PATH')]
            elif hasattr(module, 'PATHS'):
                url_paths = getattr(module, 'PATHS')
            else:
                # determine this endpoint's url, based on it's path
                url = '%s/%s/%s' % (
                    base_url,
                    path[len(src_dir):],
                    filename[:-3]
                )
                url = url.replace('//', '/')
                url_paths = [url]


            for url in url_paths:
                app.add_url_rule(
                    url,
                    view_func=view_fn,
                    endpoint=mod_name,
                    methods=http_fns.keys(),
                )
                paths[url] = mod_name


def list_routes(app, verbose=False):
    assert type(app) == flask.Flask

    output = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint == 'static':
            continue

        if verbose:
            methods = sorted([ x for x in rule.methods if x not in ['HEAD', 'OPTIONS'] ])
        else:
            methods = ''
        line = urllib.unquote("{:30s}\t{:30s}\t{}".format(rule.rule, rule.endpoint, methods))

        if not verbose:
            # truncate long lines
            if len(line) > 70:
                line = line[:70] + '...'

        output.append(line)

    output = sorted(output)
    return "\n".join(output)
