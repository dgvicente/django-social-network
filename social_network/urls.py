# coding=utf-8
from django.conf.urls import patterns, url
from .views import (FriendRequestCreateView,
                    FriendRequestListView,
                    AcceptFriendRequestView,
                    SocialGroupDetailView,
                    SocialGroupCreateView,
                    GroupCommentCreateView,
                    SocialGroupRequestCreateView,
                    SocialGroupMembershipRequestsList,
                    SocialGroupRequestAcceptView,
                    GroupPhotoCreateView,
                    SocialGroupJoinView,
                    SocialGroupMembersList, SocialGroupUserList, FriendshipButtonsTemplateView, MembershipButtonsTemplateView, FeedCommentCreateView, FollowerRelationshipCreateView, FollowerRelationshipDestroyView)

urlpatterns = patterns(
    '',
    url(r'^friend_request/create/(?P<receiver>\d+)/$',
        FriendRequestCreateView.as_view(),
        name='friend_request_create'),

    url(r'^friend_request/list/(?P<receiver>\d+)/$',
        FriendRequestListView.as_view(),
        name='friend_request_list'),

    url(r'^friend_request/accept/(?P<pk>\d+)/$',
        AcceptFriendRequestView.as_view(),
        name='friend_request_accept'),

    url(r'^friends/buttons/(?P<profile>\d+)/$',
        FriendshipButtonsTemplateView.as_view(),
        name='friendship_buttons'),

    url(r'^group/(?P<pk>\d+)/$',
        SocialGroupDetailView.as_view(),
        name='social_group_details'),

    url(r'^group/create/$',
        SocialGroupCreateView.as_view(),
        name='social_group_create'),

    url(r'^user/group_list/(?P<user>\d+)$',
        SocialGroupUserList.as_view(),
        name='social_group_user_list'),

    url(r'^group/members/list/(?P<group>\d+)$',
        SocialGroupMembersList.as_view(),
        name='social_group_members_list'),

    url(r'^group/comment/(?P<group>\d+)$',
        GroupCommentCreateView.as_view(),
        name='social_group_comment_create'),

    url(r'^group/photo/(?P<group>\d+)$',
        GroupPhotoCreateView.as_view(),
        name='social_group_photo_create'),

    url(r'^group/request/create/(?P<group>\d+)/$',
        SocialGroupRequestCreateView.as_view(),
        name='group_request_create'),

    url(r'^group/request/list/(?P<group>\d+)/$',
        SocialGroupMembershipRequestsList.as_view(),
        name='group_request_list'),

    url(r'^group/request/accept/(?P<pk>\d+)/$',
        SocialGroupRequestAcceptView.as_view(),
        name='group_request_accept'),

    url(r'^group/join/(?P<group>\d+)/$',
        SocialGroupJoinView.as_view(),
        name='group_join'),

    url(r'^group/buttons/(?P<group>\d+)/$',
        MembershipButtonsTemplateView.as_view(),
        name='membership_buttons'),

    url(
        r'^user/comment/(?P<receiver>\d+)/$',
        FeedCommentCreateView.as_view(),
        name="profile_comment_create"
    ),

    url(
        r'^user/follow/(?P<followed>\d+)/$',
        FollowerRelationshipCreateView.as_view(),
        name="follower_relationship_create"
    ),

    url(
        r'^user/unfollow/(?P<followed>\d+)/$',
        FollowerRelationshipDestroyView.as_view(),
        name="follower_relationship_destroy"
    ),
)
