"""Serializer for EmailNotification model"""
from ...models import EmailNotification

from rest_framework import serializers


class EmailNotificationSerializer(serializers.ModelSerializer):

    """Serializes EmailNotification objects. Just renders public_id as id and the email address"""

    class Meta(object):

        """Some model meta"""

        model = EmailNotification
        fields = ('email',)
