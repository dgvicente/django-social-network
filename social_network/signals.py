# coding=utf-8
from django.dispatch import Signal

friend_request_created = Signal(providing_args=['instance', 'user'])
friendship_created = Signal(providing_args=['instance', 'user'])
social_group_created = Signal(providing_args=['instance', 'user'])
social_group_comment_created = Signal(providing_args=['instance', 'user'])
social_group_photo_created = Signal(providing_args=['instance', 'user'])
social_group_membership_request_created = Signal(providing_args=['instance', 'user'])
social_group_member_added = Signal(providing_args=['instance', 'user'])
feed_comment_created = Signal(providing_args=['instance', 'user'])
follower_relationship_created = Signal(providing_args=['instance', 'user'])
follower_relationship_destroyed = Signal(providing_args=['instance', 'user'])
