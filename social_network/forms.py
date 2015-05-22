# coding=utf-8
from django import forms
from django.core.exceptions import ValidationError
from . import Manager
from models import (
    FriendRequest, 
    SocialGroup, 
    GroupComment, 
    GroupMembershipRequest, 
    GroupImage, 
    FeedComment,
    GroupSharedLink)


class FriendRequestForm(forms.ModelForm):

    class Meta:
        model = FriendRequest
        widgets = {
            'from_user': forms.widgets.HiddenInput,
            'to_user': forms.widgets.HiddenInput,
        }


class SocialGroupForm(forms.ModelForm):
    administrators = forms.ModelMultipleChoiceField(Manager.all(), required=False)

    class Meta:
        model = SocialGroup
        widgets = {
            'creator': forms.widgets.HiddenInput,
            'site': forms.widgets.HiddenInput
        }


class GroupPostForm(forms.ModelForm):

    class Meta(object):
        widgets = {
            'creator': forms.widgets.HiddenInput,
            'group': forms.widgets.HiddenInput
        }

    def clean(self):
        if not self.cleaned_data['group'].has_member(self.cleaned_data['creator']):
            raise ValidationError("Only members can post in groups")
        return self.cleaned_data


class GroupCommentForm(GroupPostForm):

    class Meta(GroupPostForm.Meta):
        model = GroupComment


class GroupSharedLinkForm(GroupPostForm):
    class Meta(GroupPostForm.Meta):
        model = GroupSharedLink


class GroupPhotoForm(GroupPostForm):

    class Meta(GroupPostForm.Meta):
        model = GroupImage


class GroupMembershipRequestForm(forms.ModelForm):
    class Meta:
        model = GroupMembershipRequest
        widgets = {
            'requester': forms.widgets.HiddenInput,
            'group': forms.widgets.HiddenInput
        }

    def clean(self):
        if GroupMembershipRequest.objects.filter(
            requester=self.cleaned_data['requester'],
            group=self.cleaned_data['group'],
            accepted=False,
            denied=False,
        ).exists():
            raise ValidationError('Pre-existing group membership request from this user to this group.')
        return self.cleaned_data


class FeedCommentForm(forms.ModelForm):
    class Meta:
        model = FeedComment
        widgets = {
            'creator': forms.widgets.HiddenInput,
            'receiver': forms.widgets.HiddenInput,
        }