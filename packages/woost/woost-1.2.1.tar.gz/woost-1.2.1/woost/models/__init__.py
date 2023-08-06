#-*- coding: utf-8 -*-
u"""
Provides base and default content types for the woost CMS.

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			June 2008
"""
from cocktail import schema
from cocktail.events import when

# Add an extension property to control the default member visibility on item listings
schema.Member.listed_by_default = True
schema.Collection.listed_by_default = False
schema.CodeBlock.listed_by_default = False

# Add an extension property to show/hide the 'Element' column on listings
schema.Schema.show_element_in_listings = True

# Add an extension property to show/hide the 'Type' column on listings
schema.Schema.show_type_in_listings = True

# Add an extension property to indicate if members should be visible by users
schema.Member.visible = True

# Add an extension property to indicate if schemas should be instantiable by
# users
schema.Schema.instantiable = True

# Add an extension property to indicate if members should be editable by users
schema.Member.editable = True

# Add an extesnion property to indiciate if members should be shown in detailed view
schema.Member.visible_in_detail_view = True

# Add an extension property to group types
schema.Schema.type_group = None

# Add an extension property to indicate if relations should be excluded if no
# relatable elements exist
schema.Collection.exclude_when_empty = False

# Add an extension property to determine if members should participate in item
# revisions
schema.Member.versioned = True

@when(schema.RelationMember.attached_as_orphan)
def _hide_self_contained_relations(event):
    if event.anonymous:
        event.source.visible = False

# Register the 'text/javascript' MIME type
import mimetypes
if not mimetypes.guess_extension("text/javascript"):
    mimetypes.add_type("text/javascript", ".js")
del mimetypes

# Base content types
#------------------------------------------------------------------------------
from woost.models.configuration import Configuration
from woost.models.website import Website
from woost.models.websitesession import (
    get_current_website,
    set_current_website
)
from woost.models.changesets import ChangeSet, Change, changeset_context
from woost.models.item import Item
from woost.models.action import Action
from woost.models.userview import UserView
from woost.models.publicationschemes import (
    PublicationScheme,
    PathResolution,
    HierarchicalPublicationScheme,
    IdPublicationScheme,
    DescriptiveIdPublicationScheme
)
from woost.models.publishable import (
    Publishable,
    IsPublishedExpression,
    IsAccessibleExpression
)
from woost.models.document import Document
from woost.models.template import Template
from woost.models.controller import Controller
from woost.models.user import (
    User,
    AuthorizationError
)
from woost.models.usersession import (
    get_current_user,
    set_current_user
)
from woost.models.role import Role
from woost.models.permission import (
    Permission,
    CreatePermission,
    ReadPermission,
    ModifyPermission,
    DeletePermission,
    ConfirmDraftPermission,
    RenderPermission,
    ReadMemberPermission,
    ModifyMemberPermission,
    CreateTranslationPermission,
    ReadTranslationPermission,
    ModifyTranslationPermission,
    DeleteTranslationPermission,
    ReadHistoryPermission,
    restricted_modification_context,
    delete_validating,
    PermissionExpression,
    ChangeSetPermissionExpression
)
from woost.models.standardpage import StandardPage
from woost.models.file import File
from woost.models.news import News
from woost.models.event import Event
from woost.models.uri import URI
from woost.models.file import File
from woost.models.style import Style
from woost.models.extension import (
    Extension,
    extension_translations,
    load_extensions
)
from woost.models.trigger import (
    Trigger,
    ContentTrigger,
    CreateTrigger,
    InsertTrigger,
    ModifyTrigger,
    DeleteTrigger,
    ConfirmDraftTrigger
)
from woost.models.triggerresponse import (
    TriggerResponse,
    CustomTriggerResponse,
    SendEmailTriggerResponse
)
from woost.models.emailtemplate import EmailTemplate
from woost.models.feed import Feed

from woost.models.userfilter import (
    OwnItemsFilter,
    IsPublishedFilter,
    TypeFilter
)

from woost.models.caching import CachingPolicy, expire_cache

from woost.models import rendering
from woost.models.videoplayersettings import VideoPlayerSettings
from woost.models import staticpublication
from woost.models import migration

