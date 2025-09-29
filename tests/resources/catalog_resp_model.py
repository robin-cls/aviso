from __future__ import annotations

from pydantic import BaseModel, Field
from datetime import datetime


class ResourceTitleObject(BaseModel):
    default: str


class ResourceAbstractObject(BaseModel):
    default: list[str]


class DescriptionObject(BaseModel):
    default: str


class UrlObject(BaseModel):
    default: str


class NameObject(BaseModel):
    default: str


class LinkItem(BaseModel):
    descriptionObject: DescriptionObject | None = None
    urlObject: UrlObject
    nameObject: NameObject | None = None
    protocol: str


class ResourceDateItem(BaseModel):
    date: datetime


class FieldSource(BaseModel):
    resourceTitleObject: ResourceTitleObject
    resourceAbstractObject: ResourceAbstractObject
    link: list[LinkItem]
    resourceDate: list[ResourceDateItem]


class Hit(BaseModel):
    field_id: str = Field(..., alias='_id')
    field_source: FieldSource = Field(..., alias='_source')


class Hits(BaseModel):
    hits: list[Hit]


class AvisoCatalogModel(BaseModel):
    hits: Hits
