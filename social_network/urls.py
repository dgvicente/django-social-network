# coding=utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from .views import (
    BaseFriendRequestCreateView,
    FriendRequestCreateView,
    FriendRequestListView,
    AcceptFriendRequestView,
    DenyFriendRequestView,
    SocialGroupListView,
    SocialGroupDetailView,
    BaseSocialGroupCreateView,
    SocialGroupCreateView,
    BaseGroupCommentCreateView,
    GroupCommentCreateView,
    SocialGroupFeedView,
    BaseSocialGroupRequestCreateView,
    SocialGroupRequestCreateView,
    SocialGroupMembershipRequestsList,
    SocialGroupRequestAcceptView,
    SocialGroupRequestDenyView,
    BaseGroupPhotoCreateView,
    GroupPhotoCreateView,
    SocialGroupJoinView,
    SocialGroupMembersList,
    SocialGroupUserList,
    FriendshipButtonsTemplateView,
    MembershipButtonsTemplateView,
    BaseFeedCommentCreateView,
    FeedCommentCreateView,
    FollowerRelationshipToggleView,
    FollowerRelationshipCreateView,
    FollowerRelationshipDestroyView,
    BaseGroupLinkCreateView, GroupLinkCreateView)

urlpatterns = patterns(
    '',
    url(
        r'^group/all/$',
        SocialGroupListView.as_view(),
        name='social_groups'
    ),

    url(
        r'^group/create/$',
        login_required(BaseSocialGroupCreateView.as_view()),
        name='social_group_create'
    ),

    url(
        r'^group/create/ajax/$',
        login_required(SocialGroupCreateView.as_view()),
        name='social_group_create_ajax'
    ),

    url(
        r'^group/(?P<pk>\d+)/$',
        SocialGroupDetailView.as_view(),
        name='social_group_details'
    ),

    url(
        r'^group/(?P<group>\d+)/members/$',
        SocialGroupMembersList.as_view(),
        name='social_group_members_list'
    ),

    url(
        r'^group/list/(?P<user>\d+)/$',
        SocialGroupUserList.as_view(),
        name='social_group_user_list'
    ),

    url(
        r'^group/(?P<group>\d+)/comment/$',
        login_required(BaseGroupCommentCreateView.as_view()),
        name='social_group_comment_create'
    ),

    url(
        r'^group/(?P<group>\d+)/comment/ajax/$',
        login_required(GroupCommentCreateView.as_view()),
        name='social_group_comment_create_ajax'
    ),

    url(
        r'^group/(?P<group>\d+)/link/$',
        login_required(BaseGroupLinkCreateView.as_view()),
        name='social_group_link_create'
    ),

    url(
        r'^group/(?P<group>\d+)/link/ajax/$',
        login_required(GroupLinkCreateView.as_view()),
        name='social_group_link_create_ajax'
    ),

    url(
        r'^group/(?P<group>\d+)/photo/$',
        login_required(BaseGroupPhotoCreateView.as_view()),
        name='social_group_photo_create'
    ),

    url(
        r'^group/(?P<group>\d+)/photo/ajax/$',
        login_required(GroupPhotoCreateView.as_view()),
        name='social_group_photo_create_ajax'
    ),

    url(
        r'^group/(?P<group>\d+)/feed/$',
        SocialGroupFeedView.as_view(),
        name='social_group_feed'
    ),

    url(
        r'^group/(?P<group>\d+)/request_membership/$',
        login_required(BaseSocialGroupRequestCreateView.as_view()),
        name='social_group_request_create'
    ),

    url(
        r'^group/(?P<group>\d+)/request_membership/ajax/$',
        login_required(SocialGroupRequestCreateView.as_view()),
        name='social_group_request_create_ajax'
    ),

    url(
        r'^group/(?P<group>\d+)/requests/$',
        login_required(SocialGroupMembershipRequestsList.as_view()),
        name='social_group_request_list'
    ),

    url(
        r'^group/requests/(?P<pk>\d+)/accept/$',
        login_required(SocialGroupRequestAcceptView.as_view()),
        name='social_group_request_accept'
    ),

    url(
        r'^group/requests/(?P<pk>\d+)/deny/$',
        login_required(SocialGroupRequestDenyView.as_view()),
        name='social_group_request_deny'
    ),

    url(
        r'^group/(?P<group>\d+)/join/$',
        login_required(SocialGroupJoinView.as_view()),
        name='social_group_join'
    ),

    url(
        r'^group/(?P<group>\d+)/buttons/$',
        login_required(MembershipButtonsTemplateView.as_view()),
        name='social_group_membership_buttons'
    ),

    url(
        r'^user/(?P<receiver>\d+)/comment/$',
        login_required(BaseFeedCommentCreateView.as_view()),
        name="profile_comment_create"
    ),

    url(
        r'^user/(?P<receiver>\d+)/comment/ajax/$',
        login_required(FeedCommentCreateView.as_view()),
        name="profile_comment_create_ajax"
    ),

    url(
        r'^user/toggle_follow/$',
        login_required(FollowerRelationshipToggleView.as_view()),
        name="toggle_follower_relationship"
    ),

    url(
        r'^user/(?P<followed>\d+)/follow/$',
        login_required(FollowerRelationshipCreateView.as_view()),
        name="follower_relationship_create"
    ),

    url(
        r'^user/(?P<followed>\d+)/stop_following/$',
        login_required(FollowerRelationshipDestroyView.as_view()),
        name="follower_relationship_destroy"
    ),

    url(
        r'^user/(?P<receiver>\d+)/request_friendship/$',
        login_required(BaseFriendRequestCreateView.as_view()),
        name='friend_request_create'
    ),

    url(
        r'^user/(?P<receiver>\d+)/request_friendship/ajax/$',
        login_required(FriendRequestCreateView.as_view()),
        name='friend_request_create_ajax'
    ),

    url(
        r'^user/(?P<receiver>\d+)/friend_requests/$',
        login_required(FriendRequestListView.as_view()),
        name='friend_request_list'
    ),

    url(
        r'^user/friend_requests/(?P<pk>\d+)/accept/$',
        login_required(AcceptFriendRequestView.as_view()),
        name='friend_request_accept'
    ),

    url(
        r'^user/friend_requests/(?P<pk>\d+)/deny/$',
        login_required(DenyFriendRequestView.as_view()),
        name='friend_request_deny'
    ),

    url(
        r'^user/(?P<profile>\d+)/buttons/$',
        login_required(FriendshipButtonsTemplateView.as_view()),
        name='friendship_buttons'
    ),
)
