#-*- coding: utf-8 -*-
u"""

@author:		Martí Congost
@contact:		marti.congost@whads.com
@organization:	Whads/Accent SL
@since:			July 2008
"""
from datetime import date
from cocktail import schema
from woost.models.document import Document
from woost.models.file import File


class News(Document):

    members_order = [
        "news_date",
        "image",
        "summary",
        "body"
    ]

    news_date = schema.Date(
        required = True,
        indexed = True,
        default = schema.DynamicDefault(date.today),
        member_group = "content"
    )

    image = schema.Reference(
        type = File,
        related_end = schema.Collection(),
        relation_constraints = {"resource_type": "image"},
        member_group = "content"
    )

    summary = schema.String(
        edit_control = "woost.views.RichTextEditor",
        listed_by_default = False,
        translated = True,
        member_group = "content"
    )

    body = schema.String(
        edit_control = "woost.views.RichTextEditor",
        listed_by_default = False,
        translated = True,
        member_group = "content"
    )

