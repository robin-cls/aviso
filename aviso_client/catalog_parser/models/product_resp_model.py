from pydantic import BaseModel, Field, model_validator


class GcoCharacterString(BaseModel):
    text: str = Field(..., alias='#text')


class MccVersion(BaseModel):
    gco_CharacterString: GcoCharacterString = Field(..., alias='gco:CharacterString')


class MccMDIdentifier(BaseModel):
    mcc_version: MccVersion = Field(..., alias='mcc:version')


class CitIdentifier(BaseModel):
    mcc_MD_Identifier: MccMDIdentifier = Field(..., alias='mcc:MD_Identifier')


class CitCICitation(BaseModel):
    cit_identifier: list[CitIdentifier] | CitIdentifier = Field(..., alias='cit:identifier')

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
    mrd_onLine: list[MrdOnLineItem] | MrdOnLineItem = Field(..., alias='mrd:onLine')


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
    
    @model_validator(mode="before")
    @classmethod
    def handle_multiple_aliases(cls, data):
        if isinstance(data, dict):
            aliases = ['mrc:MD_CoverageDescription', 'mrc:MI_CoverageDescription']
            for alias in aliases:
                if alias in data:
                    data['mrc:MD_CoverageDescription'] = data[alias]
                    break
        return data


class AvisoProductModel(BaseModel):
    mdb_identificationInfo: MdbIdentificationInfo = Field(
        ..., alias='mdb:identificationInfo'
    )
    mdb_distributionInfo: MdbDistributionInfo = Field(..., alias='mdb:distributionInfo')
    mdb_contentInfo: MdbContentInfo = Field(..., alias='mdb:contentInfo')

    def get_last_version(self):
        cit_id = self.mdb_identificationInfo.mri_MD_DataIdentification.mri_citation.cit_CI_Citation.cit_identifier
        if isinstance(cit_id, list):
            cit_id = cit_id[0]
        return cit_id.mcc_MD_Identifier.mcc_version.gco_CharacterString.text
    
    def get_tds_url(self):        
        transferOptions = self.mdb_distributionInfo.mrd_MD_Distribution.mrd_transferOptions
        if isinstance(transferOptions, list):
            transferOptions = transferOptions[0]
        online = transferOptions.mrd_MD_DigitalTransferOptions.mrd_onLine
        
        for online_resource in online:
            if online_resource is not None:
                if online_resource.cit_CI_OnlineResource.cit_description.gco_CharacterString.text == 'THREDDS':
                    return online_resource.cit_CI_OnlineResource.cit_linkage.gco_CharacterString.text
                
    def get_processing_level(self):
        return self.mdb_contentInfo.mrc_MD_CoverageDescription.mrc_processingLevelCode.mcc_MD_Identifier.mcc_code.gco_CharacterString.text
    
    def get_abstract(self):
        return self.mdb_identificationInfo.mri_MD_DataIdentification.mri_abstract.gco_CharacterString.text
    
    def get_credit(self):
        return self.mdb_identificationInfo.mri_MD_DataIdentification.mri_credit.gco_CharacterString.text

