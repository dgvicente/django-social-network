# coding=utf-8
from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
import views


urlpatterns = patterns(
    '',
    url(
        r'^group/all/$',
        views.SocialGroupListView.as_view(),
        name='social_groups'
    ),

    url(
        r'^group/create/$',
        login_required(views.BaseSocialGroupCreateView.as_view()),
        name='social_group_create'
    ),

    url(
        r'^group/create/ajax/$',
        login_required(views.SocialGroupCreateView.as_view()),
        name='social_group_create_ajax'
    ),

    url(
        r'^group/(?P<pk>\d+)/$',
        views.SocialGroupDetailView.as_view(),
        name='social_group_details'
    ),

    url(
        r'^group/(?P<group>\d+)/members/$',
        views.SocialGroupMembersList.as_view(),
        name='social_group_members_list'
    ),

    url(
        r'^group/(?P<group>\d+)/edit/$',
        login_required(views.BaseSocialGroupUpdateView.as_view()),
        name='social_group_edit'
    ),

    url(
        r'^group/(?P<group>\d+)/edit/ajax/$',
        login_required(views.SocialGroupUpdateView.as_view()),
        name='social_group_edit_ajax'
    ),

    url(
        r'^group/list/(?P<user>\d+)/$',
        views.SocialGroupUserList.as_view(),
        name='social_group_user_list'
    ),

    url(
        r'^group/(?P<group>\d+)/comment/$',
        login_required(views.BaseGroupCommentCreateView.as_view()),
        name='social_group_comment_create'
    ),

    url(
        r'^group/(?P<group>\d+)/comment/ajax/$',
        login_required(views.GroupCommentCreateView.as_view()),
        name='social_group_comment_create_ajax'
    ),

    url(
        r'^group/(?P<group>\d+)/link/$',
        login_required(views.BaseGroupLinkCreateView.as_view()),
        name='social_group_link_create'
    ),

    url(
        r'^group/(?P<group>\d+)/link/ajax/$',
        login_required(views.GroupLinkCreateView.as_view()),
        name='social_group_link_create_ajax'
    ),

    url(
        r'^group/(?P<group>\d+)/photo/$',
        login_required(views.BaseGroupPhotoCreateView.as_view()),
        name='social_group_photo_create'
    ),

    url(
        r'^group/(?P<group>\d+)/photo/ajax/$',
        login_required(views.GroupPhotoCreateView.as_view()),
        name='social_group_photo_create_ajax'
    ),

    url(
        r'^group/(?P<group>\d+)/feed/$',
        views.SocialGroupFeedView.as_view(),
        name='social_group_feed'
    ),

    url(
        r'^group/(?P<group>\d+)/request_membership/$',
        login_required(views.BaseSocialGroupRequestCreateView.as_view()),
        name='social_group_request_create'
    ),

    url(
        r'^group/(?P<group>\d+)/request_membership/ajax/$',
        login_required(views.SocialGroupRequestCreateView.as_view()),
        name='social_group_request_create_ajax'
    ),

    url(
        r'^group/(?P<group>\d+)/requests/$',
        login_required(views.SocialGroupMembershipRequestsList.as_view()),
        name='social_group_request_list'
    ),

    url(
        r'^group/requests/(?P<pk>\d+)/accept/$',
        login_required(views.SocialGroupRequestAcceptView.as_view()),
        name='social_group_request_accept'
    ),

    url(
        r'^group/requests/(?P<pk>\d+)/deny/$',
        login_required(views.SocialGroupRequestDenyView.as_view()),
        name='social_group_request_deny'
    ),

    url(
        r'^group/(?P<group>\d+)/join/$',
        login_required(views.SocialGroupJoinView.as_view()),
        name='social_group_join'
    ),

    url(
        r'^group/(?P<group>\d+)/buttons/$',
        login_required(views.MembershipButtonsTemplateView.as_view()),
        name='social_group_membership_buttons'
    ),

    url(
        r'^user/(?P<receiver>\d+)/comment/$',
        login_required(views.BaseFeedCommentCreateView.as_view()),
        name="profile_comment_create"
    ),

    url(
        r'^user/(?P<receiver>\d+)/comment/ajax/$',
        login_required(views.FeedCommentCreateView.as_view()),
        name="profile_comment_create_ajax"
    ),

    url(
        r'^user/toggle_follow/$',
        login_required(views.FollowerRelationshipToggleView.as_view()),
        name="toggle_follower_relationship"
    ),

    url(
        r'^user/(?P<followed>\d+)/follow/$',
        login_required(views.FollowerRelationshipCreateView.as_view()),
        name="follower_relationship_create"
    ),

    url(
        r'^user/(?P<followed>\d+)/stop_following/$',
        login_required(views.FollowerRelationshipDestroyView.as_view()),
        name="follower_relationship_destroy"
    ),

    url(
        r'^user/(?P<receiver>\d+)/request_friendship/$',
        login_required(views.BaseFriendRequestCreateView.as_view()),
        name='friend_request_create'
    ),

    url(
        r'^user/(?P<receiver>\d+)/request_friendship/ajax/$',
        login_required(views.FriendRequestCreateView.as_view()),
        name='friend_request_create_ajax'
    ),

    url(
        r'^user/(?P<receiver>\d+)/friend_requests/$',
        login_required(views.FriendRequestListView.as_view()),
        name='friend_request_list'
    ),

    url(
        r'^user/friend_requests/(?P<pk>\d+)/accept/$',
        login_required(views.AcceptFriendRequestView.as_view()),
        name='friend_request_accept'
    ),

    url(
        r'^user/friend_requests/(?P<pk>\d+)/deny/$',
        login_required(views.DenyFriendRequestView.as_view()),
        name='friend_request_deny'
    ),

    url(
        r'^user/(?P<profile>\d+)/buttons/$',
        login_required(views.FriendshipButtonsTemplateView.as_view()),
        name='friendship_buttons'
    ),
)
