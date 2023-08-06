###
# Copyright (c) 2016, Valentin Lorentz
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
try:
    from supybot.i18n import PluginInternationalization
    _ = PluginInternationalization('Lists')
except ImportError:
    # Placeholder that allows to run the plugin on a bot
    # without the i18n module
    _ = lambda x: x


class Lists(callbacks.Plugin):
    """Utilities for dealing with lists."""
    
    @wrap(['int', optional('int'), optional('int')])
    def range(self, irc, msg, args, arg1, arg2, step):
        """[start] end [step]

        Returns a range, from start (defaults to 0) to end, using a
        step (defaults to 1)."""
        if arg2 is None:
            (start, end) = (0, arg1)
        else:
            (start, end) = (arg1, arg2)
        if step is None:
            step = 1
        maximum = self.registryValue('range.maximum')
        minimum = self.registryValue('range.minimum')
        if end > maximum or start > maximum:
            irc.error(_('Range contains values larger than allowed by '
                'supybot.plugins.Lists.range.maximum'), Raise=True)
        if end < minimum or end < minimum:
            irc.error(_('Range contains values larger than allowed by '
                'supybot.plugins.Lists.range.minimum'), Raise=True)
        if step == 0:
            irc.error(_('Step cannot be zero.'), Raise=True)
        if (end - start)/step > self.registryValue('range.maximumLength'):
            irc.error(_('Range is longer than allowed by '
                'supybot.plugins.Lists.range.maximumLength'), Raise=True)
        irc.replies(list(map(str, range(start, end, step))))

    @wrap(['something', 'something'])


Class = Lists


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
