# coding=utf-8
from notifications.transports import BaseTransport
from .models import GroupFeedItem, SocialGroup


class GroupFeedTransport(BaseTransport):

    @staticmethod
    def send_notification(group, role, event, template, delay=False):
        if group is None or not isinstance(group, SocialGroup) or event is None or template is None:
            return
        try:
            feed_item = GroupFeedItem(group=group, event=event, template_config=template)
            feed_item.save()
        except:
            pass  # TODO Log
