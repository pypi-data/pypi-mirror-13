import wdl.engine
import wdl.parser
import argparse
import json
import sys
import os
import pkg_resources

def cli():
    command_help = {
        "run": "Run you a WDL",
        "parse": "Parse a WDL file, print parse tree",
        "expr": "Expression testing"
    }

    parser = argparse.ArgumentParser(description='Workflow Description Language (WDL)')
    parser.add_argument(
        '--version', action='version', version=str(pkg_resources.get_distribution('wdl'))
    )
    parser.add_argument(
        '--debug', required=False, action='store_true', help='Open the floodgates'
    )
    parser.add_argument(
        '--no-color', default=False, required=False, action='store_true', help="Don't colorize output"
    )

    subparsers = parser.add_subparsers(help='WDL Actions', dest='action')
    subparsers.required = True
    commands = {}
    commands['run'] = subparsers.add_parser(
        'run', description=command_help['run'], help=command_help['run']
    )
    commands['run'].add_argument(
        'wdl_file', help='Path to WDL File'
    )
    commands['run'].add_argument(
        '--inputs', help='Path to JSON file to define inputs'
    )
    commands['run'].add_argument(
        '--sge', action="store_true", help='Use SGE to execute tasks'
    )
    commands['parse'] = subparsers.add_parser(
        'parse', description=command_help['parse'], help=command_help['parse']
    )
    commands['parse'].add_argument(
        'wdl_file', help='Path to WDL File'
    )

    cli = parser.parse_args()

    if cli.action == 'run':
        sys.exit('Currently unsupported')

        inputs = {}
        run_service_name = "local"

        if cli.sge:
            run_service_name = "sge"

        if cli.inputs:
            with open(cli.inputs) as fp:
                inputs = json.loads(fp.read())

        try:
            wdl.engine.run(cli.wdl_file, run_service_name, inputs)
        except wdl.engine.MissingInputsException as error:
            print("Your workflow cannot be run because it is missing some inputs!")
            if cli.inputs:
                print("Add the following keys to your {} file and try again:".format(cli.inputs))
            else:
                print("Use the template below to specify the inputs.  Keep the keys as-is and change the values to match the type specified")
                print("Then, pass this file in as the --inputs option:\n")
            print(json.dumps(error.missing, indent=4))
    if cli.action == 'parse':
        with open(cli.wdl_file) as fp:
            ast = wdl.parser.parse(fp.read(), os.path.basename(cli.wdl_file)).ast()
            print(ast.dumps(indent=2))

if __name__ == '__main__':
    cli()
