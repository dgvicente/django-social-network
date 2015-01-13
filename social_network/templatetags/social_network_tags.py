# coding=utf-8
from django import template
from django.contrib.auth.models import User
from ..models import FriendRequest, SocialGroup, GroupMembershipRequest
from ..utils import get_user_friends_count, users_are_friends, user_is_follower_of, user_followers_count, user_followed_users_count

register = template.Library()

#--------------------------------------FOLLOWER TAGS---------------------------------------------
@register.filter
def is_follower_of(user1, user2):
    """
    Returns True if user1 and user2 have a follower_of relationship, False otherwise.

    :param user1: An User instance.
    :param user2: An User instance.

    """
    return user_is_follower_of(user1, user2)

@register.filter
def followers_count(user):
    """
    Returns user followers count
    :param user: An User instance
    """
    return user_followers_count(user)

@register.filter
def followed_count(user):
    """
    Returns the count of how many users is the user following
    :param user: An User instance
    """
    return user_followed_users_count(user)

#--------------------------------------FRIENDSHIP TAGS-------------------------------------------
@register.filter
def is_friends_with(user1, user2):
    """
    Returns True if user1 and user2 have a friendship relationship, False otherwise.

    :param user1: An User instance.
    :param user2: An User instance.

    """
    return users_are_friends(user1, user2)


@register.filter
def has_requested_friendship(user1, user2):
    """
    Returns True if user1 has requested friendship to user2, False otherwise.

    :param user1: An User instance.
    :param user2: An User instance.

    """
    if not user1 or not user2 or user1 == user2:
        return False
    return FriendRequest.objects.filter(from_user=user1, to_user=user2, accepted=False).exists()


@register.filter
def friends_count(user):
    """
    Returns how many users have a "friendship" relationship with given user

    :param user: An User instance.

    """
    if not user:
        return 0
    if isinstance(user, User):
        obj = user
    else:
        try:
            pk = int(user)
            obj = User.objects.get(pk=pk)
        except (ValueError, User.DoesNotExist):
            return 0
    return get_user_friends_count(obj)

#--------------------------------------GROUPS TAGS-------------------------------------------
@register.filter
def is_group_admin(user, group):
    """
    Returns True if user is in the group list of administrators or is the creator, False otherwise

    :param user: An User instance.
    :param group: A SocialGroup instance.

    """
    if not user or not group:
        return False

    if isinstance(user, User):
        user_obj = user
    else:
        try:
            user_obj = User.objects.get(pk=user)
        except:
            return False

    if isinstance(group, SocialGroup):
        group_obj = group
    else:
        try:
            group_obj = SocialGroup.objects.get(pk=group)
        except:
            return False

    return group_obj.is_admin(user_obj)


@register.filter
def is_group_member(user, group):
    """
    Returns True if user is in the group list of administrators or is the creator, False otherwise

    :param user: An User instance.
    :param group: A SocialGroup instance.

    """
    if not user or not group:
        return False
    if isinstance(user, User):
        user_obj = user
    else:
        try:
            user_obj = User.objects.get(pk=user)
        except:
            return False

    if isinstance(group, SocialGroup):
        group_obj = group
    else:
        try:
            group_obj = SocialGroup.objects.get(pk=group)
        except:
            return False

    return group_obj.is_member(user_obj)


@register.filter
def has_requested_membership(user, group):
    """
    Returns True if user1 has requested friendship to user2, False otherwise.

    :param user: An User instance.
    :param group: An SocialGroup instance.

    """
    if not user or not group:
        return False

    if isinstance(user, User):
        user_obj = user
    else:
        try:
            user_obj = User.objects.get(pk=user)
        except:
            return False

    if isinstance(group, SocialGroup):
        group_obj = group
    else:
        try:
            group_obj = SocialGroup.objects.get(pk=group)
        except:
            return False

    return GroupMembershipRequest.objects.filter(requester=user_obj, group=group_obj, accepted=False).exists()


@register.filter
def groups_count(user):
    """
    Returns the total count of how many groups the user has created plus how many he is member of
    """
    if not user:
        return 0
    if isinstance(user, User):
        user_obj = user
    else:
        try:
            user_obj = User.objects.get(pk=user)
        except:
            return 0

    return SocialGroup.user_group_count(user_obj)