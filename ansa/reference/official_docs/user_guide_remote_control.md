# ANSA Listener Mode

## Introduction to Remote Control

ANSA offers the capability to be executed in Listener Mode, which enables it to be remotely controlled.
Specifically, a user can remotely “stream” Python code or Python scripts to an ANSA running in Listener Mode.

This procedure can be accomplished by using the **AnsaProcessModule.py**, which can be found in the ANSA installation directory, under the path: **/scripts/RemoteControl/ansa/AnsaProcessModule.py**.

> **Note:** 
Running ANSA in Listener Mode is not restricting it in any way. It is just enhancing its capabilities.

## Connection Establishment Options

There are two distinct options in order to establish a connection with an ANSA running in Listener Mode.

- The first one is to externally launch ANSA in Listener mode, by using the command **-listenport **, and attach to it afterwards through a user script.

- The second one is to launch ANSA in Listener mode, directly from the user script, either in GUI or in no-GUI mode.

### Launching ANSA externally

In the case of “serving” an externally launched ANSA, the user should firstly launch ANSA, by adding the command -listenport and a port number.

For example:

```bash
ansa.sh -listenport 9999
```

Then attach to it, by using the class **IAPConnection** from the **AnsaProcessModule.py**

```python
from AnsaProcessModule import IAPConnection

connection = IAPConnection(9999)
```

### Launching ANSA through the user script

In the case of “driving” ANSA, the user has to launch ANSA by using the class **AnsaProcess** and then acquire the IAP Connection.

The following code has to be executed:

```python
from AnsaProcessModule import AnsaProcess

ANSA_EXE = '/home/user/path/to/ansa64.sh'

def main():
    process = AnsaProcess(ansa_command=ANSA_EXE, run_in_batch=False)
    connection = process.get_iap_connection()
```

Where **“ANSA_EXE”** holds the path to the ansa executable and the argument **“run_in_batch”** defines whether ANSA will be launched in GUI or no-GUI.

### Handshake protocol

In both cases, after the connection establishment, a handshake protocol must be established, initiating with a hello message and terminating with a goodbye one.

In between, all the remote code execution takes place.

```python
# Establish the handshake
response = connection.hello()
if response.success() == False:
    print('Handshake failed (ResultCode %d)' % response.get_result_code())
    raise SystemExit(1)

.
.
.

# Terminate the connection
response = connection.goodbye(PostConnectionAction.keep_listening)
if response.success() == False:
    print('Goodbye failed (ResultCode %d)' % response.get_result_code())
```

## Usage Examples

After successfully establishing a connection with an ANSA running in Listener mode, it is time to stream the Python code to it.

The user can either execute single or multiple Python commands, or execute a function from a complete Python module.

### Executing a single Python command

In order to execute a typical **‘Hello World’** statement, the following code has to be used.

```python
response = connection.run_script_text("print('Hello World')")
if response.success() == False:
    print('Script text execution failed (ResultCode %d)' % response.get_result_code())
```

After each execution, the response is examined to determine a possible failure.

### Executing multiple lines of Python code

Accordingly, multiple lines of code can be sent for execution, together with the function’s name to be executed.

```python
response = connection.run_script_text("def main():\n print('main is called')", "main")
if response.success() == False:
    print('Script text execution failed (ResultCode %d)' % response.get_result_code())
```

### Executing Python script files

However, the most useful part is sending a whole python module for execution, while defining the function’s name to be executed.

```python
response = connection.run_script_file('test_script_ansa.py', 'main')
if response.success() == True:
    return_type = response.get_script_return_type()

    if return_type == ScriptReturnType.string_dict:
        print('Script returned the dictionary: ', response.get_response_dict())
    elif return_type == ScriptReturnType.type_bytes:
        print('Script returned the value: ', pickle.loads(response.get_response_bytes()))
    elif return_type == ScriptReturnType.none:
        print('Script returned None')
    elif return_type == ScriptReturnType.unsupported:
        print('Script returned unsupported value')
else:
    print('Script file execution failed (ResultCode %d) (ScriptExecutionDetails %d)' % (response.get_result_code(), response.get_script_execution_details()))
```

Besides the response examination, there is also a return type examination.

That’s because the python function that is remotely executed, can only return a dictionary with strings as keys and values, or a bytes object constructed through the pickle module.

Every other data type is unsupported.

> **Note:** 
All the aforementioned examples’ code can be found in the ANSA installation directory, under the path: **/scripts/RemoteControl/ansa_examples/**