from datetime import datetime
from ..models import Matter
from ..models import Rvwmatterinventors
from ..models import Rvwmatterpersonnel
from ..models import Matterparticipant
from ..models import Orgprofile, Personprofile
from ..models import Contactinfo, ClientSpec
from ..models import Patent, Customernumbers, CustomerNos, Activity
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import connections
import os

import re

class mergefunctions:
    # For Word docs
    def mergebasic(self, keys, matter):
        merge_fn = mergefunctions()
        tables_list = merge_fn.findTables(keys)
        matter_data = merge_fn.matterFill(matter)
        basicOut = {}

        if 'matter' in tables_list:
            custcor = merge_fn.corrcustnumFill(matter_data)
            confirm = matter_data.confirmationno
            if(confirm == ''):
                confirm = 'Unknown'
            if(custcor == ''):
                custcor = 'Unknown'
                
            try:
                filedte = matter_data.fileddate.strftime("%B %d, %Y")
            except:
                filedte = ''
                
            for i in range(3):
                try:
                    hostmatterno = matter_data.hostmatterno
                    print(hostmatterno)
                    if i == 0:
                        zero = ''
                    if i == 1:
                        zero = '0'
                    if i == 2:
                        zero = '00'
                    client = zero + hostmatterno.split(".")[0] 
                    print(client)
                    clientcode = ClientSpec.objects.using('SideBar').get(clientno=client)
                    print(clientcode)
                    part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34617', roleorderno = 1)
                    print(part.matterno, clientcode.format)
                    matterno = part.matterno
                    matternumber = eval(clientcode.format)
                    break
                except:
                    matternumber = matter_data.hostmatterno

            basic = {
                'serialNo' : merge_fn.transform_serialnumber(matter_data.serialnumber),
                'filedDate' : filedte,
                'title' : matter_data.title,
                'matterNo' : matternumber,
                'custNoCorresp' : custcor,
                'custNoMFee' : custcor,
                'confirmNo' : confirm,
                'examinerName' : merge_fn.examinerFill(matter_data),
                'matterCountryName' : merge_fn.fullCountry(matter_data.country)
            }
            basic.update(merge_fn.mergebasicEmail(keys, matter))
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'patent' in tables_list:
            patent_data = merge_fn.patentFill(matter_data)
            try:
                issdate = (patent_data.issuedate).strftime('%B %d, %Y')
            except:
                issdate = ''
            if patent_data.artunitno != '':
                artunit = patent_data.artunitno
            else:
                artunit = 'Unknown'
            basic = {
                'artUnit' : artunit,
                'patNo' : patent_data.patentno,
                'issueDate' : issdate,
                'countryPatentOffice' : merge_fn.patentCountry(matter_data.country)
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'inventor' in tables_list:
            inventor_data = merge_fn.inventorFill(matter_data)
            inventoretal = merge_fn.inventoretal(inventor_data.inventor)
            
            invs = Rvwmatterinventors.objects.using('FIP').filter(matterid = matter_data.matterid)
            invlist = ''
            for inv in invs:
                invlist += inv.inventor
            
            basic = {
                'inventorEtal' : inventoretal,
                'firstInventor' : inventor_data.inventor,
                'inventorList': invlist,
                'inventorNameList': invlist, 
                'inventorName' : inventor_data.inventor,                                                
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'rvwmatterpersonnel' in tables_list:
            SA_data = merge_fn.rvwmatterpersonnelFill(matter_data)
            try:
                saname = SA_data.fname + ' ' + SA_data.mname + ' ' + SA_data.lname
                saregno = SA_data.registrationno
                nicksa = SA_data.nickname
                saphone = merge_fn.phoneFill(matter_data)
            except:
                saname = ''
                saregno = ''
                nicksa = ''
                saphone = ''
            basic = {
                'SAName' : saname,
                'SARegNo' : saregno,
                'nickSA' : nicksa,
                'SAPhone' : saphone,
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})
                    
        if 'org' in tables_list:
            try:
                part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34617', roleorderno = 1)
                profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
                basic = {
                    'orgName' : profile.orgname,
                    'This.orgName' : profile.orgname,
                }
            except:
                basic = {
                    'orgName' : '',
                    'This.orgName' : ''
                }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'para' in tables_list:
            basic = {}
            basic.update(merge_fn.parafill(keys, matter))
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})
        
        if 'WA' in tables_list:
            basic = {}
            basic.update(merge_fn.WAfill(keys, matter))
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'fa' in tables_list:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '56690', roleorderno = 1)
            profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.contactinfoid)
            try:
                personprofile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
                farecipient = personprofile.lname
            except:
                farecipient = ''
            if 'GB' in contact.country:
                country = 'United Kingdom'
            if contact.country == 'US':
                country = 'United States'

            addr = contact.address1 + '\n' + contact.address2 + '\n' + contact.city + ', ' + contact.zip + '\n' + country
            basic = {
                'faOrgName' : profile.orgname,
                'faWorkAddr' : addr,
                'faCSZ' : '',
                'faAssignee' : profile.orgname,
                'associateName' : profile.orgname,
                'recipientEmail' : contact.email,
                'faclientRefNo' : part.matterno,
                'faRecipient' : farecipient
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'current' in tables_list:
            basicOut.update({'currentDate': datetime.now().strftime("%B %d, %Y")})

        if 'matterparticipant' in tables_list:
            try:
                part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34617', roleorderno = 1)
                profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
                basic = {
                    'clientRefNo' : 'Ref. No. ' + part.matterno,
                    'clientNo' : part.matterno,
                    'This.clientRefNo' : 'Ref. No. ' + part.matterno,
                    'clientRefText' : 'Client Ref. No. ' + part.matterno,
                    'RefNo' : part.matterno,
                    'clientName' : profile.orgname
                }
            except:
                basic = {
                    'clientRefNo' : 'Ref. No. ',
                    'clientNo' : '',
                    'This.clientRefNo' : 'Ref. No. ',
                    'clientRefText' : 'Client Ref. No. ',
                    'RefNo' : '',
                    'clientName' : ''
                }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'firm' in tables_list:
            basic = {}
            basic.update(merge_fn.firmfill())
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})
                    
        if 'QA' in tables_list:
            basic = {}
            basic.update(merge_fn.QAfill(keys, matter))
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        return basicOut

    # assignee information fill 34606   
    def assigneefill(self, matter, count):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34606', roleorderno = count)
            profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.contactinfoid)

            assigne = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34606')
            assigneelen = len(assigne)

            if assigneelen == 1:
                count = 'Assignee: '

            info = {
                'assigneeCnt' : count,
                'assigneeName' : profile.orgname,
                'assigneeStreet' : contact.address1,
                'assigneeCity' : contact.city,
                'assigneeState' : contact.state,
                'assigneeZip' : contact.zip,
                'assigneeCountry' : contact.country,
                'assigneeStreet1' : contact.address1,
                'assigneeStreet2' : contact.address2,
                'assignee' : profile.orgname,
                'assigneeAddress' : str(contact.address1) + ', ' + str(contact.city) + ', ' + str(contact.state) + ', ' + str(contact.zip),
                'assigneeStateInc' : str(profile.incstate) + ', ' + merge_fn.fullCountry(str(profile.inccountry))
            }
        except:
            info = {
                'assigneeCnt' : '',
                'assigneeName' : '',
                'assigneeStreet' : '',
                'assigneeCity' : '',
                'assigneeState' : '',
                'assigneeZip' : '',
                'assigneeCountry' : '',
                'assigneeStreet1' : '',
                'assigneeStreet2' : '',
                'assignee' : '',
                'assigneeAddress' : '',
                'assigneeStateInc' : ''
            }
        return info
    
    # Applicant information fill. Update roleid  56691
    def applicantfill(self, matter, count):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '56691', roleorderno = count)
            profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.contactinfoid)

            applicant = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '56691')
            applicantlen = len(applicant)

            if applicantlen == 1:
                count = 'Applicant: '

            info = {
                'applCnt' : count,
                'applicantCity' : contact.city,
                'applicantState' : contact.state,
                'applicantZip' : contact.zip,
                'applicantCountry' : contact.country,
                'applicantStreet1' : contact.address1,
                'applicantStreet2' : contact.address2,
                'applicant' : profile.orgname,
                'applicantName' : profile.orgname,
            }
        except:
            info = {
                'applCnt' : '',
                'applicantCity' : '',
                'applicantState' : '',
                'applicantZip' : '',
                'applicantCountry' : '',
                'applicantStreet1' : '',
                'applicantStreet2' : '',
                'applicant' : '',
                'applicantName' : '',
            }
        return info
    
    def correspondenceContactfill(self, matter):
        try:
            merge_fn = mergefunctions()
            matter_data = merge_fn.matterFill(matter)
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34610', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            correspondenceContact = profile.fname + ' ' + profile.mname + ' ' + profile.lname
        except:
            correspondenceContact = ''

        info = {
            'correspondenceContact' : correspondenceContact
        }
        return info
    
    def copyContactfill(self, matter):
        try:
            merge_fn = mergefunctions()
            matter_data = merge_fn.matterFill(matter)
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34611', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            copyContact = profile.fname + ' ' + profile.mname + ' ' + profile.lname
        except:
            copyContact = ''

        info = {
            'copyContact' : copyContact
        }
        return info

    def ffcmgFill(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)

        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '79091', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            fcmg = profile.fname + ' ' + profile.mname + ' ' + profile.lname
        except:
            fcmg = 'NO FF CMG PERSONNEL'

        info = {
            'ffcmgName' : fcmg,
        }
        return info   

    def recordationRoleFill(self, matter, role):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        if role != '':
            roledata = role.split('/')
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = roledata[0], roleorderno = int(roledata[1].replace(" ", "")))
            profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.contactinfoid)

            info = {
                'assigneeCity' : contact.city,
                'assigneeState' : contact.state,
                'assigneeZip' : contact.zip,
                'assigneeCountry' : contact.country,
                'assigneeStreet' : contact.address1,
                'assigneeName' : profile.orgname,
                'assignee' : profile.orgname,
            }
            
        else:
            info = {
                'assigneeCity' : '',
                'assigneeState' : '',
                'assigneeZip' : '',
                'assigneeCountry' : '',
                'assigneeStreet' : '',
                'assigneeName' : '',
                'assignee' : '',
            }
            
        return info

    # Para fill
    def parafill(self, keys, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34609', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
            info = {
                'paraName' : profile.fname + ' ' + profile.lname,
                'paraPhone' : contact.phone1,
                'paraEmail' : contact.email,
                'This.paraName' : profile.fname + ' ' + profile.lname,
                'This.paraPhone' : contact.phone1,
                'This.paraEmail' : contact.email,
                'clientparaname' : profile.fname + ' ' + profile.lname,
                'clientparaemail' : contact.email
            }
        except:
            info = {
                'paraName' : 'NO PARALEGAL',
                'paraPhone' : 'NO PARALEGAL PHONE ',
                'paraEmail' : 'NO PARALEGAL EMAIL',
                'This.paraName' : 'NO PARALEGAL',
                'This.paraPhone' : 'NO PARALEGAL PHONE',
                'This.paraEmail' : 'NO PARALEGAL EMAIL',
                'clientparaname' : '',
                'clientparaemail' : ''
            }
        return info
    
    # Para fill
    def clientParafill(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '164406', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
            info = {
                'clientparaname' : profile.fname + ' ' + profile.lname,
                'clientparaemail' : contact.email
            }
        except:
            info = {
                'clientparaname' : '',
                'clientparaemail' : ''
            }
        return info
    
    # WA fill
    def WAfill(self, keys, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34615', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
            info = {
                'WAName' : profile.fname + ' ' + profile.lname,
                'WAattorney' : profile.fname + ' ' + profile.lname,
                'WAPhone' : contact.phone1,
                'WAEmail' : contact.email,
                'This.WAName' : profile.fname + ' ' + profile.lname,
                'This.WAPhone' : contact.phone1,
                'This.WAEmail' : contact.email,
                'WARegNo' : profile.registrationno
            }
        except:
            info = {
                'WAName' : 'NO WORKING ATTORNEY',
                'WAPhone' : 'NO WORKING ATTORNEY PHONE',
                'WAEmail' : 'NO WORKING ATTORNEY EMAIL',
                'This.WAName' : 'NO WORKING ATTORNEY',
                'This.WAPhone' : 'NO WORKING ATTORNEY PHONE',
                'This.WAEmail' : 'NO WORKING ATTORNEY EMAIL',
                'WARegNo' : ''
            }
        return info
    
    # QA fill
    def QAfill(self, keys, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '81432', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
            info = {
                'QAName' : profile.fname + ' ' + profile.lname,
                'QAPhone' : contact.phone1,
            }
        except:
            info = {
                'QAName' : '',
                'QAPhone' : '',
            }
        return info
    
    def fullCountry(self, country):
        if 'US' in country:
            return 'United States of America'
        elif 'JP' in country:
            return 'Japan'
        elif 'DE' in country:
            return 'Germany'
        elif 'KR' in country:
            return 'Korea'
        else:
            return country
        
    def patentCountry(self, country):
        if 'EP' in country:
            return 'European Patent Office'
        elif 'US' in country:
            return 'United States Patent Office'
        elif 'KR' in country:
            return 'Korean Patent Office'
        elif 'AU' in country:
            return 'Australian Patent Office'
        else:
            return country

    
    def split_name(self, full_name):
        full_name = full_name.strip()
        parts = full_name.split(' ')
        
        first_name = parts[0]
        last_name = parts[-1]
        middle_name = ""

        if len(parts) > 2:
            middle_name = " ".join(parts[1:-1])
        
        return first_name, middle_name, last_name
    
    def extract_date(text):
        date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'

        match = re.search(date_pattern, text)
        
        if match:
            return match.group()
        else:
            return None
    
    def inventorInfoName(self, matter, name):
        merge_fn = mergefunctions()
        first, middle, last = merge_fn.split_name(name)
        matter_data = merge_fn.matterFill(matter)
        parts = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34608')
        for part in parts:
            try:
                profile = Personprofile.objects.using('FIP').get(ppid = part.contactid, fname = first, lname = last)
            except:
                pass
        contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.homecontactinfoid)
        if contact.address1 != '':
            homeaddr = contact.address1 + '\n' + contact.city + ', ' + contact.state + ' ' + contact.zip
        elif contact.city != '':
            homeaddr = contact.city + ', ' + contact.state + ' ' + contact.zip
        else:
            homeaddr = contact.state + ' ' + contact.zip

        info = {
            'inventorName' : profile.lname.upper() + ', ' + profile.fname + ' ' + profile.mname,
            'inventorHomeAddress' : homeaddr,
            'inventorHomeCountry' : merge_fn.fullCountry(contact.country),
        }
        return info
    
    def inventorInfoBSC(self, matter, inv):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34608', roleorderno = inv)
        profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)

        inventors = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34608')
        invCount = len(inventors)
        
        inv2 = ''
        if invCount >= (inv + 1):
            part2 = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34608', roleorderno = inv + 1)
            profile2 = Personprofile.objects.using('FIP').get(ppid = part2.contactid)
            inv2 = profile2.fname + ' ' + profile2.mname + '. ' + profile2.lname

        info = {
            'Inventor1' : profile.fname + ' ' + profile.mname + '. ' + profile.lname,
            'Inventor2' : inv2,
        }
        return info
        
    
    def inventorInfo(self, matter, inv):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34608', roleorderno = inv)
        profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
        workcontact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
        contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.homecontactinfoid)

        inventors = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34608')
        invCount = len(inventors)

        if invCount == 1:
            inv = 'Inventor: '

        info = {
            'inventorCnt' : inv,
            'inventor' : profile.fname + ' ' + profile.mname + '. ' + profile.lname,
            'invpre' : profile.salutation,
            'inventorFirstName' : profile.fname,
            'inventorMiddleInitial' : profile.mname,
            'inventorLastName' : profile.lname,
            'inventorSuffix' : profile.namesuffix,
            'inventorHomeCity' : contact.city,
            'inventorHomeState' : contact.state,
            'inventorHomeCountry' : contact.country,
            'inventorHomeStreet1' : contact.address1,
            'inventorcitizen': profile.citizenship,
            'inventorHomeZip' : contact.zip,
            'inventorCitizenship' : profile.citizenship,
            'inventorMailingStreet1' : contact.address1,
            'inventorMailingStreet2' : contact.address2,
            'inventorMailingCity' : contact.city,
            'inventorMailingState' : contact.state,
            'inventorMailingZip' : contact.zip,
            'inventorMailingCountry' : contact.country,

            'inventorName' : profile.fname + ' ' + profile.mname + ' ' + profile.lname,
            'inventorCityState' : contact.city + ' ' + contact.state,
            'inventorCountry' : contact.country,
            'inventorAddress' : contact.address1,
            'inventorAddress1' : contact.address1,
            'inventorAddress2' : contact.address2,
            'inventorCSZ' : '',
            'Inventor2PCTdeclaration' : '',
            
            'inventorWorkEmail' : profile.sendemailtowork,
            'inventorResidence' : contact.city + contact.state + ',' + contact.country,
        }
        return info
    
    def foreignfill(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        patent_data = merge_fn.patentFill(matter_data)

        if patent_data.prioritycountry != 'US':
            foreignNo = patent_data.priorityappno
            foreigncountry = patent_data.prioritycountry
            foreigndate = patent_data.priorityappdate

        info = {
            'foreignNo' : foreignNo,
            'foreignCntry' : foreigncountry,
            'foreignFiledDate' : foreigndate,
        }
        return info

    def entityfill(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        patent_data = merge_fn.patentFill(matter_data)

        return patent_data.entitystatus
    
    def firmfill(self):
        # Might need to pull from DB
        firm = Rvwmatterpersonnel.objects.using('FIP').filter(orgid = 4)
        info = {
            'firmName' : firm[0].orgname,
            'This.upperFirmName' : firm[0].orgname,
            'firmPoBox' : 'P.O. Box 2938',
            'firmCityStZip' : 'Minneapolis, Minnesota  55402',
        }
        return info
    
    # For emails
    def mergebasicEmail(self, keys, matter):
        merge_fn = mergefunctions()
        tables_list = merge_fn.findTables(keys)
        matter_data = merge_fn.matterFill(matter)
        basicOut = {}

        if 'matter' in tables_list:
            custcor = merge_fn.corrcustnumFill(matter_data)
            confirm = matter_data.confirmationno
            if(confirm == ''):
                confirm = 'Unknown'
            if(custcor == ''):
                custcor = 'Unknown'
                
            try:
                filedte = matter_data.fileddate.strftime("%B %d, %Y")
            except:
                filedte = ''
            basic = {
                'This.serialNo' : merge_fn.transform_serialnumber(matter_data.serialnumber),
                'This.filedDate' : filedte,
                'This.title' : matter_data.title,
                'This.matterNo' : matter_data.hostmatterno,
                'recipient' : Rvwmatterinventors.objects.using('FIP').get(matterid = matter_data.matterid).inventor
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})
                    
        return basicOut

    def findTables(self, keys):
        table = {
            'serialNo' : 'matter',
            'matterCountryName' : 'matter',
            'inventorEtal' : 'inventor',
            'inventorList': 'inventor',
            'inventorNameList': 'inventor', 
            'inventorName': 'inventor', 
            'filedDate' : 'matter',
            'custNoCorresp' : 'matter',
            'title' : 'matter',
            'examinerName' : 'personnel',
            'artUnit' : 'patent',
            'patNo' : 'patent',
            'issueDate' : 'patent',
            'countryPatentOffice' : 'patent',
            'matterNo' : 'matter',
            'confirmNo' : 'matter',
            'SAName' : 'rvwmatterpersonnel',
            'SARegNo' : 'rvwmatterpersonnel',
            'SAPhone' : 'rvwmatterpersonnel',
            'nickSA' : 'rvwmatterpersonnel',
            'orgName' : 'org',
            'This.orgName' : 'org',
            'recipient' : 'rvwmatterinventors',
            'WAName' : 'WA',
            'WAattorney' : 'WA',
            'WAPhone' : 'WA',
            'WAEmail' : 'WA',
            'This.WAName' : 'WA',
            'This.WAPhone' : 'WA',
            'This.WAEmail' : 'WA',
            'WARegNo' : 'WA',
            'paraName' : 'para',
            'paraPhone' : 'para',
            'paraEmail' : 'para',
            'This.paraName' : 'para',
            'This.paraPhone' : 'para',
            'This.paraEmail' : 'para',
            'QAName' : 'QA',
            'QAPhone' : 'QA',
            'This.serialNo' : 'matter',
            'This.filedDate' : 'matter',
            'This.title' : 'matter',
            'This.matterNo' : 'matter',
            'recipient' : 'matter',
            'faOrgName' : 'fa',
            'faWorkAddr' : 'fa',
            'faCSZ' : 'fa',
            'faAssignee' : 'fa',
            'ffparaEmail' : '',
            'currentDate' :'current',
            'clientRefNo' : 'matterparticipant',
            'clientNo' : 'matterparticipant',
            'clientRefText' : 'matterparticipant',
            'This.clientRefNo' : 'matterparticipant',
            'clientName' : 'matterparticipant',
            'RefNo' : 'matterparticipant',
            'firstInventor' : 'inventor',
            'firmName' : 'firm',
            'firmPoBox' : 'firm',
            'firmCityStZip' : 'firm',
        }
        unique_values = set()
        # Iterate over the keys
        for key in keys:
            if key in table:
                unique_values.add(table[key])
        tables_list = list(unique_values)

        return tables_list
    
    def transform_serialnumber(self, s):
        part1 = s[:2]
        part2 = s[2:]
        part2 = part2[:-3] + ',' + part2[-3:]

        result = part1 + '/' + part2
        return result
    
    def esigncheck(self, esign):
        esign_out = ""
        esigndate_out = ""
        if(esign == 'true' or esign == True or esign == 'TRUE'):
            esign_out = "/ {{Sig_es_:signer1:signature}} /"
            esigndate_out = "{{Dte_es_:signer1:date}}"
            
        esignout = {
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'signatureName' : esign_out,
            'inventorSignature' : esign_out,
            'clientSignature' : esign_out
        }

        return esignout
    
    def inventoretal(self, inventor):
        firstinventor = inventor.split(", ")
        numstring = len([i for i in firstinventor if isinstance(i, str)])
        if(numstring > 1):
            firstinventor = firstinventor[0] + " et al."
        else:
            firstinventor = firstinventor[0]

        return firstinventor
        
    def appendphone(self, number):
        cleaned_number = ''.join(filter(str.isdigit, number))
        formatted_number = f"({cleaned_number[:3]}){cleaned_number[3:6]}-{cleaned_number[6:]}"
    
        return formatted_number
    
    def matterFill(self, matter):
        return Matter.objects.using('FIP').get(hostmatterno = matter)
    
    def inventorFill(self, data):
        return Rvwmatterinventors.objects.using('FIP').filter(matterid = data.matterid)[0]

    def patentFill(self, data):
        return Patent.objects.using('FIP').get(matterid = data.matterid)
    
    def examinerFill(self, data):
        try:
            examiner_data = Rvwmatterpersonnel.objects.using('FIP').get(matterid = data.matterid, rolename = "Examiner")
            examiner = examiner_data.personname   
        except:
            examiner = 'Unknown'

        return examiner

    def rvwmatterpersonnelFill(self, data):
        try:
            return Rvwmatterpersonnel.objects.using('FIP').get(matterid = data.matterid, roleid = "34619", roleorderno = 1)
        except:
            return ''
    
    # cust correspondence no
    def corrcustnumFill(self, data):
        '''
        part = Matterparticipant.objects.using('FIP').get(matterid = data.matterid, roleid = '34617')
        # profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
        try:
            cust = Customernumbers.objects.using('FIP').get(opid = part.opid).correspondencecustno
        except:
            parts = Matterparticipant.objects.using('FIP').filter(matterid = data.matterid)
            for part in parts:
                try:
                    cust = Customernumbers.objects.using('FIP').get(opid = part.contactid).correspondencecustno
                    break
                except:
                    cust = 21186
                    pass
        '''
        matter = data.hostmatterno
        matter = matter.split(".")
        try:
            cust = CustomerNos.objects.using('SideBar').get(clientno = matter[0]).correspno
        except:
            cust = 21186

        return cust
    
    def contactinfoFill(self, data):
        return Contactinfo.objects.using('FIP').get(contactinfoid = data.contactinfoid)
    
    def phoneFill(self,data):
        function_instance = mergefunctions()
        results = []
        try:
            if data != '':
                query = f"""
                    SELECT ci.phone1 as phone
                    FROM matterparticipant mp 
                        JOIN personprofile op ON mp.contactid = op.ppid
                        JOIN contactinfo ci on op.workcontactinfoid = ci.contactinfoid
                    WHERE matterid IN 
                    (SELECT matterid from matter where hostmatterno LIKE '{data.hostmatterno}')
                    and roleid = '34619'
                """
                
                with connections['FIP'].cursor() as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                phone = str(results[0]).replace('(', '').replace(')', '').replace("'", '').replace(',', '')
                phonenum = function_instance.appendphone(phone)
        except:
            phonenum = '()-'
                    
        return phonenum
    
    def depnumFill(self, data):
        part = Matterparticipant.objects.using('FIP').get(matterid = data.matterid, roleid = '34617')
        profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
        depnum = profile.ptodepositacct
        if(depnum == ''):
            part = Matterparticipant.objects.using('FIP').get(matterid = data.matterid, roleid = '34616')
            profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
            depnum = profile.ptodepositacct
        return depnum
    
    def orginfoFill(self, data):
        part = Matterparticipant.objects.using('FIP').get(matterid = data.matterid, roleid = '34617')
        profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
        return profile
    
    def getactivityid(self, matter, type):
        activity = Activity.objects.using('FIP').filter(matterid = matter.matterid, code = type)
        return activity[0]
    
    def extract_date(self, text):
        # Regular expression pattern to match dates in MM/DD/YYYY format
        date_pattern = r'\b\d{2}/\d{2}/\d{4}\b'
        match = re.search(date_pattern, text)
        if match:
            return match.group()
        return None
    
    def number_to_words(self, n):
        if not (0 <= n <= 24):
            return "NUMBER OUT OF RANGE"

        units = ["ZERO", "ONE", "TWO", "THREE", "FOUR", "FIVE", "SIX", "SEVEN", "EIGHT", "NINE"]
        teens = ["TEN", "ELEVEN", "TWELVE", "THIRTEEN", "FOURTEEN", "FIFTEEN", "SIXTEEN", "SEVENTEEN", "EIGHTEEN", "NINETEEN"]
        tens = ["", "", "TWENTY"]

        if 0 <= n < 10:
            return units[n]
        elif 10 <= n < 20:
            return teens[n - 10]
        elif 20 <= n <= 24:
            if n % 10 == 0:
                return tens[n // 10]
            else:
                return tens[n // 10] + "-" + units[n % 10]
            
    def pgCount(self, n):
        if n == 1:
            return 'pg'
        else:
            return 'pgs'

    def newDate(self, n, date):
        date_obj = datetime.strptime(date, '%m/%d/%Y')
        
        if n == 'One-Month':
            new_date = date_obj + relativedelta(months=1)
        elif n == 'Two-Month':
            new_date = date_obj + relativedelta(months=2)
        elif n == 'Three-Month':
            new_date = date_obj + relativedelta(months=3)
        elif n == 'Four-Month':
            new_date = date_obj + relativedelta(months=4)
        elif n == 'Five-Month':
            new_date = date_obj + relativedelta(months=5)
        else:
            return "Invalid input"
        
        return new_date.strftime('%B %d, %Y')
    
    def cmgfill(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34614', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
            info = {
                'cmgName' : profile.fname + ' ' + profile.mname + ' ' + profile.lname,
                'cmgEmail' : contact.email,
                'cmgPhone' : contact.phone1
            }
        except:
            info = {
                'cmgName' : 'NO CMG PERSONNEL',
                'cmgEmail' : '',
                'cmgPhone' : ''
            }
        return info
    
    def counselfill(self, matter):
        merge_fn = mergefunctions()
        try:
            matter_data = merge_fn.matterFill(matter)
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '35905', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
            name = profile.fname + ' ' + profile.lname
            email = contact.email
        except:
            name = ''
            email = ''
        info = {
            'ClientCorporateCounselname' : name,
            'ClientCorporateCounselemail' : email,
        }
        return info
    
    def linkedinRAfill(self, matter):
        merge_fn = mergefunctions()
        try:
            matter_data = merge_fn.matterFill(matter)
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '195797', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
            name = profile.fname + ' ' + profile.lname
            email = contact.email
        except:
            name = ''
            email = ''
        info = {
            'LIResponsibleAttorneyname' : name,
            'LIResponsibleAttorneyemail' : email,
        }
        return info
    
    def formatDate(self, date):
        try:
            return datetime.strptime(date, '%Y-%m-%d').strftime('%B %d, %Y')
        except:
            return date

    def formatDate2(self, date):
        try:
            return datetime.strptime(date, '%m/%d/%Y').strftime('%B %d, %Y')
        except:
            return date
    
    def ffparafill(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '58125', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
            info = {
                'ffparaName' : profile.fname + ' ' + profile.mname + ' ' + profile.lname,
                'ffparaEmail' : contact.email,
                'ffparaPhone' : contact.phone1
            }
        except:
            info = {
                'ffparaName' : '',
                'ffparaEmail' : '',
                'ffparaPhone' : ''
            }
        return info
    
    def countryType(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)

        if matter_data.countryname == 'United States of America':
            countrytype = 'American'
        
        info = {
            'countryType' : countrytype
        }
        return info
    
    def find_case_insensitive_path(self, path):
        parts = path.strip(os.sep).split(os.sep)
        current_path = os.sep if path.startswith(os.sep) else "."

        for part in parts:
            try:
                entries = os.listdir(current_path)
            except FileNotFoundError:
                return None

            match = next((entry for entry in entries if entry.lower() == part.lower()), None)
            if match is None:
                return None

            current_path = os.path.join(current_path, match)

        return current_path if os.path.exists(current_path) else None

    # Retainer Language
    def retainer(self, matter):
        pass