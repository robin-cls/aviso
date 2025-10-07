from pydantic import BaseModel, Field, model_validator


class GcoCharacterString(BaseModel):
    text: str = Field(..., alias='#text')


class MccVersion(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(
        ..., alias='gco:CharacterString')


class MccMDIdentifier(BaseModel):
    mcc_version: MccVersion = Field(..., alias='mcc:version')


class CitIdentifier(BaseModel):
    mcc_MD_Identifier: MccMDIdentifier = Field(..., alias='mcc:MD_Identifier')


class CitCICitation(BaseModel):
    cit_identifier: list[CitIdentifier] = Field(..., alias='cit:identifier')

    @model_validator(mode='before')
    @classmethod
    def normalize_identifier(cls, data):
        ids = data.get('cit:identifier')
        if not ids:
            return {'cit:identifier': []}
        if isinstance(ids, dict):
            return {'cit:identifier': [ids]}
        if isinstance(ids, list):
            cleaned = [item for item in ids if isinstance(item, dict)]
            return {'cit:identifier': cleaned}
        return data


class MriCitation(BaseModel):
    cit_CI_Citation: CitCICitation = Field(..., alias='cit:CI_Citation')


class MriAbstract(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(
        ..., alias='gco:CharacterString')


class MriCredit(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(
        ..., alias='gco:CharacterString')


class MriMDDataIdentification(BaseModel):
    mri_citation: MriCitation = Field(..., alias='mri:citation')
    mri_abstract: MriAbstract = Field(..., alias='mri:abstract')
    mri_credit: MriCredit = Field(..., alias='mri:credit')


class MdbIdentificationInfo(BaseModel):
    mri_MD_DataIdentification: MriMDDataIdentification = Field(
        ..., alias='mri:MD_DataIdentification')


class CitDescription(BaseModel):
    gco_CharacterString: GcoCharacterString | None = Field(
        None, alias='gco:CharacterString')


class CitLinkage(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(
        ..., alias='gco:CharacterString')


class CitCIOnlineResource(BaseModel):
    cit_description: CitDescription | None = Field(None,
                                                   alias='cit:description')
    cit_linkage: CitLinkage = Field(..., alias='cit:linkage')


class MrdOnLineItem(BaseModel):
    cit_CI_OnlineResource: CitCIOnlineResource = Field(
        ..., alias='cit:CI_OnlineResource')


class MrdMDDigitalTransferOptions(BaseModel):
    mrd_onLine: list[MrdOnLineItem] = Field(..., alias='mrd:onLine')

    @model_validator(mode='before')
    @classmethod
    def normalize_online(cls, data):
        online = data.get('mrd:onLine')
        if not online:
            return {'mrd:onLine': []}
        if isinstance(online, dict):
            return {'mrd:onLine': [online]}
        if isinstance(online, list):
            cleaned = [item for item in online if isinstance(item, dict)]
            return {'mrd:onLine': cleaned}
        return data


class MrdTransferOptions(BaseModel):
    mrd_MD_DigitalTransferOptions: MrdMDDigitalTransferOptions = Field(
        ..., alias='mrd:MD_DigitalTransferOptions')


class MrdMDDistribution(BaseModel):
    mrd_transferOptions: list[MrdTransferOptions] = Field(
        ..., alias='mrd:transferOptions')

    @model_validator(mode='before')
    @classmethod
    def normalize_transfer_options(cls, data):
        opts = data.get('mrd:transferOptions')
        if not opts:
            return {'mrd:transferOptions': []}
        if isinstance(opts, dict):
            return {'mrd:transferOptions': [opts]}
        if isinstance(opts, list):
            cleaned = [item for item in opts if isinstance(item, dict)]
            return {'mrd:transferOptions': cleaned}
        return data


class MdbDistributionInfo(BaseModel):
    mrd_MD_Distribution: MrdMDDistribution = Field(...,
                                                   alias='mrd:MD_Distribution')


class MccCode(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(
        ..., alias='gco:CharacterString')


class MccMDIdentifier1(BaseModel):
    mcc_code: MccCode = Field(..., alias='mcc:code')


class MrcProcessingLevelCode(BaseModel):
    mcc_MD_Identifier: MccMDIdentifier1 = Field(..., alias='mcc:MD_Identifier')


class MrcMDCoverageDescription(BaseModel):
    mrc_processingLevelCode: MrcProcessingLevelCode = Field(
        ..., alias='mrc:processingLevelCode')


class MdbContentInfo(BaseModel):
    mrc_MD_CoverageDescription: MrcMDCoverageDescription = Field(
        ..., alias='mrc:MD_CoverageDescription')

    @model_validator(mode='before')
    @classmethod
    def handle_multiple_aliases(cls, data):
        if isinstance(data, dict):
            aliases = [
                'mrc:MD_CoverageDescription', 'mrc:MI_CoverageDescription'
            ]
            for alias in aliases:
                if alias in data:
                    data['mrc:MD_CoverageDescription'] = data[alias]
                    break
        return data


class AvisoProductModel(BaseModel):
    mdb_identificationInfo: MdbIdentificationInfo = Field(
        ..., alias='mdb:identificationInfo')
    mdb_distributionInfo: MdbDistributionInfo = Field(
        ..., alias='mdb:distributionInfo')
    mdb_contentInfo: MdbContentInfo = Field(..., alias='mdb:contentInfo')

    def get_last_version(self) -> str:
        cit_id = (self.mdb_identificationInfo.mri_MD_DataIdentification.
                  mri_citation.cit_CI_Citation.cit_identifier[0])

        return cit_id.mcc_MD_Identifier.mcc_version.gco_CharacterString.text

    def get_tds_url(self) -> str:
        transferOptions = (self.mdb_distributionInfo.mrd_MD_Distribution.
                           mrd_transferOptions[0])
        online = transferOptions.mrd_MD_DigitalTransferOptions.mrd_onLine

        for online_resource in online:
            if (online_resource.cit_CI_OnlineResource.cit_description.
                    gco_CharacterString.text == 'THREDDS'):
                return (online_resource.cit_CI_OnlineResource.cit_linkage.
                        gco_CharacterString.text)
        return ''

    def get_processing_level(self) -> str:
        return (self.mdb_contentInfo.mrc_MD_CoverageDescription.
                mrc_processingLevelCode.mcc_MD_Identifier.mcc_code.
                gco_CharacterString.text)

    def get_abstract(self) -> str:
        return (self.mdb_identificationInfo.mri_MD_DataIdentification.
                mri_abstract.gco_CharacterString.text)

    def get_credit(self) -> str:
        return (self.mdb_identificationInfo.mri_MD_DataIdentification.
                mri_credit.gco_CharacterString.text)
