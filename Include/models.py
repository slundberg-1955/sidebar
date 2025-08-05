from django.db import models

class Matter(models.Model):
    matterid = models.IntegerField(db_column='matterId', primary_key=True)  # Field name made lowercase.
    title = models.CharField(max_length=500, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    lastmodified = models.DateTimeField(db_column='lastModified')  # Field name made lowercase.
    stageid = models.IntegerField(db_column='stageId')  # Field name made lowercase.
    mattertypeid = models.IntegerField(db_column='matterTypeId')  # Field name made lowercase.
    country = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    abstract = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    otherinfo = models.TextField(db_column='otherInfo', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    creatorid = models.IntegerField(db_column='creatorId')  # Field name made lowercase.
    datecreated = models.DateTimeField(db_column='dateCreated', blank=True, null=True)  # Field name made lowercase.
    rootactivityid = models.IntegerField(db_column='rootActivityId', blank=True, null=True)  # Field name made lowercase.
    class_field = models.CharField(db_column='class', max_length=25, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    subclass = models.CharField(db_column='subClass', max_length=25, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    externalmatter = models.BooleanField(db_column='externalMatter')  # Field name made lowercase.
    fileddate = models.DateTimeField(db_column='filedDate', blank=True, null=True)  # Field name made lowercase.
    confirmationno = models.CharField(db_column='confirmationNo', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    creatororgid = models.IntegerField(db_column='creatorOrgId', blank=True, null=True)  # Field name made lowercase.
    roleownerid = models.IntegerField(db_column='roleOwnerId', blank=True, null=True)  # Field name made lowercase.
    roleownertype = models.CharField(db_column='roleOwnerType', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    stagedescription = models.CharField(db_column='stageDescription', max_length=56, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    countryname = models.CharField(db_column='countryName', max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mattertypedescription = models.CharField(db_column='matterTypeDescription', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    serialnumber = models.CharField(db_column='serialNumber', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.BooleanField(db_column='isDeleted')  # Field name made lowercase.
    hostmatterno = models.CharField(db_column='hostMatterNo', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    cachedresdata = models.CharField(db_column='cachedResData', max_length=768, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    createdfromtemplateid = models.IntegerField(db_column='createdFromTemplateId', blank=True, null=True)  # Field name made lowercase.
    mattertypecatid = models.IntegerField(db_column='matterTypeCatId', blank=True, null=True)  # Field name made lowercase.
    isbillable = models.BooleanField(db_column='isBillable', blank=True, null=True)  # Field name made lowercase.
    submattertypeid = models.IntegerField(db_column='subMatterTypeId', blank=True, null=True)  # Field name made lowercase.
    hasffrights = models.BooleanField(db_column='hasFFRights')  # Field name made lowercase.
    parentmatterid = models.IntegerField(db_column='parentMatterId', blank=True, null=True)  # Field name made lowercase.
    islockatttime = models.BooleanField(db_column='isLockAttTime')  # Field name made lowercase.
    customstatusid = models.IntegerField(db_column='customStatusId', blank=True, null=True)  # Field name made lowercase.
    fmtserialno = models.CharField(db_column='fmtSerialNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    govcontractno = models.CharField(db_column='govContractNo', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mattermgmtno = models.CharField(db_column='matterMgmtNo', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isprototype = models.BooleanField(db_column='isPrototype', blank=True, null=True)  # Field name made lowercase.
    isdefaultcategoryprototype = models.BooleanField(db_column='isDefaultCategoryPrototype', blank=True, null=True)  # Field name made lowercase.
    datepurchased = models.DateTimeField(db_column='datePurchased', blank=True, null=True)  # Field name made lowercase.
    disableautoawards = models.BooleanField(db_column='disableAutoAwards')  # Field name made lowercase.
    isstatusactive = models.BooleanField(db_column='isStatusActive')  # Field name made lowercase.
    startpaydate = models.DateTimeField(db_column='startPayDate', blank=True, null=True)  # Field name made lowercase.
    startpaydatesource = models.CharField(db_column='startPayDateSource', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    primaryconfigurationid = models.IntegerField(db_column='primaryConfigurationId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Matter'

class Patent(models.Model):
    matterid = models.IntegerField(db_column='matterId', primary_key=True)  # Field name made lowercase.
    patentno = models.CharField(db_column='patentNo', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    issuedate = models.DateTimeField(db_column='issueDate', blank=True, null=True)  # Field name made lowercase.
    firstfilingdate = models.DateTimeField(db_column='firstFilingDate', blank=True, null=True)  # Field name made lowercase.
    pctappno = models.CharField(db_column='pctAppNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pctpubno = models.CharField(db_column='pctPubNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    appno = models.CharField(db_column='appNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pubno = models.CharField(db_column='pubNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pubdate = models.DateTimeField(db_column='pubDate', blank=True, null=True)  # Field name made lowercase.
    prioritycountry = models.CharField(db_column='priorityCountry', max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    prioritydate = models.DateTimeField(db_column='priorityDate', blank=True, null=True)  # Field name made lowercase.
    abandoneddate = models.DateTimeField(db_column='abandonedDate', blank=True, null=True)  # Field name made lowercase.
    isreissue = models.BooleanField(db_column='isReissue')  # Field name made lowercase.
    deadlinedate = models.DateTimeField(db_column='deadlineDate', blank=True, null=True)  # Field name made lowercase.
    priorityappno = models.CharField(db_column='priorityAppNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    priorityappdate = models.DateTimeField(db_column='priorityAppDate', blank=True, null=True)  # Field name made lowercase.
    prioritypubdate = models.DateTimeField(db_column='priorityPubDate', blank=True, null=True)  # Field name made lowercase.
    prioritypubno = models.CharField(db_column='priorityPubNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pctpubdate = models.DateTimeField(db_column='pctPubDate', blank=True, null=True)  # Field name made lowercase.
    expirationdate = models.DateTimeField(db_column='expirationDate', blank=True, null=True)  # Field name made lowercase.
    largeentitydeprecated = models.BooleanField(db_column='largeEntityDEPRECATED', blank=True, null=True)  # Field name made lowercase.
    artunitno = models.CharField(db_column='artUnitNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    prioritydocfiled = models.BooleanField(db_column='priorityDocFiled')  # Field name made lowercase.
    projectedpubdate = models.DateTimeField(db_column='projectedPubDate', blank=True, null=True)  # Field name made lowercase.
    actualpubdate = models.DateTimeField(db_column='actualPubDate', blank=True, null=True)  # Field name made lowercase.
    alloweddate = models.DateTimeField(db_column='allowedDate', blank=True, null=True)  # Field name made lowercase.
    pctappdate = models.DateTimeField(db_column='pctAppDate', blank=True, null=True)  # Field name made lowercase.
    designatedcountries = models.CharField(db_column='designatedCountries', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    othercountries = models.CharField(db_column='otherCountries', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    rceoccured = models.BooleanField(db_column='RCEOccured')  # Field name made lowercase.
    fmtpatentno = models.CharField(db_column='fmtPatentNo', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    exportcontrolled = models.BooleanField(db_column='exportControlled')  # Field name made lowercase.
    selfclassified = models.BooleanField(db_column='selfClassified')  # Field name made lowercase.
    independentclaims = models.IntegerField(db_column='independentClaims')  # Field name made lowercase.
    totalclaims = models.IntegerField(db_column='totalClaims')  # Field name made lowercase.
    totalclasses = models.IntegerField(db_column='totalClasses')  # Field name made lowercase.
    multipledesignscount = models.IntegerField(db_column='multipleDesignsCount')  # Field name made lowercase.
    designatedstatescount = models.IntegerField(db_column='designatedStatesCount')  # Field name made lowercase.
    nationalfilingdate = models.DateTimeField(db_column='nationalFilingDate', blank=True, null=True)  # Field name made lowercase.
    patenttermadjustment = models.IntegerField(db_column='patentTermAdjustment')  # Field name made lowercase.
    calculatedexpirationdate = models.DateTimeField(db_column='calculatedExpirationDate', blank=True, null=True)  # Field name made lowercase.
    correspondencecustno = models.CharField(db_column='correspondenceCustNo', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    powerofattorneycustno = models.CharField(db_column='powerOfAttorneyCustNo', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maintenancefeecustno = models.CharField(db_column='maintenanceFeeCustNo', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    parentappdate = models.DateTimeField(db_column='parentAppDate', blank=True, null=True)  # Field name made lowercase.
    parentappno = models.CharField(db_column='parentAppNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    dependentclaims = models.IntegerField(db_column='dependentClaims')  # Field name made lowercase.
    class_field = models.CharField(db_column='class', max_length=25, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field renamed because it was a Python reserved word.
    subclass = models.CharField(db_column='subClass', max_length=25, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    parentgrantdate = models.DateTimeField(db_column='parentGrantDate', blank=True, null=True)  # Field name made lowercase.
    parentexpirydate = models.DateTimeField(db_column='parentExpiryDate', blank=True, null=True)  # Field name made lowercase.
    opipublicationdate = models.DateTimeField(db_column='opiPublicationDate', blank=True, null=True)  # Field name made lowercase.
    marketingappdate = models.DateTimeField(db_column='marketingAppDate', blank=True, null=True)  # Field name made lowercase.
    isextendedpatent = models.BooleanField(db_column='isExtendedPatent')  # Field name made lowercase.
    entitystatus = models.SmallIntegerField(db_column='entityStatus')  # Field name made lowercase.
    searchauthority = models.CharField(db_column='searchAuthority', max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    parentpubdate = models.DateTimeField(db_column='parentPubDate', blank=True, null=True)  # Field name made lowercase.
    pctreceivingoffice = models.CharField(db_column='pctReceivingOffice', max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    patenttermextension = models.IntegerField(db_column='patentTermExtension')  # Field name made lowercase.
    earliesteffectiveappno = models.CharField(db_column='earliestEffectiveAppNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    earliesteffectivedate = models.DateTimeField(db_column='earliestEffectiveDate', blank=True, null=True)  # Field name made lowercase.
    lockadjustedexpirydate = models.BooleanField(db_column='lockAdjustedExpiryDate')  # Field name made lowercase.
    prioritystatementcomments = models.TextField(db_column='priorityStatementComments', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    parentlocalfilingdate = models.DateTimeField(db_column='parentLocalFilingDate', blank=True, null=True)  # Field name made lowercase.
    unitaryeffectdate = models.DateTimeField(db_column='unitaryEffectDate', blank=True, null=True)  # Field name made lowercase.
    unformattedpubno = models.CharField(db_column='unformattedPubNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    upcoptout = models.BooleanField(db_column='upcOptOut', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Patent'

class Rvwmatterinventors(models.Model):
    orgid = models.IntegerField(db_column='orgId', blank=True, null=True)  # Field name made lowercase.
    matterid = models.IntegerField(db_column='matterId', null=False, primary_key=True)  # Field name made lowercase.
    inventor = models.TextField(blank=True, null=True)
    lastnamefirstname = models.TextField(db_column='lastNameFirstName', blank=True, null=True)  # Field name made lowercase.
    inventoremail = models.TextField(db_column='inventorEmail', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rvwMatterInventors'

class Rvwmatterpersonnel(models.Model):
    orgid = models.IntegerField(db_column='orgId', blank=True, null=True)  # Field name made lowercase.
    isprototype = models.BooleanField(db_column='isPrototype', blank=True, null=True)  # Field name made lowercase.
    isdefaultcategoryprototype = models.BooleanField(db_column='isDefaultCateGOryPrototype', blank=True, null=True)  # Field name made lowercase.
    matterid = models.IntegerField(db_column='matterId', primary_key=True, null=False)  # Field name made lowercase.
    ppid = models.IntegerField(db_column='ppId', blank=True, null=True)  # Field name made lowercase.
    status = models.CharField(max_length=1)
    datejoined = models.DateTimeField(db_column='dateJoined')  # Field name made lowercase.
    notes = models.CharField(max_length=200, blank=True, null=True)
    roleorderno = models.IntegerField(db_column='roleOrderNo', blank=True, null=True)  # Field name made lowercase.
    rolename = models.CharField(db_column='roleName', max_length=32)  # Field name made lowercase.
    roledesc = models.CharField(db_column='roleDesc', max_length=256)  # Field name made lowercase.
    roleid = models.IntegerField(db_column='roleId')  # Field name made lowercase.
    matterparticipantrowid = models.IntegerField(db_column='matterParticipantRowId')  # Field name made lowercase.
    billingacct = models.CharField(db_column='billingAcct', max_length=50, blank=True, null=True)  # Field name made lowercase.
    fname = models.CharField(db_column='fName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    mname = models.CharField(db_column='mName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    lname = models.CharField(db_column='lName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    personname = models.CharField(db_column='personName', max_length=302, blank=True, null=True)  # Field name made lowercase.
    personlastnamefirstname = models.CharField(db_column='personLastNameFirstName', max_length=302, blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(max_length=48, blank=True, null=True)
    orgname = models.CharField(db_column='orgName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    nickname = models.CharField(db_column='nickName', max_length=20, blank=True, null=True)  # Field name made lowercase.
    salutation = models.CharField(max_length=5, blank=True, null=True)
    citizenship = models.CharField(max_length=4, blank=True, null=True)
    registrationno = models.CharField(db_column='registrationNo', max_length=20, blank=True, null=True)  # Field name made lowercase.
    addrgroupid = models.IntegerField(db_column='addrGroupId', blank=True, null=True)  # Field name made lowercase.
    groupname = models.CharField(db_column='groupName', max_length=50, blank=True, null=True)  # Field name made lowercase.
    groupdescription = models.CharField(db_column='groupDescription', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rvwMatterPersonnel'

class Matterparticipant(models.Model):
    contactid = models.IntegerField(db_column='contactId')  # Field name made lowercase.
    roleid = models.IntegerField(db_column='roleId')  # Field name made lowercase.
    matterid = models.IntegerField(db_column='matterId', primary_key=True)  # Field name made lowercase.
    datejoined = models.DateTimeField(db_column='dateJoined')  # Field name made lowercase.
    statusdeprecated = models.CharField(db_column='statusDEPRECATED', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    billingacct = models.CharField(db_column='billingAcct', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    matterno = models.CharField(db_column='matterNo', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    rowid = models.IntegerField(db_column='rowId')  # Field name made lowercase.
    linkedorgid = models.IntegerField(db_column='linkedOrgId', blank=True, null=True)  # Field name made lowercase.
    groupid = models.IntegerField(db_column='groupId', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    notes = models.CharField(max_length=200, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    viewed = models.BooleanField(blank=True, null=True)
    roleorderno = models.IntegerField(db_column='roleOrderNo', blank=True, null=True)  # Field name made lowercase.
    billedentity = models.BooleanField(db_column='billedEntity', blank=True, null=True)  # Field name made lowercase.
    enableereport = models.CharField(db_column='enableEReport', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'MatterParticipant'


class Orgprofile(models.Model):
    opid = models.IntegerField(db_column='opId', primary_key=True)  # Field name made lowercase.
    orgid = models.IntegerField(blank=True, null=True)
    contactinfoid = models.IntegerField(db_column='contactInfoId', blank=True, null=True)  # Field name made lowercase.
    isincorp = models.BooleanField(db_column='isIncorp')  # Field name made lowercase.
    inccountry = models.CharField(db_column='incCountry', max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    incstate = models.CharField(db_column='incState', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orgname = models.CharField(db_column='orgName', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    contactname = models.CharField(db_column='contactName', max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    lastmodified = models.DateTimeField(db_column='lastModified', blank=True, null=True)  # Field name made lowercase.
    modifier = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    webaddress = models.CharField(db_column='webAddress', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    orgformid = models.IntegerField(db_column='orgFormId', blank=True, null=True)  # Field name made lowercase.
    addritempriv = models.IntegerField(db_column='addrItemPriv', blank=True, null=True)  # Field name made lowercase.
    shortname = models.CharField(db_column='shortName', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ptodepositacct = models.CharField(db_column='PTODepositAcct', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    currency = models.CharField(max_length=3, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    identifier = models.CharField(max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    parentopid = models.IntegerField(db_column='parentOpId', blank=True, null=True)  # Field name made lowercase.
    isclientcodemandatory = models.IntegerField(db_column='isClientCodeMandatory', blank=True, null=True)  # Field name made lowercase.
    secondaryaddressid = models.IntegerField(db_column='secondaryAddressId', blank=True, null=True)  # Field name made lowercase.
    ptocorrespondenceaddr1 = models.CharField(db_column='PTOCorrespondenceAddr1', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ptocorrespondenceaddr2 = models.CharField(db_column='PTOCorrespondenceAddr2', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ptocorrespondenceaddr3 = models.CharField(db_column='PTOCorrespondenceAddr3', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ptocorrespondenceaddr4 = models.CharField(db_column='PTOCorrespondenceAddr4', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ptoorgname = models.CharField(db_column='PTOOrgName', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    showcreditmanager = models.BooleanField(db_column='showCreditManager', blank=True, null=True)  # Field name made lowercase.
    ledgernumber = models.CharField(db_column='ledgerNumber', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    costcenter = models.CharField(db_column='costCenter', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    islicensedorgchild = models.BooleanField(db_column='isLicensedOrgChild')  # Field name made lowercase.
    grouptypeid = models.IntegerField(db_column='groupTypeId', blank=True, null=True)  # Field name made lowercase.
    encodedlineage = models.CharField(db_column='encodedLineage', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    attrib = models.SmallIntegerField()
    defaultroleidinmatter = models.IntegerField(db_column='defaultRoleIdInMatter', blank=True, null=True)  # Field name made lowercase.
    cpaclientnumber = models.CharField(db_column='cpaClientNumber', max_length=7, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ownerorgid = models.IntegerField(db_column='ownerOrgId', blank=True, null=True)  # Field name made lowercase.
    entitysize = models.CharField(db_column='entitySize', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    defaultbillableentityroleid = models.IntegerField(db_column='defaultBillableEntityRoleId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'orgprofile'

class Contactinfo(models.Model):
    contactinfoid = models.IntegerField(db_column='contactInfoId',primary_key=True)  # Field name made lowercase.
    address1 = models.CharField(max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    address2 = models.CharField(max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    city = models.CharField(max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    state = models.CharField(max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    zip = models.CharField(max_length=16, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    country = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone1 = models.CharField(max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone1ext = models.CharField(db_column='phone1Ext', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    phone2 = models.CharField(max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    phone2ext = models.CharField(db_column='phone2Ext', max_length=10, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    fax = models.CharField(max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    email = models.CharField(max_length=70, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    address3 = models.CharField(max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    fax1 = models.CharField(max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'contactinfo'

# SideBar Models
class MergeCategory(models.Model):
    categoryid = models.AutoField(primary_key=True)
    categoryname = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'merge_category'

class MergeRole(models.Model):
    roleid = models.AutoField(primary_key=True)
    rolename = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'merge_role'


class MergeDef(models.Model):
    mergeid = models.AutoField(primary_key=True)
    mergename = models.CharField(max_length=200)
    mergepath = models.CharField(max_length=200)
    merge_category_id = models.CharField(max_length=50, blank=True, null=True)
    merge_role_id = models.CharField(max_length=50, blank=True, null=True)
    mergemethod = models.CharField(max_length=100)
    settrays = models.BooleanField()
    contacts = models.BooleanField()
    skipbasic = models.BooleanField()
    esign = models.BooleanField(blank=True, null=True)
    operational = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'merge_def'

class Customernumbers(models.Model):
    opid = models.IntegerField(db_column='opId', primary_key=True)  # Field name made lowercase.
    correspondencecustno = models.CharField(db_column='correspondenceCustNo', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    powerofattorneycustno = models.CharField(db_column='powerOfAttorneyCustNo', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    maintenancefeecustno = models.CharField(db_column='maintenanceFeeCustNo', max_length=6, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    overridedefaultpoano = models.BooleanField(db_column='overrideDefaultPOANo', blank=True, null=True)  # Field name made lowercase.
    overridedefaultcorrespondenceno = models.BooleanField(db_column='overrideDefaultCorrespondenceNo', blank=True, null=True)  # Field name made lowercase.
    overridedefaultmaintenancefeeno = models.BooleanField(db_column='overrideDefaultMaintenanceFeeNo', blank=True, null=True)  # Field name made lowercase.
    overrideentitymatterroleid = models.IntegerField(db_column='overrideEntityMatterRoleId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'customernumbers'

class CustomerNos(models.Model):
    clientno = models.IntegerField(primary_key=True)
    clientname = models.CharField(max_length=500)
    correspno = models.IntegerField()
    poano = models.IntegerField()
    maintfeeno = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'customer_nos'

class Personprofile(models.Model):
    ppid = models.IntegerField(db_column='ppId', primary_key = True)  # Field name made lowercase.
    userid = models.IntegerField(db_column='userId', blank=True, null=True)  # Field name made lowercase.
    homecontactinfoid = models.IntegerField(db_column='homeContactInfoId')  # Field name made lowercase.
    salutation = models.CharField(max_length=5, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    fname = models.CharField(db_column='fName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    lname = models.CharField(db_column='lName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    cellphone = models.CharField(db_column='cellPhone', max_length=15, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pager = models.CharField(max_length=15, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    citizenship = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS')
    opid = models.IntegerField(db_column='opId', blank=True, null=True)  # Field name made lowercase.
    workcontactinfoid = models.IntegerField(db_column='workContactInfoId', blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(max_length=48, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    orgname = models.CharField(db_column='orgName', max_length=255, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ppownerorgid = models.IntegerField(db_column='ppOwnerOrgId', blank=True, null=True)  # Field name made lowercase.
    isinppownerorg = models.BooleanField(db_column='isInPpOwnerOrg')  # Field name made lowercase.
    fwdemailaddr = models.CharField(db_column='fwdEmailAddr', max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    fwdenabled = models.BooleanField(db_column='fwdEnabled')  # Field name made lowercase.
    registrationno = models.CharField(db_column='registrationNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    abandoned = models.BooleanField()
    mname = models.CharField(db_column='mName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    nickname = models.CharField(db_column='nickName', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    enableereport = models.CharField(db_column='enableEReport', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    namesuffix = models.CharField(db_column='nameSuffix', max_length=16, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isbillapprover = models.BooleanField(db_column='isBillApprover')  # Field name made lowercase.
    exportcontrolled = models.BooleanField(db_column='exportControlled')  # Field name made lowercase.
    externalid = models.CharField(db_column='externalId', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mailcontactinfoid = models.IntegerField(db_column='mailContactInfoId', blank=True, null=True)  # Field name made lowercase.
    statusdeprecated = models.CharField(db_column='statusDEPRECATED', max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    secondcitizenship = models.CharField(db_column='secondCitizenship', max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    disableaccess = models.BooleanField(db_column='disableAccess')  # Field name made lowercase.
    registrationstatus = models.IntegerField(db_column='registrationStatus')  # Field name made lowercase.
    sendemailtofoundationip = models.BooleanField(db_column='sendEmailToFoundationIP')  # Field name made lowercase.
    sendemailtowork = models.BooleanField(db_column='sendEmailToWork')  # Field name made lowercase.
    sendemailtohome = models.BooleanField(db_column='sendEmailToHome')  # Field name made lowercase.
    isnewmattersearch = models.BooleanField(db_column='isNewMatterSearch')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'personprofile'

class Activity(models.Model):
    activityid = models.IntegerField(db_column='activityId', primary_key = True)  # Field name made lowercase.
    matterid = models.IntegerField(db_column='matterId', blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    notes = models.CharField(max_length=1024, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    status = models.CharField(max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    templateid = models.IntegerField(db_column='templateId', blank=True, null=True)  # Field name made lowercase.
    isprototype = models.BooleanField(db_column='isPrototype')  # Field name made lowercase.
    orgid = models.IntegerField(db_column='orgId', blank=True, null=True)  # Field name made lowercase.
    isprivate = models.BooleanField(db_column='isPrivate')  # Field name made lowercase.
    createdfromtemplateid = models.IntegerField(db_column='createdFromTemplateId', blank=True, null=True)  # Field name made lowercase.
    isdocketact = models.BooleanField(db_column='isDocketAct', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS')
    immutable = models.BooleanField()
    privname = models.CharField(db_column='privName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    smryonetype = models.CharField(db_column='smryOneType', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    smryonename = models.CharField(db_column='smryOneName', max_length=256, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    smryonelabel = models.CharField(db_column='smryOneLabel', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    smrytwotype = models.CharField(db_column='smryTwoType', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    smrytwoname = models.CharField(db_column='smryTwoName', max_length=256, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    smrytwolabel = models.CharField(db_column='smryTwoLabel', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    ispreruleversion = models.BooleanField(db_column='isPreRuleVersion')  # Field name made lowercase.
    smryonevalue = models.DateTimeField(db_column='smryOneValue', blank=True, null=True)  # Field name made lowercase.
    smrytwovalue = models.DateTimeField(db_column='smryTwoValue', blank=True, null=True)  # Field name made lowercase.
    code = models.CharField(max_length=16, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    recurcount = models.IntegerField(db_column='recurCount')  # Field name made lowercase.
    launchedfromid = models.IntegerField(db_column='launchedFromId', blank=True, null=True)  # Field name made lowercase.
    argosnextclawactivitylaunched = models.BooleanField(db_column='argosNextClawActivityLaunched')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Activity'

class Relatedmatter(models.Model):
    primarymatterid = models.IntegerField(db_column='primaryMatterId', primary_key = True)  # Field name made lowercase.
    relatedmatterid = models.IntegerField(db_column='relatedMatterId')  # Field name made lowercase.
    relationdesc = models.CharField(db_column='relationDesc', max_length=1024, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    category = models.CharField(max_length=1, db_collation='SQL_Latin1_General_CP1_CI_AS')
    relatedisparent = models.BooleanField(db_column='relatedIsParent', blank=True, null=True)  # Field name made lowercase.
    relationtype = models.IntegerField(db_column='relationType')  # Field name made lowercase.
    rowid = models.IntegerField(db_column='rowId')  # Field name made lowercase.
    citedtopto = models.BooleanField(db_column='citedToPTO', blank=True, null=True)  # Field name made lowercase.
    claimspriority = models.BooleanField(db_column='claimsPriority', blank=True, null=True)  # Field name made lowercase.
    earliestpriority = models.BooleanField(db_column='earliestPriority', blank=True, null=True)  # Field name made lowercase.
    terminaldisclaimedto = models.BooleanField(db_column='terminalDisclaimedTo')  # Field name made lowercase.
    terminaldisclaimedby = models.BooleanField(db_column='terminalDisclaimedBy')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'relatedmatter'
        
class Task(models.Model):
    taskid = models.IntegerField(db_column='taskId')  # Field name made lowercase.
    activityid = models.IntegerField(db_column='activityId', blank=True, null=True)  # Field name made lowercase.
    name = models.CharField(max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    notes = models.TextField(db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    type = models.CharField(max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS')
    templateid = models.IntegerField(db_column='templateId', blank=True, null=True)  # Field name made lowercase.
    isprototype = models.BooleanField(db_column='isPrototype')  # Field name made lowercase.
    duedate = models.DateTimeField(db_column='dueDate', blank=True, null=True)  # Field name made lowercase.
    completiondate = models.DateTimeField(db_column='completionDate', blank=True, null=True)  # Field name made lowercase.
    basedatevalue = models.DateTimeField(db_column='baseDateValue', blank=True, null=True)  # Field name made lowercase.
    matterid = models.IntegerField(db_column='matterId', blank=True, null=True)  # Field name made lowercase.
    activityname = models.CharField(db_column='activityName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    createdfromtemplateid = models.IntegerField(db_column='createdFromTemplateId', blank=True, null=True)  # Field name made lowercase.
    immutable = models.BooleanField()
    privname = models.CharField(db_column='privName', max_length=100, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    completiondatename = models.CharField(db_column='completionDateName', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    nextdatename = models.CharField(db_column='nextDateName', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    nextdateval = models.DateTimeField(db_column='nextDateVal', blank=True, null=True)  # Field name made lowercase.
    basedateattr = models.CharField(db_column='baseDateAttr', max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    completiondesc = models.TextField(db_column='completionDesc', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ptrrefersto = models.CharField(db_column='ptrRefersTo', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    isactbound = models.BooleanField(db_column='isActBound')  # Field name made lowercase.
    code = models.CharField(max_length=16, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    verificationdate = models.DateTimeField(db_column='verificationDate', blank=True, null=True)  # Field name made lowercase.
    verificationdesc = models.CharField(db_column='verificationDesc', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    abandoneddate = models.DateTimeField(db_column='abandonedDate', blank=True, null=True)  # Field name made lowercase.
    abandoneddesc = models.CharField(db_column='abandonedDesc', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    subtype = models.IntegerField(db_column='subType')  # Field name made lowercase.
    additionaldata = models.TextField(db_column='additionalData', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    usedefaultassignments = models.BooleanField(db_column='useDefaultAssignments')  # Field name made lowercase.
    usedefaultemailreminders = models.BooleanField(db_column='useDefaultEmailReminders')  # Field name made lowercase.
    oldtemplateptr = models.IntegerField(db_column='oldTemplatePtr', blank=True, null=True)  # Field name made lowercase.
    recurrencecount = models.IntegerField(db_column='recurrenceCount', blank=True, null=True)  # Field name made lowercase.
    skipupgradereason = models.CharField(db_column='skipUpgradeReason', max_length=256, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Task'
        
class Attributeval(models.Model):
    attrdefid = models.IntegerField(db_column='attrDefId')  # Field name made lowercase.
    attributableobjtypeid = models.IntegerField(db_column='attributableObjTypeId')  # Field name made lowercase.
    objid = models.IntegerField(db_column='objId')  # Field name made lowercase.
    val = models.CharField(max_length=256, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    params = models.CharField(max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    ispublic = models.BooleanField(db_column='isPublic')  # Field name made lowercase.
    label = models.CharField(max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS')
    attrorder = models.IntegerField(db_column='attrOrder', blank=True, null=True)  # Field name made lowercase.
    index = models.IntegerField()
    immutable = models.BooleanField()
    readonly = models.BooleanField(db_column='readOnly')  # Field name made lowercase.
    privlabel = models.CharField(db_column='privLabel', max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    displayflags = models.IntegerField(db_column='displayFlags')  # Field name made lowercase.
    orgid = models.IntegerField(db_column='orgId')  # Field name made lowercase.
    isrequired = models.BooleanField(db_column='isRequired')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AttributeVal'
        
class Rvwactivitydateattribute(models.Model):
    activityid = models.IntegerField(db_column='activityId')  # Field name made lowercase.
    dateval = models.DateTimeField(db_column='dateVal', blank=True, null=True)  # Field name made lowercase.
    ispublic = models.BooleanField(db_column='isPublic')  # Field name made lowercase.
    attrvallabel = models.CharField(db_column='attrValLabel', max_length=64)  # Field name made lowercase.
    attrorder = models.IntegerField(db_column='attrOrder', blank=True, null=True)  # Field name made lowercase.
    orgid = models.IntegerField(db_column='orgId', blank=True, null=True)  # Field name made lowercase.
    displayflags = models.IntegerField(db_column='displayFlags')  # Field name made lowercase.
    summarydisplay = models.BooleanField(db_column='summaryDisplay', blank=True, null=True)  # Field name made lowercase.
    readonly = models.BooleanField(db_column='readOnly')  # Field name made lowercase.
    attrdefname = models.CharField(db_column='attrDefName', max_length=32)  # Field name made lowercase.
    activityname = models.CharField(db_column='activityName', max_length=100, blank=True, null=True)  # Field name made lowercase.
    matterid = models.IntegerField(db_column='matterId', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rvwactivityDateAttribute'
        
class Docketentry(models.Model):
    docketentryid = models.IntegerField(db_column='docketEntryId', primary_key = True)  # Field name made lowercase.
    taskid = models.IntegerField(db_column='taskId')  # Field name made lowercase.
    computedduedate = models.DateTimeField(db_column='computedDueDate', blank=True, null=True)  # Field name made lowercase.
    deltaparam = models.CharField(db_column='deltaParam', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    docketentrytypeid = models.IntegerField(db_column='docketEntryTypeId')  # Field name made lowercase.
    name = models.CharField(max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS')
    notes = models.CharField(max_length=512, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    isdatecomputed = models.BooleanField(db_column='isDateComputed')  # Field name made lowercase.
    showinsummaryview = models.BooleanField(db_column='showInSummaryView')  # Field name made lowercase.
    emailleadtimeparam = models.CharField(db_column='emailLeadTimeParam', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    emailfreqparam = models.CharField(db_column='emailFreqParam', max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    nextemaildate = models.DateTimeField(db_column='nextEmailDate', blank=True, null=True)  # Field name made lowercase.
    emailbody = models.TextField(db_column='emailBody', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    immutable = models.BooleanField()
    privname = models.CharField(db_column='privName', max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    pindate = models.BooleanField(db_column='pinDate')  # Field name made lowercase.
    docketentryruleid = models.IntegerField(db_column='docketEntryRuleId', blank=True, null=True)  # Field name made lowercase.
    daycomponentfrombase = models.BooleanField(db_column='dayComponentFromBase')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DocketEntry'

class FvMatter4(models.Model):
    orgid = models.IntegerField(db_column='orgId')  # Field name made lowercase.
    level = models.CharField(max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')
    parenttype = models.CharField(db_column='parentType', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS')  # Field name made lowercase.
    actualtype = models.IntegerField(db_column='actualType')  # Field name made lowercase.
    recordid = models.IntegerField(db_column='recordId')  # Field name made lowercase.
    actual_filing_date = models.DateTimeField(db_column='ACTUAL_FILING_DATE', blank=True, null=True)  # Field name made lowercase.
    adverse_party = models.TextField(db_column='ADVERSE_PARTY', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    adverse_party_2 = models.TextField(db_column='ADVERSE_PARTY_2', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    adverse_party_3 = models.TextField(db_column='ADVERSE_PARTY_3', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    adverse_party_4 = models.TextField(db_column='ADVERSE_PARTY_4', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    annuities = models.TextField(db_column='ANNUITIES', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    billing_id = models.TextField(db_column='BILLING_ID', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    claim_tracker = models.TextField(db_column='CLAIM_TRACKER', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    division = models.TextField(db_column='DIVISION', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    no_of_claims = models.DecimalField(db_column='NO_OF_CLAIMS', max_digits=28, decimal_places=10, blank=True, null=True)  # Field name made lowercase.
    patent_nos = models.TextField(db_column='PATENT_NOS', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    priority_claim_date = models.DateTimeField(db_column='PRIORITY_CLAIM_DATE', blank=True, null=True)  # Field name made lowercase.
    priority_information = models.TextField(db_column='PRIORITY_INFORMATION', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    priority_registration_number = models.TextField(db_column='PRIORITY_REGISTRATION_NUMBER', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    public_nametype = models.TextField(db_column='PUBLIC_NAMETYPE', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ranking = models.DecimalField(db_column='RANKING', max_digits=28, decimal_places=10, blank=True, null=True)  # Field name made lowercase.
    ranking_comment = models.TextField(db_column='RANKING_COMMENT', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    reexamination_type = models.TextField(db_column='REEXAMINATION_TYPE', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    source = models.TextField(db_column='SOURCE', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    source_comment = models.TextField(db_column='SOURCE_COMMENT', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    syncmatter = models.BooleanField(db_column='SYNCMATTER', blank=True, null=True)  # Field name made lowercase.
    tech_group = models.TextField(db_column='TECH_GROUP', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    term_extension = models.DecimalField(db_column='TERM_EXTENSION', max_digits=28, decimal_places=10, blank=True, null=True)  # Field name made lowercase.
    transferredin_date = models.DateTimeField(db_column='TRANSFERREDIN_DATE', blank=True, null=True)  # Field name made lowercase.
    mining = models.BooleanField(db_column='MINING', blank=True, null=True)  # Field name made lowercase.
    generic_category = models.TextField(db_column='GENERIC_CATEGORY', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    summary = models.TextField(db_column='SUMMARY', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    test_high_priority = models.BooleanField(db_column='TEST_HIGH_PRIORITY', blank=True, null=True)  # Field name made lowercase.
    generic_category_2 = models.TextField(db_column='GENERIC_CATEGORY_2', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    generic_category_3 = models.TextField(db_column='GENERIC_CATEGORY_3', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    copyright_creation_date = models.DateTimeField(db_column='COPYRIGHT_CREATION_DATE', blank=True, null=True)  # Field name made lowercase.
    copyright_publication_date = models.DateTimeField(db_column='COPYRIGHT_PUBLICATION_DATE', blank=True, null=True)  # Field name made lowercase.
    copyright_expiry_date = models.DateTimeField(db_column='COPYRIGHT_EXPIRY_DATE', blank=True, null=True)  # Field name made lowercase.
    generic_notes = models.TextField(db_column='GENERIC_NOTES', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    generic_notes_2 = models.TextField(db_column='GENERIC_NOTES_2', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    type_of_work = models.TextField(db_column='TYPE_OF_WORK', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    copyright_description = models.TextField(db_column='COPYRIGHT_DESCRIPTION', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    supplemented_by = models.TextField(db_column='SUPPLEMENTED_BY', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    supplemented_to = models.TextField(db_column='SUPPLEMENTED_TO', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    copyright_claimant = models.TextField(db_column='COPYRIGHT_CLAIMANT', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    copyright_note = models.TextField(db_column='COPYRIGHT_NOTE', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    scrape = models.BooleanField(db_column='SCRAPE', blank=True, null=True)  # Field name made lowercase.
    portfolio = models.TextField(db_column='PORTFOLIO', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    examiner = models.TextField(db_column='EXAMINER', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    generic_category_4 = models.TextField(db_column='GENERIC_CATEGORY_4', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    brexit_clone = models.BooleanField(db_column='BREXIT_CLONE', blank=True, null=True)  # Field name made lowercase.
    link_to_brexit_original_em = models.TextField(db_column='LINK_TO_BREXIT_ORIGINAL_EM', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    publication_figure = models.TextField(db_column='PUBLICATION_FIGURE', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    for_monitoring_purposes_only = models.BooleanField(db_column='FOR_MONITORING_PURPOSES_ONLY', blank=True, null=True)  # Field name made lowercase.
    cited_reference_count = models.DecimalField(db_column='CITED_REFERENCE_COUNT', max_digits=28, decimal_places=10, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FV_MATTER_4'
        
class Trademark(models.Model):
    matterid = models.IntegerField(db_column='matterId')  # Field name made lowercase.
    applicant = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    intenttouse = models.BooleanField(db_column='intentToUse')  # Field name made lowercase.
    appbasedonuse = models.BooleanField(db_column='appBasedOnUse')  # Field name made lowercase.
    specimen = models.BooleanField()
    datefirstuse = models.DateTimeField(db_column='dateFirstUse', blank=True, null=True)  # Field name made lowercase.
    markdescription = models.TextField(db_column='markDescription', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    goodsmarked = models.TextField(db_column='goodsMarked', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    servicesmarked = models.TextField(db_column='servicesMarked', db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    mark = models.CharField(max_length=128, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    serialnumber = models.CharField(db_column='serialNumber', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    contactid = models.IntegerField(db_column='contactId', blank=True, null=True)  # Field name made lowercase.
    registrationdate = models.DateTimeField(db_column='registrationDate', blank=True, null=True)  # Field name made lowercase.
    registrationno = models.CharField(db_column='registrationNo', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pubsupreg = models.BooleanField(db_column='pubSupReg', blank=True, null=True)  # Field name made lowercase.
    pubdate = models.DateTimeField(db_column='pubDate', blank=True, null=True)  # Field name made lowercase.
    alloweddate = models.DateTimeField(db_column='allowedDate', blank=True, null=True)  # Field name made lowercase.
    commercedate = models.DateTimeField(db_column='commerceDate', blank=True, null=True)  # Field name made lowercase.
    artunitno = models.IntegerField(db_column='artUnitNo', blank=True, null=True)  # Field name made lowercase.
    tmtypeid = models.IntegerField(db_column='tmTypeId', blank=True, null=True)  # Field name made lowercase.
    designcode = models.CharField(db_column='designCode', max_length=8, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    signorname = models.CharField(db_column='signorName', max_length=32, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    signortitle = models.CharField(db_column='signorTitle', max_length=64, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    state = models.CharField(max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)
    countriescovered = models.CharField(db_column='countriesCovered', max_length=256, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    expirationdate = models.DateTimeField(db_column='expirationDate', blank=True, null=True)  # Field name made lowercase.
    abandoneddate = models.DateTimeField(db_column='abandonedDate', blank=True, null=True)  # Field name made lowercase.
    tmtype = models.IntegerField(db_column='tmType')  # Field name made lowercase.
    prioritydate = models.DateTimeField(db_column='priorityDate', blank=True, null=True)  # Field name made lowercase.
    prioritycountry = models.CharField(db_column='priorityCountry', max_length=2, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    basisappno = models.CharField(db_column='basisAppNo', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    basiscountry = models.CharField(db_column='basisCountry', max_length=4, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    agmtextensions = models.CharField(db_column='agmtExtensions', max_length=512, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    protextensions = models.CharField(db_column='protExtensions', max_length=512, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    fmtregistrationno = models.CharField(db_column='fmtRegistrationNo', max_length=30, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    priorityno = models.CharField(db_column='priorityNo', max_length=50, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    pubno = models.CharField(db_column='pubNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    filingbasis = models.IntegerField(db_column='filingBasis')  # Field name made lowercase.
    parentdate = models.DateTimeField(db_column='parentDate', blank=True, null=True)  # Field name made lowercase.
    parentregdate = models.DateTimeField(db_column='parentRegDate', blank=True, null=True)  # Field name made lowercase.
    localfilingdate = models.DateTimeField(db_column='localFilingDate', blank=True, null=True)  # Field name made lowercase.
    ibpubno = models.CharField(db_column='ibPubNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    ibpubdate = models.DateTimeField(db_column='ibPubDate', blank=True, null=True)  # Field name made lowercase.
    parentpubno = models.CharField(db_column='parentPubNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.
    parentpubdate = models.DateTimeField(db_column='parentPubDate', blank=True, null=True)  # Field name made lowercase.
    grantofprotectiondate = models.DateTimeField(db_column='grantOfProtectionDate', blank=True, null=True)  # Field name made lowercase.
    unformattedpubno = models.CharField(db_column='unformattedPubNo', max_length=20, db_collation='SQL_Latin1_General_CP1_CI_AS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Trademark'