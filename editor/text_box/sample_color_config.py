dct = {
    (
        'abs', 'all', 'any', 'ascii', 'bin', 'bool',
        'bytearray', 'bytes', 'callable', 'chr', 'compile',
        'complex', 'dict', 'dir', 'divmod', 'enumerate',
        'eval', 'exec', 'print', 'range'
    ): {'fg': (72, 120, 170), 'bg': None}
}

for key_tuple, value in dct.items():
    for key in key_tuple:
        dct[key] = value
    del dct[key_tuple]


print(dct)
