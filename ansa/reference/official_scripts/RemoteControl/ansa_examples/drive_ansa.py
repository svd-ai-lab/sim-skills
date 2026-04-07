'''
Python 3 code that showcases the use of externally driving ANSA. Update the
ansa_exe variable to point to where you have ANSA installed if exconfig cannot
find it automatically.
'''

import sys
import os
import pickle

ap_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'ansa')
if ap_path not in sys.path:
    sys.path.append(ap_path)

from AnsaProcessModule import AnsaProcess, ScriptReturnType, PreExecutionDatabaseAction, PostConnectionAction

# A script that tries to find the location of the ANSA executable.
# Currently, works only for Windows.
import exconfig
ANSA_EXE = exconfig.get_app_location('ansa')

# Enter manually the path to the ANSA executable here.
#ANSA_EXE = ''


def main():
    # Establish the connection
    process = AnsaProcess(ansa_command=ANSA_EXE, run_in_batch=False)
    connection = process.get_iap_connection()

    # Establish the handshake
    response = connection.hello()
    if response.success() == False:
        print('Handshake failed (ResultCode %d)' % response.get_result_code())
        raise SystemExit(1)

    # Send the attached file for execution to the listening ANSA
    response = connection.run_script_file('test_script_ansa.py', 'main')
    if response.success() == True:
        _print_return_value(response)
    else:
        print('Script file execution failed (ResultCode %d) (ScriptExecutionDetails %d)' % (response.get_result_code(), response.get_script_execution_details()))

    # Send the attached file for execution to the listening ANSA
    response = connection.run_script_file('test_script_bytes_ansa.py', 'main', PreExecutionDatabaseAction.keep_database)
    if response.success() == True:
        _print_return_value(response)
    else:
        print('Script file execution failed (ResultCode %d) (ScriptExecutionDetails %d)' % (response.get_result_code(), response.get_script_execution_details()))

    # Send a single python command for execution to the listening ANSA
    response = connection.run_script_text("print('Hello World')")
    if response.success() == False:
        print('Script text execution failed (ResultCode %d)' % response.get_result_code())

    # Send multiple python lines for execution to the listening ANSA
    response = connection.run_script_text("def main():\n print('main is called')", "main")
    if response.success() == False:
        print('Script text execution failed (ResultCode %d)' % response.get_result_code())

    # Terminate the connection
    response = connection.goodbye(PostConnectionAction.shut_down)
    if response.success() == False:
        print('Goodbye failed (ResultCode %d)' % response.get_result_code())


def _print_return_value(response):
    
    return_type = response.get_script_return_type()
    
    if return_type == ScriptReturnType.string_dict:
        print('Script returned the dictionary: ', response.get_response_dict())
    elif return_type == ScriptReturnType.type_bytes:
        print('Script returned the value: ', pickle.loads(response.get_response_bytes()))
    elif return_type == ScriptReturnType.none:
        print('Script returned None')
    elif return_type == ScriptReturnType.unsupported:
        print('Script returned unsupported value')


if __name__ == '__main__':
    main()
