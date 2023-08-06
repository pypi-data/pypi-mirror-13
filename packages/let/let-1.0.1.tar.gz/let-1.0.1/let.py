def let(**nameValuePair):
    '''
    Takes in a single name = value pair. The value is assigned to the name and
    returned. This is useful in if statements, while loops, and anyplace else
    where you want to both assign and use a value. Examples:

    Instead of:

        name = longInstanceName.longAttributeName
        if name:
            ...

    - Or worse, using that long identifier in the condition and then repeatedly
    in the body - you can use this:

        if let(name = longInstanceName.longAttributeName):
            ...

    Instead of:

        results = dbConnection.fetch_results():
        while results:
            ...
            results = dbConnection.fetch_results()

    You can do this:

        while let(results = dbConnection.fetch_results):
            ...

    Instead of:

        if len(nameValuePair) != 1:
            raise Exception('Bad amount: {}'.format(len(nameValuePair)))

    You could use:

        if let(count = len(nameValuePair)) != 1:
            raise Exception('Bad amount: {}'.format(count))
    '''

    count = len(nameValuePair)
    if count != 1:
        raise TypeError('let() takes exactly one key = value pair ({} given)'
                        .format(count))

    name, value = nameValuePair.items()[0]

    from inspect import stack
    frame   = stack()[1][0]
    locals_ = frame.f_locals
    if name in locals_:
        raise Exception(name + ' has already been locally assigned. Due to '
                        'optimizations in the Python interpreter, it is not '
                        'possible to write over it using let(). Sorry!')
    else:
        frame.f_globals[name] = value

    return value