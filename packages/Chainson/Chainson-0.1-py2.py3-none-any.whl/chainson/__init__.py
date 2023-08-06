from __future__ import absolute_import

from abc import ABCMeta, abstractmethod
from datetime import datetime
from json import JSONEncoder as JSONEncoder, dump, dumps

from future.builtins import super
from six import add_metaclass


class JSONEncoderChain(JSONEncoder):
    def __init__(self, skipkeys=False, ensure_ascii=True,
                 check_circular=True, allow_nan=True, sort_keys=False,
                 indent=None, separators=None, default=None):
        super().__init__(skipkeys, ensure_ascii, check_circular, allow_nan, sort_keys, indent, separators, default)
        self._encoders = []

    def add_encoder(self, encoder):
        if not isinstance(encoder, (tuple, AbstractJSONEncoderWithChecker)):
            raise TypeError("encoder must be either (chk_f, enc_f) or AbstractEncoderWithChecker")
        self._encoders.append(encoder)
        return self

    def default(self, o):
        for encoder in self._encoders:
            if isinstance(encoder, tuple):
                chk_f, enc_f = encoder
            elif isinstance(encoder, AbstractJSONEncoderWithChecker):
                chk_f, enc_f = encoder.chk, encoder.enc
            else:
                continue
            if chk_f(o):
                return enc_f(o)
        else:
            return JSONEncoder.default(self, o)

    def dumps(self, o, **kwargs):
        return dumps(o, default=self.default, **kwargs)

    def dump(self, o, fp, **kwargs):
        return dump(o, fp, default=self.default, **kwargs)


@add_metaclass(ABCMeta)
class AbstractJSONEncoderWithChecker(JSONEncoder):
    @abstractmethod
    def chk(self, o):
        pass

    @abstractmethod
    def enc(self, o):
        pass

    def default(self, o):
        return self.enc(o) if self.chk(o) else JSONEncoder.default(self, o)


class DateTimeJSONEncoder(AbstractJSONEncoderWithChecker):
    def chk(self, o):
        return isinstance(o, datetime)

    def enc(self, o):
        return o.isoformat()
