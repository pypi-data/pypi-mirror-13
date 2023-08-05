'''
    Copyright (c) 2015 Timothy Savannah under terms of LGPLv2. You should have received a copy of this LICENSE with this distribution.

    Contains pure-python functions for non-blocking IO in python
'''
# vim: ts=4 sw=4 expandtab


from .read import nonblock_read

from .BackgroundWrite import bgwrite, bgwrite_chunk, BackgroundIOPriority

__all__ = ('nonblock_read', 'bgwrite', 'bgwrite_chunk', 'BackgroundIOPriority')

__version__ = '2.0.0'
__version_tuple = (2, 0, 0)

