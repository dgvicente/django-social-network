#coding=utf-8

from sitetree.utils import tree, item

sitetrees = (
    tree('social_network', items=[
        item(title='GRUPOS SOCIALES [<b>{{object.name}}</b>]',
             url='social_group_details group.pk',
             url_as_pattern=True,
             hint='',
             alias='',
             description='',
             in_menu=False,
             in_breadcrumbs=True,
             in_sitetree=True,
             access_loggedin=False,
             access_guest=False,
             access_by_perms=None,
             perms_mode_all=True,
             children=[]),
    ]),
)



