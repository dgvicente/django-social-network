# coding=utf-8
import random
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext as _
from notifications.models import EventType
from social_graph import EdgeType

try:
    from hashlib import sha1 as sha_constructor, md5 as md5_constructor
except ImportError:
    pass


#---------------------NOTIFICATIONS---------------------------------
def group_comment_event_type():
    comment_event_type = cache.get('SOCIAL_NETWORK_COMMENT_EVENT_TYPE')
    if comment_event_type is not None:
        return comment_event_type
    try:
        from . import SOCIAL_GROUP_COMMENT_EVENT_TYPE_NAME
        comment_event_type = EventType.objects.get(name=SOCIAL_GROUP_COMMENT_EVENT_TYPE_NAME)
        cache.set('SOCIAL_NETWORK_COMMENT_EVENT_TYPE', comment_event_type)
        return comment_event_type
    except ObjectDoesNotExist as e:
        pass  # TODO Log this


def group_shared_link_event_type():
    shared_link = cache.get('SOCIAL_NETWORK_SHARED_LINK_EVENT_TYPE')
    if shared_link is not None:
        return shared_link
    try:
        from . import SOCIAL_GROUP_SHARED_LINK_EVENT_TYPE_NAME
        shared_link = EventType.objects.get(name=SOCIAL_GROUP_SHARED_LINK_EVENT_TYPE_NAME)
        cache.set('SOCIAL_NETWORK_SHARED_LINK_EVENT_TYPE', shared_link)
        return shared_link
    except ObjectDoesNotExist as e:
        pass  # TODO Log this


def group_photo_event_type():
    photo_event_type = cache.get('SOCIAL_NETWORK_PHOTO_EVENT_TYPE')
    if photo_event_type is not None:
        return photo_event_type
    try:
        from . import SOCIAL_GROUP_PHOTO_EVENT_TYPE_NAME
        photo_event_type = EventType.objects.get(name=SOCIAL_GROUP_PHOTO_EVENT_TYPE_NAME)
        cache.set('SOCIAL_NETWORK_PHOTO_EVENT_TYPE', photo_event_type)
        return photo_event_type
    except ObjectDoesNotExist as e:
        pass  # TODO Log this


#---------------------EDGES-----------------------------------------
def friendship_edge():
    _friendship = cache.get('FRIENDSHIP_EDGE_TYPE')
    if _friendship is not None:
        return _friendship
    try:
        _friendship = EdgeType.objects.get(name="Friendship")
        cache.set('FRIENDSHIP_EDGE_TYPE', _friendship)
        return _friendship
    except ObjectDoesNotExist as e:
        pass  # TODO Log this


def integrated_by_edge():
    _integrated_by = cache.get('INTEGRATED_BY_EDGE_TYPE')
    if _integrated_by is not None:
        return _integrated_by
    try:
        _integrated_by = EdgeType.objects.get(name="Integrated by")
        cache.set('INTEGRATED_BY_EDGE_TYPE', _integrated_by)
        return _integrated_by
    except ObjectDoesNotExist as e:
        pass  # TODO Log this


def member_of_edge():
    _member_of = cache.get('MEMBER_OF_EDGE_TYPE')
    if _member_of is not None:
        return _member_of
    try:
        _member_of = EdgeType.objects.get(name="Member")
        cache.set('MEMBER_OF_EDGE_TYPE', _member_of)
        return _member_of
    except ObjectDoesNotExist as e:
        pass  # TODO Log this


def follower_of_edge():
    _follower_of = cache.get('FOLLOWER_OF_EDGE_TYPE')
    if _follower_of is not None:
        return _follower_of
    try:
        _follower_of = EdgeType.objects.get(name="Follower")
        cache.set('FOLLOWER_OF_EDGE_TYPE', _follower_of)
        return _follower_of
    except ObjectDoesNotExist:
        pass


def followed_by_edge():
    _followed_by = cache.get('FOLLOWED_BY_EDGE_TYPE')
    if _followed_by is not None:
        return _followed_by
    try:
        _followed_by = EdgeType.objects.get(name="Followed by")
        cache.set('FOLLOWED_BY_EDGE_TYPE', _followed_by)
        return _followed_by
    except ObjectDoesNotExist:
        pass

#---------------------GENERAL-----------------------------------------


def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string. Doesn't need to be very secure
    because it's not used for password checking. We got Django for that.

    :param string:
        The string that needs to be encrypted.

    :param salt:
        Optionally define your own salt. If none is supplied, will use a random
        string of 5 characters.

    :return: Tuple containing the salt and hash.

    """
    if not isinstance(string, (str, unicode)):
        string = str(string)
    if isinstance(string, unicode):
        string = string.encode("utf-8")
    if not salt:
        salt = sha_constructor(str(random.random())).hexdigest()[:5]
    hash = sha_constructor(salt+string).hexdigest()

    return (salt, hash)


# A tuple of standard large number to their converters
intword_converters = (
    (3, lambda number: _('%(value)dK')),
    (6, lambda number: _('%(value)dM')),
    (9, lambda number: _('%(value)dG')),
)


def intmin(value):
    """
    """
    try:
        value = int(value)
    except (TypeError, ValueError):
        return value

    if value < 1000:
        return value

    for exponent, converter in intword_converters:
        large_number = 10 ** exponent
        if value < large_number * 1000:
            new_value = value / large_number
            tpl = "+%s" if value > large_number else "%s"
            return tpl % converter(new_value) % {'value': new_value}
    return value