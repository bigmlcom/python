# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2015 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Association Rule object.

   This module defines each Rule in an Association Rule.
"""

class AssociationRule(object):
    """ Object encapsulating an association rules as described in
        https://bigml.com/developers/associations

    """

    def __init__(self, rule_info):
        self.leverage = rule_info.get('leverage')
        self.lhs = rule_info.get('lhs', [])
        self.lhs_cover = rule_info.get('lhs_cover')
        self.lhs_desc = rule_info.get('lhs_desc', [])
        self.p_value = rule_info.get('p_value')
        self.rhs = rule_info.get('rhs', [])
        self.rhs_cover = rule_info.get('rhs_cover')
        self.rhs_desc = rule_info.get('rhs_desc', [])
        self.strength = rule_info.get('strength')
        self.support = rule_info.get('support')

    def out_format(self, language="JSON"):
        """Transforming the rule structure to a string in the required format

        """
        if language == "JSON":
            rule_dict = {}
            rule_dict.update(self.__dict__)
            return rule_dict

        if language == "CSV":
            output = [self.leverage, self.lhs_cover,
                      " and ".join(self.lhs_desc), self.p_value,
                      self.rhs_cover, "and".join(self.rhs_desc), self.strength,
                      self.support]
            return output
        return self
