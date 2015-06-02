# coding=utf-8
import logging
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from social_graph import Graph
from .signals import (
    follower_relationship_created,
    follower_relationship_destroyed,
    friendship_created,
    social_group_comment_created,
    social_group_photo_created
)
from .utils import (
    followed_by_edge,
    follower_of_edge,
    member_of_edge,
    integrated_by_edge,
    friendship_edge,
)

logger = logging.getLogger(__name__)
User = get_user_model()
Manager = User._default_manager
graph = Graph()

SOCIAL_GROUP_COMMENT_EVENT_TYPE_NAME = 'social_group_comment'
SOCIAL_GROUP_SHARED_LINK_EVENT_TYPE_NAME = 'social_group_shared_link'
SOCIAL_GROUP_PHOTO_EVENT_TYPE_NAME = 'social_group_photo'
SERVER_SUCCESS_MESSAGE = _(u"Your request has been successfully processed.")
SERVER_ERROR_MESSAGE = _(u"An error has occurred while processing your request'.")


##---------------------------------Inject functionality to Django User model---------------------------###
def get_site(self):
    return Site.objects.get_current()

setattr(User, 'get_site', get_site)


def followers(self):
    return graph.edge_count(self, followed_by_edge(), self.get_site())


setattr(User, 'followers', followers)


def following(self):
    return graph.edge_count(self, follower_of_edge(), self.get_site())


setattr(User, 'following', following)


def follower_list(self):
    count = self.followers()
    return [node for node, attributes, time in graph.edge_range(self, followed_by_edge(), 0, count, self.get_site())]


setattr(User, 'follower_list', follower_list)


def following_list(self):
    count = self.following()
    return [node for node, attributes, time in graph.edge_range(self, follower_of_edge(), 0, count, self.get_site())]


setattr(User, 'following_list', following_list)


def followed_by(self, user):
    return graph.edge_get(self, followed_by_edge(), user, self.get_site()) is not None


setattr(User, 'followed_by', followed_by)


def follow(self, user):
    _edge = graph.edge(self, user, follower_of_edge(), self.get_site(), {})
    if _edge:
        follower_relationship_created.send(sender=self.__class__, followed=user, user=self)
    return _edge


setattr(User, 'follow', follow)


def stop_following(self, user):
    _deleted = graph.no_edge(self, user, follower_of_edge(), self.get_site())
    if _deleted:
        follower_relationship_destroyed.send(sender=self.__class__, followed=user, user=self)
    return _deleted


setattr(User, 'stop_following', stop_following)


def friend_of(self, user):
    return graph.edge_get(self, friendship_edge(), user, self.get_site()) is not None


setattr(User, 'friend_of', friend_of)


def friends(self):
    return graph.edge_count(self, friendship_edge(), self.get_site())


setattr(User, 'friends', friends)


def friend_list(self):
    return [node for node, attributes, time in graph.edge_range(self, friendship_edge(), self.get_site())]


setattr(User, 'friend_list', friend_list)


def make_friend_of(self, user):
    _edge = graph.edge(self, user, friendship_edge(), self.get_site(), {})
    if _edge:
        friendship_created.send(sender=self.__class__, friend=user, user=self)
    return _edge


setattr(User, 'make_friend_of', make_friend_of)


def social_groups(self):
    return graph.edge_count(self, member_of_edge(), self.get_site())


setattr(User, 'social_groups', social_groups)


def social_group_list(self):
    count = self.social_groups()
    return [group for group, attributes, time in graph.edge_range(self, member_of_edge(), 0, count, self.get_site())]


setattr(User, 'social_group_list', social_group_list)


def specific_role_social_group_list(self, role):
    count = self.social_groups()
    return [group for group, attributes, time in graph.edge_range(self, member_of_edge(), 0, count, self.get_site())
            if attributes['role'] == role]


setattr(User, 'specific_role_social_group_list', specific_role_social_group_list)


def is_member_of(self, group):
    return graph.edge_get(group, integrated_by_edge(), self, group.site) is not None


setattr(User, 'is_member_of', is_member_of)


def is_admin_of(self, group):
    return self in group.administrators.all()


setattr(User, 'is_admin_of', is_admin_of)


def is_creator_of(self, group):
    return self == group.creator


setattr(User, 'is_creator_of', is_creator_of)


def join(self, group):
    return group.add_member(self)


setattr(User, 'join', join)


def followed_by_users(self, user):
    follower_of = follower_of_edge()
    count = graph.edge_count(user, follower_of)
    ids = [node.pk for node, attributes, time in graph.edge_range(user, follower_of, 0, count)]
    return self.get_queryset().filter(pk__in=ids)


setattr(Manager.__class__, 'followed_by', followed_by_users)


def members_of(self, group):
    integrated_by = integrated_by_edge()
    count = graph.edge_count(group, integrated_by)
    ids = [node.pk for node, attributes, time in graph.edge_range(group, integrated_by, 0, count)]
    return self.get_queryset().filter(pk__in=ids)


setattr(Manager.__class__, 'members_of', members_of)