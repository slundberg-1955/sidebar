from ..mergemethods import mergefunctions
from ..models import Activity
from datetime import date, datetime

class appealfwd:
    def appealfwd(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        esign = mergeinfo[0]

        entitystatus = function_instance.entityfill(matter)

        esign_out, esigndate_out = function_instance.esigncheck(esign)
        replace = {}

        # Fill Data
        matter_data = function_instance.matterFill(matter)
        patent_data = function_instance.patentFill(matter_data)

        depnum = function_instance.depnumFill(matter_data)
        artunitno = patent_data.artunitno
        custcor = function_instance.corrcustnumFill(matter_data)

        if(custcor == ''):
            custcor = 'Unknown'
        if(artunitno == '' or artunitno == 'None'):
            artunitno = 'Unknown'

        if(entitystatus == 0):
            billamt = '944.00'
        if(entitystatus == 2):
            billamt = '2,360.00'
        if(entitystatus == 1):
            billamt = '472.00'
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'feeAmount' : billamt,
            'depAccount' : depnum,
        })
        return replace
    
class pclaims:
    def pclaims(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({
            'claimsDate' : mergeinfo[0],
            'dateDescription' : mergeinfo[1],
        })
        return replace

class issuefee:
    def issuefee(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        reqpat = mergeinfo[2]
        numfact = mergeinfo[3]
        drawnum = mergeinfo[4]
        prevpaiddate = mergeinfo[7]
        esign = mergeinfo[12]

        dateIssueFee = ''
        try:
            feeactivity = function_instance.getactivityid(matter_data, 'IFEE')
            paid = True
        except:
            paid = False
        
        if paid:
            if feeactivity.smryonevalue:
                dateIssueFee = feeactivity.smryonevalue.strftime("%B %d, %Y")

        try:
            feeactivity = function_instance.getactivityid(matter_data, 'NOAR')
            noarDate = feeactivity.smryonevalue.strftime("%B %d, %Y")
        except:
            noarDate = ''

        if reqpat == 'true':
            adjtxt = 'X'
            adjfee = 'X'
            adjfact = 'X'
            patadjtxt =  '         Application for Patent Term Adjustment Under 37 CFR 1.705(b) (1 pg.).'
            patadjfee =  '         Check in the amount of' + '12' + 'to cover the fee for Application for Patent Term Adjustment under 37 CFR 1.18(e).'
            patadjfact = '         Statement of Facts Under 37 CFR 1.705(b)(2) in Support of Application for Patent Term Adjustment (' + numfact + ' pgs.).'
        
        else:
            adjtxt = ''
            adjfee = ''
            adjfact = ''
            patadjtxt = ''
            patadjfee = ''
            patadjfact = ''
        
        if int(drawnum) > 0:
            drawingX = 'X'
            drawtxt =    '         Formal Drawings (' + drawnum + ' sheets).'
        else:
            drawingX = ''
            drawtxt = ''

        # if withfiled == 'true':
            

        # if feeincrease:
        entitystatus = function_instance.entityfill(matter)
        description = matter_data.mattertypedescription
        if "DESIGN" in description:
            if entitystatus == 2:
                designfee = 740
            if entitystatus == 1:
                designfee = 185
            else:
                designfee = 370
                # ( - firstfeeamount)
            feeincrease = designfee
        else:
            if "PLANT" in description:
                if entitystatus == 2:
                    # ( - firstfeeamount)
                    feeincrease = 840
                    # ( - firstfeeamount)
                if entitystatus == 1:
                    # ( - firstfeeamount)
                    designfee = 210
                else:# ( - firstfeeamount)
                    designfee = 420

        wdrwtxt = ''
        if mergeinfo[8] == 'true' and mergeinfo[9] != '':
            wdrwtxt = 'A petition under 37 CFR 1.313(c)(2) to withdraw the above-identified application from issue after payment of the issue fee was subsequently filed on .  Applicant received a decision, dated '+ mergeinfo[9] +', granting the petition to withdraw.'
        
        if mergeinfo[11] == 'true':
            increasetxt = 'The present issue fee has increased from the previously-paid issue fee.  Transmitted herewith is authorization to charge Deposit Account '+ depnum +' in the amount of  to cover the issue fee increase.'

        esign_out, esigndate_out = function_instance.esigncheck(esign)
        depnum = function_instance.depnumFill(matter_data)
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            #'nickU' : '',
            'dateIssueFee': prevpaiddate,
            'withDrawText' : wdrwtxt,
            #'increaseText' : '',
            'dateNOAR' : noarDate,
            'depAccount' : depnum,
            'drawingX' : drawingX,
            'formalDrawingText' : drawtxt,
            'adjTextX' : adjtxt,
            'adjFeeX' : adjfee,
            'adjFactsX' : adjfact,
            'patentTermAdjText' : patadjtxt,
            'patentTermAdjFee' : patadjfee,
            'patentTermAdjFacts' : patadjfact,
            #'feeTextX' : '',
            #'FeeText' : '',
            'pubFeeX' : 'X',
            'pubFeeText' : '    Check in the amount of $210.00 to cover the fee for Application for Patent Term Adjustment under 37 CFR 1.18(e).',
            #'previousX' : '',
            #'applyPreviousText' : '',
            #'commentX' : '',
            #'commentText' : '',
            'dueDate' : dateIssueFee,
        })
        return replace
    
class Statement373c:
    def Statement373c(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        esign = mergeinfo[1]
        recoccur = mergeinfo[0]

        if mergeinfo[2] == 'oth':
            org = mergeinfo[3]
        else:
            if mergeinfo[2]:
                org = mergeinfo[2]
        
        esign_out, esigndate_out = function_instance.esigncheck(esign)
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'orgType' : org,
            
        })
        return replace
    
# may need to add other organization types. May need totalfee
class recordation:
    def recordation(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        depnum = function_instance.depnumFill(matter_data)
        replace = {}
        if mergeinfo[0] == '1':
            replace.update(function_instance.assigneefill(matter, 1))
            selinv = mergeinfo[4]

        if mergeinfo[0] == '2':
            selinv = mergeinfo[4]
            name = mergeinfo[7].split(": ", 1)[0]
            if name == 'Applicant':
                roleid = '56691'
            if name == 'Assignee':
                roleid = '34606'
            if name == 'Client':
                roleid = '34617'
            if name == 'Previous Client/Matter Number':
                roleid = '93476'
            if name == 'Licensee':
                roleid = '34607'
            try:
                replace.update(function_instance.recordationRoleFill(matter, roleid))
            except:
                pass

        totfee = 0
        depX = ''
        chkX = ''
        if mergeinfo[3] == 'depacc':
            depX = 'X'
        if mergeinfo[3] == 'check':
            chkX = 'X'            

        esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[3])
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'depAccount' : depnum,
            'dateExecutionText' : datetime.strptime(mergeinfo[5], "%m/%d/%Y").strftime("%B %d, %Y"),
            'selectedInventorList' : selinv,
            'totalFee' : totfee,
            'numPages' : mergeinfo[2],
            'depAcctX' : depX,
            'checkX' : chkX,
        })
        return replace
 
# Only need duedate and nickU
class LateSubmissionOfDec:
    def LateSubmissionOfDec(self, matter, mergeinfo, keys):
        esign = mergeinfo[3]
        
        function_instance = mergefunctions.mergefunctions()
        esign_out, esigndate_out = function_instance.esigncheck(esign)
        replace = {}

        # Fill Data
        matter_data = function_instance.matterFill(matter)
        depnum = function_instance.depnumFill(matter_data)
        entitystatus = function_instance.entityfill(matter)

        if(entitystatus == 0):
            feeamt = '64.00'
        if(entitystatus == 2):
            feeamt = '160.00'
        if(entitystatus == 1):
            feeamt = '32.00'

        decsubx = ''
        decsubtxt = ''
        depx = ''
        deptxt = ''
        feeamt = ''
        latepaid = ''
        if mergeinfo[1] != '' and int(mergeinfo[1]) > 0:
            decsubx = 'X'
            decsubtxt = 'Signed Declaration ('+ mergeinfo[1] +' '+ function_instance.pgCount(int(mergeinfo[1])) +'.).'
            latepaid = 'Declaration. '
        if mergeinfo[2] != '' and int(mergeinfo[2]) > 0:
            decsubx = 'X'
            decsubtxt = 'Signed Substitute Statement ('+ mergeinfo[2] +' '+ function_instance.pgCount(int(mergeinfo[2])) +'.).'
            latepaid = 'Substitute Statement in lieu of a Declaration. '
        if mergeinfo[0] == 'true':
            latepaid = latepaid + 'Corresponding fees with regard to the late submission were paid previously, therefore applicants believe no additional fees are due at this time.'
        else:
            depx = 'X'
            deptxt = 'Authorization to charge Deposit Account '+ depnum +' in the amount of $'+ feeamt +' to cover the Late Submission Surcharge. '

        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'depAccount' : depnum,
            'decsubX' : decsubx,
            'decsubText' : decsubtxt,
            'depX' : depx,
            'depText' : deptxt,
            'nickU' : '',
            'latePaid': latepaid,
            'firmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'dueDate' : '',
        })
        return replace     

class UpdateAppDataSheet:
    def UpdateAppDataSheet(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        if(mergeinfo[0] == 'true'):
            muX = 'X'
            muText = 'Marked Up Application Data Sheet (' + mergeinfo[1] + ' Pg.).'
            if int(mergeinfo[1]) > 1:
                muText = 'Marked Up Application Data Sheet (' + mergeinfo[1] + ' Pgs.).'
        
        dsX = 'X'
        dsText = 'Communication Re: Update to Application Data Sgeet (1 Pg.).'

        esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[2])
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'dsX' : dsX,
            'dsText'  : dsText,
            'muX' : muX,
            'muText' : muText,
        })
        return replace
    
class olpemail:
    def olpemail(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        replace = {}
        # Fill Data
        matter_data = function_instance.matterFill(matter)
        patent_data = function_instance.patentFill(matter_data)
        org_data = function_instance.orginfoFill(matter_data)

        # May need editing
        utilityText1 = "The patent will remain in effect for a term of twenty years from the date of the earliest filing.  To maintain the patent for its entire term, maintenance fees must be paid when due.  The fees are due as follows:"
        utilityFee1 = "3-1/2 years from the issue date"
        utilityFee2 = "7-1/2 years from the issue date"
        utilityFee3 = "11-1/2 years from the issue date"
        
        answer = mergeinfo[0]
        # Need to add use case for answer
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'This.orgName' : org_data.orgname,
            'This.clientRefNo' : '',
            'activityname' : '',
            'THIS.patNo' : patent_data.patentno,
            'THIS.issueDate' : patent_data.issuedate,
            'THIS.title'  : matter_data.title,
            'designText' : '',
            'utilityText1' : utilityText1,
            'cutilityText2' : 'Prior instructions have been received acknowledging SLW responsibility for payment of the maintenance fees through our preferred 3rd party provider, Black Hills AI (www.blackhills.ai).  If for any reason this process is no longer valid, please reach out to us expeditiously to confirm new instructions.',
            'utilityFee1' : utilityFee1,
            'utilityFee2' : utilityFee2,
            'utilityFee3' : utilityFee3,
            'cutilityText2' : '',
        })
        return replace
    
class mpcapactions:
    def mpcapactions(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        action = int(mergeinfo[0])

        if action in (1, 5):
            code = 'MPTA'
        if action in (2, 7):
            code = 'CAPR-'
        if action == 3:
            code = 'SEQL-1'
        if action == 4:
            code = 'NOMR, MRTA'
        if action == 6:
            code = 'CAPR-NA'
            nummonths = 'two'
        if action == 8:
            code = 'PCT/DO/EO/923'

        try:
            activity = function_instance.getactivityid(matter_data, code)
            if action == 5:
                actname = 'Missing Parts with Corrected Application Papers Received'
            if action == 7:
                actname = 'Corrected Application Papers with Sequence Listing Action Received'
            else:
                actname = activity.name
        except:
            actname = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'activityName' : actname,
            'THIS.dueDate' : activity.smryonelabel,
        })
        return replace

class applicationdata_new2:
    def applicationdata_new2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        entries = mergeinfo[0]
        draw = mergeinfo[1]
        earlypub = mergeinfo[2]
        nopub = mergeinfo[3]
        mailclient = mergeinfo[4]
        mailapp = mergeinfo[5]
        smallent = mergeinfo[6]

        includeapp = mergeinfo[7]
        includenonapp = mergeinfo[8]
        noinclude = mergeinfo[9]
        includeboth = mergeinfo[10]

        esign = mergeinfo[11]
        esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[2])

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'drawingSheets' : draw,
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
        })
        return replace
        
class stateofallow:
    def stateofallow(self, matter, mergeinfo, keys):
            function_instance = mergefunctions.mergefunctions()
            matter_data = function_instance.matterFill(matter)
            esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[12])

            replace = {}
            depnum = function_instance.depnumFill(matter_data)
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update({
                'depAccount' : depnum,
                'signatureDate' : esigndate_out,
                'echoSignature' : esign_out,
                'allowType' : 'Notice of Allowability',
                'dateNALL' : date.today().strftime("%B %d, %Y"),
            })
            return replace
    
class appReportFp:
    def appReportFp(self, matter, mergeinfo, keys):
            function_instance = mergefunctions.mergefunctions()
            matter_data = function_instance.matterFill(matter)
            patent_data = function_instance.patentFill(matter_data)
            entitysize = patent_data.entitystatus
            signeddec = mergeinfo[0]
            efiled = mergeinfo[1]
            exmreq = mergeinfo[2]

            ReqPriorExam = "We have requested Prioritized Examination in this matter. Participation in Prioritized Examination assumes compliance with United States Patent Office procedures as outlined at http://www.uspto.gov/aia_implementation/faq.jsp#heading-9. "
                  
            if entitysize == 1:
                smallentitytext = "This patent application was filed claiming Small Entity Status.  If at any time you believe Small Entity Status should no longer be claimed, please notify us."
            else:
                smallentitytext = ''

            if signeddec == 'true':
                actionText = 'No action is required at this time.'
            else:
                actionText = "ACTION REQUIRED:  This application was filed without a declaration executed by the inventors.  Please discard any formal documents you may have received up until this point.  "
                actionText = actionText + "A new set of documents will be forwarded to you "
                if efiled == 'false':
                    actionText = actionText + 'upon receipt of the serial number.  '
                else:
                    actionText = actionText + 'in a separate communication to follow shortly.  '
    
            if exmreq == 'true':
                if smallentitytext == '':
                    ReqPriorExam = '  ' + ReqPriorExam
            else:
                ReqPriorExam = ''

            description = matter_data.mattertypedescription
            applicationType = ''
            if "DESIGN" in description:
                # Needs to be added to
                applicationType = 'Design Patent'
            if "CIP" in description:
                applicationType = 'Utility Continuation-in-Part Patent'
            if "CON" in description:
                applicationType = 'Utility Continuation Patent'
            if "DIV" in description:
                applicationType = "Utility Divisional Patent"

            replace = {}
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update({
                'smallEntity' : smallentitytext,
                'actionText' : actionText,
                'applicationType' : applicationType,
                'currentDate' : date.today(),
                'corrContactTitle' : '',
                'patentLink' : 'http://ca.slwip.com/slwdocs/applicationfiled.doc',
                'cReqPriorExam' : '',
                'salutation' : '',
                'recipient' : '',
                'CSZ' : '',
                'workAddr' : '',
                'cmgName' : '',
                'ccTag' : '',
                'ccName' : '',
                'enclosures' : '',
                'clientRefNo' : '',
            })
            return replace

class ownerchange:
    def ownerchange(self, matter, mergeinfo, keys):
            function_instance = mergefunctions.mergefunctions()
            esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[0])

            replace = {}
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update({
                'echoSignature' : esign_out,
                'signatureDate' : esigndate_out,
                'applicantName' : mergeinfo[2]

            })
            return replace
    
class corrappln:
    def corrappln(self,matter, mergeinfo, keys):
            function_instance = mergefunctions.mergefunctions()
            matter_data = function_instance.matterFill(matter)
            esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[6])
            efiling = mergeinfo[0]
            depacc = mergeinfo[1]
            extamt = mergeinfo[2]
            wenclosures = mergeinfo[7]

            SubX = ''
            AbsX = ''
            SeqX = ''
            FrmlX = ''

            SubPg = ''
            AbsPg = ''
            SeqPg = ''
            FrmlPg = ''
            if mergeinfo[2] != '' and int(mergeinfo[2]) > 0:
                SubX = 'X'
                SubPg = 'Substitute Specification (' + mergeinfo[2] + ' pg.).'
            if mergeinfo[3] != '' and int(mergeinfo[3]) > 0:
                AbsX = 'X'
                AbsPg = 'Abstract (' + mergeinfo[3] + ' pg.).'
            if mergeinfo[4] != '' and int(mergeinfo[4]) > 0:
                SeqX = 'X'
                SeqPg = 'Sequence Listing (' + mergeinfo[4] + ' pg.).'
            if mergeinfo[5] != '' and int(mergeinfo[5]) > 0:
                FrmlX = 'X'
                FrmlPg = 'Formal Drawings (' + mergeinfo[5] + ' pg.).'

            # Set months 1-5 based on extamt
            #if extamt > 0:

            depnum = function_instance.depnumFill(matter_data)

            replace = {}
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update(function_instance.firmfill())
            replace.update({
                'echoSignature' : esign_out,
                'signatureDate' : esigndate_out,
                'depAccount' : depnum,
                'SubX' : SubX,
                'AbsX' : AbsX,
                'SeqX' : SeqX,
                'FrmlX' : FrmlX,
                'SubstitutePg' : SubPg,
                'AbstractPg' : AbsPg,
                'SeqPg' : SeqPg,
                'FormalPg' : FrmlPg,
                'docList' : '',
                'nickU' : '',
                'dueDate' : '',
            })
            return replace
    
class missingpartsNw:
    def missingpartsNw(self, matter, mergeinfo, keys):
            function_instance = mergefunctions.mergefunctions()
            esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[0])
            combined = int(mergeinfo[6])
            decpages = int(mergeinfo[8])
            poapages = int(mergeinfo[7])
            appdatasheetpg = int(mergeinfo[9])
            submittext = ''
            if combined > 0:
                submittext = 'the Signed Combined Declaration and Power of Attorney, and '
            else:
                if decpages > 0 and poapages > 0:
                    submittext = 'the Signed Declaration and Signed Power of Attorney, and '
                if decpages > 0:
                    submittext = 'the Signed Declaration, and '
                if poapages > 0:
                    submittext = 'the Signed Power of Attorney, and '

            if appdatasheetpg > 0:
                markupComments = '[add update comments here]. '
                markupCopyA = ''
                markupCopyB = ''
            else:
                markupComments = '[add update comments here]. '
                markupCopyA = ''
                markupCopyB = ''
                

            replace = {}
            # replace.update(function_instance.assigneefill(keys, matter))
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update({

            })
            return replace
    
class rptissuefee:
    def rptissuefee(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        if mergeinfo[0] == 'FALSE':
            instructData = ''
            instDue = ''
            dateFiled = ''
        else: 
            dateFiled = 'No Issue Pay Date Found'
            instDue = 'No Issue Py Date Found'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            
        })
        return replace

# Not running
class adobesign:
    def adobesign(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        choice = 'Declaration'
        if mergeinfo[1] == 'true' or mergeinfo[3] =='true':
            choice = 'Assignment'
        if mergeinfo[2] == 'true':
            choice = 'Assignment and Declaration'
        if mergeinfo[4] =='true' or mergeinfo[5] =='true' or mergeinfo[6] =='true' or mergeinfo[7] =='true' or mergeinfo[8] =='true' or mergeinfo[9] =='true' or mergeinfo[10] =='true':
            choice = 'Assignment and POA'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'userChoice' : choice,
        })

class LtrSendFmlDocNew:
    def LtrSendFmlDocNew(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        patent_data = function_instance.patentFill(matter_data)

        if mergeinfo[6] == 'true':
            missingparts = 'We have received a Notice to File Missing Parts with a response date of <<mpresponsedate>>.  '

        if mergeinfo[4] == 'true':
            allowability = 'We have received a Notice of Allowability requiring the filing of the inventor Declarations with a response date of <<responseDueDate>>.  '
        
        if mergeinfo[0] == 'true' and mergeinfo[1] == 'true':
            assignDoc =  'We have also attached an Assignment document to be executed by the inventor(s).'
        
        if mergeinfo[0] == 'true' and mergeinfo[1] == 'false':
            assignDoc = 'Attached is an Assignment document to be executed by the inventor(s).'

        if mergeinfo[0] == 'false' and mergeinfo[1] == 'false':
            assignDoc = ' '

        if patent_data.entitystatus == 1:
            smallEntity = 'This patent application was filed claiming Small Entity Status.  If at any time you believe Small Entity Status should no longer be claimed, please notify us.'
        else:
            smallEntity = ''

        if mergeinfo[2] == 'true':
            assignDoc = assignDoc + '  Please note that the inventor(s) must sign and date the Assignment document in the presence of a Notary Public.  '
        

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            
        })
        return replace
    
class basicreport:
    def basicreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        actname = mergeinfo[0]
        actdate = mergeinfo[3]

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            
        })
        return replace

class ptorecdReport:
    def ptorecdReport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        actname = mergeinfo[0]
        actdate = mergeinfo[3]

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'dateMailed' : actdate,
            'docReceived' : actname,
        })
        return replace
    
class RepNoticeofAllow:
    def RepNoticeofAllow(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        entitystatus = function_instance.entityfill(matter)

        activity = function_instance.getactivityid(matter_data, 'NOAR')
        # noarDate = function_instance.extract_date(activity.smryonevalue)

        if(entitystatus == 0):
            billamt = '1,450.00'
        if(entitystatus == 2):
            billamt = '2,050.00'
        if(entitystatus == 1):
            billamt = '1,150.00'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'noar2Mo' : '',
            'noarLink' : 'http://ca.slwip.com/slwdocs/noticeofallowance.doc',
            'noar3Mo' : '',
            'noarDate' : activity.smryonevalue.strftime("%B %d, %Y"),
            'RETLANGUAGE' : '',
        })
        return replace
    
class PCTRptOutMiscItmsRcvd:
    def PCTRptOutMiscItmsRcvd(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))

        replace.update({
            
        })
        return replace

class recordedassnreport:
    def recordedassnreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        if mergeinfo[0]:
            recorddesc = mergeinfo[0]

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({

        })
        return replace

class reportprvassnnew:
    def reportprvassnnew(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({
            'salutation' : 'Inventor(s)',
            'recipient' : '',
        })
        return replace

class abandonReport:
    def abandonReport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({

        })
        return replace
    
class issuereport:
    def issuereport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        #if mergeinfo[0] == 'TRUE':

        #else:


        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : 'Inventor(s)'
        })
        return replace

class pctcorrect:
    def pctcorrect(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        depacc = mergeinfo[0]
        check = mergeinfo[1]
        esign = mergeinfo[2]
        maildate = mergeinfo[3]
        SignAtt = mergeinfo[4]
        exttime = mergeinfo[5]
        annexA = mergeinfo[7]
        annexAtxt = mergeinfo[8]
        annexB = mergeinfo[9]
        descpg = mergeinfo[10]
        claimpg = mergeinfo[11]
        abspg = mergeinfo[12]
        annexC = mergeinfo[13]
        formalpg = mergeinfo[14]

        if annexA == 'true':
            Atxt = annexAtxt + 'which is believed to be in compliance with Annex A of the Invitation.'
        else:
            Atxt = ''

        if annexB == 'true':
            Btxt = 'Replacement description pages ' + descpg + ', replacement claims pages ' + claimpg + ' and replacement claims pages ' + abspg + ' which are believed to be in compliance with Annex B1 of the Invitation.'
        else:
            Btxt = ''

        if annexC == 'true':
            Ctxt = 'Formal drawing sheets (' + formalpg + ') which are all believed to be in compliance with Annex C1 of the Invitation.'
        else:
            Ctxt = ''

        esign_out, esigndate_out = function_instance.esigncheck(esign)
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'mailDate' : maildate,
            # add phone number at end
            'cAnnexAText' : Atxt,
            'cAnnexBText' : Btxt,
            'cAnnexCText' : Ctxt,
            'properApplicant' : 'Applicant',
            'encloseText' : 'enclose',
            'depAccount' : function_instance.depnumFill(matter_data),
        })
        return replace

class applicationdata_new2:
    def applicationdata_new2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update(function_instance.applicantfill(matter, 1))
        replace.update({
            
        })
        return replace
    
class pctextention:
    def pctextention(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        esign = mergeinfo[2]

        esign_out, esigndate_out = function_instance.esigncheck(esign)

        annexes = []

        if mergeinfo[7] == 'true':
            annexes.append('Annex A')

        if mergeinfo[9] == 'true':
            annexes.append('Annex B')

        if mergeinfo[13] == 'true':
            annexes.append('Annex C')

        if len(annexes) == 2:
            annexTxt = ' and '.join(annexes)
        elif len(annexes) > 2:
            annexTxt = ', '.join(annexes[:-1]) + ', and ' + annexes[-1]
        else:
            annexTxt = ''.join(annexes)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'extensionLenTextHdr' : function_instance.number_to_words(int(mergeinfo[6])),
            'mailDate' : mergeinfo[3],
            'properApplicant' : 'Applicant',
            'extensionLenText' : function_instance.number_to_words(int(mergeinfo[6])).lower(),
            'requestText' : 'requests',
            'annexSelectText' : annexTxt,
        })
        return replace

class nonfinalreportFp:
    def nonfinalreportFp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'cReqPriorExam' : 'We have requested Prioritized Examination in this matter. '
        })
        return replace

# mergeinfo data not transfering correctly
class PCTAsgnPOALetter:
    def PCTAsgnPOALetter(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        sendingpoa = ''
        if mergeinfo[2] == 'true':
            sendingpoa = 'We have also enclosed a Power of Attorney document for the assignee.'

        if mergeinfo[1] == 'true':
            sendingpoa = sendingpoa + "This Power of Attorney needs to be signed by an officer of the organization or a person empowered to sign on the organization's behalf."
 
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'pctdueDate' : mergeinfo[0],
            'cSendingPOA' : sendingpoa,
            'Notary' : '',
        })
        return replace
    
class RptInvtPayFees:
    def RptInvtPayFees(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        tabledata = mergeinfo[2]

        pairs = tabledata.split('^')

        # Initialize arrays for keys and values
        keys = []
        values = []

        # Split each pair by '*' and add to respective arrays
        for pair in pairs:
            key, value = pair.split('*')
            keys.append(key)
            values.append(value)

        # Convert arrays to strings
        groups = '\n '.join(keys)
        claims = '\n                '.join(values)

        partial = ''
        if mergeinfo[0] == 'true':
            partial = 'and a Communication Regarding the Results of the Partial International Search'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'claimAmt' : mergeinfo[1],
            'partialSearch' : partial,
            'groupNbr' : '',
            'citedCopies' : '',
            'groupNbr' : groups,
            'claims' : claims,
            'npdueDate' : '',
            
        })
        return replace

class PctCommRe:
    def PctCommRe(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        depnum = function_instance.depnumFill(matter_data)
        esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[7])

        if int(mergeinfo[4]) > 0:
            seqpaper = 'Sequence Listing on Paper (' + mergeinfo[4] + ' pgs).'
            lpX = 'X'
        else:
            seqpaper = ''
            lpX = ''

        cdX = ''
        Xdepacc = ''
        if float(mergeinfo[6]) > 0:
            Xdepacc = 'Please charge Deposit Account ' + depnum + ' in the amount of $' + mergeinfo[6]
            cdX = 'X'

        title = ''
        pctadd = ''
        currency = ''
        if mergeinfo[9] == 'EP(n)':
            title = 'In the European Patent Office'
            currency = 'Euro '
            pctadd = 'European Patent Office\nP.B. 5818 Patentlaan 2\nNL-2880 HV Rijswijk\nNETHERLANDS'
        if mergeinfo[9] == 'EP(g)':
            title = 'In the European Patent Office'
            currency = 'Euro '
            pctadd = 'European Patent Office\n27 Erhardtstrasse\nD-80298 Munich\nGERMANY'
        if mergeinfo[9] == 'US':
            title = 'IN THE UNITED STATES PATENT AND TRADEMARK OFFICE'
            currency = '$ '
            pctadd = 'Mail Stop PCT\nCommissioner of Patents\nP.O. Box 1450\nAlexandria, VA 22313-1450'
        if mergeinfo[9] == 'KR':
            title = 'In the Korean Intellectual Property Office'
            currency = 'KRW '
            pctadd = 'Korean Intellectual Property Office\nGovernment Complex Daejeon\n189 Cheongsa-ro,\nSeo-gu\nDaejeon 302-701\nRepublic of Korea'
        if mergeinfo[9] == 'IB':
            title = 'In The International Bureau of WIPO'
            currency = 'CHF '
            pctadd = 'The International Bureau of WIPO\n34, Chemin Des Colombettes\n1211 Geneva 20\nSWITZERLAND'
        if mergeinfo[9] == 'AU':
            title = 'In the Australian Patent Office'
            currency = 'AUD '
            pctadd = 'Australian Patent Office\nDiscovery House\n47 Bowes Street, Phillip\nCanberra A.C.T. 2606, Australia'
        if mergeinfo[9] == 'RU':
            title =  'Russian Federation - Federal Service for Intellectual Property'
            currency = 'RUB '
            pctadd = 'Russian Federation - Federal Service for Intellectual Property\nROSPATENT\nBerezhkovskaya nab, 30/1\nMoscow 123995\nRussian Federation'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'mailDate' : mergeinfo[3],
            'lpX' : lpX,
            'seqListingLine' : seqpaper,
            'rfX' : '',
            # 'seqRFLine' : mergeinfo[9],
            'cdX' : cdX,
            'inthePatentOffice' : title,
            'chgDepAcct' : Xdepacc,
            'selSAName' : '',
            'depAccountLine' : 'Please charge any additional required fees or credit overpayment to Deposit Account ' + depnum + '.',
            'pctAddress' : pctadd,
            'tvUSPSDHL' : '',
        })
        return replace
    
class PCTRptFileOfApp:
    def PCTRptFileOfApp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        recoffice = mergeinfo[0]
        searchingauth = mergeinfo[1]
        if mergeinfo[2] != '':
            exclusion = 'The application designated all PCT contracting states except ' + mergeinfo[2] +'. The exclusion of this designation prevents the priority application from becoming abandoned, in accordance with country law.<br>'
        else:
            exclusion = 'The application designated all PCT contracting states.\n'

        selserial = mergeinfo[3].replace('*', ',').replace(';','\n')
        seldate = mergeinfo[4].replace('*', ',').replace(';','\n')
        selcountry = mergeinfo[5].replace('*', ',').replace(';','\n')

        rows = zip(selserial.split('\n'), seldate.split('\n'), selcountry.split('\n'))
        formatted_data = "\n".join(["\t\t\t".join(row) for row in rows])

        prapp = 'The PCT application claims priority to the following earlier-filed application(s):'

        action = 'ACTION REQUIRED:'
        action = action + ' None at this time.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'priorAppNo' : formatted_data,
            'priorAppDate' : '',
            'priorAppCntry' : '',
            'crcvOffice' : recoffice,
            'cpatentOffice' : searchingauth,
            'excluDesigPhs' : exclusion,
            'actionText' : action,
            'cpriorApps' : prapp
        })
        return replace
    
class applicationdata_updnew:
    def applicationdata_updnew(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        #replace.update(function_instance.inventorInfo(matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update(function_instance.applicantfill(matter, 1))
        replace.update({
            'pageDraw' : mergeinfo[3],
            # get update tag
            '' : mergeinfo[6]
        })
        return replace

class nopreport:
    def nopreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        patent = function_instance.patentFill(matter_data)
        pubno = patent.pubno
        pubdate = patent.pubdate

        replace = {}
        replace.update(function_instance.WAfill(keys, matter))
        replace.update({
            'pubNo' : pubno,
            'pubDate' : pubdate,
            'salutation' : '',
             
        })
        return replace

class foarreport:
    def foarreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace

class generalxmitCF:
    def generalxmitCF(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[0])

        mailstop = 'Mail Stop Amendment'
        aftFinal = ''
        aftFinalX = ''
        terminal = ''
        terminalX = ''
        formal = ''
        formalX = ''
        ids = ''
        idsX = ''
        mainX = ''
        main = ''
        comm = ''
        commX = ''
        if mergeinfo[8] != '' and int(mergeinfo[8]) > 0:
            aftFinal = 'After Final Consideration Program Request (' + mergeinfo[8] + ' pg.)'
            aftFinalX = 'X'
        if mergeinfo[21] != '' and int(mergeinfo[21]) > 0:
            terminal = 'Terminal Disclaimer (' + mergeinfo[21] + ' pgs.)'
            terminalX = 'X'
        if mergeinfo[20] != '' and int(mergeinfo[20]) > 0:
            formal = 'Formal Drawings (' + mergeinfo[21] + ' pgs.)'
            formalX = 'X'
        if mergeinfo[13] != '' and mergeinfo[14] != '' and int(mergeinfo[13]) > 0 and int(mergeinfo[14]) > 0:
            ids = 'Supplemental Information Disclosure Statement ('+ mergeinfo[13] +' pgs.), Form 1449 ('+ mergeinfo[14] +' pgs.)  Documents NOT enclosed, cited in parent application'
            idsX = 'X'
        if mergeinfo[5] != '' and int(mergeinfo[5]) > 0:
            main = 'Amendment and Response under 37 C.F.R. § 1.111 (' + mergeinfo[5] + ' pgs.)'
            mainX = 'X'
        if mergeinfo[19] != '' and int(mergeinfo[19]) > 0:
            comm = 'Communication Concerning Prior and Copending Applications ('+ mergeinfo[19] +' pgs.)'
            commX = 'X'
        #if mergeinfo[19] != '' and int(mergeinfo[19]) > 0:
        #    extention = 'Petition for Extension of Time ('+ mergeinfo[19] +' pgs.)'
        #    extX = 'X'
        if mergeinfo[2] == '1':
            dep = 'Authorization to charge Deposit Account <<depAccount>> in the amount of'
        if mergeinfo[2] == '2':
            dep = 'A check in the amount of'
        if mergeinfo[2] == '3':
            dep = 'Authorization to charge the credit card (details provided herewith) in the amount of'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'mailStopText' : mailstop,
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'afterFinalX' : aftFinalX,
            'afterFinalText' : aftFinal,
            'terminalX' : terminalX,
            'terminalText' : terminal,
            'idsX' : idsX,
            'idsText' : ids,
            'mainX' : mainX,
            'mainDocText' : main,
            'claimsAfter' : mergeinfo[8],
            'indAfter' : mergeinfo[10],
            'commText' : comm,
            'commX' : commX,
            'drawText' : formal,
            'drawX' : formalX,

        })
        return replace
    
class filerectreportNw2:
    def filerectreportNw2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        try:
            activity = function_instance.getactivityid(matter_data, 'FECT')

        except:
            activity = ''

        addnotes = mergeinfo[0] + mergeinfo[1]
        count = 0
        if mergeinfo[3] == 'true' or mergeinfo[4] == 'true':
            addnotes += 'We have also received'
            if mergeinfo[3] == 'true':
                addnotes += ' an Informational Notice to Applicant'
                count = count + 1
            if mergeinfo[4] == 'true':
                if count > 0:
                    addnotes += ' and a Notice of Acceptance'
                else:
                    addnotes += ' a Notice of Acceptance'
        
        addnotes += '. No action is required at this time; we will contact you if we require additional information.'

        description = matter_data.mattertypedescription
        if "PROV" in description:
            # insert filedate
            addnotes = addnotes + " This Provisional patent application will expire one year from the filing date.  If a regular (non-provisional) U.S. application is not filed by " + ", the ability to claim priority to the filing date of the provisional application will be lost."

        receiptType = mergeinfo[2]
        

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'additionalNotes' : addnotes,

        })
        return replace
    
class PatentCoopTreaty2:
    def PatentCoopTreaty2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        patent_data = function_instance.patentFill(matter_data)

        dates = [patent_data.pctappno, patent_data.pctappdate, patent_data.pctpubno, patent_data.pctpubdate, patent_data.prioritydate]
        valid_dates = [date for date in dates if date not in [None, '']]
        priority = min(valid_dates)

        poatype = ''
        if mergeinfo[15] == 'true':
            poatype = 'General POA'

        if mergeinfo[14] == 'true':
            poatype = 'Separate POA'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        try:
            replace.update(function_instance.applicantfill(matter, 1))
        except:
            applicantName = ''
        replace.update({
            'requestFormSheets' : mergeinfo[6],
            'descriptionSheets' : mergeinfo[7],
            'claimSheets' : mergeinfo[8],
            'abstractSheets' : mergeinfo[9],
            'drawingSheets' : mergeinfo[10],
            'seqListSheets' : mergeinfo[11],
            'poapages' : mergeinfo[12] + ' ',
            'priorityDate' : priority,
            'selSAName' : mergeinfo[5],
            'applicantName' : applicantName,
            'addlDocs' : '',
            'poatype' : poatype
        })
        return replace
    
class PctSearchRep:
    def PctSearchRep(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        # Need to fix doc
        replace.update({
            '19duedate' : mergeinfo[0],
            '34duedate' : mergeinfo[1],
            '30mduedate' : mergeinfo[3],
        })
        return replace
    
class PCTRptOutIpRp:
    def PCTRptOutIpRp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        try:
            activity = function_instance.getactivityid(matter_data, 'NPAD')
            pcta = True
        except:
            pcta = False

        if pcta:
            if activity.smryonevalue:
                npdueDate = activity.smryonevalue

        # Need to add action notes and attorney info
        action = 'ADDITIONAL NOTES:  Please contact if you would like to discuss this matter more fully, or if you need a cost estimate for filing in specific countries/regions.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'actionRequired' : action,
        })
        return replace

class idsCommCfNew:
    def idsCommCfNew(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        filing = mergeinfo[0]
        feemethod = mergeinfo[1]
        filingstatus = mergeinfo[2]
        offaction = mergeinfo[3]
        offaction2 = mergeinfo[4]

        sup = ''
        if offaction2 == '1':
            sup = 'UNDER 37 C.F.R §1.97(e)(1)'
        if offaction2 == '2':
            sup = 'UNDER 37 C.F.R §1.97(e)(2)'
        if offaction2 == '3':
            sup = 'UNDER 37 CFR 1.97(i)'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'mailStopText' : mergeinfo[12],
            'supplText' : '',
            'supplementalText' : '',
        })
        return replace

class idsmemo:
    def idsmemo(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        actionrec = mergeinfo[0]
        blank = mergeinfo[1]
        moduedate = mergeinfo[2]  

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace

class utilityapp:
    def utilityapp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        esign = mergeinfo[28]
        esign_out, esigndate_out = function_instance.esigncheck(esign)
        entitystatus = function_instance.entityfill(matter)

        drawx = ''
        drawtxt = ''
        signx = ''
        signtxt = ''
        priorsignx = ''
        priorsigntxt = ''
        invx = ''
        invtxt = ''
        poax = ''
        poatxt = ''
        smallx = ''
        smalltxt = ''
        prelimx = ''
        prelimtxt = '' 
        compriorx = ''
        compriortxt = '' 
        if mergeinfo[8] != '' and int(mergeinfo[8]) > 0:
            drawx = 'X'
            drawtxt = 'Formal Drawing(s) ('+ mergeinfo[8] +' sheets).'
        if mergeinfo[17] != '' and int(mergeinfo[17]) > 0:
            signx = 'X'
            signtxt = 'Copy of Signed Declaration ('+ mergeinfo[17] +' pgs).'
        if mergeinfo[25] != '' and int(mergeinfo[25]) > 0:
            priorsignx = 'X'
            priorsigntxt = 'Copy of Signed Declaration ('+ mergeinfo[25] +' pgs) from prior application.'
        if mergeinfo[26] != '' and int(mergeinfo[26]) > 0:
            invx = 'X'
            invtxt = 'Deletion of Inventors:  Signed statement deleting inventor(s) named in the prior application ('+ mergeinfo[26] +' pgs).'
        if mergeinfo[27] != '' and int(mergeinfo[27]) > 0:
            poax = 'X'
            poatxt = 'Power of Attorney  ('+ mergeinfo[27] +' pgs).'  
        if mergeinfo[20] != '' and int(mergeinfo[20]) > 0:
            prelimx = 'X'
            prelimtxt = 'Preliminary Amendment ('+ mergeinfo[20] +' pgs).'  
        if mergeinfo[22] != '' and int(mergeinfo[22]) > 0:
            compriorx = 'X'
            compriortxt = 'Communication Concerning Prior and Copending Applications ('+ mergeinfo[22] +' pgs).' 
        if mergeinfo[13] != '' and int(mergeinfo[13]) > 0 and  mergeinfo[15] != '' and int(mergeinfo[15]) > 0:
            idsx = 'X'
            idstxt = 'Information Disclosure Statement ('+ mergeinfo[13] +' pgs), Form 1449 ('+ mergeinfo[15] +' pgs), and copies of cited references (7).' 
        
        if entitystatus == 1:
            smallx = 'X'
            smalltxt = 'Applicant claims small entity status under 37 CFR 1.27.'
        

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'appTypeText' : 'Utility Patent Application under 37 CFR 1.53(b) comprising:',
            'docx' : 'DOCX',
            'specPages' : mergeinfo[4],
            'claimTotal' : mergeinfo[6],
            'drawX' : drawx,
            'drawText' : drawtxt,
            'signDecX' : signx,
            'signDecPagesText' : signtxt,
            'decX' : priorsignx,
            'decText' : priorsigntxt,
            'inventX' : invx,
            'inventText' : invtxt,
            'poaX' : poax,
            'poaText' : poatxt,
            'smallentityX' : smallx,
            'smallentityText' : smalltxt,
            'preliminaryX' : prelimx,
            'preliminaryText' : prelimtxt,
            'relatedX' : compriorx,
            'relatedText' : compriortxt,
        })
        return replace

class assignment2016:
    def assignment2016(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace
    
class ffOfficeActRcvd:
    def ffOfficeActRcvd(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

        typeaction = mergeinfo[0]
        deadline = mergeinfo[1]
        reqresp = mergeinfo[2]
        citedref = mergeinfo[3]
        if citedref == 'true' and typeaction != '':
            cite = ' and cited references '
        if citedref == 'true' and typeaction == '':
            cite = ' cited references '

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'cdueDate' : deadline,
            'crespDate' : reqresp,
            'actionType' : typeaction,
            'citedRef' : cite,
        })
        return replace

class mrgfforder:
    def mrgfforder(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace
    
class DraftOAInstruct:
    def DraftOAInstruct(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'corrDate' : mergeinfo[0],
            'cdueDate' : mergeinfo[1],
            # Need to edit country
            'countryType' : 'American',
            'matterCountryName' : 'United States of America'
        })
        return replace

class exttimeCF:
    def exttimeCF(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        depnum = function_instance.depnumFill(matter_data)
        esign = mergeinfo[0]
        esign_out, esigndate_out = function_instance.esigncheck(esign)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'extLength' : mergeinfo[11].upper(),
            'depCheckText' : 'Please charge Deposit Account No. '+ depnum +' ',
            'feeAmount' : mergeinfo[1],
            'enclosed' : '',
            'depAccount' : depnum,
            'extLengthL' : mergeinfo[11].lower(),
            'mailstopText' : mergeinfo[7],
            'extResponse' : mergeinfo[8],
            'dateMailed' : datetime.strptime(mergeinfo[9], '%m/%d/%Y').strftime('%B %d, %Y'),
            'dueDate' : datetime.strptime(mergeinfo[10], '%m/%d/%Y').strftime('%B %d, %Y'),
            'newDate' : function_instance.newDate(mergeinfo[11], mergeinfo[10]),
            'petitionText' : '',
        })
        return replace

# Only need dueDate
class incorrectfilerect:
    def incorrectfilerect(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        esign = mergeinfo[0]
        esign_out, esigndate_out = function_instance.esigncheck(esign)
        depnum = function_instance.depnumFill(matter_data)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'depAccount' : depnum,
            'nickU' : '',
            'postcardX' :'',
            'postcardText' : '',
            'dueDate' : '',
        })
        return replace
    
# Need to fix SARegNo - will not fill with mergebasic
class corrinventorship:
    def corrinventorship(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        esign = mergeinfo[0]
        esign_out, esigndate_out = function_instance.esigncheck(esign)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'depAccount' : function_instance.depnumFill(matter_data),
        })
        return replace

# e-signature and SA data not filling correctly.
class corrapplicant:
    def corrapplicant(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        esign = mergeinfo[0]
        esign_out, esigndate_out = function_instance.esigncheck(esign)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
        })
        return replace

# Need small changes. clientreftxt and inventor info
class pctdeclaration2:
    def pctdeclaration2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        esign = mergeinfo[0]
        esign_out, esigndate_out = function_instance.esigncheck(esign)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.inventorInfo(matter , 1))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'clientRefText' : '',
        })
        return replace

class rcexmit3:
    def rcexmit3(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        esign = mergeinfo[2]
        esign_out, esigndate_out = function_instance.esigncheck(esign)

        aarfx = ''
        aarftxt = ''
        abrfx = ''
        abrftxt = ''
        amendx = ''
        amendtxt = ''
        idsx = ''
        idstxt = ''
        ccpx = ''
        ccptxt = ''
        if mergeinfo[5] != '':
            aarfx = 'X'
            aarftxt = 'Consider the amendment(s)/reply under 37 C.F.R. § 1.116 previously filed on ' + mergeinfo[5]
        if mergeinfo[6] != '':
            abrfx = 'X'
            abrftxt = 'Consider the arguments in the Appeal Brief or Reply Brief previously filed on ' + mergeinfo[6]
        if mergeinfo[7] != '' and int(mergeinfo[7]) > 0:
            amendx = 'X'
            amendtxt = 'Amendment and Response Under 37 C.F.R § 1.116 ('+ mergeinfo[7] +' pages) is enclosed.'
        if mergeinfo[19] != '' and int(mergeinfo[19]) > 0:
            ccpx = 'X'
            ccptxt = 'Communication Concerning Prior or Copending Applications ('+ mergeinfo[19] +' pgs).'

        fee = ''
        if mergeinfo[1] == '1':
            deptxt = 'Subject to the conditions of the QPIDS Pilot Program as stated above: Authorization to charge deposit account 19-0743 in the amount of '+ fee +' to pay the RCE filing fee required under 37 CFR § 1.17(e)(2).'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'aarfX' : aarfx,
            'aarfText' : aarftxt,
            'abrfX' : abrfx,
            'abrfText' : abrftxt,
            'amendX' : amendx,
            'amendText' : amendtxt,
            'ccpX' : ccpx,
            'ccpText' : ccptxt,
            'depCheckText' : deptxt
        })
        return replace
    
class pctgeneric:
    def pctgeneric(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        esign = mergeinfo[3]
        esign_out, esigndate_out = function_instance.esigncheck(esign)

        deptxt = ''
        pctaddr = ''
        if mergeinfo[0] == 'ger':
            pctaddr = 'European Patent Office\nErhardtstrasse 27\nD-80298 Munich\nGERMANY'
            deptxt = 'Please charge any deficiency in fees or credit overpayment to Deposit Account 2830 0215.'
        if mergeinfo[0] == 'sw':
            pctaddr = 'The International Bureau of WIPO\n34, Chemin des Colombettes\n1211 Geneva 20\nSWITZERLAND'
        if mergeinfo[0] == 'va':
            pctaddr = 'Mail Stop PCT\nCommissioner of Patents\nP.O. Box 1450\nAlexandria, VA 22313-1450'
        if mergeinfo[0] == 'kor':
            pctaddr = 'PCT Part, International Application Team\nKorean Intellectual Property Office\nGovernment Complex-Daejeon\n189 Cheongsa-ro\nSeo-gu\nDaejeon 302-701\nRepublic of Korea'
        if mergeinfo[0] == 'net':
            pctaddr = 'European Patent Office\nP.B. 5818 Patentlaan 2\nNL-2280 HV Rijswijk\nNETHERLANDS'
            deptxt = 'Please charge any deficiency in fees or credit overpayment to Deposit Account 2830 0215.'

        replace = {}
        try:
            replace.update(function_instance.assigneefill(matter, 1))
        except:
            pass

        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'headerText' : mergeinfo[1],
            'pctAddress' : pctaddr,
            'depositText' : deptxt,
            'SAName' : mergeinfo[2],
        })
        return replace