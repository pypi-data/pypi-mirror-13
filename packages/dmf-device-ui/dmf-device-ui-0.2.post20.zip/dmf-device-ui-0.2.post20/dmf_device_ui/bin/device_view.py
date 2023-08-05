# -*- coding: utf-8 -*-
# # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
#
# Use a separate Cairo surface for each layer of the device view (e.g.,
# electrodes, connections).
#
# Cairo surfaces can be composited over one another by using
# `set_source_surface`, which will, by default, blend according to the alpha
# channel of the source and the existing surface content.  Other blending modes
# can be used by selecting the appropriate operator.
#
# See [here][1] and [here][2] for more information.
#
# [1]: http://cairographics.org/operators/
# [2]: http://cairographics.org/FAQ/#paint_from_a_surface
#
# # TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
import pkg_resources

import gtk
import logging

from ..canvas import DmfDeviceCanvas
from ..view import DmfDeviceFixedHubView, DmfDeviceConfigurableHubView
from .. import generate_plugin_name


def parse_args(args=None):
    '''Parses arguments, returns (options, args).'''
    import sys
    from argparse import ArgumentParser

    if args is None:
        args = sys.argv

    parser = ArgumentParser(description='Example app for drawing shapes from '
                            'dataframe, scaled to fit to GTK canvas while '
                            'preserving aspect ratio (a.k.a., aspect fit).')
    parser.add_argument('-p', '--padding-fraction', type=float, default=0)
    parser.add_argument('-a', '--connections-alpha', type=float, default=.5)
    parser.add_argument('-c', '--connections-color', default='#ffffff')
    parser.add_argument('-w', '--connections-width', type=float, default=1)
    parser.add_argument('-n', '--plugin-name', default=None)

    subparsers = parser.add_subparsers(help='help for subcommand',
                                       dest='command')

    parser_fixed = subparsers.add_parser('fixed', help='Start view with fixed'
                                         'name and hub URI.')
    parser_fixed.add_argument('hub_uri')

    parser_config = subparsers.add_parser('configurable', help='Start view '
                                          'with configurable name and hub '
                                          'URI.')
    parser_config.add_argument('hub_uri', nargs='?')

    args = parser.parse_args()
    return args


def main():
    logging.basicConfig(level=logging.INFO)

    args = parse_args()
    canvas = DmfDeviceCanvas(connections_color=args.connections_color,
                             connections_alpha=args.connections_alpha,
                             padding_fraction=args.padding_fraction)
    canvas.connections_attrs['line_width'] = args.connections_width

    if args.command == 'fixed':
        view = DmfDeviceFixedHubView(canvas, hub_uri=args.hub_uri,
                                     plugin_name=args.plugin_name)
    elif args.command == 'configurable':
        view = DmfDeviceConfigurableHubView(canvas, hub_uri=args.hub_uri,
                                            plugin_name=args.plugin_name)

    view.widget.connect('destroy', gtk.main_quit)

    def init_window_titlebar(widget):
        '''
        Set window title and icon.
        '''
        view.widget.parent.set_title('DMF device user interface')
        try:
            (view.widget.parent
            .set_icon_from_file(pkg_resources.resource_filename('microdrop',
                                                                'microdrop.ico')))
        except ImportError:
            pass
    view.widget.connect('realize', init_window_titlebar)
    if args.command == 'fixed':
        logging.info('Register connect_plugin')
        view.canvas_slave.widget.connect('realize', lambda *args:
                                         view.connect_plugin())

    view.show_and_run()


if __name__ == '__main__':
    main()
