from ..models import Matter
from ..models import Rvwmatterinventors
from ..models import Rvwmatterpersonnel
from ..models import Matterparticipant
from ..models import Orgprofile, Personprofile
from ..models import Contactinfo
from ..models import Patent, Customernumbers, CustomerNos, Activity
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
                'inventorEtal' : inventoretal
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})
        if 'rvwmatterpersonnel' in tables_list:
            SA_data = merge_fn.rvwmatterpersonnelFill(matter_data)
            basic = {
                'SAName' : SA_data.personname,
                'SARegNo' : SA_data.registrationno,
                'orgName' : SA_data.orgname,
            }
            for key, value in basic.items():
                if key in keys:
                    basicOut.update({key: value})

        return basicOut

    # assignee information fill    
    def assigneefill(self, keys, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34617')
        profile = Orgprofile.objects.using('FIP').get(opid = part.contactid)
        contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.contactinfoid)
        info = {
            'assigneeName' : profile.orgname,
            'assigneeStreet' : contact.address1,
            'assigneeCity' : contact.city,
            'assigneeState' : contact.state,
            'assigneeZip' : contact.zip,
            'assigneeCountry' : contact.country,
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
        }
        return info
    
    def inventorInfo(self, keys, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        part = Matterparticipant.objects.using('FIP').get(matterid = matter_data.matterid, roleid = '34608', roleorderno = 1)
        profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
        workcontact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid)
        contact = Contactinfo.objects.using('FIP').get(contactinfoid = profile.homecontactinfoid)

        inventors = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34608')
        invCount = len(inventors)

        info = {
            'inventorCnt' : invCount,
            'inventor' : '',
            'invpre' : profile.salutation,
            'inventorFirstName' : profile.fname,
            'inventorMiddleInitial' : profile.mname,
            'inventorLastName' : profile.lname,
            'inventorSuffix' : profile.namesuffix,
            'inventorHomeCity' : contact.city,
            'inventorHomeState' : contact.state,
            'inventorHomeCountry' : contact.country,
            'inventorMailingStreet1' : workcontact.address1,
            'inventorMailingStreet2' : workcontact.address2,
            'inventorMailingCity' : workcontact.city,
            'inventorMailingState' : workcontact.state,
            'inventorMailingZip' : workcontact.zip,
            'inventorMailingCountry' : workcontact.country,
        }
        return info

    def entityfill(self, matter):
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        patent_data = merge_fn.patentFill(matter_data)

        return patent_data.entitystatus
    
    def firmfill(self, keys, matter):
        # Might need to pull from DB
        info = {
            'firmName' : 'Schwegman Lundberg & Woessner, P.A.',
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
            'custNoCorresp' : 'patent',
            'title' : 'matter',
            'examinerName' : 'personnel',
            'artUnit' : 'patent',
            'matterNo' : 'matter',
            'confirmNo' : 'matter',
            'SAName' : 'rvwmatterpersonnel',
            'SARegNo' : 'rvwmatterpersonnel',
            'orgName' : 'rvwmatterpersonnel',
            'recipient' : 'rvwmatterinventors',
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