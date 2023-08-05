QuickVars
=========

| Python 3 variable storage module centered around the in-built
  ``pickle`` module.
| This module contains 3 functions: "``QuickVars.setVar()``",
  "``QuickVars.getVar()``", and "``QuickVars.delVar()``".
| Though very self-explanitory, more details on each function are below.

QuickVars.setVar(key, val, t = 'data')
--------------------------------------

::

    @param key : The key param is used as the key in a Dictionary, choose your datatype
                 accordingly.
     
    @param val : The val param takes the data stored under the key, and can be any Dictionary
                 compatible value.
     
    @param t   : The t param chooses the file to store the key-value pair in.
     
    @returns   : Dictionary containing values stored in the file.

    The setVar function will take a minimum of two params (key, val), and has an optional
    param (t). The key-value pairs will be added to an encoded (Please note: Strictly speaking
    it is not encrypted and should not be considered safe to store valuable information) JSON
    file at: "data/{Script Name Without Extension}_{t}.dat".

QuickVars.getVar(key, t = 'data')
---------------------------------

::

    @param key : The key to search for in stored dictionary.

    @param t   : The t param chooses the file to search for the key-value pair in.

    @returns   : Stored Value (May be one of many data types).

    The getVar function will take a minimum of one param (key), and has an optional param (t). The
    function will search the chosen files dictionary for the key and return it if found, otherwise
    return 'None'.

QuickVars.delVar(key, t = 'data')
---------------------------------

::

    @param key : The key to remove from stored dictionary.

    @param t   : The t param chooses the file to search for the key-value pair in.

    @returns   : Stored Dictionary after attempting to remove indicated key.

    The delVar function will take a minimum of one param (key), and has an optional param (t). The
    function will search the chosen files dictionary for the key and delete it if found, returning
    the dictionary.

Examples
========

::

    import QuickVars as QV

    lst = []
    for (i in range(20)):
        lst.append(i)
    QV.setVar('test', lst)
    # Returns: {'test': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]}

    print(QV.getVar('test'))
    # Outputs: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]

    QV.setVar('test1', '5*9.2=' + str(5*9.2))
    # Returns: {'test': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19], 'test1': '5*9.2=46.0'}

    QV.setVar('test', 'different value here!', 'foo')
    # Returns: {'test': 'different value here!'}

    QV.delVar('test', 'data')
    # Return: {'test1': '5*9.2=46.0'}