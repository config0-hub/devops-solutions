#!/usr/bin/env python

import os

def mkdir(directory):
    """
    Creates a directory using shell command 'mkdir -p'.

    Args:
        directory (str): Path of the directory to create.

    Returns:
        bool: True if directory creation was successful or directory already exists,
              False if an error occurred.

    Notes:
        Uses '-p' flag to create parent directories as needed without error.
    """
    try:
        if not os.path.exists(directory):
            os.system(f"mkdir -p {directory}")
        return True
    except Exception:
        return False


def rm_rf(location):
    """
    Forcefully and recursively removes a file or directory using shell command 'rm -rf'.

    Args:
        location (str): Path of file or directory to remove.

    Returns:
        bool or None: 
            - True if removal was successful
            - False if removal failed
            - None if location is empty or doesn't exist

    Notes:
        First attempts to use os.remove(), falls back to shell 'rm -rf' command if that fails.
        Redirects stderr and stdout to /dev/null when using shell command.
    """
    if not location:
        return

    if not os.path.exists(location):
        return

    try:
        os.remove(location)
        status = True
    except Exception:
        status = False

    if status:
        return True

    if os.path.exists(location):
        try:
            os.system(f"rm -rf {location} > /dev/null 2>&1")
            status = True
        except Exception:
            print(f"problems with removing {location}")
            status = False

        return status

def system_exec(command, raise_on_error=True):
    """
    Executes a shell command and handles the return status.

    Args:
        command (str): Shell command to execute.
        raise_on_error (bool, optional): If True, raises RuntimeError on non-zero exit code.
                                       Defaults to True.

    Returns:
        dict: Dictionary containing:
            - status (bool): True if exitcode is 0, False otherwise
            - exitcode (int): The command's exit code

    Raises:
        RuntimeError: If command returns non-zero exit code and raise_on_error is True.

    Notes:
        Extracts exit code from system call return value using binary manipulation.
    """
    _return = os.system(command)

    # Calculate the return value code
    exitcode = int(bin(_return).replace("0b", "").rjust(16, '0')[:8], 2)

    if exitcode != 0 and raise_on_error:
        failed_msg = f'The system command\n{command}\nexited with return code {exitcode}'
        raise RuntimeError(failed_msg)

    results = {"status":True}

    if exitcode != 0:
        results = {"status":False}

    results["exitcode"] = exitcode

    return results
