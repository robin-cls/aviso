from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FieldShards(BaseModel):
    total: int
    successful: int
    skipped: int
    failed: int


class Total(BaseModel):
    value: int
    relation: str


class StandardNameObject(BaseModel):
    default: str
    langeng: str


class StandardVersionObject(BaseModel):
    default: str
    lang: str


class ClCharacterSetItem(BaseModel):
    key: str
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ClResourceScopeItem(BaseModel):
    key: str
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ClFunctionItem(BaseModel):
    key: str
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ClGeometricObjectTypeItem(BaseModel):
    key: str
    default: str
    langeng: str
    link: str


class ClStatu(BaseModel):
    key: str
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ClSpatialRepresentationTypeItem(BaseModel):
    key: str
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ClTypeItem(BaseModel):
    key: str
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ClAccessConstraint(BaseModel):
    key: str
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ClUseConstraint(BaseModel):
    key: str
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ResourceTitleObject(BaseModel):
    default: str
    langeng: str
    langfre: str | None = None


class ResourceDateItem(BaseModel):
    type: str
    date: datetime


class ResourceTemporalDateRangeItem(BaseModel):
    gte: str
    lte: str


class ResourceAbstractObject(BaseModel):
    default: str


class ClResourceCharacterSetItem(BaseModel):
    key: str
    default: str
    langeng: str
    link: str


class OrgForResourceObjectItem(BaseModel):
    default: str
    langeng: str


class DistributorOrgForResourceObject(BaseModel):
    default: str
    langeng: str


class OrganisationObject(BaseModel):
    default: str
    langeng: str


class Identifier(BaseModel):
    code: str
    codeSpace: str
    link: str


class ContactForResourceItem(BaseModel):
    organisationObject: OrganisationObject
    role: str
    email: str
    website: str
    logo: str
    individual: str
    position: str
    phone: str
    address: str
    identifiers: list[Identifier] | None = None


class FunderOrgForResourceObject(BaseModel):
    default: str
    langeng: str


class PointOfContactOrgForResourceObject(BaseModel):
    default: str
    langeng: str


class OriginatorOrgForResourceObject(BaseModel):
    default: str
    langeng: str


class OriginatorOrgForResourceObjectItem(BaseModel):
    default: str
    langeng: str


class ResourceCreditObjectItem(BaseModel):
    default: str
    langeng: str
    langfre: str | None = None


class TagItem(BaseModel):
    default: str
    langeng: str
    key: str | None = None
    link: str | None = None
    langfre: str | None = None


class KeywordTypeThemeItem(BaseModel):
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class KeywordTypeProcessingLevelItem(BaseModel):
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ThOdatisCentreDonnee(BaseModel):
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ThGCMDparameterItem(BaseModel):
    default: str
    langeng: str
    link: str


class ThNVSOD1Item(BaseModel):
    default: str
    langeng: str
    langfre: str
    link: str


class ThMyoceanProcessingLevelItem(BaseModel):
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ThTypeJeuxDonneeItem(BaseModel):
    default: str
    langeng: str
    langfre: str
    link: str


class ThOtherKeywords(BaseModel):
    title: str
    theme: str
    keywords: list


class MultilingualTitle(BaseModel):
    default: str
    langeng: str
    link: str


class Keyword(BaseModel):
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ThOdatisCentreDonnees(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle
    theme: str
    link: str
    keywords: list[Keyword]


class Keyword1(BaseModel):
    default: str
    langeng: str
    link: str


class ThGCMDparameter(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle
    theme: str
    link: str
    keywords: list[Keyword1]


class Keyword2(BaseModel):
    default: str
    langeng: str
    langfre: str
    link: str


class ThNVSOD1(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle
    theme: str
    link: str
    keywords: list[Keyword2]


class Keyword3(BaseModel):
    default: str
    langeng: str
    link: str
    langfre: str | None = None


class ThMyoceanProcessingLevel(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle
    theme: str
    link: str
    keywords: list[Keyword3]


class Keyword4(BaseModel):
    default: str
    langeng: str
    langfre: str
    link: str


class ThTypeJeuxDonnee(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle
    theme: str
    link: str
    keywords: list[Keyword4]


class MultilingualTitle5(BaseModel):
    default: str
    langeng: str


class ThOdatisVariables(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle5
    theme: str
    link: str
    keywords: list


class ThOtherKeywordsPlatform(BaseModel):
    title: str
    theme: str
    keywords: list


class MultilingualTitle6(BaseModel):
    default: str
    langeng: str
    link: str


class ThCersatLatency(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle6
    theme: str
    link: str
    keywords: list[Keyword4]


class ThCersatParameter(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle6
    theme: str
    link: str
    keywords: list[Keyword4]


class ThCersatProcessingLevel(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle6
    theme: str
    link: str
    keywords: list[Keyword4]


class ThCersatProject(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle6
    theme: str
    link: str
    keywords: list[Keyword4]


class ThHttpinspireeceuropaeuthemeTheme(BaseModel):
    id: str
    multilingualTitle: MultilingualTitle6
    theme: str
    link: str
    keywords: list[Keyword4]


class AllKeywords(BaseModel):
    th_otherKeywords_: ThOtherKeywords | None = Field(
        None, alias='th_otherKeywords-')
    th_odatis_centre_donnees: ThOdatisCentreDonnees
    th_GCMDparameter: ThGCMDparameter
    th_NVS_OD1: ThNVSOD1 = Field(..., alias='th_NVS-OD1')
    th_myocean_processing_level: ThMyoceanProcessingLevel | None = Field(
        None, alias='th_myocean-processing-level')
    th_type_jeux_donnee: ThTypeJeuxDonnee
    th_odatis_variables: ThOdatisVariables | None = None
    th_otherKeywords_platform: ThOtherKeywordsPlatform | None = Field(
        None, alias='th_otherKeywords-platform')
    th_cersat_latency: ThCersatLatency | None = None
    th_cersat_parameter: ThCersatParameter | None = None
    th_cersat_processing_level: ThCersatProcessingLevel | None = None
    th_cersat_project: ThCersatProject | None = None
    th_httpinspireeceuropaeutheme_theme: ThHttpinspireeceuropaeuthemeTheme | None = (
        Field(None, alias='th_httpinspireeceuropaeutheme-theme'))


class ThOdatisCentreDonneesTree(BaseModel):
    default: list[str]
    key: list[str]


class ThGCMDparameterTree(BaseModel):
    default: list[str]
    key: list[str]


class ThMyoceanProcessingLevelTree(BaseModel):
    default: list[str]
    key: list[str]


class ClTopicItem(BaseModel):
    key: str
    default: str
    langeng: str
    langfre: str | None = None


class MDLegalConstraintsOtherConstraintsObjectItem(BaseModel):
    default: str
    langeng: str
    link: str | None = None
    langfre: str | None = None


class MDLegalConstraintsUseLimitationObjectItem(BaseModel):
    default: str
    langeng: str
    link: str | None = None


class LicenseObjectItem(BaseModel):
    default: str
    langeng: str
    link: str | None = None
    langfre: str | None = None


class GeomItem(BaseModel):
    type: str
    coordinates: list[list[list[float]]]


class ResourceTemporalExtentDateRangeItem(BaseModel):
    gte: str
    lte: str


class Start(BaseModel):
    date: str


class End(BaseModel):
    date: str | None = None


class ResourceTemporalExtentDetail(BaseModel):
    start: Start
    end: End


class LineageObject(BaseModel):
    default: str
    langeng: str


class UrlObject(BaseModel):
    default: str
    langeng: str
    langfre: str | None = None


class NameObject(BaseModel):
    default: str
    langeng: str


class DescriptionObject(BaseModel):
    default: str
    langeng: str
    langfre: str | None = None


class LinkItem(BaseModel):
    protocol: str
    mimeType: str
    urlObject: UrlObject
    nameObject: NameObject | None = None
    descriptionObject: DescriptionObject | None = None
    function: str
    applicationProfile: str
    group: int


class OverviewItem(BaseModel):
    data: str
    nameObject: NameObject | None = None
    url: str


class ContactItem(BaseModel):
    organisationObject: OrganisationObject
    role: str
    email: str
    website: str
    logo: str
    individual: str
    position: str
    phone: str
    address: str


class ClAssociationTypeItem(BaseModel):
    key: str
    default: str
    langeng: str
    langfre: str
    link: str


class KeywordTypePlaceItem(BaseModel):
    default: str
    langeng: str
    langfre: str | None = None


class ThCersatLatencyItem(BaseModel):
    default: str
    langeng: str
    langfre: str
    link: str


class ThCersatParameterItem(BaseModel):
    default: str
    langeng: str
    langfre: str
    link: str


class ThCersatProcessingLevelItem(BaseModel):
    default: str
    langeng: str
    langfre: str
    link: str


class ThCersatProjectItem(BaseModel):
    default: str
    langeng: str
    langfre: str
    link: str


class ThHttpinspireeceuropaeuthemeThemeItem(BaseModel):
    default: str
    langeng: str
    langfre: str
    link: str


class ThCersatParameterTree(BaseModel):
    default: list[str]
    key: list[str]


class ThCersatProcessingLevelTree(BaseModel):
    default: list[str]
    key: list[str]


class ThHttpinspireeceuropaeuthemeThemeTree(BaseModel):
    default: list[str]
    key: list[str]


class ThNVSOD1Tree(BaseModel):
    default: list[str]
    key: list[str]


class ThTypeJeuxDonneeTree(BaseModel):
    default: list[str]
    key: list[str]


class ExtentIdentifierObjectItem(BaseModel):
    default: str
    langeng: str


class CrsDetail(BaseModel):
    code: str
    codeSpace: str
    name: str
    url: str


class DescriptionObject1(BaseModel):
    default: str
    langeng: str


class ProcessStep(BaseModel):
    descriptionObject: DescriptionObject1
    date: str


class ContactForDistributionItem(BaseModel):
    role: str
    email: str
    website: str
    logo: str
    individual: str
    position: str
    phone: str
    address: str


class RecordLinkItem(BaseModel):
    type: str
    associationType: str | None = None
    initiativeType: str | None = None
    to: str
    url: str
    title: str
    origin: str


class ThCersatLatencyTree(BaseModel):
    default: list[str]
    key: list[str]


class ResourceIdentifierItem(BaseModel):
    code: str
    codeSpace: str
    link: str


class ThCersatProjectTree(BaseModel):
    default: list[str]
    key: list[str]


class IndexingErrorMsgItem(BaseModel):
    string: str
    type: str
    values: dict[str, Any]


class ClInitiativeTypeItem(BaseModel):
    key: str
    default: str
    langeng: str
    langfre: str
    link: str


class FieldSource(BaseModel):
    docType: str
    document: str
    metadataIdentifier: str
    standardNameObject: StandardNameObject
    standardVersionObject: StandardVersionObject | None = None
    indexingDate: int
    dateStamp: str
    mainLanguage: str
    cl_characterSet: list[ClCharacterSetItem]
    resourceType: list[str]
    cl_resourceScope: list[ClResourceScopeItem]
    cl_function: list[ClFunctionItem]
    cl_geometricObjectType: list[ClGeometricObjectTypeItem] | None = None
    cl_status: list[ClStatu]
    cl_spatialRepresentationType: list[ClSpatialRepresentationTypeItem]
    cl_type: list[ClTypeItem]
    cl_accessConstraints: list[ClAccessConstraint]
    cl_useConstraints: list[ClUseConstraint] | None = None
    resourceTitleObject: ResourceTitleObject
    publicationDateForResource: list[str] | None = None
    publicationYearForResource: str | None = None
    publicationMonthForResource: str | None = None
    resourceDate: list[ResourceDateItem]
    resourceTemporalDateRange: list[ResourceTemporalDateRangeItem]
    platforms: str | list[str]
    instruments: str | list[str]
    resourceAbstractObject: ResourceAbstractObject
    cl_resourceCharacterSet: list[ClResourceCharacterSetItem] | None = None
    OrgForResourceObject: list[OrgForResourceObjectItem]
    distributorOrgForResourceObject: DistributorOrgForResourceObject
    contactForResource: list[ContactForResourceItem]
    funderOrgForResourceObject: FunderOrgForResourceObject | None = None
    pointOfContactOrgForResourceObject: PointOfContactOrgForResourceObject
    originatorOrgForResourceObject: (OriginatorOrgForResourceObject
                                     | list[OriginatorOrgForResourceObjectItem]
                                     | None) = None
    resourceCreditObject: list[ResourceCreditObjectItem]
    hasOverview: str
    resourceLanguage: list[str] | None = None
    inspireThemeNumber: str
    hasInspireTheme: str
    tag: list[TagItem]
    tagNumber: str
    isOpenData: str
    keywordType_theme: list[KeywordTypeThemeItem] = Field(
        ..., alias='keywordType-theme')
    keywordType_processing_level: list[
        KeywordTypeProcessingLevelItem] | None = Field(
            None, alias='keywordType-processing-level')
    th_otherKeywords_Number: str | None = Field(
        None, alias='th_otherKeywords-Number')
    th_otherKeywords_: list | None = Field(None, alias='th_otherKeywords-')
    th_odatis_centre_donneesNumber: str
    th_odatis_centre_donnees: list[ThOdatisCentreDonnee]
    th_GCMDparameterNumber: str
    th_GCMDparameter: list[ThGCMDparameterItem]
    th_NVS_OD1Number: str = Field(..., alias='th_NVS-OD1Number')
    th_NVS_OD1: list[ThNVSOD1Item] = Field(..., alias='th_NVS-OD1')
    th_myocean_processing_levelNumber: str | None = Field(
        None, alias='th_myocean-processing-levelNumber')
    th_myocean_processing_level: list[
        ThMyoceanProcessingLevelItem] | None = Field(
            None, alias='th_myocean-processing-level')
    th_type_jeux_donneeNumber: str
    th_type_jeux_donnee: list[ThTypeJeuxDonneeItem]
    th_odatis_variablesNumber: str | None = None
    th_odatis_variables: list | None = None
    allKeywords: AllKeywords
    th_odatis_centre_donnees_tree: ThOdatisCentreDonneesTree
    th_GCMDparameter_tree: ThGCMDparameterTree
    th_myocean_processing_level_tree: ThMyoceanProcessingLevelTree | None = Field(
        None, alias='th_myocean-processing-level_tree')
    cl_topic: list[ClTopicItem]
    resolutionDistance: list[str]
    spatialRepresentationType: str
    MD_LegalConstraintsOtherConstraintsObject: list[
        MDLegalConstraintsOtherConstraintsObjectItem]
    MD_LegalConstraintsUseLimitationObject: list[
        MDLegalConstraintsUseLimitationObjectItem]
    licenseObject: list[LicenseObjectItem]
    geom: list[GeomItem]
    location: str
    resourceTemporalExtentDateRange: (list[ResourceTemporalExtentDateRangeItem]
                                      | None) = None
    resourceTemporalExtentDetails: list[ResourceTemporalExtentDetail]
    featureTypes: list
    lineageObject: LineageObject | None = None
    format: list[str]
    linkUrl: list[str]
    linkProtocol: list[str]
    linkUrlProtocolWWWLINK: list[str]
    link: list[LinkItem]
    linkUrlProtocolOGCWMS: str | None = None
    linkUrlProtocolWWWLINK10httppublicationURL: str | list[str] | None = None
    linkUrlProtocolDOI: str
    recordGroup: str
    recordOwner: str
    valid_inspire: str
    uuid: str
    displayOrder: str
    groupPublishedId: list[int | str]
    popularity: int
    userinfo: str
    groupPublished: list[str]
    isPublishedToAll: str | list[bool]
    record: str
    draft: str
    changeDate: str
    valid_schematron_rules_datacite: str = Field(
        ..., alias='valid_schematron-rules-datacite')
    id: str
    valid_xsd: str
    createDate: str
    isPublishedToIntranet: str | list[bool]
    owner: str
    valid_schematron_rules_iso: str = Field(...,
                                            alias='valid_schematron-rules-iso')
    groupOwner: str
    logo: str
    hasxlinks: str
    op0: list[str]
    featureOfRecord: str
    op1: list[str]
    isPublishedToGuest: str | list[bool]
    extra: str
    documentStandard: str
    op3: str | list[str]
    op5: list[str]
    valid: str
    isTemplate: str
    feedbackCount: str
    rating: str
    isHarvested: str
    userSavedCount: str
    sourceCatalogue: str
    overview: list[OverviewItem]
    otherLanguage: list[str] | None = None
    otherLanguageId: str | None = None
    contact: list[ContactItem] | None = None
    cl_associationType: list[ClAssociationTypeItem] | None = None
    lastUpdateDateForResource: list[str] | None = None
    lastUpdateYearForResource: str | list[str] | None = None
    lastUpdateMonthForResource: str | list[str] | None = None
    processingLevel: str | None = None
    inspireTheme_syn: list[str] | None = None
    inspireTheme: list[str] | None = None
    inspireThemeFirst_syn: str | None = None
    inspireThemeFirst: str | None = None
    inspireAnnexForFirstTheme: str | None = None
    inspireThemeUri: list[str] | None = None
    inspireAnnex: list[str] | None = None
    keywordType_platform: list | None = Field(None,
                                              alias='keywordType-platform')
    keywordType_place: list[KeywordTypePlaceItem] | None = Field(
        None, alias='keywordType-place')
    th_otherKeywords_platformNumber: str | None = Field(
        None, alias='th_otherKeywords-platformNumber')
    th_otherKeywords_platform: list | None = Field(
        None, alias='th_otherKeywords-platform')
    th_cersat_latencyNumber: str | None = None
    th_cersat_latency: list[ThCersatLatencyItem] | None = None
    th_cersat_parameterNumber: str | None = None
    th_cersat_parameter: list[ThCersatParameterItem] | None = None
    th_cersat_processing_levelNumber: str | None = None
    th_cersat_processing_level: list[ThCersatProcessingLevelItem] | None = None
    th_cersat_projectNumber: str | None = None
    th_cersat_project: list[ThCersatProjectItem] | None = None
    th_httpinspireeceuropaeutheme_themeNumber: str | None = Field(
        None, alias='th_httpinspireeceuropaeutheme-themeNumber')
    th_httpinspireeceuropaeutheme_theme: (
        list[ThHttpinspireeceuropaeuthemeThemeItem] | None) = Field(
            None, alias='th_httpinspireeceuropaeutheme-theme')
    th_cersat_parameter_tree: ThCersatParameterTree | None = None
    th_cersat_processing_level_tree: ThCersatProcessingLevelTree | None = None
    th_httpinspireeceuropaeutheme_theme_tree: (
        ThHttpinspireeceuropaeuthemeThemeTree | None) = Field(
            None, alias='th_httpinspireeceuropaeutheme-theme_tree')
    th_NVS_OD1_tree: ThNVSOD1Tree | None = Field(None, alias='th_NVS-OD1_tree')
    th_type_jeux_donnee_tree: ThTypeJeuxDonneeTree | None = None
    extentIdentifierObject: list[ExtentIdentifierObjectItem] | None = None
    coordinateSystem: list[str] | None = None
    crsDetails: list[CrsDetail] | None = None
    processSteps: list[ProcessStep] | None = None
    dqCpt: str | None = None
    contactForDistribution: list[ContactForDistributionItem] | None = None
    recordLink: list[RecordLinkItem] | None = None
    recordLink_siblingsassociationTypecrossReference_initiativeType: (
        str | list[str] | None) = None
    recordLink_siblingsassociationTypecrossReference_initiativeType_uuid: (
        str | list[str] | None) = None
    recordLink_siblingsassociationTypecrossReference_initiativeType_url: (
        str | list[str] | None) = None
    agg_associated: str | list[str] | None = None
    agg_associated_crossReference: str | list[str] | None = None
    op2: str | list[str] | None = None
    creationDateForResource: list[str] | None = None
    creationYearForResource: str | None = None
    creationMonthForResource: str | None = None
    th_cersat_latency_tree: ThCersatLatencyTree | None = None
    resourceIdentifier: list[ResourceIdentifierItem] | None = None
    th_cersat_project_tree: ThCersatProjectTree | None = None
    indexingErrorMsg: list[IndexingErrorMsgItem] | None = None
    hassource: str | None = None
    recordLink_sources: str | None = None
    recordLink_sources_uuid: str | None = None
    recordLink_sources_url: str | None = None
    indexingError: str | None = None
    linkUrlProtocolnull: str | list[str] | None = None
    cl_initiativeType: list[ClInitiativeTypeItem] | None = None
    recordLink_siblingsassociationTypecrossReference_initiativeTypecollection: (
        str | None) = None
    recordLink_siblingsassociationTypecrossReference_initiativeTypecollection_uuid: (
        str | None) = None
    recordLink_siblingsassociationTypecrossReference_initiativeTypecollection_url: (
        str | None) = None


class Hit(BaseModel):
    field_index: str = Field(..., alias='_index')
    field_id: str = Field(..., alias='_id')
    field_score: float = Field(..., alias='_score')
    field_ignored: list[str] = Field(..., alias='_ignored')
    field_source: FieldSource = Field(..., alias='_source')
    edit: bool
    canReview: bool
    owner: bool
    isPublishedToAll: bool
    view: bool
    notify: bool
    download: bool
    dynamic: bool
    featured: bool
    selected: bool


class Hits(BaseModel):
    total: Total
    max_score: float
    hits: list[Hit]


class AvisoCatalogModel(BaseModel):
    took: int
    timed_out: bool
    field_shards: FieldShards = Field(..., alias='_shards')
    hits: Hits
