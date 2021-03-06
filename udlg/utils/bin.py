# -*- coding: utf-8 -*-
"""
.. module:: udlg.utils.bin
    :synopsis: Binary utils
    :platform: Linux, Unix, Windows
.. moduleauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
.. sectionauthor:: Nickolas Fox <tarvitz@blacklibary.ru>
"""
from struct import unpack
from collections import deque
from functools import partial

from ..structure.constants import BYTE_SIZE


def search(sequence, stream, stream_offset=0x0):
    """
    process simple search sequence inside stream

    :param stream: stream object, file
    :param bytes | str sequence: binary sequence to find
    :param int stream_offset: stream offset where process should start from,
        0x0 by default
    :rtype: int
    :return: index or offset found sequence
    :raise IndexError:
        - if nothing was found
    """
    if isinstance(sequence, str):
        sequence = bytes(sequence.encode('utf-8'))
    elif isinstance(sequence, bytes):
        pass
    else:
        raise TypeError("`sequence` should be str, bytes "
                        "instance")

    chunk_size = 1
    pos = stream.tell()
    offset = 0
    stream.seek(stream_offset)
    # byte = stream.read(1)
    stream_by_byte = partial(stream.read, chunk_size)
    to_int = partial(int.from_bytes, byteorder='little')
    sequence_length = len(sequence)
    found = -1
    for sign in iter(stream_by_byte, b''):
        byte = to_int(sign)
        if offset == sequence_length:
            found = stream.tell() - (len(sequence) + 1)
            break
        if offset < sequence_length and byte == sequence[offset]:
            offset += 1
        elif offset and byte != sequence[offset]:
            offset = 0
        else:
            pass
    else:
        raise IndexError("sequence `%r` not found" % sequence)
    stream.seek(pos)
    return found


def search_all(sequence, stream):
    """
    search all sequence pattern inside stream

    :param stream: stream object, file
    :param bytes | str sequence: sequence to found
    :rtype: list
    :return: list of found position inside stream for given sequence
    """
    if isinstance(sequence, str):
        sequence = bytes(sequence.encode('utf-8'))
    elif isinstance(sequence, bytes):
        pass
    else:
        raise TypeError('sequences should be str or bytes instance')

    last_offset = 0x0
    indexes = []
    sequence_length = len(sequence)
    while 1:
        try:
            last_offset = search(
                sequence, stream, stream_offset=last_offset + sequence_length
            )
            indexes.append(last_offset)
        except IndexError:
            break
    return indexes


def read_7bit_encoded_int_from_stream(stream):
    """
    read int with 7 bit encoded format from stream

    :param stream: stream object, file for example
    :rtype: int
    :return: int

    .. code-block:: c
        do {
            b = ReadUByte(pos);
            ++pos;
            ++amount;
            entryLength |= (uint)(b & 127) << offset;
            offset += 7;
            if ((b & 128) == 0){
                break;
            }
        } while( offset != 35);
    """
    b, = unpack('B', stream.read(BYTE_SIZE))
    entry, offset = 0, 0
    while offset != 35:
        entry |= (b & 127) << offset
        offset += 7
        if (b & 128) == 0:
            break
        b, = unpack('B', stream.read(BYTE_SIZE))
    return entry


def read_7bit_encoded_int(source):
    """
    read int with 7 bit encoded format

    :param bytes source:
    :rtype: int
    :return: encoded value
    """
    src = deque(source[::-1])
    num2 = 0
    num = 0
    while num2 != 35:
        byte = src.pop()
        num |= (byte & 127) << num2
        num2 += 7
        if (byte & 128) == 0:
            return num


#: todo: improve
def write_7bit_int(value):
    """
    encode value to 7bit encoded bytestring representing this value

    :param int value: value to encode
    :rtype: bytes
    :return: byte
    """
    temp = value
    byte_storage = b''

    while temp >= 128:
        byte_storage += chr(0x000000FF & (temp | 0x80)).encode('latin1')
        temp >>= 7
    byte_storage += bytes(chr(temp).encode('latin1'))
    return byte_storage
