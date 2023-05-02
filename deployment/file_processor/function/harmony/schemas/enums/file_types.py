from enum import Enum


class FileType(str, Enum):
    pdf: str = 'pdf'
    xlsx: str = 'xlsx'
    txt: str = 'txt'