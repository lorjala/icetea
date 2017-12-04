"""
Copyright 2017 ARM Limited
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re

from icedtea_lib.Events.Generics import Observer


class EventMatcher(Observer):
    def __init__(self, event_type, match_data, caller=None,
                 flag=None, callback=None):
        Observer.__init__(self)
        self.caller = caller
        self.observe(event_type, self._event_received)
        self.event_type = event_type
        self.flag_to_set = flag
        self.callback = callback
        self.match_data = match_data

    def _event_received(self, ref, data):
        if self._resolve_match_data(ref, data):
            if self.flag_to_set:
                self.flag_to_set.set()
            if self.callback:
                self.callback(ref, data)
            self.forget()

    def _resolve_match_data(self, ref, event_data):
        """
        If match_data is prefixed with regex: compile it to a regular expression pattern.
        Match event data with match_data as either regex or string.

        :param ref: Reference to object that generated this event.
        :param event_data: Data from event, as string.
        :return: return True if match found, False if ref is not caller set for this Matcher or if
        no match was found.
        """
        if self.caller is None:
            pass
        elif ref is not self.caller:
            return False
        try:
            dat = event_data.decode("utf-8")
            if self.match_data.startswith("regex:"):
                splt = self.match_data.split(":", 1)
                pttrn = re.compile(splt[1])
                match = re.search(pttrn, dat)
                return True if match is not None else False
            else:
                return True if self.match_data in dat else False
        except UnicodeDecodeError:
            dat = repr(event_data)
            return self._resolve_match_data(ref, dat)