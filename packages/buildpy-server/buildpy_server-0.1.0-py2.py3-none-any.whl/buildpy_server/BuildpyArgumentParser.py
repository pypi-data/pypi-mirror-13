# -*- coding: utf-8 -*-

import argparse


class BuildpyArgumentParser(argparse.ArgumentParser):
    """Provides convenience functions for argparse. The original code 
    is based on devpi's MyArgumentParser class"""

    def __init__(self, *args, **kwargs):
        super(BuildpyArgumentParser, self).__init__(*args, **kwargs)

    def add_option(self, *args, **kwargs):
        """Wraps :func:`argparse.ArgumentParser.add_argument` and 
        renames it to be more clear.

        :returns: a new option
        """
        opt = super(BuildpyArgumentParser, self).add_argument(
            *args, **kwargs)
        return opt

    def add_group(self, *args, **kwargs):
        """Wraps :func:`argparse.ArgumentParser.add_argument_group` 
        and renames it to be more clear.

        :returns: a new argument group
        """

        grp = super(BuildpyArgumentParser, self).add_argument_group(
                *args, **kwargs)

        def group_add_option(*args2, **kwargs2):
            opt = grp.add_argument(*args2, **kwargs2)
            return opt
        grp.add_option = group_add_option
        return grp
