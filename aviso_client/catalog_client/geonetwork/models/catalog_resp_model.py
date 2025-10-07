from datetime import datetime

from pydantic import BaseModel, Field


class ResourceTitleObject(BaseModel):
    default: str


class ResourceAbstractObject(BaseModel):
    default: str


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

    def get_product_id(self) -> str:
        return self.field_id

    def get_product_title(self) -> str:
        return self.field_source.resourceTitleObject.default

    def get_product_keywords(self) -> str:
        return self.field_source.resourceAbstractObject.default

    def get_product_tds_catalog_url(self) -> str:
        for link in self.field_source.link:
            if (link.descriptionObject is not None
                    and link.descriptionObject.default == 'THREDDS'):
                return link.urlObject.default
        return ''

    def get_product_short_name(self) -> str:
        for link in self.field_source.link:
            if link.descriptionObject is not None:
                if (link.descriptionObject.default == 'THREDDS'
                        and link.nameObject is not None):
                    return link.nameObject.default.replace(' ', '_')
        return ''

    def get_product_doi(self) -> str:
        for link in self.field_source.link:
            if link.protocol == 'DOI':
                return link.urlObject.default
        return ''

    def get_product_last_update(self) -> datetime:
        return self.field_source.resourceDate[-1].date


class Hits(BaseModel):
    hits: list[Hit]


class AvisoCatalogModel(BaseModel):
    hits: Hits
