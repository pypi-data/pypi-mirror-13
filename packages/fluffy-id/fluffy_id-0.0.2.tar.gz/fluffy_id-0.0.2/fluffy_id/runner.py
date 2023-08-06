#!/usr/bin/env python
from flask.ext.script import Manager, Server
from flask_script.commands import ShowUrls, Clean
from fluffy_id import app

manager = Manager(app)
server = Server(host="0.0.0.0", port=7001)
manager.add_command("runserver", server)


@manager.shell
def make_shell_context():
    """
    Creates a python REPL with several default imports
    in the context of the app
    """
    return dict(app=app)


def main():
    manager.add_command("clean", Clean())
    manager.add_command("show_urls", ShowUrls())
    manager.run()


if __name__ == "__main__":
    main()
