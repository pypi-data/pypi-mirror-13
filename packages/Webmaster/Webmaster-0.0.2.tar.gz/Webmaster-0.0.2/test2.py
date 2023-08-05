
class BaseClass(object):
    def hello(self):
        print "Hello"

print "bad_boy".capitalize()
new_class = type("NewClassName", (BaseClass,), {})
print new_class
nc = new_class()
nc.hello()


exit()
import werkzeug.exceptions as wex
import sys
import inspect

def import_string(import_name):
    """Imports an object based on a string.  This is useful if you want to
    use import paths as endpoints or something similar.  An import path can
    be specified either in dotted notation (``xml.sax.saxutils.escape``)
    or with a colon as object delimiter (``xml.sax.saxutils:escape``).
    If `silent` is True the return value will be `None` if the import fails.
    :param import_name: the dotted name for the object to import.
    :param silent: if set to `True` import errors are ignored and
                   `None` is returned instead.
    :return: imported object
    """
    # force the import name to automatically convert to strings
    # __import__ is not able to handle unicode strings in the fromlist
    # if the module is a package
    import_name = str(import_name).replace(':', '.')

    try:
        try:
            __import__(import_name)
        except ImportError:
            if '.' not in import_name:
                raise
        else:
            return sys.modules[import_name]

        module_name, obj_name = import_name.rsplit('.', 1)

        try:
            module = __import__(module_name, None, None, [obj_name])
        except ImportError:
            # support importing modules not yet set up by the parent module
            # (or package for that matter)
            module = import_string(module_name)

        try:
            print getattr(module, obj_name)
            return getattr(module, obj_name)
        except AttributeError as e:
            raise ImportError(e)

    except ImportError as e:
        pass



class HTTPException(object):
    pass

class Hello(HTTPException):
    pass

maps = {}
g = import_string("webmaster.exceptions")
for name in dir(g):
    obj = getattr(g, name)
    try:
        if issubclass(obj, wex.HTTPException):
            maps[name] = obj
    except TypeError as ter:
        pass
print maps

exit()
for name, obj in g.items():
    try:
        if issubclass(obj, HTTPException):
            print name
    except TypeError as ter:
        pass


exit()


print (403 // 100)
exit()

def f(*a):
    l = ["a", "b"]
    l += list(a)
    print l

f("jone", "marie", "Locs")

exit()
class Deploy(object):
    """
    A class that allows you to deploy with git without setting up git remotes

    """
    def __init__(self, CWD, config_file="propel.yml"):
        """

        :param CWD: Current working dir
        :param config_file: the config file
        :return:
        """
        key = "deploy-remotes"
        with open(config_file) as propel_file:
            config = yaml.load(propel_file)
        self.config = config[key]
        self.CWD = CWD

    def run(self, cmd):
        subprocess.call(cmd.strip(), shell=True)

    def remote(self, name):
        remotes = self.config[name]
        name = "webcli_push__%s" % name
        cmd = self._gen_git_remote_command(name, remotes)
        cmd += self._gen_git_push_remote(name, force)
        cmd += self._gen_git_remove_remote(name)
        self.run("cd %s; %s" % (self.CWD, cmd))

    def all(self):
        l = []
        [l.extend(h) for k, h in self.config.items()]
        remotes = list(set(l))
        name = "webcli_push__all"
        cmd = self._gen_git_remote_command(name, remotes)
        cmd += self._gen_git_push_remote(name, force)
        cmd += self._gen_git_remove_remote(name)
        self.run("cd %s; %s" % (self.CWD, cmd))

    def reset_git(self):
        cmd = ""
        for k, values in self.config.items():
            cmd += self._gen_git_remote_command(k, values)
        self.run("cd %s; %s" % (self.CWD, cmd))

    def _gen_git_push_remote(self, name, force=False):
        force = " -f" if force else ""
        return "git push %s %s master;" % (force, name)

    def _gen_git_remove_remote(self, name):
        return "git remote remove %s;" % name

    def _gen_git_remote_command(self, name, remotes):
        """
        Generate the push command for a remote
        :param name (str): the remote name
        :param remotes (list): list of
        :return str:
        """
        if not isinstance(remotes, list):
            raise TypeError("'remotes' must be of list type")

        cmd = gen_git_remove_remote(name)
        cmd += "git remote add %s %s;" % (name, remotes[0])
        if len(remotes) > 1:
            for h in remotes:
                cmd += "git remote set-url %s --push --add %s;" % (name, h)
        return cmd





