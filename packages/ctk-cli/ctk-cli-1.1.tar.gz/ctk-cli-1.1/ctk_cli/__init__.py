import logging
from module import CLIModule
from execution import getXMLDescription, isCLIExecutable, listCLIExecutables, popenCLIExecutable

def add_logging_handler(handler):
    """Add logging handler to loggers of both submodules"""
    for name in ('ctk_cli.module', 'ctk_cli.execution'):
        logger = logging.getLogger(name)
        logger.addHandler(handler)

def add_stderr_logging_handler():
    """Add logging handler to all submodules for simple stderr output"""
    pass
