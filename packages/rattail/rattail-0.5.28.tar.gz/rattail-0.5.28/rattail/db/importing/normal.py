# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Rattail Data Normalization
"""

from __future__ import unicode_literals, absolute_import


class Normalizer(object):
    """
    Base class for data normalizers.
    """

    def normalize(self, instance):
        raise NotImplementedError


class UserNormalizer(Normalizer):
    """
    Normalizer for user data.
    """
    # Must set this to the administrator Role instance.
    admin = None

    def normalize(self, user):
        return {
            'uuid': user.uuid,
            'username': user.username,
            'password': user.password,
            'salt': user.salt,
            'person_uuid': user.person_uuid,
            'active': user.active,
            'admin': self.admin in user.roles,
        }


class MessageNormalizer(Normalizer):
    """
    Normalizer for message data.
    """

    def normalize(self, message):
        return {
            'uuid': message.uuid,
            'sender_uuid': message.sender_uuid,
            'subject': message.subject,
            'body': message.body,
            'sent': message.sent,
        }


class MessageRecipientNormalizer(Normalizer):
    """
    Normalizer for message recipient data.
    """

    def normalize(self, recip):
        return {
            'uuid': recip.uuid,
            'message_uuid': recip.message_uuid,
            'recipient_uuid': recip.recipient_uuid,
            'status': recip.status,
        }
