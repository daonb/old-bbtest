import logging
import os

from bbtest import HomeBox

logger = logging.getLogger('bblog')


class ToDoBox(HomeBox):
    """A black box wrapper for todo.sh.
    Like every black box, the todo box has the `install` and `clean`
    (TODO: uninstall?) methods. On top of that we have methods to be used
    by the test coders to poke the box and peek into it.
    """

    NAME = 'todo'

    def install(self):
        """ installing todo.txt
        First creates a temp dir on the host and then copies the assets
        in. On Linux, we need to make sure `todo.sh` is executable.
        """
        super().install()
        src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                               'src')
        self.todopy = self.put(os.path.join(src_dir, 'todo.py'), 'todo.py')
        # need to run once so it creates its config file
        self.run()

    def run(self, *args):
        """Pass the args to a todo.sh running on the host. See `todo.sh -h`
        for more details.
        """
        logger.info(f"ToDoBox Starts: {args}")
        result = super().run(f'python {self.todopy} -d {self.path}' + ' '.join(args))
        logger.info(f"ToDoBox returns: {result}")
        return result

    def add(self, todo):
        """Add a to do.
        Add is a *Porceline method* - one that adds only a shining interface.
        The same function can be achived by using the low level, aka `plumbing`
        methods.
        """
        return self.run('add', todo)

    def list(self):
        """Return a list of todos."""
        todos = list()
        list_out = self.run('list')
        for line in list_out[:-2]:
            todos.append(line[2:])
        return todos

    def remove(self):
        """Remove our home directory"""
        return self.host.rmtree(self.home)

    def clean(self):
        """Clean's job is to wipe all data. In todo's case, it's just a file"""
        return self.host.rmfile(self.host.join(self.path, 'todo.txt'))
