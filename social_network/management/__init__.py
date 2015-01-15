# coding=utf-8
from django.db.models.signals import post_syncdb
from django.conf import settings
from .. import models as social_app

AUTOCONFIGURE_NOTIFICATIONS = getattr(settings, 'SOCIAL_NETWORK_AUTOCONFIGURE_NOTIFICATIONS', True)
COMMENT_ACTION_READ_AS = getattr(settings, 'SOCIAL_NETWORK_COMMENT_ACTION_READ_AS', 'Comment')
PHOTO_ACTION_READ_AS = getattr(settings, 'SOCIAL_NETWORK_PHOTO_ACTION_READ_AS', 'Image Post')
COMMENT_EVENT_READ_AS = getattr(settings, 'SOCIAL_NETWORK_COMMENT_EVENT_READ_AS', 'Community Comment')
PHOTO_EVENT_READ_AS = getattr(settings, 'SOCIAL_NETWORK_PHOTO_EVENT_READ_AS', 'Community Image Post')


def create_edge_types(**kwargs):
    from social_graph import EdgeType, EdgeTypeAssociation

    #FRIENDSHIP EDGES
    friendship, created = EdgeType.objects.get_or_create(name="Friendship", defaults={
        'read_as': 'is friends with'
    })
    EdgeTypeAssociation.objects.get_or_create(direct=friendship, inverse=friendship)

    # FOLLOWER EDGES
    follower_of, created = EdgeType.objects.get_or_create(name="Follower", defaults={
        'read_as': 'is follower of'
    })
    followed_by, created = EdgeType.objects.get_or_create(name="Followed by", defaults={
        'read_as': 'is followed by'
    })
    EdgeTypeAssociation.objects.get_or_create(direct=follower_of, inverse=followed_by)

    # GROUP EDGES
    member_of, created = EdgeType.objects.get_or_create(name="Member", defaults={
        'read_as': 'is member of'
    })
    integrated_by, created = EdgeType.objects.get_or_create(name="Integrated by", defaults={
        'read_as': 'is integrated by'
    })
    EdgeTypeAssociation.objects.get_or_create(direct=member_of, inverse=integrated_by)

post_syncdb.connect(create_edge_types, sender=social_app)


def configure_notifications(**kwargs):
    from notifications.models import Transport, Action, EventType, EventTypeCategory, AttendantRole, EventAttendantsConfig, NotificationTemplateConfig
    from .. import SOCIAL_GROUP_COMMENT_EVENT_TYPE_NAME, SOCIAL_GROUP_PHOTO_EVENT_TYPE_NAME
    group_transport, created = Transport.objects.get_or_create(
        name='group_transport',
        cls='social_network.transports.GroupFeedTransport',
        defaults={
            'allows_context': False,
            'allows_freq_config': False,
            'delete_sent': False
        }
    )
    category, created = EventTypeCategory.objects.get_or_create(
        name='social_network_category',
        defaults={'read_as': 'Social'}
    )
    group_attendant_role, created = AttendantRole.objects.get_or_create(role='owner', defaults={'priority': 1})

    comment, created = Action.objects.get_or_create(name='comment', defaults={'read_as': COMMENT_ACTION_READ_AS})
    photo, created = Action.objects.get_or_create(name='photo', defaults={'read_as': PHOTO_ACTION_READ_AS})

    comment_event, created = EventType.objects.get_or_create(
        name=SOCIAL_GROUP_COMMENT_EVENT_TYPE_NAME,
        action=comment,
        target_type='social_network.socialgroup',
        defaults={
            'read_as': COMMENT_EVENT_READ_AS,
            'category': category,
            'immediate': True
        }
    )
    photo_event, created = EventType.objects.get_or_create(
        name=SOCIAL_GROUP_PHOTO_EVENT_TYPE_NAME,
        action=photo,
        target_type='social_network.socialgroup',
        defaults={
            'read_as': PHOTO_EVENT_READ_AS,
            'category': category,
            'immediate': True
        }
    )

    comment_attendants_config, created = EventAttendantsConfig.objects.get_or_create(
        event_type=comment_event,
        transport=group_transport,
        defaults={
            'get_attendants_methods': [
                {'source': 'target_obj', 'type': 'property', 'value': "group,owner"}
            ]
        }
    )
    photo_attendants_config, created = EventAttendantsConfig.objects.get_or_create(
        event_type=photo_event,
        transport=group_transport,
        defaults={
            'get_attendants_methods': [
                {'source': 'target_obj', 'type': 'property', 'value': "group,owner"}
            ]
        }
    )

    comment_template_config, created = NotificationTemplateConfig.objects.get_or_create(
        event_type=comment_event,
        transport=group_transport,
        defaults={
            'template_path': 'social_network/group/feed/comment.html'
        }
    )
    photo_template_config, created = NotificationTemplateConfig.objects.get_or_create(
        event_type=photo_event,
        transport=group_transport,
        defaults={
            'template_path': 'social_network/group/feed/photo.html'
        }
    )

if AUTOCONFIGURE_NOTIFICATIONS:
    post_syncdb.connect(configure_notifications, sender=social_app)