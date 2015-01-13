# coding=utf-8
from social_graph import Graph
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from social_graph import EdgeType
import random

try:
    from hashlib import sha1 as sha_constructor, md5 as md5_constructor
except ImportError:
    pass


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


#---------------------FRIENDSHIP-----------------------------------------
def get_user_friends(user):
    graph = Graph()
    edge = friendship_edge()
    count = graph.edge_count(user, edge)
    return [
        friend for friend, attributes, time in
        graph.edge_range(user, edge, 0, count)]


def get_user_friends_count(user):
    graph = Graph()
    edge = friendship_edge()
    return graph.edge_count(user, edge)


def users_are_friends(user1, user2):
    if not user1 or not user2:
        return False
    graph = Graph()
    edge = friendship_edge()
    return graph.edge_get(user1, edge, user2) is not None


#---------------------FOLLOWERS-----------------------------------------
def user_is_follower_of(user1, user2):
    graph = Graph()
    edge = follower_of_edge()
    return graph.edge_get(user1, edge, user2) is not None


def user_followers(user):
    graph = Graph()
    edge = followed_by_edge()
    count = graph.edge_count(user, edge)
    return [
        follower for follower, attributes, time in
        graph.edge_range(user, edge, 0, count)]


def user_followers_count(user):
    graph = Graph()
    edge = followed_by_edge()
    return graph.edge_count(user, edge)


def user_followed_users(user):
    graph = Graph()
    edge = follower_of_edge()
    count = graph.edge_count(user, edge)
    return [
        followed for followed, attributes, time in
        graph.edge_range(user, edge, 0, count)]


def user_followed_users_count(user):
    graph = Graph()
    edge = follower_of_edge()
    return graph.edge_count(user, edge)


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


