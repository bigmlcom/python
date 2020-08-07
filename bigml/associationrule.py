# -*- coding: utf-8 -*-
#
# Copyright 2015-2020 BigML
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

SUPPORTED_LANGUAGES = ["JSON", "CSV"]

class AssociationRule(object):
    """ Object encapsulating an association rule as described in
        https://bigml.com/developers/associations

    """

    def __init__(self, rule_info):
        self.rule_id = rule_info.get('id')
        self.confidence = rule_info.get('confidence')
        self.leverage = rule_info.get('leverage')
        self.lhs = rule_info.get('lhs', [])
        self.lhs_cover = rule_info.get('lhs_cover', [])
        self.p_value = rule_info.get('p_value')
        self.rhs = rule_info.get('rhs', [])
        self.rhs_cover = rule_info.get('rhs_cover', [])
        self.lift = rule_info.get('lift')
        self.support = rule_info.get('support', [])

    def out_format(self, language="JSON"):
        """Transforming the rule structure to a string in the required format

        """
        if language in SUPPORTED_LANGUAGES:
            return getattr(self, "to_%s" % language.lower())()
        return self

    def to_csv(self):
        """Transforming the rule to CSV formats
           Metrics ordered as in ASSOCIATION_METRICS in association.py

        """
        output = [self.rule_id, self.lhs, self.rhs,
                  self.lhs_cover[0] if self.lhs_cover else None,
                  self.lhs_cover[1] if self.lhs_cover else None,
                  self.support[0] if self.support else None,
                  self.support[1] if self.support else None,
                  self.confidence,
                  self.leverage,
                  self.lift,
                  self.p_value,
                  self.rhs_cover[0] if self.rhs_cover else None,
                  self.rhs_cover[1] if self.rhs_cover else None
                 ]
        return output

    def to_json(self):
        """Transforming the rule to JSON

        """
        rule_dict = {}
        rule_dict.update(self.__dict__)
        return rule_dict

    def to_lisp_rule(self, item_list):
        """Transforming the rule in a LISP flatline filter to select the
        rows in the dataset that fulfill the rule

        """

        items = [item_list[index].to_lisp_rule() for index in self.lhs]
        rhs_items = [item_list[index].to_lisp_rule() for index in self.rhs]
        items.extend(rhs_items)
        return "(and %s)" % "".join(items)
