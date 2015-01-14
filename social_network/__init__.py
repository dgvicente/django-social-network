# coding=utf-8
import logging
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _
from social_graph import Graph
from .signals import (
    follower_relationship_created,
    follower_relationship_destroyed
)
from .utils import (
    followed_by_edge,
    follower_of_edge
)

logger = logging.getLogger(__name__)
User = get_user_model()
Manager = User._default_manager
graph = Graph()


def get_site(self):
    profile = getattr(self, 'profile', None)
    return getattr(profile, 'site', Site.objects.get_current()) if profile else Site.objects.get_current()

setattr(User, 'get_site', get_site)


def followers(self):
    return graph.edge_count(self, followed_by_edge(), self.get_site())


setattr(User, 'followers', followers)


def follower_list(self):
    count = self.followers()
    return [node for node, attributes, time in graph.edge_range(self, followed_by_edge(), 0, count, self.get_site())]


setattr(User, 'follower_list', follower_list)


def followed_by(self, user):
    return graph.edge_get(self, followed_by_edge(), user, self.get_site()) is not None


setattr(User, 'followed_by', followed_by)


def follow(self, user):
    _edge = graph.edge(self, user, follower_of_edge(), self.get_site(), {})
    if _edge:
        follower_relationship_created.send(sender=self.__class__, instance=user, user=self)
    return _edge


setattr(User, 'follow', follow)


def stop_following(self, user):
    _deleted = graph.no_edge(self, user, follower_of_edge(), self.get_site())
    if _deleted:
        follower_relationship_destroyed.send(sender=self.__class__, instance=user, user=self)
    return _deleted


setattr(User, 'stop_following', stop_following)


def followed_by_users(self, user):
    follower_of = follower_of_edge()
    count = graph.edge_count(user, follower_of)
    content_type = ContentType.objects.get_for_model(self.model)
    ids = [node.pk for node, attributes, time in graph.edge_range(user, follower_of, 0, count) if ContentType.objects.get_for_model(node) == content_type]
    return self.get_queryset().filter(pk__in=ids)


setattr(Manager.__class__, 'followed_by', followed_by_users)


SERVER_SUCCESS_MESSAGE = _(u"Su petición ha sido procesada correctamente.")