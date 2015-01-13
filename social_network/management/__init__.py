# coding=utf-8
from django.db.models.signals import post_syncdb
from .. import models as social_app


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
