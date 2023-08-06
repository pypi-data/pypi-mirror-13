from flask.ext.script import Option, Manager, Command

# Manager Factory.
def MainManager(app, tests_module=None, **kwargs):
    """
    A factory which creates a flask-script manager and configure it for use
    with the boilerplate. 

    :param kwargs: keyword arguments to send to flask-script's Manager
                   class initialiser
    """

    manager = Manager(app,**kwargs)
    info_manager = AppInfoManager(app, **kwargs)
    info_manager.add_command('routes', GetRoutes(app))

    manager.add_command('server', Run(app))
    manager.add_command('meinheld', Host(app))
    manager.add_command('info', info_manager)
    if tests_module:
        tests_command = Test(app)
        tests_command.tests_module = tests_module
        manager.add_command('test', tests_command)

    if not app.config.get('IS_CLEAN', True):
        manager.add_command('cleanup', Cleanup(app))

    return manager

class BaseCommand(Command):
    """
    Base command class which comes with the default options
    """

    option_list = (Option('--config', '-c', dest='config', nargs=1, action='store', help='Provide'\
            'a configuation class defined in config.'),)

    def __init__(self, app):
        super(Command, self).__init__()
        self.app = app

class AppInfoManager(Manager):
    """
    Query info about the app.
    """

class GetRoutes(BaseCommand):
    """
    Get all the App's routes and a presentable fashion. Good for debugging endpoints.
    """
    def run(self, **kwargs):
        from flask import url_for
        rules = []
        largest = [0,0,0]

        for rule in self.app.url_map.iter_rules():
            if len(str(rule.endpoint)) > largest[0]:
                largest[0] = len(rule.endpoint)

            if len(str(rule.rule)) > largest[1]:
                largest[1] = len(rule.rule)

            if len(str(rule.methods)) > largest[2]:
                largest[2] = len(rule.methods)

            rules.append((str(rule.endpoint), str(rule.rule), str(rule.methods)))
        

        for endpoint, rule, methods in rules:
            print("{}:{}:{}".format(
                endpoint.ljust(largest[0]), 
                rule.ljust(largest[1]), 
                methods.ljust(largest[2])))


class Run(BaseCommand):
    "Run the Flask Builtin Server (Not for production)"

    option_list = (
        Option('--hostname', '-h', dest='hostname', default=None, type=str),
        Option('--port', '-p', dest='port', default=None, type=int),
        Option('--no-debug', '-n', dest='debug', default=True, action='store_false'),    
        Option('--no-threaded', dest='threaded', default=True, action='store_false'),
    ) + BaseCommand.option_list

    def run(self, port, hostname, debug, config, threaded, **kwargs):
        if port is None:
            port = self.app.config.setdefault('LISTEN_PORT', 8000)
        if hostname is None:
            hostname = self.app.config.setdefault('LISTEN_HOST', '0.0.0.0')


        self.app.run(debug=debug, host=hostname, port=port, threaded=threaded)

class Test(BaseCommand):
    def run(self, **kwargs):
        import unittest
        suite = unittest.TestLoader().loadTestsFromModule(self.tests_module)
        unittest.TextTestRunner(verbosity=2).run(suite)

class Cleanup(BaseCommand):
    """
    Remove all submodules and cleanup the skeleton.
    """

    def run(self, **kwargs):
        import shutil
        print(" * Cleaning up...")
        print(" * Unlinking Submodules")
        kept_lines = None
        with open('./Application/modules/frontend/__init__.py', 'r') as fh:
            kept_lines = fh.readlines()

        with open('./Application/modules/frontend/__init__.py', 'w') as fh:
            for line in kept_lines:
                if "Pragma - Submodule Registration Start" in line:
                    break

                fh.write(line)

        print(" * Deleting Submodules")
        shutil.rmtree('./Application/modules/frontend/modules')

        print(" * Deleting Models")
        shutil.rmtree('./libs/models/models/examples')

        print(" * Updating Config")
        kept_lines = None
        with open('./libs/config/config/__init__.py', 'r') as fh:
            kept_lines = fh.readlines()

        with open('./libs/config/config/__init__.py', 'w') as fh:
            for line in kept_lines:
                if "IS_CLEAN = False" in line:
                    continue

                fh.write(line)

        print(" * Cleaning Index Page")
        kept_lines = None
        with open('./Application/modules/frontend/templates/frontend/index.html', 'r') as fh:
            kept_lines = fh.readlines()

        with open('./Application/modules/frontend/templates/frontend/index.html', 'w') as fh:
            ignoring = False
            for line in kept_lines:
                if "Pragma - Start Remove After Cleanup" in line:
                    ignoring = True
                if "Pragma - End Remove After Cleanup" in line:
                    ignoring = False
                    continue

                if not ignoring:
                    fh.write(line)

        print(" * Cleanup Complete!")

class Host(BaseCommand):
    """
    Run a Web Server for Hosting using meinheld.
    """

    option_list = (
        Option('--hostname', '-h', dest='hostname', default='0.0.0.0', type=str),
        Option('--port', '-p', dest='port', default=8000, type=int),
    ) + BaseCommand.option_list
    def run(self, port, hostname, **kwargs):
        if port is None:
            port = self.app.config.setdefault('LISTEN_PORT', 8000)
        if hostname is None:
            hostname = self.app.config.setdefault('LISTEN_HOST', '127.0.0.1')

        from meinheld import server, patch
        patch.patch_all()
        print(" - Running Hosting Server using Meinheld")
        print(" - http://%s:%s/" % (hostname, port))
        server.listen((hostname, port))
        server.run(self.app)
