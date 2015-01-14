import json
import logging
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView, View, DetailView, TemplateView
from social_graph import Graph
from .utils import intmin

from . import SERVER_SUCCESS_MESSAGE, User, Manager
from .models import FriendRequest, SocialGroup, GroupComment, GroupMembershipRequest, GroupImage, FeedComment
from .forms import (FriendRequestForm,
                    SocialGroupForm,
                    GroupCommentForm,
                    GroupMembershipRequestForm,
                    GroupPhotoForm,
                    FeedCommentForm)
from .signals import (
    friend_request_created,
    friendship_created,
    social_group_created,
    social_group_comment_created,
    social_group_membership_request_created,
    social_group_member_added,
    social_group_photo_created,
    feed_comment_created,
)
from .utils import friendship_edge, member_of_edge, integrated_by_edge


logger = logging.getLogger(__name__)


class FriendRequestCreateView(CreateView):
    form_class = FriendRequestForm
    template_name = 'social_network/friend_request_create.html'

    def get_context_data(self, **kwargs):
        context = super(FriendRequestCreateView, self).get_context_data(**kwargs)
        context.update({
            'receiver': self.kwargs['receiver']
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(FriendRequestCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'from_user': self.request.user,
            'to_user': Manager.get(pk=self.kwargs['receiver']),
        }
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        friend_request_created.send(sender=FriendRequest, user=self.request.user, instance=self.object)
        return HttpResponse(json.dumps({
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }), status=201, content_type='application/json')


class FriendRequestListView(ListView):
    template_name = 'social_network/friends_list.html'

    def get_queryset(self):
        self.queryset = FriendRequest.objects.filter(to_user__pk=self.kwargs['receiver'], accepted=False)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(FriendRequestListView, self).get_context_data(**kwargs)
        graph = Graph()
        edge = friendship_edge()
        user = Manager.get(pk=self.kwargs['receiver'])
        count = graph.edge_count(user, edge)
        friends_list = [
            user for user, attributes, time in graph.edge_range(user, edge, 0, count)
        ]
        context['friends'] = list(set(friends_list))
        return context


class AcceptFriendRequestView(View):
    def post(self, request, *args, **kwargs):
        try:
            friend_request = FriendRequest.objects.get(pk=kwargs['pk'])
            friend_request.accepted = True
            friend_request.save()
            graph = Graph()
            edge = friendship_edge()
            graph.edge(friend_request.from_user, friend_request.to_user, edge, Site.objects.get_current())
            friendship_created.send(sender=FriendRequest, instance=friend_request, user=friend_request.to_user)
            return HttpResponse(json.dumps({
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            }), status=201, content_type='application/json')
        except (FriendRequest.DoesNotExist, Exception) as e:
            return HttpResponseBadRequest()


class FriendshipButtonsTemplateView(TemplateView):
    template_name = 'social_network/buttons/_friendship_buttons.html'

    def get_context_data(self, **kwargs):
        context = super(FriendshipButtonsTemplateView, self).get_context_data(**kwargs)
        context.update({
            'user': self.request.user,
            'profile_user': Manager.get(pk=self.kwargs['profile'])
        })
        return context


class SocialGroupCreateView(CreateView):
    form_class = SocialGroupForm
    template_name = 'social_network/social_group_create.html'

    def get_form_kwargs(self):
        kwargs = super(SocialGroupCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'creator': self.request.user,
        }
        return kwargs

    def post(self, request, *args, **kwargs):
        return super(SocialGroupCreateView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        social_group_created.send(sender=SocialGroup, instance=self.object, user=self.request.user)
        return HttpResponse(json.dumps({
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }), status=201, content_type='application/json')


class SocialGroupUserList(ListView):
    template_name = 'social_network/user_group_list.html'

    def get_queryset(self):
        self.queryset = SocialGroup.objects.filter(creator__pk=self.kwargs['user'])
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(SocialGroupUserList, self).get_context_data(**kwargs)

        graph = Graph()
        edge = member_of_edge()
        user = Manager.get(pk=self.kwargs['user'])
        count = graph.edge_count(user, edge)
        group_member_list = [
            user for user, attributes, time in graph.edge_range(user, edge, 0, count)
        ]
        context.update({
            'group_member_list': group_member_list,
            'owner': int(self.kwargs['user']),
            'user': self.request.user
        })
        return context


class SocialGroupDetailView(DetailView):
    model = SocialGroup
    template_name = 'social_network/social_group.html'
    context_object_name = 'group'


class SocialGroupRequestCreateView(CreateView):
    form_class = GroupMembershipRequestForm
    template_name = 'social_network/group_request_create.html'

    def get_context_data(self, **kwargs):
        context = super(SocialGroupRequestCreateView, self).get_context_data(**kwargs)
        context.update({
            'group': self.kwargs['group']
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(SocialGroupRequestCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'requester': self.request.user,
            'group': SocialGroup.objects.get(pk=self.kwargs['group'])
        }
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        social_group_membership_request_created.send(sender=GroupMembershipRequest, instance=self.object,
                                                     user=self.request.user)
        return HttpResponse(json.dumps({
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }), status=201, content_type='application/json')


class SocialGroupRequestAcceptView(View):
    def post(self, request, *args, **kwargs):
        try:
            membership_request = GroupMembershipRequest.objects.get(pk=kwargs['pk'])
            membership_request.accepted = True
            membership_request.save()
            graph = Graph()
            edge = member_of_edge()
            graph.edge(membership_request.requester, membership_request.group, edge, Site.objects.get_current())
            social_group_member_added.send(sender=SocialGroup, instance=membership_request.group,
                                           user=membership_request.requester)
            return HttpResponse(json.dumps({
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            }), status=201, content_type='application/json')
        except (GroupMembershipRequest.DoesNotExist, Exception) as e:
            return HttpResponseBadRequest()


class SocialGroupJoinView(View):
    def post(self, request, *args, **kwargs):
        try:
            graph = Graph()
            edge = member_of_edge()
            group = SocialGroup.objects.get(pk=kwargs['group'])
            graph.edge(self.request.user, group, edge, Site.objects.get_current())
            social_group_member_added.send(sender=SocialGroup, instance=group,
                                           user=self.request.user)
            return HttpResponse(json.dumps({
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            }), status=201, content_type='application/json')
        except (SocialGroup.DoesNotExist, Exception) as e:
            return HttpResponseBadRequest()


class GroupCommentCreateView(CreateView):
    form_class = GroupCommentForm
    template_name = 'social_network/group_comment_create.html'

    def get_context_data(self, **kwargs):
        context = super(GroupCommentCreateView, self).get_context_data(**kwargs)
        context.update({
            'group': self.kwargs['group']
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(GroupCommentCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'creator': self.request.user,
            'group': SocialGroup.objects.get(pk=self.kwargs['group']),
        }
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        social_group_comment_created.send(sender=GroupComment, user=self.request.user, instance=self.object)
        return HttpResponse(json.dumps({
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }), status=201, content_type='application/json')


class GroupPhotoCreateView(CreateView):
    form_class = GroupPhotoForm
    template_name = 'social_network/group_photo_create.html'

    def get_context_data(self, **kwargs):
        context = super(GroupPhotoCreateView, self).get_context_data(**kwargs)
        context.update({
            'group': self.kwargs['group']
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(GroupPhotoCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'creator': self.request.user,
            'group': SocialGroup.objects.get(pk=self.kwargs['group']),
        }
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        social_group_photo_created.send(sender=GroupImage, user=self.object.creator, instance=self.object)
        return HttpResponse(json.dumps({
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }), status=201, content_type='application/json')


class SocialGroupMembershipRequestsList(ListView):
    template_name = 'social_network/membership_requests_list.html'

    def get_queryset(self):
        self.queryset = GroupMembershipRequest.objects.filter(group__pk=self.kwargs['group'], accepted=False)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(SocialGroupMembershipRequestsList, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        context['group'] = self.kwargs['group']
        return context


class SocialGroupMembersList(ListView):
    template_name = 'social_network/group_members_list.html'

    def get_queryset(self):
        group = SocialGroup.objects.get(pk=self.kwargs['group'])
        self.queryset = group.administrators.exclude(pk=group.creator.pk)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(SocialGroupMembersList, self).get_context_data(**kwargs)

        graph = Graph()
        edge = integrated_by_edge()
        group = SocialGroup.objects.get(pk=self.kwargs['group'])
        count = graph.edge_count(group, edge)
        members_list = [
            user for user, attributes, time in graph.edge_range(group, edge, 0, count)
        ]
        context.update({
            'members': list(set(members_list)),
            'creator': group.creator
        })

        return context


class MembershipButtonsTemplateView(TemplateView):
    template_name = 'social_network/buttons/_membership_buttons.html'

    def get_context_data(self, **kwargs):
        context = super(MembershipButtonsTemplateView, self).get_context_data(**kwargs)
        context.update({
            'user': self.request.user,
            'group': SocialGroup.objects.get(pk=self.kwargs['group'])
        })
        return context


class FeedCommentCreateView(CreateView):
    template_name = 'social_network/feed_comment_create.html'
    form_class = FeedCommentForm

    def get_context_data(self, **kwargs):
        context = super(CreateView, self).get_context_data(**kwargs)
        context.update({
            'receiver': self.kwargs['receiver']
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(CreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'receiver': Manager.get(pk=self.kwargs['receiver']),
            'creator': self.request.user
        }
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        feed_comment_created.send(sender=FeedComment, user=self.request.user, instance=self.object)
        return HttpResponse(json.dumps({
            'comment_id': self.object.pk,
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }), status=201, content_type='application/json')


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    response_class = HttpResponse

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.response_class(
            self.convert_context_to_json(context),
            **response_kwargs
        )

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return json.dumps(context)


class FollowerRelationshipToggleView(JSONResponseMixin, View):

    def post(self, request, *args, **kwargs):
        try:
            pk = request.POST['pk']
            user = Manager.get(pk=pk)

            if user.followed_by(request.user):
                request.user.stop_following(user)
                tooltip = _(u"Follow")
                toggle_status = False
            else:
                request.user.follow(user)
                tooltip = _(u"Stop Following")
                toggle_status = True

            followers = user.followers()

            return self.render_to_response({
                'result': True,
                'toggle_status': toggle_status,
                'counter': followers,
                'counterStr': intmin(followers),
                'tooltip': force_text(tooltip)
            })

        except Exception as e:
            logger.exception(e)
            return self.render_to_response({'result': False})


class FollowerRelationshipCreateView(View):

    def post(self, request, *args, **kwargs):
        try:
            user = Manager.get(pk=kwargs['followed'])
            request.user.follow(user)
            return HttpResponse(json.dumps({
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            }), status=201, content_type='application/json')
        except (User.DoesNotExist, Exception):
            return HttpResponseBadRequest()


class FollowerRelationshipDestroyView(View):

    def post(self, request, *args, **kwargs):
        try:
            user = Manager.get(pk=kwargs['followed'])
            request.user.stop_following(user)
            return HttpResponse(json.dumps({
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            }), status=201, content_type='application/json')
        except (User.DoesNotExist, Exception):
            return HttpResponseBadRequest()