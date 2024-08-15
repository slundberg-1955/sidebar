from ..mergemethods import mergefunctions
from ..models import Activity
from datetime import date

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

        SAPhone = function_instance.phoneFill(matter_data)

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
            'SAPhone' : SAPhone,
            'feeAmount' : billamt,
            'depAccount' : depnum,
        })
        return replace
    
class pclaims:
    def pclaims(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        matter_data = function_instance.matterFill(matter)
        inventor_data = function_instance.inventorFill(matter_data)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'clientRefNo' : '',
            'assignee' : '',
            'claimsDate' : mergeinfo[0],
            'dateDescription' : mergeinfo[1],
        })
        return replace

class issuefee:
    def issuefee(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        dep = mergeinfo[0]
        check = mergeinfo[1]
        reqpat = mergeinfo[2]
        numfact = mergeinfo[3]
        drawnum = mergeinfo[4]
        prevpaid = mergeinfo[6]
        prevpaiddate = mergeinfo[7]
        withfiled = mergeinfo[8]
        withmailed = mergeinfo[9]
        amtinc = mergeinfo[10]
        amtfrstpay = mergeinfo[11]
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
        

        esign_out, esigndate_out = function_instance.esigncheck(esign)
        depnum = function_instance.depnumFill(matter_data)
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'custNoCorresp' : '',
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'upperFirmName' : '',
            'SAPhone' : '',
            'nickSA' : '',
            'nickU' : '',
            'dateIssueFee': prevpaiddate,
            'withDrawText' : '',
            'increaseText' : '',
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
            'feeTextX' : '',
            'FeeText' : '',
            'pubFeeX' : '',
            'pubFeeText' : '',
            'previousX' : '',
            'applyPreviousText' : '',
            'commentX' : '',
            'commentText' : '',
            'dueDate' : dateIssueFee,
        })
        return replace
    
class Statement373c:
    def Statement373c(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        filing = mergeinfo[0]
        account = mergeinfo[1]
        requestpat = mergeinfo[2]
        pagedraw = mergeinfo[3]
        mrgexam = mergeinfo[4]
        isspaid = mergeinfo[5]
        esign = mergeinfo[6]
        
        esign_out, esigndate_out = function_instance.esigncheck(esign)
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
        })
        return replace
    
# update  
class recordation:
    def recordation(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        depnum = function_instance.depnumFill(matter_data)



        replace = {}
        esign_out, esigndate_out = function_instance.esigncheck('true')
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(keys, matter))
        replace.update({
            'SAName' : '',
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'depAccount' : depnum,
            'dateExecutionText' : '',
            'selectedInventorList' : mergeinfo[0],
            'totalFee' : '',
            'numPages' : mergeinfo[1],
            'depAcctX' : '',
            'checkX' : '',
        })
        return replace

class LateSubmissionOfDec:
    def LateSubmissionOfDec(self, matter, mergeinfo, keys):
        paid = mergeinfo[0]
        pageDec = mergeinfo[1]
        pageSub = mergeinfo[2] 
        esign = mergeinfo[3]
        
        function_instance = mergefunctions.mergefunctions()
        esign_out, esigndate_out = function_instance.esigncheck(esign)
        replace = {}

        # Fill Data
        matter_data = function_instance.matterFill(matter)
        inventor_data = function_instance.inventorFill(matter_data)
        patent_data = function_instance.patentFill(matter_data)

        SAPhone = function_instance.phoneFill(matter_data)

        depnum = function_instance.depnumFill(matter_data)
        artunitno = patent_data.artunitno
        custcor = function_instance.corrcustnumFill(matter_data)
        confirm = matter_data.confirmationno

        if(custcor == ''):
            custcor = 'Unknown'
        if(artunitno == '' or artunitno == 'None'):
            artunitno = 'Unknown'
        if(confirm == ''):
            confirm = 'Unknown'
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'SAPhone' : SAPhone,
            'depAccount' : depnum,
            'pgs' : pageDec,
            'subX' : '',
            'subText' : '',
            'firmName' : '',
            'nickSA' : '',
            'nickU' : '',
            'latePaid': '',
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

        
        replace.update({
            'This.orgName' : org_data.orgname,
            'This.clientRefNo' : '',
            'This.matterNo' : matter_data.hostmatterno,
            'activityname' : '',
            'This.WAName' : '',
            'This.WAPhone' : '',
            'THIS.WAName' : '',
            'THIS.WAPhone' : '',
            'This.WAEmail' : '',
            'This.paraName' : '',
            'This.paraPhone' : '',
            'This.paraEmail' : '',
            'This.serialNo' : function_instance.transform_serialnumber(matter_data.serialnumber),
            'This.filedDate' : matter_data.fileddate.strftime("%B %d, %Y"),
            'THIS.patNo' : patent_data.patentno,
            'THIS.issueDate' : patent_data.issuedate,
            'THIS.title'  : matter_data.title,
            'This.title'  : matter_data.title,
            'designText' : '',
            'utilityText1' : utilityText1,
            'cutilityText2' : '',
            'utilityFee1' : utilityFee1,
            'utilityFee2' : utilityFee2,
            'utilityFee3' : utilityFee3,
            'cutilityText2' : '',
        })
        return replace
    
class capactions:
    def capactions(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        radio = mergeinfo[0]
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
                
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
            replace = {}
            depnum = function_instance.depnumFill(matter_data)
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update({
                'depAccount' : depnum,
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

            # Need to add ereport

            replace = {}
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update(function_instance.parafill(keys, matter))
            replace.update(function_instance.WAfill(keys, matter))
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
            esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[8])
            efiling = mergeinfo[0]
            paperfiling = mergeinfo[1]
            depacc = mergeinfo[2]
            extamt = mergeinfo[3]
            subspec = mergeinfo[4]
            abstract = mergeinfo[5]
            seqlist = mergeinfo[6]
            formaldraw = mergeinfo[7]
            wenclosures = mergeinfo[9]

            # Set months 1-5 based on extamt
            #if extamt > 0:


            depnum = function_instance.depnumFill(matter_data)

            replace = {}
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'depAccount' : depnum,

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
            replace.update(function_instance.assigneefill(keys, matter))
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
        replace.update(function_instance.mergebasicEmail(keys, matter))
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
        replace.update(function_instance.mergebasicEmail(keys, matter))
        # replace.update(function_instance.parafill(keys, matter))
        # replace.update(function_instance.WAfill(keys, matter))
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
        replace.update(function_instance.mergebasicEmail(keys, matter))
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
        replace.update(function_instance.mergebasicEmail(keys, matter))
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
        replace.update(function_instance.mergebasicEmail(keys, matter))
        replace.update(function_instance.assigneefill(keys, matter))
        replace.update(function_instance.parafill(keys, matter))
        replace.update(function_instance.WAfill(keys, matter))
        replace.update({

        })
        return replace

class reportprvassnnew:
    def reportprvassnnew(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.mergebasicEmail(keys, matter))
        replace.update(function_instance.assigneefill(keys, matter))
        replace.update(function_instance.parafill(keys, matter))
        replace.update(function_instance.WAfill(keys, matter))
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
        replace.update(function_instance.mergebasicEmail(keys, matter))
        replace.update(function_instance.assigneefill(keys, matter))
        replace.update(function_instance.parafill(keys, matter))
        replace.update(function_instance.WAfill(keys, matter))
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
        replace.update(function_instance.mergebasicEmail(keys, matter))
        replace.update(function_instance.parafill(keys, matter))
        replace.update(function_instance.WAfill(keys, matter))
        replace.update({
            'salutation' : 'Inventor(s)'
        })
        return replace

class pctcorrect:
    def pctcorrect(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        SAPhone = function_instance.phoneFill(matter_data)
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
            'SAPhone' : SAPhone,
        })
        return replace

class applicationdata_new2:
    def applicationdata_new2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
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
            'annexSelectText' : annexTxt
        })
        return replace

class nonfinalreportFp:
    def nonfinalreportFp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.parafill(keys, matter))
        replace.update(function_instance.WAfill(keys, matter))
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
        replace.update(function_instance.parafill(keys, matter))
        replace.update(function_instance.WAfill(keys, matter))
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

        tabledata = mergeinfo[5]

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
        if mergeinfo[3] == 'true':
            partial = 'and a Communication Regarding the Results of the Partial International Search'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.parafill(keys, matter))
        replace.update(function_instance.WAfill(keys, matter))
        replace.update({
            'claimAmt' : mergeinfo[4],
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
        esign_out, esigndate_out = function_instance.esigncheck(mergeinfo[8])

        #if int(mergeinfo[5]) > 0:
        #    seqpaper = 'Sequence Listing on Paper (' + mergeinfo[5] + ' pgs).'
        #    lpX = 'X'
        #else:
        #    seqpaper = ''
        #    lpX = ''

        #cdX = ''
        #Xdepacc = ''
        #if float(mergeinfo[7]) > 0:
        #    Xdepacc = 'Please charge Deposit Account ' + depnum + ' in the amount of $' + mergeinfo[7]
        #    cdX = 'X'

        title = 'In the '
        if mergeinfo[0] == 'EP(n)':
            title += 'European Patent Office'
        if mergeinfo[0] == 'EP(g)':
            title += 'European Patent Office'
        if mergeinfo[-1] == 'US':
            pctadd = 'Mail Stop PCT\nCommissioner of Patents\nP.O. Box 1450\nAlexandria, VA 22313-1450'
        if mergeinfo[0] == 'KR':
            title += 'Korean Intellectual Property Office'
        if mergeinfo[0] == 'IB':
            title += 'The International Bureau of WIPO'
        if mergeinfo[0] == 'AU':
            title += 'Australian Patent Office'
        if mergeinfo[0] == 'RU':
            title +=  'Russian Federation - Federal Service for Intellectual Property'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'echoSignature' : esign_out,
            'signatureDate' : esigndate_out,
            'mailDate' : mergeinfo[1],
            'lpX' : lpX,
            'seqListingLine' : seqpaper,
            'rfX' : '',
            # 'seqRFLine' : mergeinfo[9],
            'cdX' : cdX,
            'inthePatentOffice' : title,
            'chgDepAcct' : Xdepacc,
            'selSAName' : mergeinfo[9],
            'depAccountLine' : 'Please charge any additional required fees or credit overpayment to Deposit Account ' + depnum + '.',
            'pctAddress' : pctadd,
        })
        return replace
    
class PCTRptFileOfApp:
    def PCTRptFileOfApp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        recoffice = mergeinfo[0]
        searchingauth = mergeinfo[1]

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace