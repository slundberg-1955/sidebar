from datetime import datetime
from ..models import Matter
from ..models import Rvwmatterinventors
from ..models import Rvwmatterpersonnel
from ..models import Matterparticipant
from ..models import Orgprofile, Personprofile
from ..models import Contactinfo, ClientSpec
from ..models import Patent, Customernumbers, CustomerNos, Activity, MergeFees, CustNos, FvMatter4, CountryLookup, Relatedmatter
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db import connections
import os
from django.db.models import Q

import re

class mergefunctions:
    # For Word docs
    def mergebasic(self, keys, matter):
        merge_fn = mergefunctions()
        tables_list = merge_fn.findTables(keys)
        matter_data = merge_fn.matterFill(matter)
        basicOut = {}

        if 'matter' in tables_list:
            custcor = merge_fn.corrcustnumFill(matter_data, 'corresp')
            confirm = matter_data.confirmationno
            if(confirm == ''):
                confirm = 'Unknown'
            if(custcor == ''):
                custcor = 'Unknown'
                
            mfee = merge_fn.corrcustnumFill(matter_data, 'maint')
            if(mfee == ''):
                mfee = 'Unknown'
                
            try:
                filedte = matter_data.fileddate.strftime("%B %d, %Y")
            except:
                filedte = ''
                
            matternumber = merge_fn.clientMatterNo(matter_data)

            serialno = matter_data.fmtserialno
            if serialno is None or (isinstance(serialno, str) and not serialno.strip()):
                serialno = 'Unknown'

            basic = {
                'serialNo' : serialno,
                'filedDate' : filedte,
                'title' : matter_data.title,
                'matterNo' : matternumber,
                'custNoCorresp' : custcor,
                'custNoMFee' : mfee,
                'confirmNo' : confirm,
                'examinerName' : merge_fn.examinerFill(matter_data),
                'matterCountryName' : matter_data.countryname
            }
            basic.update(merge_fn.mergebasicEmail(keys, matter))
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'patent' in tables_list:
            try:
                patent_data = merge_fn.patentFill(matter_data)
                try:
                    issdate = (patent_data.issuedate).strftime('%B %d, %Y')
                except:
                    issdate = ''
                if patent_data.artunitno != '':
                    artunit = patent_data.artunitno
                else:
                    artunit = 'Unknown'

                patno = merge_fn.transform_patnumber(patent_data.patentno)

                basic = {
                    'artUnit' : artunit,
                    'patNo' : patno,
                    'issueDate' : issdate,
                    'countryPatentOffice' : merge_fn.patentCountry(matter_data.country)
                }
            except:
                basic = {
                    'artUnit' : '',
                    'patNo' : '',
                    'issueDate' : '',
                    'countryPatentOffice' : ''
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
                'firstInventor' : inventoretal.replace(' et al.', ''),
                'inventorList': invlist,
                'inventorNameList': invlist, 
                'inventorName' : inventoretal.replace(' et al.', ''),                                                
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
            try:
                part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '56690', roleorderno = 1)
                profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
                contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.contactinfoid)
                try:
                    #personprofile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
                    farecipient = profile.contactname
                except:
                    farecipient = ''

                country = matter_data.countryname
                if country == 'European Patent Office':
                    country = 'United Kingdom'

                addr = contact.address1 + '\n'
                if contact.address2 != '':
                    addr = addr + contact.address2 + '\n'
                if contact.address3 != '':
                    addr = addr + contact.address3 + '\n'
                
                addr = addr + contact.city + ', ' + contact.state + ' ' + contact.zip + '\n' + country

                basic = {
                    'faOrgName' : profile.orgname,
                    'faWorkAddr' : addr,
                    'faCSZ' : '',
                    'associateName' : profile.orgname,
                    'recipientEmail' : contact.email,
                    'recipientPhone' : contact.phone1,
                    'recipientFax' : contact.fax,
                    'faclientRefNo' : part.matterno,
                    'faRecipient' : farecipient
                }
            except:
                basic = {
                    'faOrgName' : '',
                    'faWorkAddr' : '',
                    'faCSZ' : '',
                    'associateName' : '',
                    'recipientEmail' : '',
                    'faclientRefNo' : '',
                    'faRecipient' : ''
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
    def assigneefill(self, matter, count, matter_data=None):
        merge_fn = mergefunctions()
        if matter_data is None:
            matter_data = merge_fn.matterFill(matter)
        try:
            parts = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34606', roleorderno = count)
            part = parts[0]
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
                'assigneeCountry' : merge_fn.full_country(contact.country),
                'assigneeStreet1' : contact.address1,
                'assigneeStreet2' : contact.address2,
                'assignee' : profile.orgname,
                'assigneeAddress' : str(contact.address1) + ', ' + str(contact.city) + ', ' + str(contact.state) + ', ' + str(contact.zip),
                'assigneeStateInc' : str(profile.incstate) + ', ' + merge_fn.fullCountry(str(profile.inccountry)),
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
                'assigneeStateInc' : '',
            }
            
        return info
    
    # Applicant information fill. Update roleid  56691
    def applicantfill(self, matter, count, matter_data=None):
        merge_fn = mergefunctions()
        if matter_data is None:
            matter_data = merge_fn.matterFill(matter)
        
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '56691', roleorderno = count)
            profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.contactinfoid)

            applicant = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '56691')
            applicantlen = len(applicant)

            appstreet = contact.address1
            if contact.address2 != '':
                appstreet = appstreet + '/n' + contact.address2

            if applicantlen == 1:
                count = 'Applicant: '

            info = {
                'applCnt' : count,
                'applicantCity' : contact.city,
                'applicantState' : contact.state,
                'applicantZip' : contact.zip,
                'applicantCountry' : merge_fn.full_country(contact.country),
                'applicantStreet1' : contact.address1,
                'applicantStreet2' : contact.address2,
                'applicantStreet' : appstreet,
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
    
    def applicantCount(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        
        try:
            applicant = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '56691')
            applicantlen = len(applicant)
            
        except:
            applicantlen = 0
        
        return applicantlen
    
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

    def getNameFromEmail(self, email):
        """
        Look up a contact's name from their email address.
        Returns person's full name or organization name, or empty string if not found.
        """
        if not email or not email.strip():
            return ''
        
        email = email.strip()
        try:
            # Try to find Contactinfo by email
            contact = Contactinfo.objects.using('FIP').filter(email=email).first()
            if contact:
                # Try to find Personprofile by workcontactinfoid
                try:
                    person = Personprofile.objects.using('FIP').filter(workcontactinfoid=contact.contactinfoid).first()
                    if person:
                        return (person.fname + ' ' + person.lname).strip()
                except:
                    pass
                
                # Try to find Personprofile by homecontactinfoid
                try:
                    person = Personprofile.objects.using('FIP').filter(homecontactinfoid=contact.contactinfoid).first()
                    if person:
                        return (person.fname + ' ' + person.lname).strip()
                except:
                    pass
                
                # Try to find Personprofile by mailcontactinfoid
                try:
                    person = Personprofile.objects.using('FIP').filter(mailcontactinfoid=contact.contactinfoid).first()
                    if person:
                        return (person.fname + ' ' + person.lname).strip()
                except:
                    pass
                
                # Try to find Orgprofile by contactinfoid
                try:
                    org = Orgprofile.objects.using('FIP').filter(contactinfoid=contact.contactinfoid).first()
                    if org and org.orgname:
                        return org.orgname.strip()
                except:
                    pass
        except:
            pass
        
        return ''
    
    def workAddressFill(self, matter, roleid='34610'):
        """
        Get work address for a contact based on roleid.
        Default roleid is 34610 (correspondence contact).
        Returns formatted multi-line address string.
        """
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        work_addr = ''
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid=matter_data.matterid, roleid=roleid, roleorderno=1)
            profile = Personprofile.objects.using('FIP').get(ppid=part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid=profile.workcontactinfoid)
            
            addr_parts = []
            if contact.address1:
                addr_parts.append(contact.address1)
            if contact.address2:
                addr_parts.append(contact.address2)
            if contact.address3:
                addr_parts.append(contact.address3)
            
            city_state_zip = ''
            if contact.city:
                city_state_zip = contact.city
            if contact.state:
                city_state_zip = city_state_zip + ', ' + contact.state if city_state_zip else contact.state
            if contact.zip:
                city_state_zip = city_state_zip + ' ' + contact.zip if city_state_zip else contact.zip
            if city_state_zip:
                addr_parts.append(city_state_zip)
            
            work_addr = '\n'.join(addr_parts) if addr_parts else ''
        except:
            work_addr = ''
        
        return work_addr

    def foreignAssociateFill(self, matter):
        """
        Get foreign associate data for recipient, recipientTitle, orgName, and workAddr.
        Returns a dictionary with these fields filled from FA data.
        """
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        
        result = {
            'recipient': '',
            'recipientTitle': '',
            'orgName': '',
            'workAddr': ''
        }
        
        try:
            # Get foreign associate participant (roleid = '56690')
            part = Matterparticipant.objects.using('FIP').get(matterid=matter_data.matterid, roleid='56690', roleorderno=1)
            profile = Orgprofile.objects.using('FIP').get(opid=part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid=profile.contactinfoid)
            
            # Set orgName
            result['orgName'] = profile.orgname if profile.orgname else ''
            
            try:
                personprofile = Personprofile.objects.using('FIP').get(ppid=part.contactid)
                result['recipientTitle'] = personprofile.title.strip()
            except:
            #     # If no person profile, use org name as recipient
                result['recipientTitle'] = ''

            try:
                result['recipient'] = profile.contactname
            except:
                result['recipient'] = ''
            
            # Build work address
            country = matter_data.countryname
            if country == 'European Patent Office':
                country = 'United Kingdom'
            
            addr_parts = []
            if contact.address1:
                addr_parts.append(contact.address1)
            if contact.address2:
                addr_parts.append(contact.address2)
            if contact.address3:
                addr_parts.append(contact.address3)
            
            city_state_zip = ''
            if contact.city:
                city_state_zip = contact.city
            if contact.state:
                city_state_zip = city_state_zip + ', ' + contact.state if city_state_zip else contact.state
            if contact.zip:
                city_state_zip = city_state_zip + ' ' + contact.zip if city_state_zip else contact.zip
            if city_state_zip:
                addr_parts.append(city_state_zip)
            if country:
                addr_parts.append(country)
            
            result['workAddr'] = '\n'.join(addr_parts)
            
        except Exception as e:
            # If any error occurs, return empty values
            pass
        
        return result

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
            
            street = contact.address1
            if (contact.address2):
                street = street + '\n' + contact.address2
            if (contact.address3):
                street = street + '\n' + contact.address3

            info = {
                'assigneeCity' : contact.city,
                'assigneeState' : contact.state,
                'assigneeZip' : contact.zip,
                'assigneeCountry' : contact.country,
                'assigneeStreet' : street,
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
            paraname = profile.fname + ' ' + profile.mname + ' ' + profile.lname
            if profile.mname == '':
                paraname = profile.fname + ' ' + profile.lname
            info = {
                'paraName' : paraname,
                'paraPhone' : merge_fn.appendphone(contact.phone1),
                'paraEmail' : contact.email,
                'This.paraName' : paraname,
                'This.paraPhone' : merge_fn.appendphone(contact.phone1),
                'This.paraEmail' : contact.email,
                'clientparaname' : paraname,
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
            waname = profile.fname + ' ' + profile.mname + ' ' + profile.lname
            if profile.mname == '':
                waname = profile.fname + ' ' + profile.lname
            info = {
                'WAName' : waname,
                'WAattorney' : waname,
                'WAPhone' : merge_fn.appendphone(contact.phone1),
                'WAEmail' : contact.email,
                'This.WAName' : waname,
                'This.WAPhone' : merge_fn.appendphone(contact.phone1),
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

    def full_country(self, code: str) -> str:
        print(code)
        if not code:
            return code
        
        c = code.strip().upper()
        base = c[:2]   # handles CAON → CA, USOH → US

        # Try exact code first
        record = CountryLookup.objects.filter(code=c).first()

        if record:
            return record.country_name

        # Fallback: Try first 2 letters as base country
        record = CountryLookup.objects.filter(code=base).first()

        if record:
            return record.country_name

        # Otherwise return the original code
        return c
    
    def fullCountry(self, code: str) -> str:
        print(code)
        if not code:
            return code
        
        c = code.strip().upper()
        base = c[:2]   # handles CAON → CA, USOH → US

        # Try exact code first
        record = CountryLookup.objects.filter(code=c).first()

        if record:
            return record.country_name

        # Fallback: Try first 2 letters as base country
        record = CountryLookup.objects.filter(code=base).first()

        if record:
            return record.country_name

        # Otherwise return the original code
        return c
        
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
    
    def extract_date2(self, text):
        date_pattern = r'\b\d{1,2}/\d{1,2}/\d{2}\b'

        match = re.search(date_pattern, text)
        
        if match:
            return match.group()
        else:
            return None
    
    def inventorInfoName(self, matter, name):
        try:
            merge_fn = mergefunctions()
            first, middle, last = merge_fn.split_name(name)
            matter_data = merge_fn.matterFill(matter)
            parts = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34608')
            for part in parts:
                try:
                    #print(first, last)
                    profile = Personprofile.objects.using('FIP').get(ppid = part.contactid, fname = first, lname = last)
                except:
                    pass
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.homecontactinfoid)
            # if contact.address1 != '':
            #     homeaddr = contact.address1 + '\n' + contact.city + ', ' + contact.state + ' ' + contact.zip
            # elif contact.city != '':
            #     homeaddr = contact.city + ', ' + contact.state + ' ' + contact.zip
            # else:
            #     homeaddr = contact.state + ' ' + contact.zip

            #homeaddr = contact.address1 + '\n' + contact.address2 + '\n' + contact.city + ', ' + contact.zip + '\n'

            homeaddr = ''
            if contact.address1 != '':
                homeaddr = contact.address1
            if contact.address2 != '':
                homeaddr = homeaddr + '\n' + contact.address2
            if contact.city != '':
                homeaddr = homeaddr + '\n' + contact.city + ', ' + contact.state + ' ' + contact.zip + '\n' 

            info = {
                'inventorName' : profile.lname.upper() + ', ' + profile.fname + ' ' + profile.mname,
                'inventorHomeAddress' : homeaddr,
                'inventorHomeCountry' : merge_fn.fullCountry(contact.country),
            }
        except:
            info = {
                'inventorName' : '',
                'inventorHomeAddress' : '',
                'inventorHomeCountry' : ''
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
        

    def faAssigneefill(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        try:
            parts = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34606')

            faassignee = ''
            for part in parts:
                profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
                if faassignee != '':
                    faassignee = faassignee + ', ' + profile.orgname
                    apptxt = 'Applicants'
                else:
                    faassignee = profile.orgname
                    apptxt = 'Applicant'

            info = {
                'faAssignee' : faassignee,
                'applicantTxt' : apptxt
            }
        except:
            info = {
                'faAssignee' : '',
                'applicantTxt' : 'Applicant'
            }
            
        return info
    
    def inventorInfo(self, matter, inv, matter_data=None):
        merge_fn = mergefunctions()
        if matter_data is None:
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
            'inventorHomeCountry' : merge_fn.full_country(contact.country),
            'inventorHomeStreet1' : contact.address1,
            'inventorcitizen': profile.citizenship,
            'inventorHomeZip' : contact.zip,
            'inventorCitizenship' : profile.citizenship,
            'inventorMailingStreet1' : contact.address1,
            'inventorMailingStreet2' : contact.address2,
            'inventorMailingCity' : contact.city,
            'inventorMailingState' : contact.state,
            'inventorMailingZip' : contact.zip,
            'inventorMailingCountry' : merge_fn.full_country(contact.country),

            'inventorName' : profile.fname + ' ' + profile.mname + ' ' + profile.lname,
            'inventorCityState' : contact.city + ' ' + contact.state,
            'inventorCountry' : merge_fn.full_country(contact.country),
            'inventorAddress' : contact.address1,
            'inventorAddress1' : contact.address1,
            'inventorAddress2' : contact.address2,
            'inventorCSZ' : '',
            'Inventor2PCTdeclaration' : '',
            
            'inventorWorkEmail' : profile.sendemailtowork,
            'inventorResidence' : contact.city + contact.state + ',' + contact.country,
        }
        return info
    
    def foreignfillBulk(self, matter):
        """One merge dict per non-US related matter (priority / foreign filing), in stable order."""
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        out = []
        related_matters = Relatedmatter.objects.using('FIP').filter(
            primarymatterid=matter_data.matterid
        ).order_by('relatedmatterid')
        for rel in related_matters:
            try:
                relation_desc = (rel.relationdesc or '').strip().lower()
                if relation_desc == 'other':
                    continue
                rel_matter = Matter.objects.using('FIP').get(matterid=rel.relatedmatterid)
                rel_country = (rel_matter.country or '').strip().upper()
                if rel_country == 'US':
                    continue
                foreign_no = (rel_matter.fmtserialno or rel_matter.serialnumber or '').strip() or ''
                foreign_country = (rel_matter.country or '').strip() or ''
                try:
                    foreign_date = rel_matter.fileddate.strftime("%Y-%m-%d") if rel_matter.fileddate else ''
                except (AttributeError, ValueError):
                    foreign_date = ''
                out.append({
                    'foreignNo': foreign_no,
                    'foreignCntry': foreign_country,
                    'foreignFiledDate': foreign_date,
                })
            except Matter.DoesNotExist:
                continue
        return out

    def foreignfill(self, matter):
        bulk = self.foreignfillBulk(matter)
        if bulk:
            return dict(bulk[0])
        return {
            'foreignNo': '',
            'foreignCntry': '',
            'foreignFiledDate': '',
        }

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
            custcor = merge_fn.corrcustnumFill(matter_data, 'corresp')
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
                'This.serialNo' : matter_data.fmtserialno,
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
        try:
            part1 = s[:2]
            part2 = s[2:]
            part2 = part2[:-3] + ',' + part2[-3:]

            result = part1 + '/' + part2
        except:
            result = 'Unknown'
            
        return result
    
    def transform_patnumber(self, s):
        try:
            part1 = s[:2]
            part2 = s[2:]
            part2 = part2[:-3] + ',' + part2[-3:]

            result = part1 + ',' + part2
        except:
            result = 'Unknown'
            
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
        try:
            cleaned_number = ''.join(filter(str.isdigit, number))
            formatted_number = f"({cleaned_number[:3]}) {cleaned_number[3:6]}-{cleaned_number[6:]}"
        except:
            formatted_number = '()-'
        
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

        if examiner == 'Unknown':
            try:
                examiner = FvMatter4.objects.using('FIP').get(recordid = data.matterid).examiner
            except:
                pass
        
        if examiner == 'None' or examiner == None:
            examiner = 'Unknown'

        return examiner

    def rvwmatterpersonnelFill(self, data):
        try:
            return Rvwmatterpersonnel.objects.using('FIP').get(matterid = data.matterid, roleid = "34619", roleorderno = 1)
        except:
            return ''
    
    # cust correspondence no
    def corrcustnumFill(self, data, no):
        merge_fn = mergefunctions()
        hostmatterno = data.hostmatterno
        custno = ''

        for i in range(3):
            prefix = '' if i == 0 else '0' * i
            client = prefix + hostmatterno.split('.')[0]

            try:
                cust = CustNos.objects.using('SideBar').get(clientno=client)
            except CustNos.DoesNotExist:
                continue

            # Try alternate first
            if cust.alternate:
                alt = cust.alternate.split(')')
                if merge_fn.checkalternate(alt, data):
                    try:
                        if no == 'corresp':
                            custno = cust.correspondencenoalt
                        elif no == 'poa':
                            custno = cust.powerofattorneynoalt
                        elif no == 'maint':
                            custno = cust.maintenancefeenoalt
                        break
                    except Exception as e:
                        print(f"Error retrieving alternate custno: {e}")

            # Try alternate2 next
            if not custno and cust.alternate2:
                alt2 = cust.alternate2.split(')')
                if merge_fn.checkalternate(alt2, data):
                    try:
                        if no == 'corresp':
                            custno = cust.correspondencenoalt2
                        elif no == 'poa':
                            custno = cust.powerofattorneynoalt2
                        elif no == 'maint':
                            custno = cust.maintenancefeenoalt2
                        break
                    except Exception as e:
                        print(f"Error retrieving alternate2 custno: {e}")

            # Fallback to standard number
            if not custno:
                try:
                    if no == 'corresp':
                        custno = cust.correspondenceno
                    elif no == 'poa':
                        custno = cust.powerofattorneyno
                    elif no == 'maint':
                        custno = cust.maintenancefeeno
                    break
                except Exception as e:
                    custno = '21186'

        if not custno:
            custno = '21186'
            
        return custno

    def checkalternate(self, alt, matter_data):
        if alt[0] == '(OPID':
            opids = alt[1].split('/')
            print(opids)
            parts = Matterparticipant.objects.using('FIP').filter(
                Q(roleid='34610') | Q(roleid='56691'),
                matterid=matter_data.matterid
            )
            for part in parts:
                print(part.contactid)
                if str(part.contactid) in opids:
                    return True
                    
            return False
                
        if alt[0] == '(MID':
            mids = alt[1].split('/')
            for mid in mids:
                if matter_data.hostmatterno.startswith(mid):
                    return True
            
        if alt[0] == '(CORR':
            parts = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34610')
            for part in parts:
                try:
                    print((alt[1]).capitalize())
                    profile = Personprofile.objects.using('FIP').get(ppid = part.contactid, lname = (alt[1]).capitalize())
                    return True
                except:
                    pass
    
        return False
    
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
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = data.matterid, roleid = '34617')
            profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
            depnum = profile.ptodepositacct
            if(depnum == ''):
                part = Matterparticipant.objects.using('FIP').get(matterid = data.matterid, roleid = '34616')
                profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
                depnum = profile.ptodepositacct
        except:
            return ''
        return depnum
    
    def orginfoFill(self, data):
        part = Matterparticipant.objects.using('FIP').get(matterid = data.matterid, roleid = '34617')
        profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
        return profile
    
    def getactivityid(self, matter, type):
        try:
            activity = Activity.objects.using('FIP').filter(matterid = matter.matterid, code = type)
            return activity[0]
        except:
            return ''
    
    def getactivityidLast(self, matter, type):
        try:
            activity = Activity.objects.using('FIP').filter(matterid = matter.matterid, code = type)
            return activity.last()
        except:
            return ''
    
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
        date_obj = datetime.strptime(date, '%Y-%m-%d')
        
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

            if profile.mname != '':
                ffname = profile.fname + ' ' + profile.mname + ' ' + profile.lname
            else:
                ffname = profile.fname + ' ' + profile.lname

            info = {
                'ffparaName' : ffname,
                'ffparaEmail' : contact.email,
                'ffparaPhone' : merge_fn.appendphone(contact.phone1)
            }
        except:
            info = {
                'ffparaName' : '',
                'ffparaEmail' : '',
                'ffparaPhone' : ''
            }
        return info
    
    def ffWAfill(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        try:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '58125', roleorderno = 1)
            profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)

            if profile.mname != '':
                ffname = profile.fname + ' ' + profile.mname + ' ' + profile.lname
            else:
                ffname = profile.fname + ' ' + profile.lname

            info = {
                'ffWAName' : ffname,
                'ffWAEmail' : contact.email,
                'ffWAPhone' : merge_fn.appendphone(contact.phone1)
            }
        except:
            info = {
                'ffWAName' : '',
                'ffWAEmail' : '',
                'ffWAPhone' : ''
            }
        return info
    
    def matterCountryName(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        countryname = ''
        try:
            countryname = matter_data.countryname

        except:
            pass
        
        info = {
            'matterCountryName' : countryname,
        }
        return info

    def countryType(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        countrytype = ''
        try:
            countrytype = matter_data.countryname
            if (matter_data.country).strip() == 'US':
                countrytype = 'American'
            if (matter_data.country).strip() == 'CN':
                countrytype = 'Chinese'
            if (matter_data.country).strip() == 'GB':
                countrytype = 'United Kingdom'
            if (matter_data.country).strip() == 'EP':
                countrytype = 'European'
            if (matter_data.country).strip() == 'US':
                countrytype = 'American'
            if (matter_data.country).strip() == 'KR':
                countrytype = 'Korean'
            if (matter_data.country).strip() == 'AU':
                countrytype = 'Australian'
            if (matter_data.country).strip() == 'CA':
                countrytype = 'Canadian'
            if (matter_data.country).strip() == 'JP':
                countrytype = 'Japanese'

        except:
            pass
        
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
    
    def getfrct(self, matter):
        results = []
        try:
            print('trying...')
            query = f"""
                SELECT smryonevalue
                FROM activity WHERE code LIKE 'FRCT%' 
                and smryonelabel like '%Mailed%' 
                AND matterid IN
                (SELECT matterid FROM matter WHERE hostmatterno like '{matter}%') 
                ORDER BY smryonevalue DESC
            """
            
            with connections['FIP'].cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                
            print(results[0][0])
            #frct = str(results[0]).replace('(', '').replace(')', '').replace("'", '').replace(',', '')
            frct = results[0][0].strftime('%B %d, %Y')
            print(frct)
            
        except:
            frct = ''
                    
        return frct
    
    def getFee(self, fee, matter):
        try:
            FeeData = MergeFees.objects.using('SideBar').get(rule_id = fee)
            function_instance = mergefunctions()
            print(function_instance.extract_date2(FeeData.comments))
                
            entitystatus = function_instance.entityfill(matter)
            if(entitystatus == 1 or entitystatus == 0):
                size = 'small'
            if(entitystatus == 2):
                size = 'large'
            if(entitystatus == 3):
                size = 'micro'
                    
            if size == 'large':
                if function_instance.is_date_before_today(function_instance.extract_date2(FeeData.comments)):
                    fee = FeeData.large_new
                else:
                    fee = FeeData.large_old
                        
            if size == 'small':
                if function_instance.is_date_before_today(function_instance.extract_date2(FeeData.comments)):
                    fee = FeeData.small_new
                else:
                    fee = FeeData.small_old
                        
            if size == 'micro':
                if function_instance.is_date_before_today(function_instance.extract_date2(FeeData.comments)):
                    fee = FeeData.micro_new
                else:
                    fee = FeeData.micro_old   
            fee = fee + '.00'
        except:
            fee = ''
        
        return fee.replace(' ', '')
    
    def is_date_before_today(self, date_str):
        """Compares a date string to today's date."""
        try:
            date_obj = datetime.strptime(date_str, "%m/%d/%y")
            today = datetime.today()
            return date_obj <= today
        except ValueError:
            return False
        
    def getPreviousPaidData(self, matter):
        results = []
        try:
            print('trying...')
            query = f"""
                SELECT code, smryonelabel, smryonevalue 
                FROM activity WHERE code IN ('NOWI', 'PWFI') 
                AND matterid IN
                (SELECT matterid FROM matter WHERE hostmatterno LIKE '{matter}%')
            """
            
            with connections['FIP'].cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()
                
            print(results[0][0])
            data = results[0][0].strftime('%B %d, %Y')
            print(data)
            
        except:
            data = ''
                    
        return data
        
    def phoneFillSA(self, fullname):
        # Split the full name into first and last name
        fname, lname = fullname.strip().split(' ', 1)
        
        try:
            profile = Personprofile.objects.using('FIP').filter(fname=fname, lname=lname)
            
            contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile[0].workcontactinfoid)
            info = contact.phone1
        except:
            info = ''
            
        return info
    
    def fullSAName(self, fullname):
        # Split the full name into first and last name
        fname, lname = fullname.strip().split(' ', 1)
        info = fullname
        regno = ''
        try:
            profile = Personprofile.objects.using('FIP').filter(fname=fname, lname=lname)
            info = fname + ' ' + profile[0].mname + ' ' + lname
            if profile[0].mname == '' or profile[0].mname == None:
                info = fname + ' ' + lname
            regno = profile[0].registrationno
        except:
            pass
    
        return info, regno
    
    def feeAddition(self, amount1: str, amount2: str):
        # Remove dollar signs and convert to float
        amount1 = amount1.replace(',', '')
        amount2 = amount2.replace(',', '')

        value1 = float(amount1.replace('$', '').strip())
        value2 = float(amount2.replace('$', '').strip())
        
        # Add the values
        total = value1 - value2
        
        # Format the result as a dollar string
        return f"${total:.2f}"
    
    def entityName(self, entitystatus):
        size = ''
        if(entitystatus == 1 or entitystatus == 0):
            size = 'small'
        if(entitystatus == 2):
            size = 'large'
        if(entitystatus == 3):
            size = 'micro'

        return size
    
    def clientMatterNo(self, matter_data):
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
                clientcode = ClientSpec.objects.using('SideBar').get(clientno=client)
                part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34617', roleorderno = 1)
                matterno = part.matterno
                matternumber = eval(clientcode.format)
                break
            except:
                matternumber = matter_data.hostmatterno

        return matternumber
    
    def getDuedateTag(self, matter):

        matter_data = self.matterFill(matter)
        dateIssueFee = ''
        try:
            feeactivity = self.getactivityid(matter_data, 'IFEE')
            if feeactivity and feeactivity.smryonevalue:
                dateIssueFee = feeactivity.smryonevalue.strftime("%B %d, %Y")
        except:
            pass
        
        return {'dueDate': dateIssueFee}
    
    def SAEmailFill(self, name):
        # Split the full name into first and last name
        fname, lname = name.strip().split(' ', 1)

        try:
            profile = Personprofile.objects.using('FIP').filter(fname=fname, lname=lname)
            contact = Contactinfo.objects.using('FIP').filter(contactinfoid=profile[0].workcontactinfoid)
            info = contact[0].email
        except:
            info = ''
    
        return info
    

    def _safe_str(self, val):
        return str(val) if val is not None else ''

    def inventorInfoBulk(self, matter_data, method, mailing_address_source='home'):
        """
        Bulk fetch all inventors. Home address always from inventor's home contact.
        mailing_address_source: 'home' | 'client' | 'applicant'
        - home: inventor mailing address = inventor's home contact
        - client: inventor mailing address = client (role 34617) contact
        - applicant: inventor mailing address = first applicant's contact
        """
        inventors = list(Matterparticipant.objects.using('FIP').filter(
            matterid=matter_data.matterid, roleid='34608'
        ).order_by('roleorderno'))
        if not inventors:
            return []
        pp_ids = [p.contactid for p in inventors]
        profiles = {p.ppid: p for p in Personprofile.objects.using('FIP').filter(ppid__in=pp_ids)}
        contact_ids = set()
        for p in profiles.values():
            if p.workcontactinfoid:
                contact_ids.add(p.workcontactinfoid)
            if p.homecontactinfoid:
                contact_ids.add(p.homecontactinfoid)
        contacts = {c.contactinfoid: c for c in Contactinfo.objects.using('FIP').filter(contactinfoid__in=contact_ids)} if contact_ids else {}

        # Applicant contact for mailing_address_source='applicant'
        applicant_contact = None
        applicant_orgname = ''
        if mailing_address_source == 'applicant':
            try:
                app_part = Matterparticipant.objects.using('FIP').filter(
                    matterid=matter_data.matterid, roleid='56691'
                ).order_by('roleorderno').first()
                if app_part:
                    app_profile = Orgprofile.objects.using('FIP').get(opid=app_part.contactid)
                    applicant_orgname = self._safe_str(app_profile.orgname)
                    if app_profile.contactinfoid:
                        applicant_contact = Contactinfo.objects.using('FIP').get(contactinfoid=app_profile.contactinfoid)
            except Exception:
                pass

        # Client contact for mailing_address_source='client' (client org = role 34617)
        client_contact = None
        client_orgname = ''
        if mailing_address_source == 'client':
            try:
                client_part = Matterparticipant.objects.using('FIP').filter(
                    matterid=matter_data.matterid, roleid='34617'
                ).order_by('roleorderno').first()
                if client_part:
                    client_profile = Orgprofile.objects.using('FIP').get(opid=client_part.contactid)
                    client_orgname = self._safe_str(client_profile.orgname)
                    if client_profile.contactinfoid:
                        client_contact = Contactinfo.objects.using('FIP').get(contactinfoid=client_profile.contactinfoid)
            except Exception:
                pass

        inv_count = len(inventors)
        result = []
        for inv_num, part in enumerate(inventors, 1):
            profile = profiles.get(part.contactid)
            if not profile:
                result.append({'inventorCnt': inv_num if inv_count > 1 else 'Inventor: ', 'inventor': '', 'invpre': '', 'inventorFirstName': '', 'inventorMiddleInitial': '', 'inventorLastName': '', 'inventorSuffix': '', 'inventorHomeCity': '', 'inventorHomeState': '', 'inventorHomeCountry': '', 'inventorMailingStreet1': '', 'inventorMailingStreet2': '', 'inventorMailingCity': '', 'inventorMailingState': '', 'inventorMailingZip': '', 'inventorMailingCountry': ''})
                continue
            home_contact = contacts.get(profile.homecontactinfoid) if profile.homecontactinfoid else None

            if mailing_address_source == 'applicant' and applicant_contact:
                mail_contact = applicant_contact
                mail_orgname = applicant_orgname
            elif mailing_address_source == 'client' and client_contact:
                mail_contact = client_contact
                mail_orgname = client_orgname
            else:
                mail_contact = home_contact
                mail_orgname = ''

            if not mail_contact:
                result.append({'inventorCnt': inv_num if inv_count > 1 else 'Inventor: ', 'inventor': '', 'invpre': '', 'inventorFirstName': '', 'inventorMiddleInitial': '', 'inventorLastName': '', 'inventorSuffix': '', 'inventorHomeCity': '', 'inventorHomeState': '', 'inventorHomeCountry': '', 'inventorMailingStreet1': '', 'inventorMailingStreet2': '', 'inventorMailingCity': '', 'inventorMailingState': '', 'inventorMailingZip': '', 'inventorMailingCountry': ''})
                continue

            inv_label = 'Inventor: ' if inv_count == 1 else inv_num
            s = self._safe_str
            if mail_orgname:
                mail_prefix = f"c/o {mail_orgname} "
                mail_street1 = (mail_prefix + s(mail_contact.address1)).strip()
                mail_street2 = (s(mail_contact.address2)).strip() if s(mail_contact.address2).strip() else ''
            else:
                mail_street1 = s(mail_contact.address1)
                mail_street2 = s(mail_contact.address2)
            if profile.mname != '' and profile.mname != None:
                fullname = f"{s(profile.fname)} {s(profile.mname)} {s(profile.lname)}"
            else:
                fullname = f"{s(profile.fname)} {s(profile.lname)}"
                
            result.append({
                'inventorCnt': inv_label, 'inventor': fullname,
                'invpre': s(profile.salutation), 'inventorFirstName': s(profile.fname), 'inventorMiddleInitial': s(profile.mname),
                'inventorLastName': s(profile.lname), 'inventorSuffix': s(profile.namesuffix),
                'inventorHomeCity': s(home_contact.city) if home_contact else '', 'inventorHomeState': s(home_contact.state) if home_contact else '', 'inventorHomeCountry': (s(home_contact.country)) if home_contact else '',
                'inventorMailingStreet1': mail_street1, 'inventorMailingStreet2': mail_street2,
                'inventorMailingCity': s(mail_contact.city), 'inventorMailingState': s(mail_contact.state),
                'inventorMailingZip': s(mail_contact.zip), 'inventorMailingCountry': s(mail_contact.country),
            })
        return result

    def applicantfillBulk(self, matter_data):
        """Bulk fetch all applicants - 3 queries instead of ~4 per applicant."""
        applicants = list(Matterparticipant.objects.using('FIP').filter(
            matterid=matter_data.matterid, roleid='56691'
        ).order_by('roleorderno'))
        if not applicants:
            return []
        op_ids = [p.contactid for p in applicants]
        profiles = {p.opid: p for p in Orgprofile.objects.using('FIP').filter(opid__in=op_ids)}
        contact_ids = {profiles[p].contactinfoid for p in op_ids if p in profiles and profiles[p].contactinfoid is not None}
        contacts = {c.contactinfoid: c for c in Contactinfo.objects.using('FIP').filter(contactinfoid__in=contact_ids)} if contact_ids else {}
        app_count = len(applicants)
        result = []
        for app_num, part in enumerate(applicants, 1):
            profile = profiles.get(part.contactid)
            contact = contacts.get(profile.contactinfoid) if profile and profile.contactinfoid else None
            if not profile or not contact:
                result.append({'applCnt': app_num if app_count > 1 else 'Applicant: ', 'applicantCity': '', 'applicantState': '', 'applicantZip': '', 'applicantCountry': '', 'applicantStreet1': '', 'applicantStreet2': '', 'applicant': '', 'applicantName': '', 'applicantIsOrg': False})
                continue
            label = 'Applicant: ' if app_count == 1 else app_num
            s = self._safe_str
            result.append({
                'applCnt': label, 'applicantCity': s(contact.city), 'applicantState': s(contact.state),
                'applicantZip': s(contact.zip), 'applicantCountry': s(contact.country),
                'applicantStreet1': s(contact.address1), 'applicantStreet2': s(contact.address2),
                'applicant': s(profile.orgname), 'applicantIsOrg': True,
            })
        return result

    def assigneefillBulk(self, matter_data):
        """Bulk fetch all assignees - 3 queries instead of ~4 per assignee."""
        assignees = list(Matterparticipant.objects.using('FIP').filter(
            matterid=matter_data.matterid, roleid='34606'
        ).order_by('roleorderno'))
        if not assignees:
            return []
        op_ids = [p.contactid for p in assignees]
        profiles = {p.opid: p for p in Orgprofile.objects.using('FIP').filter(opid__in=op_ids)}
        contact_ids = {profiles[p].contactinfoid for p in op_ids if p in profiles and profiles[p].contactinfoid is not None}
        contacts = {c.contactinfoid: c for c in Contactinfo.objects.using('FIP').filter(contactinfoid__in=contact_ids)} if contact_ids else {}
        assign_count = len(assignees)
        result = []
        for assign_num, part in enumerate(assignees, 1):
            profile = profiles.get(part.contactid)
            contact = contacts.get(profile.contactinfoid) if profile and profile.contactinfoid else None
            if not profile or not contact:

                result.append({'assigneeCnt': assign_num if assign_count > 1 else 'Assignee: ', 'assigneeCity': '', 'assigneeState': '', 'assigneeZip': '', 'assigneeCountry': '', 'assigneeStreet1': '', 'assigneeStreet2': '', 'assignee': '', 'assigneeIsOrg': False})
                continue
            label = 'Assignee: ' if assign_count == 1 else assign_num
            s = self._safe_str
            result.append({
                'assigneeCnt': label,
                'assigneeCity': s(contact.city), 'assigneeState': s(contact.state), 'assigneeZip': s(contact.zip),
                'assigneeCountry': s(contact.country), 'assigneeStreet1': s(contact.address1),
                'assigneeStreet2': s(contact.address2), 'assignee': s(profile.orgname),
                'assigneeIsOrg': True,
            })
        return result

    def statement373c_reel_frame_count(self, matter):
        """
        Return count of reel/frame assignment pairs for Statement373c.
        Same query as Statement373c in merges.py. Returns 0, 1, or >1.
        """
        matter_data = self.matterFill(matter)
        query_matter_id = int(matter_data.matterid)
        query = f"""
            SELECT 
                (select cast(val as varchar(30)) from AttributeVal av where label like '%Starting%' and objid = activity.activityId),
                (select cast(val as varchar(30)) from AttributeVal av where label like '%Ending%' and objid = activity.activityId),
                (select cast(val as varchar(30)) from AttributeVal av where label like '%Reel%' and objid = activity.activityId)
            FROM activity 
            JOIN rvwActivityDateAttribute da on da.activityId = activity.activityid
            WHERE activity.MATTERID = '{query_matter_id}'
            and CODE in ('ASSN-11', 'ASSN-7', 'ASSN-2')
            and attrValLabel like '%Record%'
            and dateval is not null
            ORDER by dateval
        """
        try:
            with connections['FIP'].cursor() as cursor:
                cursor.execute(query)
                assignments = cursor.fetchall()
            return len(assignments)
        except Exception as e:
            print(f"Error in statement373c_reel_frame_count: {e}")
            return 0

    def merge_fee_amount(self, rule_id, matter):
        """
        Fee amount (float) from merge_fees for entity size, using the same old vs new columns as getFee():
        if the effective date parsed from comments is on or before today, use *_new; otherwise *_old.
        If no date is found in comments, uses *_old (matches getFee when date parsing fails).
        """
        try:
            rid = str(rule_id).strip()
            row = MergeFees.objects.using('SideBar').get(pk=rid)
            entitystatus = self.entityfill(matter)
            comments = row.comments or ''
            eff = self.extract_date2(comments)
            use_new = self.is_date_before_today(eff) if eff else False
            if entitystatus == 2:
                raw = row.large_new if use_new else row.large_old
            elif entitystatus == 3:
                raw = row.micro_new if use_new else row.micro_old
            else:
                raw = row.small_new if use_new else row.small_old
            if raw is None or str(raw).strip() == '':
                return None
            s = str(raw).replace('$', '').replace(',', '').strip()
            return float(s)
        except (MergeFees.DoesNotExist, ValueError, TypeError, AttributeError):
            return None

    def merge_fee_new_amount(self, rule_id, matter):
        """Deprecated alias: use merge_fee_amount (old/new per effective date)."""
        return self.merge_fee_amount(rule_id, matter)