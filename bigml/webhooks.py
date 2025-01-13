# -*- coding: utf-8 -*-
#
# Copyright 2022-2025 BigML
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

"""Utilities for webhooks

"""
import json
import hmac

try:
    from hashlib import sha1
except ImportError:
    import sha
    sha1 = sha.sha


SORTING_SEQUENCE = ["timestamp", "message", "resource", "event"]


def dict_to_msg(obj):
    """Builds a representation of the dict object in a specific key sequence"""
    pair_list = []
    for key in SORTING_SEQUENCE:
        pair_list.append("'%s': '%s'" % (key, obj.get(key)))
    return "{%s}" % ", ".join(pair_list)


def compute_signature(msg, secret, encoding="utf-8"):
    """Computes the signature used by BigML when issuing the webhook call"""
    return hmac.new(
        secret.encode(encoding),
        msg=msg.encode(encoding),
        digestmod=sha1
    ).hexdigest()


def check_signature(request, secret):
    """Checks the signature when the webhook has been given one"""
    sig_header = request.meta['HTTP_X_BIGML_SIGNATURE'].replace('sha1=', '')
    payload = request.body
    computed_sig = compute_signature(payload, secret)
    if sig_header == computed_sig:
        return True
    # code for old version of the msg hash
    payload = dict_to_msg(json.loads(payload))
    computed_sig = compute_signature(payload, secret)
    if sig_header == computed_sig:
        return True
    return False
