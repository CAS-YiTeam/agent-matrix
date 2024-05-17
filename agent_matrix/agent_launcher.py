import os
import sys
import argparse
import traceback
import cloudpickle as pickle
import base64

if __name__ == "__main__":

    def validate_path():
        dir_name = os.path.dirname(__file__)
        root_dir_assume = os.path.abspath(dir_name + "/..")
        os.chdir(root_dir_assume)
        sys.path.append(root_dir_assume)
    validate_path()  # return to project root

    from agent_matrix.shared.dynamic_import import hot_reload_class

    # Define the command-line argument parser
    parser = argparse.ArgumentParser(
        description='Take Agent ID, class or script path, and a string.')

    # Add the command-line arguments
    parser.add_argument('-i', '--agent-id', type=str, help='Agent ID')
    parser.add_argument('-c', '--agent-class', type=str)
    parser.add_argument('-t', '--matrix-host', type=str)
    parser.add_argument('-p', '--matrix-port', type=str)
    parser.add_argument('-s', '--agent-kwargs', type=str)

    # Parse the command-line arguments
    args = parser.parse_args()

    # Print the parsed inputs
    agent_id = args.agent_id
    agent_class = pickle.loads(base64.b64decode(args.agent_class))
    agent_kwargs = pickle.loads(base64.b64decode(args.agent_kwargs))
    matrix_host = args.matrix_host
    matrix_port = args.matrix_port
    agent_init_kwargs = {
        "agent_id": agent_id,
        "matrix_host": matrix_host,
        "matrix_port": matrix_port,
        "is_proxy": False,
    }
    agent_init_kwargs.update(agent_kwargs)
    if isinstance(agent_class, str):
        agent = hot_reload_class(agent_class)(**agent_init_kwargs)
    else:
        agent = (agent_class)(**agent_init_kwargs)

    try:
        agent.run()
    except KeyboardInterrupt:
        print('\nKeyboardInterrupt: Exiting...\n')
        print('---------------------------------')
        print(agent_id)
        traceback.print_exc()
        print('---------------------------------')
