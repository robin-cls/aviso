from __future__ import annotations

from pydantic import BaseModel, Field


class GcoCharacterString(BaseModel):
    text: str = Field(..., alias='#text')


class MccVersion(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(..., alias='gco:CharacterString')


class MccMDIdentifier(BaseModel):
    mcc_version: MccVersion = Field(..., alias='mcc:version')


class CitIdentifier(BaseModel):
    mcc_MD_Identifier: MccMDIdentifier = Field(..., alias='mcc:MD_Identifier')


class CitCICitation(BaseModel):
    cit_identifier: CitIdentifier = Field(..., alias='cit:identifier')


class MriCitation(BaseModel):
    cit_CI_Citation: CitCICitation = Field(..., alias='cit:CI_Citation')


class MriAbstract(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(..., alias='gco:CharacterString')


class MriCredit(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(..., alias='gco:CharacterString')


class MriMDDataIdentification(BaseModel):
    mri_citation: MriCitation = Field(..., alias='mri:citation')
    mri_abstract: MriAbstract = Field(..., alias='mri:abstract')
    mri_credit: MriCredit = Field(..., alias='mri:credit')


class MdbIdentificationInfo(BaseModel):
    mri_MD_DataIdentification: MriMDDataIdentification = Field(
        ..., alias='mri:MD_DataIdentification'
    )


class CitDescription(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(..., alias='gco:CharacterString')


class CitLinkage(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(..., alias='gco:CharacterString')


class CitCIOnlineResource(BaseModel):
    cit_description: CitDescription = Field(..., alias='cit:description')
    cit_linkage: CitLinkage = Field(..., alias='cit:linkage')


class MrdOnLineItem(BaseModel):
    cit_CI_OnlineResource: CitCIOnlineResource = Field(
        ..., alias='cit:CI_OnlineResource'
    )


class MrdMDDigitalTransferOptions(BaseModel):
    mrd_onLine: list[MrdOnLineItem] = Field(..., alias='mrd:onLine')


class MrdTransferOptions(BaseModel):
    mrd_MD_DigitalTransferOptions: MrdMDDigitalTransferOptions = Field(
        ..., alias='mrd:MD_DigitalTransferOptions'
    )


class MrdMDDistribution(BaseModel):
    mrd_transferOptions: MrdTransferOptions = Field(..., alias='mrd:transferOptions')


class MdbDistributionInfo(BaseModel):
    mrd_MD_Distribution: MrdMDDistribution = Field(..., alias='mrd:MD_Distribution')


class MccCode(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(..., alias='gco:CharacterString')


class MccMDIdentifier1(BaseModel):
    mcc_code: MccCode = Field(..., alias='mcc:code')


class MrcProcessingLevelCode(BaseModel):
    mcc_MD_Identifier: MccMDIdentifier1 = Field(..., alias='mcc:MD_Identifier')


class MrcMDCoverageDescription(BaseModel):
    mrc_processingLevelCode: MrcProcessingLevelCode = Field(
        ..., alias='mrc:processingLevelCode'
    )


class MdbContentInfo(BaseModel):
    mrc_MD_CoverageDescription: MrcMDCoverageDescription = Field(
        ..., alias='mrc:MD_CoverageDescription'
    )


class AvisoProductModel(BaseModel):
    mdb_identificationInfo: MdbIdentificationInfo = Field(
        ..., alias='mdb:identificationInfo'
    )
    mdb_distributionInfo: MdbDistributionInfo = Field(..., alias='mdb:distributionInfo')
    mdb_contentInfo: MdbContentInfo = Field(..., alias='mdb:contentInfo')
