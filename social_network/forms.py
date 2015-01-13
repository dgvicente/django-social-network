# coding=utf-8
from django import forms
from django.contrib.auth.models import User
from django.forms import widgets
from django_select2 import AutoModelSelect2TagField
from .models import FriendRequest, SocialGroup, GroupComment, GroupMembershipRequest, GroupImage, FeedComment


class MultipleUsersField(AutoModelSelect2TagField):
    queryset = User.objects
    search_fields = ['username__icontains', ]

    def get_model_field_values(self, value):
        return {'user': value}


class FriendRequestForm(forms.ModelForm):
    class Meta:
        model = FriendRequest
        widgets = {
            'from_user': widgets.HiddenInput,
            'to_user': widgets.HiddenInput,
        }


class SocialGroupForm(forms.ModelForm):
    administrators = MultipleUsersField(required=False)
    class Meta:
        model = SocialGroup
        widgets = {
            'creator': widgets.HiddenInput
        }


class GroupCommentForm(forms.ModelForm):
    class Meta:
        model = GroupComment
        widgets = {
            'creator': widgets.HiddenInput,
            'group': widgets.HiddenInput
        }


class GroupPhotoForm(forms.ModelForm):
    class Meta:
        model = GroupImage
        widgets = {
            'creator': widgets.HiddenInput,
            'group': widgets.HiddenInput
        }


class GroupMembershipRequestForm(forms.ModelForm):
    class Meta:
        model = GroupMembershipRequest
        widgets = {
            'requester': widgets.HiddenInput,
            'group': widgets.HiddenInput
        }


class FeedCommentForm(forms.ModelForm):
    class Meta:
        model = FeedComment
        widgets = {
            'creator': widgets.HiddenInput,
            'receiver': widgets.HiddenInput,
        }