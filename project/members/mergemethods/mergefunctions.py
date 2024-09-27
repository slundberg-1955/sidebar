from datetime import datetime
from ..models import Matter
from ..models import Rvwmatterinventors
from ..models import Rvwmatterpersonnel
from ..models import Matterparticipant
from ..models import Orgprofile, Personprofile
from ..models import Contactinfo
from ..models import Patent, Customernumbers, CustomerNos, Activity
from datetime import datetime
from dateutil.relativedelta import relativedelta

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

            basic = {
                'serialNo' : merge_fn.transform_serialnumber(matter_data.serialnumber),
                'filedDate' : matter_data.fileddate.strftime("%B %d, %Y"),
                'title' : matter_data.title,
                'matterNo' : matter_data.hostmatterno,
                'custNoCorresp' : custcor,
                'custNoMFee' : custcor,
                'confirmNo' : confirm,
                'examinerName' : merge_fn.examinerFill(matter_data)
            }
            basic.update(merge_fn.mergebasicEmail(keys, matter))
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'patent' in tables_list:
            patent_data = merge_fn.patentFill(matter_data)
            basic = {
                'artUnit' : patent_data.artunitno
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'inventor' in tables_list:
            inventor_data = merge_fn.inventorFill(matter_data)
            inventoretal = merge_fn.inventoretal(inventor_data.inventor)
            basic = {
                'inventorEtal' : inventoretal,
                'firstInventor' : inventor_data.inventor
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'rvwmatterpersonnel' in tables_list:
            SA_data = merge_fn.rvwmatterpersonnelFill(matter_data)
            basic = {
                'SAName' : SA_data.fname + ' ' + SA_data.mname + '. ' + SA_data.lname,
                'SARegNo' : SA_data.registrationno,
                'orgName' : SA_data.orgname,
                'nickSA' : SA_data.nickname,
                'SAPhone' : merge_fn.phoneFill(matter_data),
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
            if 'GB' in contact.country:
                country = 'United Kingdom'
            if contact.country == 'US':
                country = 'United States'

            addr = contact.address1 + '\n' + contact.address2 + '\n' + contact.city + ', ' + contact.zip + '\n' + country
            basic = {
                'faOrgName' : profile.orgname,
                'faWorkAddr' : addr,
                'faCSZ' : '',
                'faAssignee' : '',
                'recipientEmail' : contact.email
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        if 'current' in tables_list:
            basicOut.update({'currentDate': datetime.now().strftime("%B %d, %Y")})

        if 'matterparticipant' in tables_list:
            part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34617', roleorderno = 1)
            basic = {
                'clientRefNo' : 'Ref. No. ' + part.matterno
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

        return basicOut

    # assignee information fill 34606   
    def assigneefill(self, matter, count):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
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
        }
        return info
    
    # Applicant information fill. Update roleid  56691
    def applicantfill(self, matter, count):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
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
        return info

    def recordationRoleFill(self, matter, role):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)

        part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = role, roleorderno = 1)
        profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
        contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.contactinfoid)

        info = {
            'assigneeCity' : contact.city,
            'assigneeState' : contact.state,
            'assigneeZip' : contact.zip,
            'assigneeCountry' : contact.country,
            'assigneeStreet' : contact.address1,
            'assigneeName' : profile.orgname,
        }
        return info

    # Para fill
    def parafill(self, keys, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
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
        }
        return info
    
    # WA fill
    def WAfill(self, keys, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34615', roleorderno = 1)
        profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
        contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
        info = {
            'WAName' : profile.fname + ' ' + profile.lname,
            'WAPhone' : contact.phone1,
            'WAEmail' : contact.email,
            'THIS.WAName' : profile.fname + ' ' + profile.lname,
            'THIS.WAPhone' : contact.phone1,
            'THIS.WAEmail' : contact.email,
            'This.WAName' : profile.fname + ' ' + profile.lname,
            'This.WAPhone' : contact.phone1,
            'This.WAEmail' : contact.email,
        }
        return info
    
    def split_name(self, full_name):
        parts = full_name.split(' ')
        
        first_name = parts[0]
        last_name = parts[-1]
        middle_name = ""

        if len(parts) > 2:
            middle_name = " ".join(parts[1:-1])
        
        return first_name, middle_name, last_name
    
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

        info = {
            'inventorName' : profile.lname.upper() + ', ' + profile.fname + ' ' + profile.mname,
            'inventorHomeAddress' : contact.state,
            'inventorHomeCountry' : contact.country,
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
            'inventorMailingStreet1' : contact.address1,
            'inventorMailingStreet2' : contact.address2,
            'inventorMailingCity' : contact.city,
            'inventorMailingState' : contact.state,
            'inventorMailingZip' : contact.zip,
            'inventorMailingCountry' : contact.country,

            'inventorName' : profile.fname + ' ' + profile.mname + '. ' + profile.lname,
            'inventorCityState' : contact.city + ' ' + contact.state,
            'inventorCountry' : contact.country,
            'inventorAddress1' : contact.address1,
            'inventorAddress2' : contact.address2,
            'inventorCSZ' : '',
            'Inventor2PCTdeclaration' : '',
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
            basic = {
                'This.serialNo' : merge_fn.transform_serialnumber(matter_data.serialnumber),
                'This.filedDate' : matter_data.fileddate.strftime("%B %d, %Y"),
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
            'inventorEtal' : 'inventor',
            'filedDate' : 'matter',
            'custNoCorresp' : 'matter',
            'title' : 'matter',
            'examinerName' : 'personnel',
            'artUnit' : 'patent',
            'matterNo' : 'matter',
            'confirmNo' : 'matter',
            'SAName' : 'rvwmatterpersonnel',
            'SARegNo' : 'rvwmatterpersonnel',
            'SAPhone' : 'rvwmatterpersonnel',
            'nickSA' : 'rvwmatterpersonnel',
            'orgName' : 'rvwmatterpersonnel',
            'recipient' : 'rvwmatterinventors',
            'WAName' : 'WA',
            'WAPhone' : 'WA',
            'WAEmail' : 'WA',
            'THIS.WAName' : 'WA',
            'THIS.WAPhone' : 'WA',
            'THIS.WAEmail' : 'WA',
            'This.WAName' : 'WA',
            'This.WAPhone' : 'WA',
            'This.WAEmail' : 'WA',
            'paraName' : 'para',
            'paraPhone' : 'para',
            'paraEmail' : 'para',
            'This.paraName' : 'para',
            'This.paraPhone' : 'para',
            'This.paraEmail' : 'para',
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
        if(esign == 'true' or esign == True):
            esign_out = "/ {{Sig_es_:signer1:signature}} /"
            esigndate_out = "{{Dte_es_:signer1:date}}"

        return esign_out, esigndate_out
    
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
        formatted_number = f"({cleaned_number[:3]})-{cleaned_number[3:6]}-{cleaned_number[6:]}"
    
        return formatted_number
    
    def matterFill(self, matter):
        return Matter.objects.using('FIP').get(hostmatterno = matter)
    
    def inventorFill(self, data):
        return Rvwmatterinventors.objects.using('FIP').get(matterid = data.matterid)

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
            return Rvwmatterpersonnel.objects.using('FIP').get(matterid = data.matterid, roleid = "34619")
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
        part = Matterparticipant.objects.using('FIP').get(matterid = data.matterid, roleid = '34617')
        profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
        contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.contactinfoid)
        function_instance = mergefunctions()
        phonenum = function_instance.appendphone(contact.phone1)
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
        activity = Activity.objects.using('FIP').get(matterid = matter.matterid, code = type)

        return activity
    
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