easy_map = {
    (
        'abs', 'all', 'any', 'ascii', 'bin', 'bool',
        'bytearray', 'bytes', 'callable', 'chr', 'compile',
        'complex', 'dict', 'dir', 'divmod', 'enumerate',
        'eval', 'exec', 'print', 'range'
    ): {'fg': (72, 120, 170), 'bg': None}
}

dct = {}
for key_tuple, value in easy_map.items():
    for key in key_tuple:
        dct[key] = value
