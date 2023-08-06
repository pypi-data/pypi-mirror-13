# -*- coding: utf-8 -*-

import sys
import time

from tbutils import ExceptionInfo, Callpoint

from common import DEBUG, INFO, CRITICAL
from formatters import Formatter


class DefaultException(Exception):
    "Only used when traceback extraction fails"


class Record(object):
    """The ``Record`` type is one of the three core Lithoxyl types, and
    the underlying currency of the Lithoxyl system. Records are
    usually instantiated through convenience methods on
    :class:`~lithoxyl.logger.Logger` instances, and most
    instrumentation will be done through populating records with
    relevant data.

    Args:
        name (str): The name of the Record.
        level: Log level of the Record. Generally one of
            :data:`~lithoxyl.common.DEBUG`,
            :data:`~lithoxyl.common.INFO`, or
            :data:`~lithoxyl.common.CRITICAL`. Defaults to ``None``.
        logger: The Logger instance responsible for creating (and
            publishing) the Record.
        status (str): State of the task represented by the Record. One
            of 'begin', 'success', 'failure', or 'exception'. Defaults
            to 'begin'.
        extras (dict): A mapping of non-builtin fields to user
            values. Defaults to ``{}`` and can be populated after
            Record creation by accessing the Record like a ``dict``.
        raw_message (str): A message or message template that further
            describes the status of the record.
            Defaults to ``'<name> <status>'``, using the values above.
        message (str): A pre-formatted message that similar to
            *raw_message*, but will not be treated as a template.
        begin_time (float): A timestamp of when the Record was created
            or started. Defaults to the output of :func:`time.time`.
        end_time (float): A timestamp of when the Record was
            completed, assuming it is a transactional record. Defaults
            to ``None``, which is valid when a record is incomplete or
            is not transactional and thus has no duration.
        duration (float): The duration of the record. Defaults to ``0.0``.
        frame: Frame of the callpoint creating the Record. Defaults to
            the caller's frame.
        reraise (bool): Whether or not the Record should catch and
            reraise exceptions. Defaults to ``True``. Setting to
            ``False`` will cause all exceptions to be caught and
            logged appropriately, but not reraised. This should be
            used to eliminate ``try``/``except`` verbosity.

    All additional keyword arguments are automatically included in the
    Record's ``extras`` attribute.

    >>> record = Record('our_mission', CRITICAL, mission='explore new worlds')

    Most of these parameters are managed by the Records and respective
    Loggers themselves. While they are provided here for advanced use
    cases, usually only the *name*, *raw_message*, *reraise*, and
    extra values should be provided.

    Records are :class:`dict`-like, and can be accessed as mappings
    and used to store additional structured data:

    >>> record['my_data'] = 20.0
    >>> record['my_lore'] = -record['my_data'] / 10.0
    >>> from pprint import pprint
    >>> pprint(record.extras)
    {'mission': 'explore new worlds', 'my_data': 20.0, 'my_lore': -2.0}
    """
    _is_trans = None
    _defer_publish = False

    def __init__(self, name, level=None, **kwargs):
        # TODO: default level
        self.name = name
        self.level = level
        self.logger = kwargs.pop('logger', None)
        self.status = kwargs.pop('status', 'begin')
        try:
            self.raw_message = kwargs.pop('raw_message')
        except:
            self.raw_message = '%s %s' % (name, self.status)
        self._message = kwargs.pop('message', None)
        self.extras = kwargs.pop('extras', {})
        self.begin_time = kwargs.pop('begin_time', time.time())
        self.end_time = kwargs.pop('end_time', None)
        # TODO: make end_time - begin_time if end_time is not None?
        self.duration = kwargs.pop('duration', 0.0)
        self._reraise = kwargs.pop('reraise', True)
        self.warnings = []

        self.exc_info = None

        frame = kwargs.pop('frame', None)
        if frame is None:
            frame = sys._getframe(1)
        # TODO: should Callpoint actually be at __exit__?
        self.callpoint = Callpoint.from_frame(frame)

        if kwargs:
            self.extras.update(kwargs)

    def __repr__(self):
        cn = self.__class__.__name__
        # TODO on the upper() stuff. better repr for level?
        return ('<%s %r %s %r>'
                % (cn, self.name, self.level.name.upper(), self.status))

    @property
    def level_name(self):
        try:
            return self.level.name
        except:
            return repr(self.level)

    def warn(self, message):
        "Append a warning *message* to the warnings tracked by this record."
        self.warnings.append(message)
        return self

    def success(self, message=None, *a, **kw):
        """Mark this Record as complete and successful. Also set the Record's
        *message* template. Positional and keyword arguments will be
        used to generate the formatted message. Keyword arguments will
        also be added to the Record's ``extras`` attribute.

        >>> record = Record('important_task', CRITICAL)
        >>> record.success('{record_name} {status_str}: {0} {my_kwarg}', 'this is', my_kwarg='fun')
        <Record CRITICAL 'success'>
        >>> record.message
        u'important_task success: this is fun'
        """
        if not message:
            message = self.name + ' succeeded'  # TODO: localize
        return self._complete('success', message, *a, **kw)

    def failure(self, message=None, *a, **kw):
        """Mark this Record as complete and failed. Also set the Record's
        *message* template. Positional and keyword arguments will be
        used to generate the formatted message. Keyword arguments will
        also be added to the Record's ``extras`` attribute.

        >>> record = Record('important_task', CRITICAL)
        >>> record.failure('{record_name} {status_str}: {0} {my_kwarg}', 'this is', my_kwarg='no fun')
        <Record CRITICAL 'failure'>
        >>> record.message
        u'important_task failure: this is no fun'
        """
        if not message:
            message = self.name + ' failed'
        return self._complete('failure', message, *a, **kw)

    def exception(self, message=None, *a, **kw):
        """Mark this Record as complete and having had an exception. Also
        sets the Record's *message* template similar to
        :meth:`Record.success` and :meth:`Record.failure`.

        Unlike those two attributes, this method is rarely called
        explicitly by application code, because the context manager
        aspect of the Record catches and sets the appropriate
        exception fields. When called explicitly, this method should
        only be called in an :keyword:`except` block.
        """
        return self._exception(None, message, *a, **kw)

    def _exception(self, exc_info, message, *a, **kw):
        if not exc_info:
            exc_info = sys.exc_info()
        try:
            exc_type, exc_val, exc_tb = exc_info
        except:
            exc_type, exc_val, exc_tb = (None, None, None)
        exc_type = exc_type or DefaultException

        self.logger.on_exception(self, exc_type, exc_val, exc_tb)

        self.exc_info = ExceptionInfo.from_exc_info(exc_type, exc_val, exc_tb)
        if not message:
            message = '%s raised exception: %r' % (self.name, exc_val)
        return self._complete('exception', message, *a, **kw)

    def _complete(self, status, message=None, *a, **kw):
        self._pos_args = a
        self.extras.update(kw)
        if self._is_trans:
            self.end_time = time.time()
            self.duration = self.end_time - self.begin_time
        else:
            self.end_time, self.duration = self.begin_time, 0.0
        self.status = status
        if message is None:
            message = u''
        elif not isinstance(message, unicode):
            # TODO: use to_unicode
            # if you think this is excessive, see the issue with the
            # unicode constructor as semi-detailed here:
            # http://pythondoeswhat.blogspot.com/2013/09/unicodebreakers.html
            try:
                message = str(message).decode('utf-8', errors='replace')
            except:
                message = unicode(object.__repr__(message))  # space nuke
        self.raw_message = message
        if not self._defer_publish and self.logger:
            self.logger.on_complete(self)
        return self

    @property
    def message(self):
        # TODO: will have to invalidate this on record status change
        if self._message is not None:
            return self._message
        raw_message = self.raw_message
        if raw_message is None:
            return None

        if '{' not in raw_message:  # yay premature optimization
            self._message = raw_message
        else:
            # TODO: Formatter cache
            fmtr = Formatter(raw_message, quoter=False)
            args = getattr(self, '_pos_args', [])
            self._message = fmtr.format_record(self, *args)
        return self._message

    def __enter__(self):
        self._is_trans = self._defer_publish = True
        if self.logger:
            self.logger.on_begin(self)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: handle logger = None
        self._defer_publish = False
        if exc_type:
            # then, normal completion behavior
            exc_info = (exc_type, exc_val, exc_tb)
            try:
                self._exception(exc_info, message=None)
            except:
                # TODO: something? grasshopper mode maybe.
                pass
            # TODO: should probably be three steps:
            # set certain attributes, then do on_exception, then do completion.
        elif self.status is 'begin':
            self.success()
        else:
            # TODO: a bit questionable
            self._complete(self.status, self.message)
        if self._reraise is False:
            return True  # ignore exception
        return

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            return self.extras[key]

    def __setitem__(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.extras[key] = value

    def get_elapsed_time(self):
        """Simply get the amount of time that has passed since the record was
        created or begun. This method has no side effects.
        """
        return time.time() - self.begin_time

    @property
    def status_char(self):
        """A single-character representation of the status of the Record. See
        the ``status_chr`` field in the
        :class:`~lithoxyl.formatter.Formatter` field documentation for
        more details.
        """
        ret = '_'
        try:
            if self._is_trans:
                if self.end_time:
                    ret = self.status[:1].upper()
                else:
                    ret = 'b'
            else:
                ret = self.status[:1].lower()
        except:
            pass
        return ret

    @property
    def warn_char(self):
        "``'W'`` if the Record has warnings, ``' '`` otherwise."
        return 'W' if self.warnings else ' '
