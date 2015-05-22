import json
import logging
from django.contrib.sites.models import Site
from django.http import HttpResponse
from django.http.response import HttpResponseBadRequest
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView, View, DetailView, TemplateView
from . import SERVER_SUCCESS_MESSAGE, User, Manager, SERVER_ERROR_MESSAGE
from utils import intmin
from models import FriendRequest, SocialGroup, GroupMembershipRequest, GroupFeedItem
from forms import (
    FriendRequestForm,
    SocialGroupForm,
    GroupCommentForm,
    GroupMembershipRequestForm,
    GroupPhotoForm,
    FeedCommentForm,
    GroupSharedLinkForm)

logger = logging.getLogger(__name__)


class JSONResponseEnabledMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    json_response_class = HttpResponse
    json_enabled_methods = ['post']

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.json_enabled_methods:
            self.json_enabled = True
        else:
            self.json_enabled = False
        return super(JSONResponseEnabledMixin, self).dispatch(request, *args, **kwargs)

    def render_to_json(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        response_kwargs['content_type'] = 'application/json'
        return self.json_response_class(
            json.dumps(context),
            **response_kwargs
        )

    def render_to_response(self, context, **response_kwargs):
        if self.json_enabled:
            return self.render_to_json(context, **response_kwargs)
        else:
            return super(JSONResponseEnabledMixin, self).render_to_response(context, **response_kwargs)


class BaseFriendRequestCreateView(CreateView):
    form_class = FriendRequestForm
    template_name = 'social_network/friend/request.html'

    def get_context_data(self, **kwargs):
        context = super(BaseFriendRequestCreateView, self).get_context_data(**kwargs)
        context.update({
            'receiver': self.kwargs['receiver']
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(BaseFriendRequestCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'from_user': self.request.user,
            'to_user': Manager.get(pk=self.kwargs['receiver']),
        }
        return kwargs


class FriendRequestCreateView(JSONResponseEnabledMixin, BaseFriendRequestCreateView):

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_json({
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }, status=201)


class FriendRequestListView(ListView):
    template_name = 'social_network/friend/list/main.html'

    def get_queryset(self):
        self.queryset = FriendRequest.objects.filter(to_user__pk=self.kwargs['receiver'], accepted=False)
        return super(FriendRequestListView, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(FriendRequestListView, self).get_context_data(**kwargs)
        user = Manager.get(pk=self.kwargs['receiver'])
        context.update({
            'friends': user.friend_list()
        })
        return context


class AcceptFriendRequestView(JSONResponseEnabledMixin, View):

    def post(self, request, *args, **kwargs):
        try:
            FriendRequest.objects.get(pk=kwargs['pk']).accept(self.request.user)
            return self.render_to_json({
                'result': True,
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            })
        except (FriendRequest.DoesNotExist, Exception) as e:
            return HttpResponseBadRequest()


class DenyFriendRequestView(JSONResponseEnabledMixin, View):

    def post(self, request, *args, **kwargs):
        try:
            result = FriendRequest.objects.get(pk=kwargs['pk']).deny(self.request.user)
            if not result:
                raise
            return self.render_to_json({
                'result': result,
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            })
        except (FriendRequest.DoesNotExist, Exception) as e:
            return HttpResponseBadRequest()


class FriendshipButtonsTemplateView(TemplateView):
    template_name = 'social_network/buttons/_friendship_buttons.html'

    def get_context_data(self, **kwargs):
        context = super(FriendshipButtonsTemplateView, self).get_context_data(**kwargs)
        context.update({
            'profile_user': Manager.get(pk=self.kwargs['profile'])
        })
        return context


class SocialGroupListView(ListView):
    template_name = 'social_network/group/detail/members.html'
    paginate_by = 10

    def get_queryset(self):
        self.queryset = SocialGroup.on_site.all()
        return super(SocialGroupListView, self).get_queryset()


class BaseSocialGroupCreateView(CreateView):
    form_class = SocialGroupForm
    template_name = 'social_network/group/form.html'

    def get_form_kwargs(self):
        kwargs = super(BaseSocialGroupCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'creator': self.request.user,
            'site': Site.objects.get_current()
        }
        return kwargs


class SocialGroupCreateView(JSONResponseEnabledMixin, BaseSocialGroupCreateView):

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_json({
            'result': True,
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }, status=201)


class SocialGroupUserList(ListView):
    template_name = 'social_network/group/list/main.html'

    def get_queryset(self):
        self.queryset = SocialGroup.on_site.integrated_by(self.request.user)
        return super(SocialGroupUserList, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(SocialGroupUserList, self).get_context_data(**kwargs)
        context.update({
            'owner': int(self.kwargs['user'])
        })
        return context


class SocialGroupDetailView(DetailView):
    model = SocialGroup
    template_name = 'social_network/group/detail/main.html'
    context_object_name = 'group'


class BaseSocialGroupRequestCreateView(CreateView):
    form_class = GroupMembershipRequestForm
    template_name = 'social_network/group/request.html'

    def get_context_data(self, **kwargs):
        context = super(BaseSocialGroupRequestCreateView, self).get_context_data(**kwargs)
        context.update({
            'group': self.kwargs['group']
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(BaseSocialGroupRequestCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'requester': self.request.user,
            'group': SocialGroup.objects.get(pk=self.kwargs['group'])
        }
        return kwargs


class SocialGroupRequestCreateView(JSONResponseEnabledMixin, BaseSocialGroupRequestCreateView):

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_json({
            'result': True,
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE),
            'sentLabel': force_text(_(u"Solicitud Enviada"))
        }, status=201)


class SocialGroupRequestAcceptView(JSONResponseEnabledMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            result = GroupMembershipRequest.objects.get(pk=kwargs['pk']).accept(self.request.user)
            if not result:
                raise
            return self.render_to_json({
                'result': result,
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            })
        except (GroupMembershipRequest.DoesNotExist, Exception) as e:
            return HttpResponseBadRequest()


class SocialGroupRequestDenyView(JSONResponseEnabledMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            result = GroupMembershipRequest.objects.get(pk=kwargs['pk']).deny(self.request.user)
            if not result:
                raise
            return self.render_to_json({
                'result': result,
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            })
        except (GroupMembershipRequest.DoesNotExist, Exception) as e:
            return HttpResponseBadRequest()


class SocialGroupJoinView(JSONResponseEnabledMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            result = self.request.user.join(SocialGroup.objects.get(pk=kwargs['group']))
            if not result:
                raise
            return self.render_to_json({
                'result': result,
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            })
        except (SocialGroup.DoesNotExist, Exception) as e:
            return HttpResponseBadRequest()


class BaseGroupPostCreateView(CreateView):

    def get_context_data(self, **kwargs):
        context = super(BaseGroupPostCreateView, self).get_context_data(**kwargs)
        context.update({
            'group': self.kwargs['group']
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(BaseGroupPostCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'creator': self.request.user,
            'group': SocialGroup.objects.get(pk=self.kwargs['group']),
        }
        return kwargs


class GroupPostCreateView(JSONResponseEnabledMixin):

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_json({
            'result': True,
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }, status=201)


class BaseGroupCommentCreateView(BaseGroupPostCreateView):
    form_class = GroupCommentForm
    template_name = 'social_network/group/comment.html'


class GroupCommentCreateView(GroupPostCreateView, BaseGroupCommentCreateView):
    pass


class BaseGroupLinkCreateView(BaseGroupPostCreateView):
    form_class = GroupSharedLinkForm
    template_name = 'social_network/group/link.html'


class GroupLinkCreateView(GroupPostCreateView, BaseGroupLinkCreateView):
    pass


class BaseGroupPhotoCreateView(BaseGroupPostCreateView):
    form_class = GroupPhotoForm
    template_name = 'social_network/group/photo.html'


class GroupPhotoCreateView(GroupPostCreateView, BaseGroupPhotoCreateView):
    pass


class SocialGroupFeedView(ListView):
    template_name = 'social_network/group/detail/feed.html'

    def get_queryset(self):
        self.queryset = GroupFeedItem.on_site.filter(group=self.kwargs.get('group')).order_by('-event__date')
        return super(SocialGroupFeedView, self).get_queryset()


class SocialGroupMembershipRequestsList(ListView):
    template_name = 'social_network/group/detail/requests.html'

    def get_queryset(self):
        self.queryset = GroupMembershipRequest.objects.filter(
            group__pk=self.kwargs['group'],
            accepted=False,
            denied=False
        )
        return super(SocialGroupMembershipRequestsList, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(SocialGroupMembershipRequestsList, self).get_context_data(**kwargs)
        context['group'] = self.kwargs['group']
        return context


class SocialGroupMembersList(ListView):
    template_name = 'social_network/group/detail/members.html'

    def get_queryset(self):
        self.group = SocialGroup.objects.get(pk=self.kwargs['group'])
        self.queryset = Manager.filter(pk__in=[user.pk for user in self.group.member_list])
        return super(SocialGroupMembersList, self).get_queryset()

    def get_context_data(self, **kwargs):
        context = super(SocialGroupMembersList, self).get_context_data(**kwargs)
        context.update({
            'roles': self.group.member_role_list,
        })

        return context


class MembershipButtonsTemplateView(TemplateView):
    template_name = 'social_network/buttons/_membership_buttons.html'

    def get_context_data(self, **kwargs):
        context = super(MembershipButtonsTemplateView, self).get_context_data(**kwargs)
        context.update({
            'group': SocialGroup.objects.get(pk=self.kwargs['group'])
        })
        return context


class BaseFeedCommentCreateView(CreateView):
    template_name = 'social_network/userfeed/comment.html'
    form_class = FeedCommentForm

    def get_context_data(self, **kwargs):
        context = super(BaseFeedCommentCreateView, self).get_context_data(**kwargs)
        context.update({
            'receiver': self.kwargs['receiver']
        })
        return context

    def get_form_kwargs(self):
        kwargs = super(BaseFeedCommentCreateView, self).get_form_kwargs()
        kwargs['initial'] = {
            'receiver': Manager.get(pk=self.kwargs['receiver']),
            'creator': self.request.user
        }
        return kwargs


class FeedCommentCreateView(JSONResponseEnabledMixin, BaseFeedCommentCreateView):

    def form_valid(self, form):
        self.object = form.save()
        return self.render_to_json({
            'result': True,
            'comment_id': self.object.pk,
            'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
        }, status=201)


class FollowerRelationshipToggleView(JSONResponseEnabledMixin, View):

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

            return self.render_to_json({
                'result': True,
                'toggle_status': toggle_status,
                'counter': followers,
                'counterStr': intmin(followers),
                'tooltip': force_text(tooltip)
            })

        except Exception as e:
            logger.exception(e)
            return self.render_to_json({'result': False})


class FollowerRelationshipCreateView(JSONResponseEnabledMixin, View):

    def post(self, request, *args, **kwargs):
        try:
            request.user.follow(Manager.get(pk=kwargs['followed']))
            return self.render_to_json({
                'result': True,
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            }, status=201)
        except (User.DoesNotExist, Exception):
            return HttpResponseBadRequest()


class FollowerRelationshipDestroyView(JSONResponseEnabledMixin, View):

    def post(self, request, *args, **kwargs):
        try:
            request.user.stop_following(Manager.get(pk=kwargs['followed']))
            return self.render_to_json({
                'result': True,
                'successMsg': force_text(SERVER_SUCCESS_MESSAGE)
            })
        except (User.DoesNotExist, Exception):
            return HttpResponseBadRequest()