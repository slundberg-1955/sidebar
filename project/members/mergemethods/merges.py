import webbrowser
from ..mergemethods import mergefunctions
from ..models import Activity, Task, Rvwactivitydateattribute, Relatedmatter, Docketentry, Task, FvMatter4, Trademark
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Q

# Transmittal - Communication Appeal Forwarding Fee
class appealfwd:
    def appealfwd(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        entitystatus = function_instance.entityfill(matter)
        replace = {}

        # Fill Data
        matter_data = function_instance.matterFill(matter)
        patent_data = function_instance.patentFill(matter_data)

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
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'feeAmount' : billamt,
            'depAccount' : function_instance.depnumFill(matter_data),
        })
        return replace
    
# Header - Pending Claims
class pclaims:
    def pclaims(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({
            'claimsDate' : function_instance.formatDate(mergeinfo[0]),
            'dateDescription' : mergeinfo[1],
        })
        return replace

# Transmittal - Issue Fee
class issuefee:
    def issuefee(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        reqpat = mergeinfo[2]
        numfact = mergeinfo[3]
        drawnum = mergeinfo[4]
        prevpaiddate = mergeinfo[7]
        
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
            
        depnum = function_instance.depnumFill(matter_data)
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[12]))
        replace.update({
            'upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'nickU' : '',
            'dateIssueFee': function_instance.formatDate(prevpaiddate),
            'withDrawText' : wdrwtxt,
            'withdrawCopyText' : '',
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
            'dueDate' : function_instance.formatDate(dateIssueFee),
        })
        return replace
    
# PTO Form - Statement Under 3.73(c) - App filed on/or after Sept 16, 2012
class Statement373c:
    def Statement373c(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        recoccur = mergeinfo[0]

        if mergeinfo[2] == 'oth':
            org = mergeinfo[3]
        else:
            if mergeinfo[2]:
                org = mergeinfo[2]
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[1]))
        replace.update({
            'orgType' : org,
        })
        return replace
    
# Formal Document - Assignment Recordation Cover Sheet
# may need to add other organization types. May need totalfee
class recordation:
    def recordation(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        depnum = function_instance.depnumFill(matter_data)
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
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

        replace.update(function_instance.esigncheck(mergeinfo[3]))
        replace.update({
            'depAccount' : depnum,
            'dateExecutionText' : function_instance.formatDate(mergeinfo[5]),
            'selectedInventorList' : selinv,
            'totalFee' : totfee,
            'numPages' : mergeinfo[2],
            'depAcctX' : depX,
            'checkX' : chkX,
        })
        return replace
 
# Transmittal - Late Submission of Declaration or Substitute Statement
# Only need duedate and nickU
class LateSubmissionOfDec:
    def LateSubmissionOfDec(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
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
        replace.update(function_instance.esigncheck(mergeinfo[3]))
        replace.update({
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

# Transmittal - Update to Application Data Sheet
class UpdateAppDataSheet:
    def UpdateAppDataSheet(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        if(mergeinfo[0] == 'true'):
            muX = 'X'
            muText = 'Marked Up Application Data Sheet (' + mergeinfo[1] + ' Pg.).'
            if mergeinfo[1] != '' and int(mergeinfo[1]) > 1:
                muText = 'Marked Up Application Data Sheet (' + mergeinfo[1] + ' Pgs.).'
        
        dsX = 'X'
        dsText = 'Communication Re: Update to Application Data Sgeet (1 Pg.).'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({
            'dsX' : dsX,
            'dsText'  : dsText,
            'muX' : muX,
            'muText' : muText,
            'dueDate' : '',
            'currentMo' : datetime.now().strftime("%B"),
            'currentYr' : datetime.now().year,
        })
        return replace

# Report Out - Original Letters Patent (Email)
class olpemail:
    def olpemail(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        replace = {}
        # Fill Data
        matter_data = function_instance.matterFill(matter)

        # May need editing
        utilityText1 = "The patent will remain in effect for a term of twenty years from the date of the earliest filing.  To maintain the patent for its entire term, maintenance fees must be paid when due.  The fees are due as follows:"
        utilityFee1 = "3-1/2 years from the issue date"
        utilityFee2 = "7-1/2 years from the issue date"
        utilityFee3 = "11-1/2 years from the issue date"
        
        try:
            actname = function_instance.getactivityid(matter_data, 'OLPR').name
        except:
            actname = ''
        try:    
            if matter_data.fileddate and matter_data.fileddate > datetime(2015, 5, 13):
                designtxt = 'The term of a design patent extends up to a maximum of 15 years from the date of issue.", "The term of a design patent extends up to a maximum of 14 years from the date of issue.'
            else:
                designtxt = ''
        except:
            designtxt = ''
            
        cultxt = ''
        if mergeinfo[0] == 'TRUE':
            cultxt = 'Prior instructions have been received acknowledging SLW responsibility for payment of the maintenance fees through our preferred 3rd party provider, Black Hills AI (www.blackhills.ai).  If for any reason this process is no longer valid, please reach out to us expeditiously to confirm new instructions.'
        else:
            cultxt = 'Maintenance fees may be submitted by any recognized party, including a patentee or third party. Generally we refer clients to Black Hills AI (www.blackhills.ai) for maintenance payment services. However, this is in no way an endorsement of their services and you may choose to pay the maintenance fees directly or may have another third party administer payment. Therefore, if you haven\'t already done so, please provide instructions regarding who will be handling your maintenance fee payments.'
            
        # Need to add use case for answer
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'activityname' : actname,
            'THIS.title'  : matter_data.title,
            'designText' : designtxt,
            'utilityText1' : utilityText1,
            'utilityFee1' : utilityFee1,
            'utilityFee2' : utilityFee2,
            'utilityFee3' : utilityFee3,
            'cutilityText2' : cultxt,
        })
        return replace

# Report Out - MP/CAP/Sequence Listing Actions
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
        if action == 9:
            code = 'MPTA'
        if action == 10:
            code = 'MPTA'

        try:
            activity = function_instance.getactivityid(matter_data, code)
            attr = Rvwactivitydateattribute.objects.using('FIP').filter(activityid = activity.activityid)
            if attr.attrvallabel == 'Date Mailed':
                if action == 5:
                    actname = 'Missing Parts with Corrected Application Papers Received'
                if action == 7:
                    actname = 'Corrected Application Papers with Sequence Listing Action Received'
                else:
                    actname = activity.name
                datemailed = activity.smryonevalue
                duedate = (datemailed + relativedelta(months=2)).strftime('%B %d, %Y')
                duedate1mo = (datemailed + relativedelta(months=1)).strftime('%B %d, %Y')
        except:
            actname = ''
            duedate = ''
            duedate1mo = ''
            datemailed = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'activityName' : actname,
            'dueDate' : duedate,
            'dueDate1mo' : duedate1mo,
            'dateMailed' : datemailed
        })
        return replace

# PTO Form - Application Data Sheet - On/after Sept 16, 2012
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

        radio = mergeinfo[7]

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[11])) #or 2?
        replace.update({
            'drawingSheets' : draw,
        })
        return replace
        
class stateofallow:
    def stateofallow(self, matter, mergeinfo, keys):
            function_instance = mergefunctions.mergefunctions()
            matter_data = function_instance.matterFill(matter)

            replace = {}
            depnum = function_instance.depnumFill(matter_data)
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update(function_instance.esigncheck(mergeinfo[12]))
            replace.update({
                'depAccount' : depnum,
                'allowType' : 'Notice of Allowability',
                'dateNALL' : date.today().strftime("%B %d, %Y"),
            })
            return replace
    
# Report Out - Application Filed (including CIP and Design)
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
                  
            if entitysize == 1 or entitysize == 0:
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
            replace.update(function_instance.cmgfill(matter))
            replace.update({
                'smallEntity' : smallentitytext,
                'actionText' : actionText,
                'applicationType' : applicationType,
                'currentDate' : date.today(),
                'patentLink' : 'http://ca.slwip.com/slwdocs/applicationfiled.doc',
                'cReqPriorExam' : ReqPriorExam,
                'salutation' : '',
                'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            })
            return replace

# PCT - 92bis Comm: Change in Rights of Ownership
class ownerchange:
    def ownerchange(self, matter, mergeinfo, keys):
            function_instance = mergefunctions.mergefunctions()

            replace = {}
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update(function_instance.applicantfill(matter, 1))
            replace.update(function_instance.esigncheck(mergeinfo[0]))  
            replace.update({
                'applicantName' : mergeinfo[2]
            })
            return replace
    
# Transmittal - Communication Regarding Corrected Application Papers
# Need due date and fee
class corrappln:
    def corrappln(self,matter, mergeinfo, keys):
            function_instance = mergefunctions.mergefunctions()
            matter_data = function_instance.matterFill(matter)
            depnum = function_instance.depnumFill(matter_data)

            SubX = ''
            AbsX = ''
            SeqX = ''
            FrmlX = ''
            
            madx = ''
            madpg = ''

            SubPg = ''
            AbsPg = ''
            SeqPg = ''
            FrmlPg = ''
            depx = ''
            deppg = ''
            extx = ''
            extpg = ''
            doclist = ''
            docs = []

            if mergeinfo[2] != '' and int(mergeinfo[2]) > 0:
                SubX = 'X'
                SubPg = 'Substitute Specification (' + mergeinfo[2] + ' pg.).'
                docs.append('a Substitute Specification')

            if mergeinfo[3] != '' and int(mergeinfo[3]) > 0:
                AbsX = 'X'
                AbsPg = 'Abstract (' + mergeinfo[3] + ' pg.).'
                docs.append('a Substitute Abstract')

            if mergeinfo[4] != '' and int(mergeinfo[4]) > 0:
                SeqX = 'X'
                SeqPg = 'Sequence Listing (' + mergeinfo[4] + ' pg.).'
                docs.append('a Sequence Listing')

            if mergeinfo[5] != '' and int(mergeinfo[5]) > 0:
                FrmlX = 'X'
                FrmlPg = 'Formal Drawings (' + mergeinfo[5] + ' pg.).'
                docs.append('Formal Drawings')
                
            if mergeinfo[6] != '' and int(mergeinfo[6]) > 0:
                madx = 'X'
                madpg = 'Marked-up Application Data Sheet (' + mergeinfo[6] + ' pgs.)'

            if len(docs) == 4:
                doclist = 'A Substitute Specification, a Substitute Abstract, a Sequence Listing, and Formal Drawings are attached.'
            elif len(docs) == 2:
                doclist = ' and '.join(docs)
                doclist += ' are attached.'
            elif len(docs) == 1:
                doclist = docs[0]
                doclist += ' is attached.'
            else:
                doclist = ', '.join(docs[:-1])
                if len(docs) > 1:
                    doclist += ', and ' + docs[-1]
                    doclist += ' are attached.'

            if mergeinfo[1] != '' and int(mergeinfo[1]) > 0:
                extx = 'X'
                extpg = 'Petition for Extension of Time (1 pg.).'
                if mergeinfo[0] == 'true':
                    depx = 'X'
                    deppg = 'Authorization to charge Deposit Account '+ depnum +' in the amount of $'+ '' +' to cover the Extension of Time Fee.'

            replace = {}
            replace.update(function_instance.mergebasic(keys, matter))
            replace.update(function_instance.esigncheck(mergeinfo[6]))
            replace.update({
                'depAccount' : depnum,
                'SubX' : SubX,
                'AbsX' : AbsX,
                'SeqX' : SeqX,
                'FrmlX' : FrmlX,
                'SubstitutePg' : SubPg,
                'AbstractPg' : AbsPg,
                'SeqPg' : SeqPg,
                'FormalPg' : FrmlPg,
                'docList' : doclist[0].upper() + doclist[1:],
                'nickU' : '',
                'dueDate' : '',

                'extX' : extx,
                'extPg' : extpg,
                'depX' : depx,
                'depPg' : deppg,
                
                'MadX' : madx,
                'DataPg' : madpg
            })
            return replace

# Transmittal - Missing Parts Response
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
    
# Report Out - Issue Fee
class rptissuefee:
    def rptissuefee(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        try:
            compdate = Task.objects.using('FIP').get(matterid = matter_data.matterid, code = 'IFEE-D').completiondate
        except:
            compdate = 'No Issue Pay Date Found'
        
        if mergeinfo[0] == 'FALSE':
            acttxt = '\nACTION NEEDED: Please instruct us as to whether any continuing application filing is desired.\n'
        else:
            acttxt = ''
            
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'dateFiled' : compdate,
            'ActionTxt' : acttxt
        }) 
        return replace

# Letter - Send Formal Documents via Adobe Sign
class adobesign:
    def adobesign(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        choice = 'Declaration'
        if mergeinfo[0] == '1' or mergeinfo[0] =='3':
            choice = 'Assignment'
        if mergeinfo[0] == '2':
            choice = 'Assignment and Declaration'
        if mergeinfo[0] == '4' or mergeinfo[0] == '5' or mergeinfo[0] == '6' or mergeinfo[0] == '7' or mergeinfo[0] == '8' or mergeinfo[0] == '9' or mergeinfo[0] == '10':
            choice = 'Assignment and POA'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'userChoice' : choice,
        })
        return replace

# Letter - Send Formal Document(s)
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
            'fmlContent' : mergeinfo[5]
        })
        return replace

# Report Out - Basic Letter
class basicreport:
    def basicreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        selnames = mergeinfo[1].replace(';','\n')
        
        seldates = mergeinfo[0].split(';')
        finaldates = ''
        for date in seldates:
            try:
                actdate = function_instance.extract_date(date)
                date_object = datetime.strptime(actdate, "%m/%d/%Y")
                finaldates += date_object.strftime("%B %d, %Y") + '\n'
            except:
                finaldates += 'NO DATE FOUND' + '\n'

        rows = zip(finaldates.split('\n'), selnames.split('\n'))
        formatted_data = "\n".join(["\t\t\t".join(row) for row in rows])

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'activityname' : mergeinfo[1],
            'dateFiled' : formatted_data,
            'docFiled' : '',
        })
        return replace

# Report Out - Miscellaneous Items Received from the PTO
class ptorecdReport:
    def ptorecdReport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        selnames = mergeinfo[1].replace(';','\n')
        
        seldates = mergeinfo[0].split(';')
        finaldates = ''
        for date in seldates:
            try:
                actdate = function_instance.extract_date(date)
                date_object = datetime.strptime(actdate, "%m/%d/%Y")
                finaldates += date_object.strftime("%B %d, %Y") + '\n'
            except:
                finaldates += 'NO DATE FOUND' + '\n'

        rows = zip(finaldates.split('\n'), selnames.split('\n'))
        formatted_data = "\n".join(["\t\t".join(row) for row in rows])

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'dateMailed' : formatted_data,
            'docReceived' : '',
            'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'salutation' : '',
            'activityname' : mergeinfo[1].split(';')[0]
        })
        return replace

# Report Out - Notice of Allowance
class RepNoticeofAllow:
    def RepNoticeofAllow(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        entitystatus = function_instance.entityfill(matter)

        try:
            smryone = (function_instance.getactivityid(matter_data, 'NOAR').smryonevalue)
            noardate = smryone.strftime('%B %d, %Y')
            noar2date = (smryone + relativedelta(months=2)).strftime('%B %d, %Y')
            noar3date = (smryone + relativedelta(months=3)).strftime('%B %d, %Y')

        except:
            noardate = '' 
            noar2date = ''
            noar3date = ''

        # may need in ret language
        if(entitystatus == 0):
            billamt = '1,450.00'
        if(entitystatus == 2):
            billamt = '2,050.00'
        if(entitystatus == 1):
            billamt = '1,150.00'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'noar2Mo' : noar2date,
            'noarLink' : 'http://ca.slwip.com/slwdocs/noticeofallowance.doc',
            'noar3Mo' : noar3date,
            'noarDate' : noardate,
            'RETLANGUAGE' : '',
            'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'salutation' : '',
        })
        return replace
    
# PCT - Report Out Miscellaneous Items Received
class PCTRptOutMiscItmsRcvd:
    def PCTRptOutMiscItmsRcvd(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        selnames = mergeinfo[1].replace(';','\n')
        
        seldates = mergeinfo[0].split(';')
        finaldates = ''
        for date in seldates:
            try:
                actdate = function_instance.extract_date(date)
                date_object = datetime.strptime(actdate, "%m/%d/%Y")
                finaldates += date_object.strftime("%B %d, %Y") + '\n'
            except:
                finaldates += 'NO DATE FOUND' + '\n'

        rows = zip(finaldates.split('\n'), selnames.split('\n'))
        formatted_data = "\n".join(["\t\t\t".join(row) for row in rows])
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'dateFiled' : formatted_data,
            'activityName' : (mergeinfo[1]).replace(';',', '),
        })  
        return replace


# Report Out - Recorded Assignment
# use activity and attributeval to get reel and frames
class recordedassnreport:
    def recordedassnreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        if mergeinfo[0]:
            recorddesc = '\nCORRECTION CONFIRMED: ' + mergeinfo[0] +'\n'
            actrep = 'Corrected Notice of Recordation of Assignment.  The'
        else:
            actrep = 'Recorded Assignment in the'
            recorddesc = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({
            'salutation'  : '',
            'correctionText' : recorddesc,
            'actText' : '',
            'addText' : '',
            'clientName' : '',
            'actrepText' : actrep,
            'activityname' : ''
        })
        return replace

# Letter - Send Provisional Assignment
class reportprvassnnew:
    def reportprvassnnew(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            rdate = function_instance.formatDate(mergeinfo[3])
        except:
            rdate = mergeinfo[3]

        ddue = (matter_data.fileddate + relativedelta(years=1)).strftime('%B %d, %Y')
        
        nottxt = ''
        if mergeinfo[4] == 'true':
            nottxt = 'in the presence of a Notary Public '

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update(function_instance.cmgfill(matter))
        replace.update({
            'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'salutation' : '',
            'haveInvSgn' : 'have the inventor(s) ',
            'ascFax' : '612-339-3061',
            'returnDate' : rdate,
            'notaryText' : nottxt,
            'dueDate' : ddue,
            'activityname' : 'Send Provisional Assignment'
        })
        return replace

# Report Out - Notice of Abandonment
class abandonReport:
    def abandonReport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'instFrom' : mergeinfo[0],
            'instDate' : function_instance.formatDate(mergeinfo[1]),
            'salutation' : ''
        })
        return replace
    
# Report Out - Issue Notification
class issuereport:
    def issuereport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            issdate = str((function_instance.patentFill(matter_data).issuedate).strftime('%B %d, %Y'))
        except:
            issdate = ''

        if mergeinfo[0] == 'TRUE':
            actreq = 'None at this time.  Instructions already received with regard to any continuing (divisional, continuation, continuation-in-part) application filing(s).'
        else:
            actreq = 'Please instruct us as to whether any continuing application filing is desired.  The last day for filing any continuing application is '+ issdate +'.  Absent your written instructions, we will not file any additional applications based on the above-identified application. '

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'actreq' : actreq,
        })
        return replace

# PCT - Response to Invitation to Correct Defects (PCT/RO/106)
# check/dep
class pctcorrect:
    def pctcorrect(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        depacc = mergeinfo[0]
        check = mergeinfo[1]
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
            Btxt = 'Replacement description pages ' + descpg + ', replacement claims pages ' + claimpg + ' and replacement abstract pages ' + abspg + ' which are believed to be in compliance with Annex B1 of the Invitation.'
        else:
            Btxt = ''

        if annexC == 'true':
            Ctxt = 'Formal drawing sheets (' + formalpg + ') which are all believed to be in compliance with Annex C1 of the Invitation.'
        else:
            Ctxt = ''

        label = 'CERTIFICATE UNDER 37 CFR 1.8:  The undersigned hereby certifies that this correspondence is filed using the USPTO\'s electronic filing system EFS-Web, and is addressed to: MS PCT, Commissioner for Patents, P.O. Box 1450, Alexandria, VA 22313-1450 on this ________ day of '+ str(datetime.now().strftime("%B")) +', '+ str(datetime.now().year) +'.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({
            'mailDate' : function_instance.formatDate(mergeinfo[3]),
            # add phone number at end
            'cAnnexAText' : Atxt,
            'cAnnexBText' : Btxt,
            'cAnnexCText' : Ctxt,
            'properApplicant' : 'Applicant',
            'encloseText' : 'enclose',
            'depAccount' : function_instance.depnumFill(matter_data),
            'upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'userName' : '',
            'certificateForPaperFilingExpressMail' : '',
            'certificateForEmailPaperFilingStandard' : label,
        })
        return replace

# PTO Form - Application Data Sheet - On/after Sept 16, 2012
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

        label = 'CERTIFICATE UNDER 37 CFR 1.8:  The undersigned hereby certifies that this correspondence is filed using the USPTO\'s electronic filing system EFS-Web, and is addressed to: MS PCT, Commissioner for Patents, P.O. Box 1450, Alexandria, VA 22313-1450 on this ________ day of '+ str(datetime.now().strftime("%B")) +', '+ str(datetime.now().year) +'.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({
            'extensionLenTextHdr' : function_instance.number_to_words(int(mergeinfo[6])),
            'mailDate' : mergeinfo[3],
            'properApplicant' : 'Applicant',
            'extensionLenText' : function_instance.number_to_words(int(mergeinfo[6])).lower(),
            'requestText' : 'requests',
            'annexSelectText' : annexTxt,
            'upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'requestDueDate' : '',
            'SAName' : mergeinfo[4],
            'certificateForPaperFilingExpressMail' : '',
            'certificateForEmailPaperFilingStandard' : label,
        })
        return replace

# Report Out - Non-Final Office Action Received
class nonfinalreportFp:
    def nonfinalreportFp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        if mergeinfo[0] == 'true':
            reqtxt = 'We have requested Prioritized Examination in this matter. Participation in Prioritized Examination assumes compliance with United States Patent Office procedures as outlined at http://www.uspto.gov/aia_implementation/faq.jsp#heading-9.  Please be advised that any extension of time for response in this matter will automatically remove this application from the Prioritized Examination program.\n\n'
        else:
            reqtxt = 'We have requested Prioritized Examination in this matter. '
        
        try:
            smryone = (function_instance.getactivityid(matter_data, 'OARN').smryonevalue)
            oarndate = smryone.strftime('%B %d, %Y')
            oarn3date = (smryone + relativedelta(months=3)).strftime('%B %d, %Y')
            instdate = (smryone + relativedelta(months=2)).strftime('%B %d, %Y')

        except:
            oarndate = '' 
            instdate = ''
            oarn3date = ''


        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'cReqPriorExam' : reqtxt,
            'salutation' : '',
            'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'instDate' : instdate,
            'oarnDate' : oarndate,
            'oarn3MoDate' : oarn3date
        })
        return replace

# PCT - Letter to send Assignment and POA
class PCTAsgnPOALetter:
    def PCTAsgnPOALetter(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        sendingpoa = ''
        nottxt = ''
        if mergeinfo[2] == 'true':
            sendingpoa = 'We have also enclosed a Power of Attorney document for the assignee.'

        if mergeinfo[1] == 'true':
            sendingpoa = sendingpoa + "This Power of Attorney needs to be signed by an officer of the organization or a person empowered to sign on the organization's behalf."
            nottxt = 'Please have the inventors sign and date the Assignment document in the presence of a Notary Public. '
 
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'pctdueDate' : function_instance.formatDate(mergeinfo[0]),
            'cSendingPOA' : sendingpoa,
            'Notary' : nottxt,
            'salutation' : '',
        })
        return replace
    
# PCT - Report out Invitation to Pay Additional Fees
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

# PCT - Response to Invitation to Furnish Sequence Listing
class PctCommRe:
    def PctCommRe(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        depnum = function_instance.depnumFill(matter_data)

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
        replace.update(function_instance.esigncheck(mergeinfo[7]))
        replace.update({
            'mailDate' : function_instance.formatDate(mergeinfo[3]),
            'lpX' : lpX,
            'seqListingLine' : seqpaper,
            'seqRFLine' : '',
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
    
# PCT - Report Filing of Application
class PCTRptFileOfApp:
    def PCTRptFileOfApp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        recoffice = mergeinfo[0]
        searchingauth = mergeinfo[1]
            
        if mergeinfo[2] != '':
            exclusion = 'The application designated all PCT contracting states except ' + function_instance.fullCountry(mergeinfo[2]) +'. The exclusion of this designation prevents the priority application from becoming abandoned, in accordance with country law.'
        else:
            exclusion = 'The application designated all PCT contracting states.\n'

        selserial = mergeinfo[3].replace('*', ',').replace(';','\n')
        seldate = mergeinfo[4].replace('*', ',').replace(';','\n')
        selcountry = mergeinfo[5].replace('*', ',').replace(';','\n')

        # Convert selcountry using fullCountry method
        selcountry_list = [function_instance.fullCountry(str(country)) for country in selcountry.split('\n')]
        selcountry = "\n".join(selcountry_list)

        rows = zip(selserial.split('\n'), seldate.split('\n'), selcountry.split('\n'))
        formatted_data = "\n".join(["\t\t\t".join(row) for row in rows])

        prapp = 'The PCT application claims priority to the following earlier-filed application(s):'

        action = 'ACTION REQUIRED:'
        action = action + ' None at this time.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'priorAppNo' : formatted_data,
            # no longer needed
            'priorAppDate' : '',
            'priorAppCntry' : '',
            'crcvOffice' : recoffice,
            'cpatentOffice' : searchingauth,
            'excluDesigPhs' : exclusion,
            'actionText' : action,
            'cpriorApps' : prapp,
            'salutation' : '',
        })
        return replace
    
# PTO Form - Update Application Data Sheet
class applicationdata_updnew:
    def applicationdata_updnew(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        sadata = function_instance.rvwmatterpersonnelFill(matter_data)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[7]))
        replace.update({
            # get update tag
            '' : mergeinfo[6],
            'custNoEmail' : 'request@slwip.com',
            'apptitle' : matter_data.title,
            'appmatterNo' : matter_data.hostmatterno,
            'appmatterType' : matter_data.mattertypedescription,
            'drawingSheets' : mergeinfo[3],
            'appprov' : 'Non-Provisional',
            'SAFirstName' : sadata.fname,
            'SALastName' : sadata.lname,
            'SARegNo' : sadata.registrationno
        })
        if mergeinfo[1] == 'false':
            replace.update({'custNoCorresp' : '', 'custNoEmail' : ''})
        if mergeinfo[2] == 'false':
            replace.update({'apptitle' : '', 'appmatterNo' : '', 'appmatterType' : '', 'drawingSheets' : '', 'appprov' : ''})
        return replace

# Report Out - Notice of Publication
class nopreport:
    def nopreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        patent = function_instance.patentFill(matter_data)
        pubno = patent.pubno
        try:
            pubdate = (patent.pubdate).strftime('%B %d, %Y')
        except:
            pubdate = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'pubNo' : pubno,
            'pubDate' : pubdate,
            'salutation' : '',
        })
        return replace

# Report Out - Final Office Action Received
class foarreport:
    def foarreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            foaract = (function_instance.getactivityid(matter_data, 'FOAR'))
            foardate = foaract.smryonevalue.strftime('%B %d, %Y')
            foar2date = (foaract.smryonevalue + relativedelta(months=2)).strftime('%B %d, %Y')
            foar3date = (foaract.smryonevalue + relativedelta(months=2)).strftime('%B %d, %Y')
            instdate = (foaract.smryonevalue + relativedelta(months=1)).strftime('%B %d, %Y')
            actname = foaract.name

        except:
            foardate = '*bad date*' 
            foar2date = '*bad date*'
            foar3date = '*bad date*'
            instdate = '*bad date*'
            actname = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'foar2Mo' : foar2date,
            'foar3Mo' : foar3date,
            'instDate' : instdate,
            'foarDate' : foardate,
            'salutation'  : '',
            'activityName' : actname
        })
        return replace

# Transmittal - General
class generalxmitCF:
    def generalxmitCF(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

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
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'mailStopText' : mailstop,
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
    
# Report Out - Filing Receipt Received
class filerectreportNw2:
    def filerectreportNw2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

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
            addnotes = addnotes + " This Provisional patent application will expire one year from the filing date.  If a regular (non-provisional) U.S. application is not filed by " + matter_data.fileddate + ", the ability to claim priority to the filing date of the provisional application will be lost."

        # Cant find where rectype is used
        activity = ''
        if mergeinfo[2] == '1':
            activity = Activity.objects.using('FIP').filter(Q(code='FRCT-AE') | Q(code='FRCT'), matterid = matter.matterid)
            rectype = 'an Official Filing Receipt'
        if mergeinfo[2] == '2':
            activity = Activity.objects.using('FIP').filter(matterid = matter.matterid, code = 'FRCT-4')
            rectype = 'a Replacement Filing Receipt'
        if mergeinfo[2] == '3':
            activity = Activity.objects.using('FIP').filter(Q(code='FRCT-3') | Q(code='UFRR'), matterid = matter.matterid)
            rectype = 'an Updated Filing Receipt'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'additionalNotes' : addnotes,
            'salutation' : '',
            'actionRep' : '',
            'actionReq' : 'None at this time.',
            'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
        })
        return replace
    
# PCT - General Transmittal (WIPO)
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
    
# PCT - Report out Search Report and Written Opinion    
class PctSearchRep:
    def PctSearchRep(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.applicantfill(matter, 1))
        replace.update({
            '19duedate' : function_instance.formatDate(mergeinfo[1]),
            '34duedate' : function_instance.formatDate(mergeinfo[2]),
            '30mduedate' : function_instance.formatDate(mergeinfo[3]),
            'instructionsDue' : function_instance.formatDate(mergeinfo[0]),
            'activityName'  : ''
        })
        return replace
    
# PCT - Report Out IPRP
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
        
        if mergeinfo[0] == 'false':
            action = '\nACTION REQUIRED:  Since the PCT application is complete, no action is needed at this time.\n'
            addnotes = 'ADDITIONAL NOTES: If you have any questions or comments, please contact <<This.WAName>> at <<This.WAPhone>> or <<This.paraName>> at <<This.paraPhone>>.'
        else:
            action = 'Now that we have received the Report, you must make a decision regarding the conversion of the Application filed under the Patent Cooperation Treaty (PCT) to one or more national or regional stage applications in the various countries and/or regional offices for which you would like to procure patent protection.  Under the rules of the PCT, the Application will terminate for many countries on '+' (that is, 30 months from the priority date of the PCT Application).  Therefore, to seek patent protection in those countries/regions, the Application must be converted to national/regional applications prior to that date.  Currently, based on the rules in a given country or region, the Application must be converted from 30 months to 42 months of the priority date of the Application.'
            action += '\nPlease give this matter your prompt consideration.  The time for converting from the international stage under the PCT to national/regional stage patent applications is non-extendable.  Since each national application requires a number of documents to be prepared, and possibly translated into different languages, to be received by the various country or regional patent offices, we must receive your instructions regarding this matter by '+'.  As indicated above, the national stage application filings for many countries/regions must be completed by '+'.  A decision not to file national stage applications by the due date for that country/region will result in abandonment of the PCT Application.\n'
            addnotes = 'ADDITIONAL NOTES:  Please contact <<This.WAName>> at <<This.WAPhone>> if you would like to discuss this matter more fully, or if you need a cost estimate for filing in specific countries/regions.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'actionRequired' : action,
            'addNotes' : addnotes,
            'salutation' : '',
        })
        return replace

# IDS - Communication New
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

# IDS - Search Report Memo
class idsmemo:
    def idsmemo(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        actionrec = mergeinfo[0]
        if actionrec == 'Other':
            actionrec = mergeinfo[1]
        
        relmattersAct = mergeinfo[5:]
        
        actindex = relmattersAct.index('endrellist')
        activitylist = relmattersAct[actindex + 1:]
        relmatters = relmattersAct[:actindex]
        
        selmatter = relmatters[0].replace('*', ',').replace(';','\n')
        selserial = relmatters[1].replace('*', ',').replace(';','\n')
        selstatus = relmatters[2].replace('*', ',').replace(';','\n')

        rows = zip(selmatter.split('\n'), selserial.split('\n'), selstatus.split('\n'))
        formatted_data = "\n".join(["\t\t\t".join(row) for row in rows])

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'relmatterdata' : formatted_data,
            'docFiled' : actionrec,
            'actionDueDate' : function_instance.formatDate(mergeinfo[4]),
            'activityname' : activitylist[0],
            'userName' : ''
        })
        return replace

# Transmittal - Patent Application (Utility)
class utilityapp:
    def utilityapp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
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
        replace.update(function_instance.esigncheck(mergeinfo[28]))
        replace.update({
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

# Formal Document - Assignment (with or w/out Notary)
class assignment2016:
    def assignment2016(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

        replace = {}
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.inventorInfo(matter , 1))
        replace.update({
            'hasHave' : 'has'
        })
        return replace
    
# FF Report Out - Office Actions Received
class ffOfficeActRcvd:
    def ffOfficeActRcvd(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

        typeaction = mergeinfo[4]
        deadline = function_instance.formatDate(mergeinfo[5])
        reqresp = function_instance.formatDate(mergeinfo[6])
        citedref = mergeinfo[7]
        cite = ''
        if citedref == 'true' and typeaction != '':
            cite = ' and cited references '
        if citedref == 'true' and typeaction == '':
            cite = ' cited references '

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.cmgfill(matter))
        replace.update({
            'cdueDate' : deadline,
            'crespDate' : reqresp,
            'actionType' : typeaction,
            'citedRef' : cite,
            'activityName' : (mergeinfo[1].split(';'))[0],
            'salutation' : ''
        })
        return replace

# Letter - FF Order Letter
class mrgfforder:
    def mrgfforder(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({

        })
        return replace
    
# Letter - FF Draft OA Instructions to Associate
class DraftOAInstruct:
    def DraftOAInstruct(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.ffparafill(matter))
        replace.update(function_instance.countryType(matter))
        replace.update({
            'corrDate' : function_instance.formatDate(mergeinfo[0]),
            'cdueDate' : function_instance.formatDate(mergeinfo[1])
        })
        return replace

# Header - Extension of Time
class exttimeCF:
    def exttimeCF(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        depnum = function_instance.depnumFill(matter_data)

        try:
            datemail = function_instance.formatDate(mergeinfo[9])
        except:
            datemail = ''
        try:
            duedate = function_instance.formatDate(mergeinfo[10])
        except:
            duedate = ''
        try:
            newdate = function_instance.newDate(mergeinfo[11], mergeinfo[10])
        except:
            newdate = ''
            
        cert = 'CERTIFICATE UNDER 37 CFR 1.8:  The undersigned hereby certifies that this correspondence is being filed using the USPTO\'s electronic filing system EFS-Web, and is addressed to: test, Commissioner for Patents, P.O. Box 1450, Alexandria, VA 22313-1450 on {{Dte_es_:signer2:date}}.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[17]))
        replace.update({
            'extLength' : mergeinfo[12].upper(),
            'depCheckText' : 'Please charge Deposit Account No. '+ depnum +' ',
            'feeAmount' : mergeinfo[1],
            'enclosed' : '',
            'depAccount' : depnum,
            'extLengthL' : mergeinfo[12].lower(),
            'mailstopText' : mergeinfo[8],
            'extResponse' : mergeinfo[9],
            'dateMailed' : datemail,
            'dueDate' : duedate,
            'newDate' : newdate,
            'petitionText' : '',
            'certificateCF' : cert
        })
        return replace

# Transmittal - Communication Regarding Incorrect Filing Receipt
# Only need dueDate
class incorrectfilerect:
    def incorrectfilerect(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        depnum = function_instance.depnumFill(matter_data)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'depAccount' : depnum,
            'nickU' : '',
            'postcardX' :'',
            'postcardText' : '',
            'dueDate' : '',
        })
        return replace
    
# PTO Form - Correction of Inventorship  (AIA/40)
# Need to fix SARegNo - will not fill with mergebasic
class corrinventorship:
    def corrinventorship(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'depAccount' : function_instance.depnumFill(matter_data),
        })
        return replace

# PTO Form - Correction of Applicant  (AIA/41)
# e-signature and SA data not filling correctly.
class corrapplicant:
    def corrapplicant(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
        })
        return replace

# PCT - Declaration
# Need small changes. clientreftxt and inventor info
class pctdeclaration2:
    def pctdeclaration2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.inventorInfo(matter , 1))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'clientRefText' : '',
        })
        return replace

# Transmittal - RCE
class rcexmit3:
    def rcexmit3(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

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
            aarftxt = 'Consider the amendment(s)/reply under 37 C.F.R. § 1.116 previously filed on ' + function_instance.formatDate(mergeinfo[5])
        if mergeinfo[6] != '':
            abrfx = 'X'
            abrftxt = 'Consider the arguments in the Appeal Brief or Reply Brief previously filed on ' + function_instance.formatDate(mergeinfo[6])
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
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({
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
    
# PCT - Generic Header
class pctgeneric:
    def pctgeneric(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 

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
        replace.update(function_instance.esigncheck(mergeinfo[3]))
        replace.update({
            'headerText' : mergeinfo[1],
            'pctAddress' : pctaddr,
            'depositText' : deptxt,
            'SAName' : mergeinfo[2],
        })
        return replace

# PCT - 92bis Comm: Change in Inventor Address
class invchange:
    def invchange(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter) 
        
        inventlist = mergeinfo[2:]
        inventlist = inventlist[:-1]
        
        invtxt = ''
        hastxt = 'has'
        if len(inventlist) == 2:
            invtxt = inventlist[0] + ' and ' + inventlist[1]
        elif len(inventlist) > 2:
            invtxt = ', '.join(inventlist[:-1]) + ', and ' + inventlist[-1]
        elif len(inventlist) == 1:
            invtxt = inventlist[0]
            
        if len(inventlist) > 1:
            hastxt = 'have'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'SAName' : mergeinfo[1],
            'invList' : invtxt,
            'hasText' : hastxt,
            'SAPhone' : '',
            'SARegNo' : '',
        })
        return replace       

# Report Out - Application Filed (Provisional)
class prvAppReport:
    def prvAppReport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        # , name__contains = 'Deadline'
        try:
            deadline = Task.objects.using('FIP').get(matterid = matter_data.matterid, code = 'FFIL-D').nextdateval
        except:
            deadline = (matter_data.fileddate + relativedelta(months=12)).strftime('%B %d, %Y')
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'activityname' : '',
            'instDate' : (matter_data.fileddate + relativedelta(months=9, days=15)).strftime('%B %d, %Y'),
            'usDeadline' : deadline,
            'patentLink': 'http://ca.slwip.com/slwdocs/applicationfiled.doc',   
        })
        return replace

# Report Out - Advisory Action Received
class advisoryreport:
    def advisoryreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        actcode = ['ADAF-N','ADAF', 'PTOL-304', 'PTOL-303']
        iscode = False

        for code in actcode:
            try:
                activity = function_instance.getactivityid(matter_data, code)
                iscode = True
                break
            except:
                continue
        
        if iscode:
            try:
                actdate = Rvwactivitydateattribute.objects.using('FIP').filter(
                    activityid__icontains=activity.activityid,
                    attrvallabel__icontains='Mailed'
                ).exclude(
                    attrvallabel__icontains='Final'
                ).get()
                adardate = actdate.dateval
            except:
               adardate = 'No Date Found' 
        else:
            adardate = 'No Date Found'
        
        try:
            foaractivity = function_instance.getactivityid(matter_data, "FOAR")
            foardate = foaractivity.smryonevalue.strftime('%B %d, %Y')
        except:
            foardate = ''
            
        try:
            instdue = function_instance.formatDate(mergeinfo[0])
        except:
            instdue = 'Invalid Date'
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'adarDate' : adardate,
            'foarDate' : foardate,
            'instDue'  : instdue,
            'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
        })
        return replace
    
# Report Out - Certificate of Correction (Email)
class cocReportEmail:
    def cocReportEmail(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
 
        })
        return replace

# PCT - Report Out Invitation to Correct Defects
class correctdefects:
    def correctdefects(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            mailsmryone = function_instance.getactivityid(matter_data, 'PCT/RO/106').smryonevalue
            invdate = mailsmryone
            inv1mo = (mailsmryone + relativedelta(months=1)).strftime('%B %d, %Y')
            inv2mo = (mailsmryone + relativedelta(months=2)).strftime('%B %d, %Y')
            
        except:
            invdate = ''
            inv1mo = ''
            inv2mo = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'inviteDate' : invdate,
            'invite1Mo' : inv1mo,
            'invite2Mo' : inv2mo
        })
        return replace

# Report Out - Application Filed (Provisional - PV2)
class pv2appReport:
    def pv2appReport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        matter_data = function_instance.matterFill(matter)
        deadlinedte = (matter_data.fileddate + relativedelta(months=12)).strftime('%B %d, %Y')

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'patentLink' : 'http://ca.slwip.com/slwdocs/applicationfiled.doc',
            'deadlineDate' : deadlinedte,
        })
        return replace
    
# PCT - Report Out Published Application
class PCTRptPubApp:
    def PCTRptPubApp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        patent = function_instance.patentFill(matter_data)
        pubno = patent.pubno
        try:
            pubdate = (patent.pubdate).strftime('%B %d, %Y')
        except:
            pubdate = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'pubDate' : pubdate,
            'pubNo' : pubno
        })
        return replace
    
# PCT - Declaration
class pctdeclaration2:
    def pctdeclaration2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.inventorInfo(matter , 1))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
        })
        return replace

# Report Out - Restriction Requirement
class rerrReport:
    def rerrReport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        act = False
        for code in ['RERR', 'RERR-PE']:
            try:
                activity = function_instance.getactivityid(matter_data, code)
                if activity:
                    act = True
            except:
                continue
        
        if act == True:
            rerrdte = activity.smryonevalue
            instdte = (rerrdte + relativedelta(months=1)).strftime('%B %d, %Y')
            rerr2mo = (rerrdte + relativedelta(months=2)).strftime('%B %d, %Y')
        else:
            rerrdte = ''
            instdte = ''
            rerr2mo = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'rerrDate' : rerrdte,
            'instDate' : instdte,
            'rerr1Mo' : rerr2mo,
            'salutation' : '',
        })
        return replace
    
# Report Out - Maintenance Fee Reminder
class maintfee:
    def maintfee(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            activity = function_instance.getactivityid(matter_data, 'MAINR')
            maildte = activity.smryonevalue.strftime('%B %d, %Y')
        except:
            maildte = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'dateMailed' : maildte,
            'activityname' : 'Maintenance Fee'
        })
        return replace
    
# FF Report Out - Items Filed with Foreign PTO
class FFRptOutBasic:
    def FFRptOutBasic(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        docs = mergeinfo[1].replace(';', '\n')
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'documentName' : docs,
            'salutation' : '',
            'activityname' : (mergeinfo[1].split(';'))[0],
        })
        return replace

# FF Report Out - Associate Confirms Filing/Filing Receipt
class FFFilingReceipt:
    def FFFilingReceipt(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            
        })
        return replace

# FF Report Out - SLW Report / Honu
class honureport:
    def honureport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        if mergeinfo[4] == 'NO':
            cortxt = '.'
            actreq = ''
        else:
            cortxt = 'together with the correspondence from the associate.'
            actreq = '\nACTION REQUIRED:\nThe deadline for responding to the communication is:  '+ function_instance.formatDate(mergeinfo[4]) +'\nWe would welcome your instructions no later than:  '+ function_instance.formatDate(mergeinfo[5]) + '\n'
                    
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.ffcmgFill(matter))
        replace.update({
            'activityname' : (mergeinfo[1].split(';'))[0],
            'corrtxt' : cortxt,
            'actionReq' : actreq
        })
        return replace

# Letter - Request for Instructions (FF/Conversion)
class ffinstructions:
    def ffinstructions(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        if mergeinfo[2] == 'true':
            ffnonprov = ''
            contype = 'INTERNATIONAL FILING'
            actname = 'Foreign Filing Instructions Needed'
        else:
            ffnonprov = 'This is also the deadline to convert the above-referenced provisional application into a regular non-provisional U.S. application. '
            contype = 'INTERNATIONAL FILING AND NON-PROVISIONAL CONVERSION'
            actname = 'Instructions Needed - U.S. Non-Provisional/Foreign Filing'
        try:
            relatedmatter = Relatedmatter.objects.using('FIP').filter(primarymatterid = matter.matterid, relationdesc__icontains = 'Priority')[0]
            primatter = function_instance.matterFill(relatedmatter.relatedmatterid)
            pridate = primatter.fileddate.strftime("%B %d, %Y")
            priser = primatter.serialnumber
        except:
            pridate = ''
            priser = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'instDate' : function_instance.formatDate(mergeinfo[1]),
            'ffDueDate' : (function_instance.formatDate(mergeinfo[0])).capitalize(),
            'conversionType' : contype,
            'cFFNonProvText1' : ffnonprov,
            'earlyPrioSerialNo' : priser,
            'earlyPriorFilingDate' : pridate,
            'cFFNonProvText2Header' : '',
            'cFFNonProvText2' : '',
            'activityName' : actname
        })
        return replace
    
# FF Report Out - Miscellaneous Items Received
class ffMiscItemsRcvd:
    def ffMiscItemsRcvd(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        docs = mergeinfo[1].replace(';', '\n')
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'documentName' : docs,
            'activityname' : mergeinfo[1].split(';')[0]
        })
        return replace

# Letter - FF Instructions to Pay Grant Fees
class CommunicationLetter:
    def CommunicationLetter(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'assocLttrDate' : function_instance.formatDate(mergeinfo[0]),
            'feeType' : mergeinfo[2],
            'feeDue' : function_instance.formatDate(mergeinfo[1]),
        })
        return replace
    
# FF Report Out - Decision to Grant
class FFDecisiontoGrant_NEW:
    def FFDecisiontoGrant_NEW(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        currtxt = ''
        acttxt = 'None at this time.'
        feetxt = ''
        
        if mergeinfo[0] == 'true':
            acttxt = 'Provide authorization to submit the fees'
            if mergeinfo[1] == 'true':
                acttxt += '; and\nProvide instructions as to submitting a divisional application'
                
            acttxt += '\nDeadline Date: ' + function_instance.formatDate(mergeinfo[2]) + '\nRequested Response Date:  ' + function_instance.formatDate(mergeinfo[3])
            feetxt = '\nThe Patent Office has set a deadline of '+ function_instance.formatDate(mergeinfo[2]) +' to pay the required fees. Please provide us with your instructions regarding this by '+ function_instance.formatDate(mergeinfo[3]) +'. Unless we receive your instructions to the contrary by this date, we will authorize our associate to pay the fees by the deadline date.\n'
        elif mergeinfo[1] == 'true':
            acttxt = 'Provide instructions as to submitting a divisional application\nRequested Response date: ' + function_instance.formatDate(mergeinfo[3])
            feetxt = '\nIf you are interested in filing a divisional application, please provide your instructions by '+ function_instance.formatDate(mergeinfo[3]) +'. In the absence of your instructions, we will not file a divisional application.\n'
            
        if mergeinfo[4] == 'true':
            currtxt = 'In view of the current pending status of corresponding applications, you may be eligible for voluntary participation in the Patent Prosecution Highway (PPH) program to possibly reduce costs and obtain accelerated examination. Please contact us to discuss your options should you wish to further explore this program.'
            
        currtxt += '\n\nIt is our understanding that you will be responsible for any annuity/maintenance fee payments.  If our understanding is incorrect, please advise us.\n\n'
            
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'actionText' : acttxt,
            'feesduePara' : feetxt,
            'currFutPend' : currtxt,
            'salutation' : ''
        })
        return replace

# Letter - Request for Instructions (PCT National Stage)
class natlphase:
    def natlphase(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            activity = function_instance.getactivityid(matter_data, 'NPAD')
            npaddte = (activity.smryonevalue).strftime('%B %d, %Y')
            duedte = (npaddte - relativedelta(months=1)).strftime('%B %d, %Y')

        except:
            duedte = ''
        
        if mergeinfo[3] == 'false':
            nonprov1 = 'Since no separate United States patent application was filed for this case, domestic as well as foreign patent rights will be lost unless corresponding national stage patent applications are filed in the countries or regional patent offices in which you seek protection. '
            nonprov2 = ''
        else:
            nonprov1 = ''
            nonprov2 = ''
            
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'instDate' : function_instance.formatDate(mergeinfo[2]),
            'priorityDate' : function_instance.formatDate(mergeinfo[1]),
            'npdueDate' : function_instance.formatDate(mergeinfo[0]),
            'nonProvText1' : nonprov1,
            'nonProvText2' : nonprov2,
            'dueDate1mo' : duedte
        })
        return replace
    
# FF Report Out - Notice of Publication Received
# not done
class FFNoticePubRcvd:
    def FFNoticePubRcvd(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        matter_data = function_instance.matterFill(matter)
        patent = function_instance.patentFill(matter_data)
        
        if 'CN' in matter_data.country :
            hactreq = '\nACTION REQUIRED: Instructions to file in Hong Kong\n'
            try:
                activity = function_instance.getactivityid(matter_data, 'HKRR')
                smryone = activity.smryonevalue
                hkduedate = smryone.strftime('%B %d, %Y')
                hkrespdate = (smryone - relativedelta(months=1)).strftime('%B %d, %Y')
                
            except:
                hkduedate = 'No date found'
                hkrespdate = 'No date found'
                
            cnmatter = '\nIn view of the publication, the deadline to extend the above-mentioned Chinese application to Hong Kong is ' + hkduedate + '.  If you are interested in registering the application in Hong Kong, please provide us with your instructions by ' + hkrespdate + '.  Unless we receive your instructions by this date, we will take no further action in this regard.\n'
            hactreq += 'Deadline Date: ' + hkduedate + '\nRequested Response Date: ' + hkrespdate
        else:
            hactreq = ''
            cnmatter = ''
        
        if mergeinfo[0] == 'true':
            voltxt = '\nPlease note that the deadline to file a voluntary amendment is '+ function_instance.formatDate(mergeinfo[1]) +'.  Please let us have your instructions before '+ function_instance.formatDate(mergeinfo[2]) +' if an amendment should be filed.\n'
            actreq = '\nACTION REQUIRED: Instructions for file Voluntary Amendment\n'
            actreq += 'Deadline Date: ' + function_instance.formatDate(mergeinfo[1]) + '\nRequested Response Date: ' + function_instance.formatDate(mergeinfo[2])
        else:
            voltxt = ''
            actreq = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'volAmend' : voltxt,
            'cnMatter' : cnmatter,
            'salutation' : '',
            'hkactionReq' : hactreq,
            'actionReq' : actreq,
            'cpubDate' : patent.opipublicationdate,
            'cpubNo' : patent.pubno,
            'This.upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
        })
        return replace
    
# FF Report Out - Notice of Allowance Received
class ffNoticeOfAllancRcvdFp:
    def ffNoticeOfAllancRcvdFp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        currtxt = ''
        if mergeinfo[5] == 'true':
            currtxt += 'In view of the current pending status of corresponding applications, you may be eligible for voluntary participation in the Patent Prosecution Highway (PPH) program to possibly reduce costs and obtain accelerated examination. Please contact us to discuss your options should you wish to further explore this program.'

        if mergeinfo[4] == 'true':
            currtxt += '\n\nWe will pay any annuity or maintenances fees on your behalf unless instructed to the contrary. \n\n'
        else:
            currtxt += '\n\nIt is our understanding that you will be responsible for any annuity/maintenance fee payments.  If our understanding is incorrect, please advise us.\n\n'
            
        divtxt = ''
        if mergeinfo[0] == 'true':
            divtxt = 'If you are interested in filing a divisional application, please provide your instructions by . In the absence of your instructions, we will not file a divisional application.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'cdueDate' : function_instance.formatDate(mergeinfo[1]),
            'crespDate' : function_instance.formatDate(mergeinfo[2]),
            'currFutPend' : currtxt,
            'divTxt' : divtxt
        }) 
        return replace

# FF Report Out - Annuity or Patent Expiration Communication
class anncomm:
    def anncomm(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        replace = {}
        replace.update(function_instance.cmgfill(matter))
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            
        })
        return replace
    
# PTO Form - Statement Under 3.73(b)
class StatementUnder373b:
    def StatementUnder373b(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        if mergeinfo[0] == 'oth':
            org = mergeinfo[3]
        else:
            if mergeinfo[0]:
                org = mergeinfo[0]
        
        replace = {}
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({
            'orgType' : org,
        })
        return replace
    
# Report Out - Decision on Appeal
class DecisionAppeal:
    def DecisionAppeal(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            activity = function_instance.getactivityid(matter_data, 'APDR')
            smryone = activity.smryonevalue
            instdue = (smryone + relativedelta(months=1)).strftime('%B %d, %Y')
            doadate = smryone.strftime('%B %d, %Y')
            rrrrdate = (smryone + relativedelta(months=2)).strftime('%B %d, %Y')
            
        except:
            instdue = 'No date found'
            doadate = 'No date found'
            rrrrdate = 'No date found'
        
        if mergeinfo[0] == 'TRUE':
            acttxt = 'Please provide authorization and instructions by '+ instdue +' for filing a response to the Decision on Appeal.  The final due date for response is '+ rrrrdate +'. This date is NOT extendable. Failure to respond will result in abandonment of the application.'
            addtxt1 = 'When you have reviewed these materials, please call '
            addtxt2 = ' to discuss the appropriate response.'
            optiontxt = '\nOPTIONS FOR RESPONSE: Appeal the Decision to the Court of Appeals for the Federal Circuit; Request a Rehearing; Reopen prosecution by filing a Request for Continued Examination; Allow the application to go abandoned.\n'
            dectxt = 'Affirmed'
            
        else:
            acttxt = 'None at this time'
            addtxt1 = 'If you have any questions or comments, please contact '
            addtxt2 = '.'
            optiontxt = ''
            dectxt = 'Reversed'
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'doaDate' : doadate,
            'actTxt' : acttxt,
            'addtxt1' : addtxt1,
            'addtxt2' : addtxt2,
            'optionsTxt' : optiontxt,
            'decTxt' : dectxt
        })
        return replace
    
# FF Report Out - Letter to Send Formal Documents
class ffLtrSndFormalDocs:
    def ffLtrSndFormalDocs(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        if mergeinfo[0] != '':
            duedateln = 'The deadline to file the Power of Attorney is ' + function_instance.formatDate(mergeinfo[0])
            duedate = '\nDeadline Date: ' + function_instance.formatDate(mergeinfo[0])
        else:
            duedateln = ''
            duedate = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'cdueDate' : duedate,
            'crespDate' : function_instance.formatDate(mergeinfo[1]),
            'cdueDateLn' : duedateln,
            'salutation' : ''
        })
        return replace

# Letter - Client Agreement Letter
class clientagree_sp:
    def clientagree_sp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'salutation' : '',
            'retainerParagraph' : '',
            
        })
        return replace

# Header - Generic Header
class genericheader:
    def genericheader(self,matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'headerText' : mergeinfo[1],
            'mailStopText' : mergeinfo[2],
            'depAccount' : function_instance.depnumFill(matter_data),
            'properApplicant' : 'Applicant',
            'submitText' : 'submits',
            'properPossessiveApplicant' : 'Applicant\'s'
        })
        return replace
    
# Header - Allowed Claims
class allowedclaims:
     def allowedclaims(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace
    
# FF Report Out - EP Approval of Text (Rule 71(3))
class ffepApprovalofTxt:
    def ffepApprovalofTxt(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'cdueDate' : function_instance.formatDate(mergeinfo[0]),
            'crespDate' : function_instance.formatDate(mergeinfo[1])
        })
        return replace
    
# FF Report Out - Notice to Request Exam
class reqexamdue:
    def reqexamdue(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        try:
            reqactivity = function_instance.getactivityid(matter_data, "REXN")
            task = Task.objects.using('FIP').filter(activityid = reqactivity.activityid)
            docket = Docketentry.objects.using('FIP').filter(taskid = task.taskid, docketentrytypeid = '2')
            if docket:
                reqduedate = reqactivity.smryonevalue.strftime('%B %d, %Y')
                priordate = (reqduedate + relativedelta(weeks=2)).strftime('%B %d, %Y')
        except:
            reqduedate = ''
            priordate = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'REXNdueDate' : reqduedate,
            'PriorDueDate2Week' : priordate,
        })
        return replace

# PCT - Foreign Filing Order Form
# not filling because of tables in doc
class pctorderform:
    def pctorderform(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)


        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace
    
# Report Out - Miscellaneous Items Due
class miscitemsdue:
    def miscitemsdue(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        if 'Mail' in mergeinfo[0]:
            datemail = function_instance.extract_date(mergeinfo[0])
            datemail = datemail.split('/')
            datemail = datemail[2] + '-' + datemail[0] + '-' + datemail[1]
        else:
            datemail = 'MAIL DATE NOT FOUND'
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'dueDate' : function_instance.formatDate(mergeinfo[4]),
            'requestedDate' : function_instance.formatDate(mergeinfo[5]),
            'activityName' : mergeinfo[1].split(';')[0],
            'dateMailed' : function_instance.formatDate(datemail),
        })
        return replace

# Report Out - Corrected Filing Receipt
class correctedfrreport:
    def correctedfrreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.cmgfill(matter))
        replace.update({
            'salutation' : '',
            'correctionText' : mergeinfo[0]
        })
        return replace

# Trademark - Basic Report Out Letter
class tm_basicreport:
    def tm_basicreport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        selnames = mergeinfo[1].replace(';','\n')
        
        seldates = mergeinfo[0].split(';')
        finaldates = ''
        for date in seldates:
            try:
                actdate = function_instance.extract_date(date)
                date_object = datetime.strptime(actdate, "%m/%d/%Y")
                finaldates += date_object.strftime("%B %d, %Y") + '\n'
            except:
                finaldates += 'NO DATE FOUND' + '\n'

        rows = zip(finaldates.split('\n'), selnames.split('\n'))
        formatted_data = "\n".join(["\t\t\t".join(row) for row in rows])

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'activityname' : mergeinfo[0],
            'dateFiled' : formatted_data,
            'docFiled' : '',   
        })
        return replace

# IDS - 1449 Form-Cited in Parent
# Tables not filling
class ids_citedparent_2012:
    def ids_citedparent_2012(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace

# Letter - FF Send Items to Associate
class ffSndItmsToAssoc:
    def ffSndItmsToAssoc(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        docs = [mergeinfo[0], mergeinfo[1], mergeinfo[2], mergeinfo[3], mergeinfo[4]]
        
        docnames = ''
        count = 0
        for doc in docs:
            if doc != '':
                count += 1
                docnames += '\t' + str(count) + '. ' + doc + '\n'
                
        if mergeinfo[5]:
            duedate = 'by the ' + function_instance.formatDate(mergeinfo[5]) + ' deadline'
        else:
            duedate = 'at your earliest convenience'
                
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.cmgfill(matter))
        replace.update(function_instance.ffparafill(matter))
        replace.update({
            'documentName' : docnames,
            'cdeadLine' : 'Kindly see to the prompt filing of the enclosed document(s) ',
            'dueDate' : duedate,
            'faRecipientTitle' : '',
            
        })
        return replace

# Formal Document - BSC Combined Assn/Dec -App filed on/after Sept. 16, 2012
# inventors appearing on new page
class BSCCombinedAssnDec:
    def BSCCombinedAssnDec(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({

        })
        return replace
    
# FF Report Out - Office Actions Received (AU or NZ)
class ffOfficeActRcvdAuNz:
    def ffOfficeActRcvdAuNz(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        if mergeinfo[7] == 'true':
            citeref = 'and cited references '
        else:
            citeref = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'activityName' : mergeinfo[1].split(';')[0],
            'cdueDate' : mergeinfo[5],
            'crespDate' : mergeinfo[6],
            'actionType' : mergeinfo[4],
            'citedRef' : citeref,
            'salutation' : ''
        })
        return replace

# Formal Document - ADI Assignment
# priority not filling correctly
class adiassign:
    def adiassign(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        try:
            relatedmatter = Relatedmatter.objects.using('FIP').filter(primarymatterid = matter.matterid)[0]
            primatter = function_instance.matterFill(relatedmatter.relatedmatterid)
            pridate = primatter.fileddate.strftime("%B %d, %Y")
            priser = primatter.serialnumber
            pricountry = primatter.country
            prititle = primatter.title
        except:
            pridate = ''
            priser = ''
            pricountry = ''
            prititle = ''
        
        prioritytxt = ' , and which are described in a patent application filed on '+ pridate +', which application was assigned '+ pricountry +' application serial number '+ priser +', and which is titled '+ prititle +'<<priorCont>>'
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({
            'priorInformation' : prioritytxt,
            'inventorNameList' : ''
        })
        return replace
    
# Micron Allowance Recommendation - Foreign
class micnffallow:
    def micnffallow(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        try:
            gen = FvMatter4.objects.using('FIP').get(recordid = matter_data.matterid)
            gencat3 = gen.generic_category_3
        except:
            gencat3 = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'DueDate' : function_instance.formatDate(mergeinfo[0]),
            'totalclaims' : mergeinfo[1],
            'independent' : mergeinfo[2],
            'prosecutionItem' : mergeinfo[4],
            'GenCat3' : gencat3
        })
        return replace
    
# PTO Form - Certification and Request for Prioritized Examination (AIA/424)
class priorexam2012:
    def priorexam2012(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({
            'SAName' : mergeinfo[1]
        })
        return replace 
    
# Header - Preliminary Amendment
class prelimamend:
    def prelimamend(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        amendtxt = 'PRELIMINARY AMENDMENT'
        if mergeinfo[1] == 'true':
            amendtxt = 'SUPPLEMENTAL PRELIMINARY AMENDMENT'
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'amendmentText' : amendtxt,
            'mailStopText' : mergeinfo[2],
            'upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'preperApplicant' : 'Applicant',
            'submitText' : 'submits'
        })
        return replace

# FF Report Out - Original Letters Patent (OLP)
# Not done
class ffOlp:
    def ffOlp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        resptxt = 'It is our understanding that you will be responsible for the payment of the renewal fees for this patent.  As such, we have not entered this date into our computerized docketing system.  If our understanding is incorrect, please advise immediately. '
        if mergeinfo[0] == 'true':
            resptxt = 'With regard to the maintenance fees, unless we hear from you to the contrary, we will contact you closer to the deadline date for your payment instructions. '
        
        try:
            expdate = (matter_data.fileddate + relativedelta(years=20)).strftime('%B %d, %Y')
        except:
            expdate = ''
            
        resptxt += 'If a supplemental sheet is enclosed, please review the details relating to working requirements, compulsory licenses and marking requirement as there are dates that will affect the patent.  Please contact us if you have any questions about the information and dates noted in the supplemental sheet.  Unless instructed in writing, we will not send any further reminders regarding the deadlines and requirements for working and/or marking your patent. '
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'annuDate' : function_instance.formatDate(mergeinfo[1]),
            'expirDate': expdate,
            'claimNo' : mergeinfo[2],
            'countryList' : '',
            'slwResp' : resptxt,
            'applicant' : ''
        })
        try:
            replace.update(function_instance.applicantfill(matter, 1))
        except:
            pass
        return replace

# Transmittal - Communication Regarding Incorrect Notice of Recordation
class incorrectrecd:
    def incorrectrecd(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            assnact = Activity.objects.using('FIP').filter(matterid = matter.matterid, code__icontains = 'ASSN')[0]
            assndate = ''
            if 'Mailed' in assnact.smryonelabel:
                assndate = assnact.smryonevalue.strftime("%B %d, %Y")
        except:
            assndate = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'dueDate' : assndate
        })
        return replace

# Header - Communication Regarding Filing of Priority Document
# Not done
class CommFilingPriDoc:
    def CommFilingPriDoc(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)


        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({
            'mailStopText' : mergeinfo[0]
        })
        return replace
    
# MS Post Allowance Recommendation
class mspostallow:
    def mspostallow(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        if mergeinfo[0] == 'TRUE':
            cancel = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({

        })
        return replace
        
# Formal Document - ADI Assignment
class adiassign:
    def adiassign(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        priortxt = ', and which are described in a patent application filed on '+ matter_data.fileddate +', which application was assigned US application serial number '+ matter_data.serialnumber +', and which is titled '+ matter_data.title +', and which are described in a patent application filed on '+ matter_data.fileddate +', which application was assigned US application serial number '+', and which is titled '+''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.inventorInfo(matter , 1))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({
            'priorInformation' : priortxt,
        })
        return replace
        
# Letter - Send General POA- App filed on/after Sep. 16, 2012
class LtrGeneralPOA:
    def LtrGeneralPOA(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        try:
            lrtact = Activity.objects.using('FIP').filter(matterid = matter.matterid, code__icontains = 'LFDC')[0]
        except:
            pass
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.cmgfill(matter))
        replace.update({
            'salutation' : '',
            'returnDate' : (date.today() + relativedelta(weeks=2)).strftime('%B %d, %Y'),
            
        })  
        return replace
    
# Formal Document - Micron Declaration Using an ADS
class microndec:
    def microndec(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })  
        return replace
    
# FF Report Out - Laid Open for Public Inspection
class ffapplaidopen:
    def ffapplaidopen(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        duedate = ''
        respdate = ''
        acttxt = 'None at this time '
        loexamdue = ''
        if mergeinfo[2] == 'true':
            duedate = '\nDeadline Date: ' + function_instance.formatDate(mergeinfo[3])
            respdate = '\nRequested Response Date: ' + function_instance.formatDate(mergeinfo[4])
            acttxt = 'Instructions to file the Request for Examination '
            loexamdue = '\nA request for examination has not yet been filed in connection with this application.  Such a request must be filed no later than '+ function_instance.formatDate(mergeinfo[3]) +' or the application will become abandoned.  Please provide us with your instructions by '+ function_instance.formatDate(mergeinfo[4]) +', so that we may authorize the associate to file the request for examination.\n'
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.cmgfill(matter))
        replace.update({
            'salutation' : '',
            'actionReq' : acttxt,
            'cdueDate' : duedate,
            'crespDate' : respdate,
            'openDate' : function_instance.formatDate(mergeinfo[0]),
            'openNo' :  mergeinfo[1],
            'loexamdue' : loexamdue
        })  
        return replace
    
# FF Report Out - Notice of Acceptance (AU/NZ)
class ffNoticeOfAcceptAuNzFp:
    def ffNoticeOfAcceptAuNzFp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        currtxt = ''
        # Au
        if mergeinfo[0] == 'true':
            acttxt = 'Instructions to pay the Acceptance Fees and file Divisional Applications (Optional)'
            deadline = '\nDeadline Date: ' + function_instance.formatDate(mergeinfo[2])
            reqresp = '\nRequested Response Date: ' + function_instance.formatDate(mergeinfo[3])
            auornztxt = 'Acceptance of the application was advertised in the Australian Official Journal on ' + function_instance.formatDate(mergeinfo[1]) + '.  Any interested party may file an opposition to the patentability of the application for a period of three months following advertisement.  If no opposition is filed, the final date for sealing will be ' + function_instance.formatDate(mergeinfo[2]) + '.  Please provide us with your instructions to pay the fees by ' + function_instance.formatDate(mergeinfo[3])
            auornztxt = 'Please note that if any divisional applications need to be filed, they must be filed by the final date of sealing i.e. ' + function_instance.formatDate(mergeinfo[2])
            if mergeinfo[4] == 'true':
                currtxt = 'In view of the current pending status of corresponding applications, you may be eligible for voluntary participation in the Patent Prosecution Highway (PPH) program to possibly reduce costs and obtain accelerated examination. Please contact us to discuss your options should you wish to further explore this program.'
            
        # Nz
        if mergeinfo[6] == 'true':
            acttxt = 'None at this time.'
            deadline = ''
            reqresp = ''
            auornztxt = 'Acceptance of the application was advertised in the New Zealand Patent Office Journal No. 1 on ' + function_instance.formatDate(mergeinfo[8]) + '.  Any interested party may file an opposition to the patentability of the application for a period of three months following advertisement.  If no opposition is filed, the New Zealand associate will automatically pay the sealing fee without further instruction.'
            
        if mergeinfo[5] == 'true':
            currtxt += '\n\nWe will pay any annuity or maintenances fees on your behalf unless instructed to the contrary.\n\n'
        else:
            currtxt += '\n\nIt is our understanding that you will be responsible for any annuity/maintenance fee payments.  If our understanding is incorrect, please advise us.\n\n'            
            
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'activityName' : '',
            'salutation' : '',
            'actionReq' : acttxt,
            'cdueDate' : deadline,
            'crespDate' : reqresp,
            'auornzSelect' : auornztxt,
            'currFutPend' : currtxt
        })  
        return replace

# PCT - Report Out Basic Letter
class PCTRptOutBasicLtr:
    def PCTRptOutBasicLtr(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        selnames = mergeinfo[1].replace(';','\n')
        
        seldates = mergeinfo[0].split(';')
        finaldates = ''
        for date in seldates:
            try:
                actdate = function_instance.extract_date(date)
                date_object = datetime.strptime(actdate, "%m/%d/%Y")
                finaldates += date_object.strftime("%B %d, %Y") + '\n'
            except:
                finaldates += 'NO DATE FOUND' + '\n'

        rows = zip(finaldates.split('\n'), selnames.split('\n'))
        formatted_data = "\n".join(["\t\t\t".join(row) for row in rows])
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'dateFiled' : formatted_data,
            'activityName' : (mergeinfo[1]).replace(';',', '),
        })  
        return replace

# Trademark - Report Out Miscellaneous Items Received
class tmrecdReport:
    def tmrecdReport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        selnames = mergeinfo[1].replace(';','\n')
        
        seldates = mergeinfo[0].split(';')
        finaldates = ''
        for date in seldates:
            try:
                actdate = function_instance.extract_date(date)
                date_object = datetime.strptime(actdate, "%m/%d/%Y")
                finaldates += date_object.strftime("%B %d, %Y") + '\n'
            except:
                finaldates += 'NO DATE FOUND' + '\n'

        rows = zip(finaldates.split('\n'), selnames.split('\n'))
        formatted_data = "\n".join(["\t\t".join(row) for row in rows])

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'dateMailed' : formatted_data,
            'This.MarkType' : '',
            'docReceived' : mergeinfo[1].split(';')[0]
        })
        return replace
    
# Trademark - Notice of Change of Counsel
class TM_ChgCounsel:
    def TM_ChgCounsel(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        try:
            replace.update(function_instance.applicantfill(matter, 1))
        except:
            replace.update({
                'applicant' : '',
            })  
        replace.update({
            'This.MarkType' : '',
            'userName' : '',
            'owner' : ''
        })  
        return replace
    
# Trademark - Report Notice of Publication
class TM_NoticeofPubRep:
    def TM_NoticeofPubRep(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        patent = function_instance.patentFill(matter_data)
        pubno = patent.pubno
        try:
            pubdate = (patent.pubdate).strftime('%B %d, %Y')
        except:
            pubdate = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.cmgfill(matter))
        replace.update({
            'pubDate' : pubdate
        })
        return replace

# Trademark - Report Office Action Received
class TM_OaReport:
    def TM_OaReport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        actiontxt = 'Non-Final Office Action'
        if mergeinfo[0] == 'YES':
            actiontxt = 'Final Office Action'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'action' : actiontxt
        })
        return replace

# Report Out - Ex Parte Quayle
class expartereport:
    def expartereport(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            activity = function_instance.getactivityid(matter_data, 'EPQA')
            epqadte = (activity.smryonevalue).strftime('%B %d, %Y')
            instdte = (epqadte + relativedelta(months=1)).strftime('%B %d, %Y')
            epqa2dte = (epqadte + relativedelta(months=2)).strftime('%B %d, %Y')
        except:
            epqadte = ''
            instdte = ''
            epqa2dte = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'instDate' : instdte,
            'exparteDate' : epqa2dte,
            'exparte2Mo' : epqa2dte,
        })
        return replace

# Header - Request for Patent Term Adjustment
class reqtermadj:
    def reqtermadj(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            activity = function_instance.getactivityid(matter_data, 'PPTA2')
            pptadte = (activity.smryonevalue).strftime('%B %d, %Y')

        except:
            pptadte = 'NO PPTA2 Activity'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'depAccount' : function_instance.depnumFill(matter_data),
            'upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
            'currentMo' : datetime.now().strftime("%B"),
            'currentYr' : datetime.now().year,
            'certificateText' : 'filed using the USPTO\'s electronic filing system EFS-Web, and is ',
            'dueDate' : pptadte
        })
        return replace

# Letter - Request for Instructions (CMG Follow-up Reminder: FF/Conversion)
class ffremind:
    def ffremind(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            relatedmatter = Relatedmatter.objects.using('FIP').filter(primarymatterid = matter.matterid, relationdesc__icontains = 'Priority')[0]
            primatter = function_instance.matterFill(relatedmatter.relatedmatterid)
            pridate = primatter.fileddate.strftime("%B %d, %Y")
            priser = primatter.serialnumber
        except:
            pridate = ''
            priser = ''
            
        conversion = 'INTERNATIONAL FILING AND NON-PROVISIONAL CONVERSION '
        nonprov1 = 'regular non-provisional and'
        nonprov2 = 'or regular non-provisional U.S.'
        rptout = 'Instructions Needed - U.S. Non-Provisional/Foreign Filing'
        if mergeinfo[3] == 'true':
            conversion = 'INTERNATIONAL FILING '
            nonprov1 = ''
            nonprov2 = ''
            rptout = ' Foreign Filing Instructions Needed'

        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'earlyPriorFilingDate' : pridate,
            'instDate' : function_instance.formatDate(mergeinfo[1]),
            'ffDueDate' : function_instance.formatDate(mergeinfo[0]),
            'prevDate' : function_instance.formatDate(mergeinfo[2]),
            'cFFNonProvText2' : nonprov2,
            'cFFNonProvText1' : nonprov1,
            'earlyPrioSerialNo' : priser,
            'conversionType' : conversion,
            'rptout' : rptout
        })
        return replace

# PCT - Report Out Filing Receipt
class ReportOutFilingReceipt:
    def ReportOutFilingReceipt(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'activityName' : 'PCT Filing Receipt'
        })
        return replace

# Letter - Request for Instructions (FF/NS Email to Client)
class ltrFFNS:
    def ltrFFNS(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace
    
# SAP Filing Summary
class sapsummary:
    def sapsummary(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            targactivity = function_instance.getactivityid(matter_data, 'TARG')
            targetdate = targactivity.smryonevalue.strftime("%B %d, %Y")
        except:
            targetdate = ''
            
        try:
            bardactivity = function_instance.getactivityid(matter_data, 'BARD')
            barddate = bardactivity.smryonevalue.strftime("%B %d, %Y")
        except:
            barddate = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.correspondenceContactfill(matter))
        replace.update(function_instance.copyContactfill(matter))
        replace.update({
            'TARG' : targetdate,
            'BARD' : barddate
        }) 
        return replace
    
# Email - Send Order Letter to Associate (New)
class sendorderletter:
    def sendorderletter(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        try:
            relatedmatter = Relatedmatter.objects.using('FIP').filter(primarymatterid = matter.matterid, relationdesc__icontains = 'Priority')[0]
            relmatter = function_instance.matterFill(relatedmatter.relatedmatterid)
            reldate = relmatter.fileddate.strftime("%B %d, %Y")
            relser = relmatter.serialnumber
            relcountry = relmatter.countryname
            
        except:
            reldate = ''
            relser = ''
            relcountry = ''
        
        honunotreg = ''
        if mergeinfo[2] == '2':
            honunotreg = 'Access to the HONU reporting platform is by invitation only. If your firm has not yet received an invitation to report directly to the HONU platform, please let us know immediately and we can organise for an invitation to be sent to your firm.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.applicantfill(matter, 1))
        replace.update(function_instance.ffparafill(matter))
        replace.update({
            'salutation' : '',
            'DEADLINEDATE' : function_instance.formatDate(mergeinfo[1]) + '('+ mergeinfo[0] +' MONTH DEADLINE) ',
            'relSerial' : relser,
            'relFiled' : reldate,
            'relCountry' : relcountry,
            'honuNotReg' : honunotreg
        })
        return replace

# FF Report Out - Miscellaneous Items Due
class ffMiscItemsDue:
    def ffMiscItemsDue(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'actionType' : mergeinfo[4],
            'cdueDate' : function_instance.formatDate(mergeinfo[5]),
            'crespDate' : function_instance.formatDate(mergeinfo[6]),
            'activityname' : (mergeinfo[1].split(';'))[0]
        })
        return replace

# PTO Form - Transmittal of POA (PTO/AIA/82A)
class poatransmit:
    def poatransmit(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({

        })
        return replace
    
# MS Email - PAR to MS
# Need usename
class mspar:
    def mspar(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.cmgfill(matter))
        replace.update(function_instance.counselfill(matter))
        replace.update({
            'userName' : '',
        })
        return replace

# FF Report Out - Original Letters Patent (OLP) for EP
# needs work
class epOLP:
    def epOLP(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            expdate = (matter_data.fileddate + relativedelta(years=20)).strftime('%B %d, %Y')
        except:
            expdate = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'annuDate' : function_instance.formatDate(mergeinfo[1]),
            'exprirDate' : expdate,
            'claimNo' : mergeinfo[3],
        })
        return replace

# MS Email - To Client
# Might need different para data
class msemails:
    def msemails(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.counselfill(matter))
        replace.update(function_instance.clientParafill(matter))
        replace.update({
            'Item being reported' : mergeinfo[1].split(';')[0]
        })
        return replace

# PTO Form - Notice of Appeal (AIA/31)
class noticeofAppeal:
    def noticeofAppeal(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        entitystatus = function_instance.entityfill(matter)

        microfee = ''
        smallfee = ''
        if(entitystatus == 0):
            smallfee = '362.00'
        if(entitystatus == 1):
            microfee = '181.00'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[1]))
        replace.update({
            'depAccount' : function_instance.depnumFill(matter_data),
            'smallFee' : smallfee,
            'microFee' : microfee,
            'echoSignatureDatePara' : '',
            'echoSignaturePara' : ''
        })
        return replace

# Letter - Email Filing Confirmation to Associate
class fa_confirm:
    def fa_confirm(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'recipientName' : '',
            'fullName' : ''
        })
        return replace
    
# Formal Document - Intel Inventor to Intel Corporation Assignment
class intelcorp:
    def intelcorp(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()


        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'countryText' : '',
        })
        return replace

# Formal Document - Zimmer Combined Dec Assignment
class zimmerdec:
    def zimmerdec(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()


        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({

        })
        return replace
    
# Microsoft Application Filing Summary
class msfilingsummary:
    def msfilingsummary(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()



        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.inventorInfo(matter , 1))
        replace.update({
            'Abstract' : '',
            'priorityMatterList' : ''
        })
        return replace

# PCT - Power of Attorney NEW
class pctpoa_new:
    def pctpoa_new(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        if mergeinfo[5] == 'true':
            genpoa = 'GENERAL POWER OF ATTORNEY'
        else:
            genpoa = 'POWER OF ATTORNEY'
        
        if mergeinfo[6] == 'true':
            revpoa = 'revokes all former Powers of Attorney and appoints the following attorneys/agents of the firm of Schwegman Lundberg & Woessner (SLW) as Agents for so long as they remain with SLW, to act before all competent International Authorities via the U.S. Receiving Office and to make and receive payments on behalf of, in connection with:'
            revpoa += '\n\n\t(a) any and all International Applications filed by one or more of the named attorneys/agents acting on behalf of; and\n\n\t(b) any and all International Applications previously on file but into which this General Power of Attorney document is filed by one or more of the named attorneys/agents acting on behalf of: '
        else:
            revpoa = 'appoints the following attorneys/agents of the firm of Schwegman Lundberg & Woessner (SLW) as Agents for so long as they remain with SLW, to act before all competent International Authorities via the U.S. Receiving Office and to make and receive payments on behalf of, in connection with International Application No. <<serialNo>>, Attorney Reference No. <<matterNo>>, and entitled <<title>>'
            
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[7]))
        replace.update({
            'assigneeCity' : mergeinfo[0],
            'assigneeState' : mergeinfo[1],
            'assigneeCountry' : mergeinfo[2],
            'authSignor' : mergeinfo[3],
            'authSignorTitle' : mergeinfo[4],
            'cGenPOA' : genpoa,
            'revApt' : 'Appointment of Agent\n',
            'agentGS' : '',
            'assignee' : '',
            'revPoA' : revpoa
        })
        return replace

# Nike Action Required (HTML)
class nikeaction_new:
    def nikeaction_new(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()



        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'dueDate' : function_instance.formatDate(mergeinfo[4]),
            'deadDueDate' : function_instance.formatDate(mergeinfo[5]),
            'documentName' : mergeinfo[1],
            'Other Information' : ''
        })
        return replace
    
# FF Report Out - EP Search Report and Opinion
class ffEPSrchRptandOpinion:
    def ffEPSrchRptandOpinion(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        pleasenote = ''
        if mergeinfo[3] == 'true':
            pleasenote = 'PLEASE NOTE:  A response to the search report and opinion is mandatory.  If a response is not filed, the application will be withdrawn.'

        intent = ''
        if mergeinfo[0] == 'true':
            intent = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'cdueDate' : function_instance.formatDate(mergeinfo[1]),
            'crespDate' : function_instance.formatDate(mergeinfo[2]),
            'salutation' : '',
            'deadLineConfirmTop' : '',
            'pleaseNote' : pleasenote,
            'deadLineConfirmBot' : ''
        })
        return replace
    
# Micron Allowance email for inventors (first allowance)
class micnallow:
    def micnallow(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace

# PTO Form - Declaration - Apps filed on/or after Sept. 16, 2012 (AIA/01)
class aiashortdecl:
    def aiashortdecl(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({

        })
        return replace

# Intel - Send Formal Document(s)
class intelformal:
    def intelformal(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.cmgfill(matter))
        replace.update({
            'returnDate' : function_instance.formatDate(mergeinfo[0])
        })
        return replace
    
# POA - Combined Transmittal and PTO/AIA/82A
class poa82combined:
    def poa82combined(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        replace = {}
            
        adddocsodd = []
        adddocseven = []
        mergedata = []
        split_found = False
        index = 0

        for entry in mergeinfo:
            if entry == 'split':
                split_found = True
                continue
            if split_found:
                mergedata.append(entry)
            else:
                if index % 2 == 0:
                    adddocseven.append(entry)
                else:
                    adddocsodd.append(entry)
                index += 1
            
        # Finish
        docs = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        i = 0
        # Assuming adddocs is defined somewhere above
        for doc in adddocseven:
            replace.update({
                'doc' + docs[i] + 'X': 'X',
                'doc' + docs[i] + 'Text': doc + ' (' + adddocsodd[i] + ' pg)'
            })
            i += 1

        # Fill remaining unfilled docs with blank values
        for j in range(i, len(docs)):
            replace.update({
                'doc' + docs[j] + 'X': '',
                'doc' + docs[j] + 'Text': ''
            })
            
        mailstop = mergedata[4]
        if mergedata[4] == 'Other':
            mailstop = mergedata[5]
            
        xmitx = ''
        xmittxt = ''
        if int(mergedata[2]) > 0:
            tpg = 'pg'
            if int(mergedata[2]) > 1:
                tpg = 'pgs'
            xmitx = 'X'
            xmittxt = 'Transmittal for Power of Attorney to one or More Registered Practioners (PTO/AIA/82) ('+ mergedata[2] +' '+ tpg +'.)'
            
        poax = ''
        poatxt = ''
        if int(mergedata[3]) > 0:
            ppg = 'pg'
            if int(mergedata[2]) > 1:
                ppg = 'pgs'
            poax = 'X'
            poatxt = 'Transmittal for Power of Attorney to one or More Registered Practioners (PTO/AIA/82) ('+ mergedata[3] +' '+ ppg +'.)'
        
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergedata[0]))
        replace.update({
            'mailStopText' : mailstop,
            'xmitX' : xmitx,
            'xmitText' : xmittxt,
            'POAX' : poax,
            'POAText' : poatxt,
            'depAccount' : function_instance.depnumFill(matter_data),
            'postcardX' : '',
            'postcardText' : '',
            'SAName' : mergedata[6]
        })
        return replace
    
# Request Retainer US Items
class retainer:
    def retainer(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({

        })
        return replace
    
# Formal Document - Microsoft Assignment
class msassn:
    def msassn(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        invname = ''
        try:
            invname = ", ".join(mergeinfo[1:])
        except:
            pass
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'inventorName' : invname
        })
        return replace

# PTO Form - Express Abandonment (AIA/24, 24A, 24B)
class expressaban:
    def expressaban(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'depAccount' : function_instance.depnumFill(matter_data),
        })
        return replace
    
class expressaban2:
    def expressaban2(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'depAccount' : function_instance.depnumFill(matter_data),
        })
        return replace
    
# Letter - Send POA (Matter Specific)
class poaMatter:
    def poaMatter(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'returnDate' : function_instance.formatDate(mergeinfo[0])
        })
        return replace

class cornellassnnew:
    def cornellassnnew(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        apptxt = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'applicationTypeText' : apptxt
        })
        return replace
    
# Intel EOU Questions to Inventors
class intelbasic:
    def intelbasic(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        codes = ['RCEF', 'ABRF', 'NPDPABR']
        for code in codes:
            try:
                activity = function_instance.getactivityid(matter_data, code)
                break
            except:
                pass
            
        try:
            noardte = (activity.smryonevalue + relativedelta(weeks=2)).strftime('%B %d, %Y')
        except:
            noardte = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'NOARDate' : noardte,
            'userName' : ''
        })
        return replace

# Formal Document - Notarial Certificate
class nsnotarialcert:
    def nsnotarialcert(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        
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
        
        replace.update(function_instance.ffcmgFill(matter))
        replace.update({
            'inventorList' : selinv
        })
        return replace
    
# PTO Form - Authorization for Internet Communications (SB/439)
class internetauth:
    def internetauth(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        sadata = function_instance.rvwmatterpersonnelFill(matter_data)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'SAName' : sadata.fname + ' ' + sadata.lname
        })
        return replace
    
# Header - Change of Entity Status
class entstatus:
    def entstatus(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        if mergeinfo[2] == '':
            fee1 = 0
        else:
            fee1 = int(mergeinfo[2])
        if mergeinfo[5] == '':
            fee2 = 0
        else:
            fee2 = int(mergeinfo[5])
        
        fee = fee1 + fee2
        withtxt = ''
        entytxt = ''
        willpay = ''
        repay = ''
        
        if mergeinfo[1] == 'true':
            fee = mergeinfo[2]
            withtxt = 'It has been brought to the attention of Applicant\'s Representatives that the small entity status is no longer appropriate in the above-identified application.  In accordance with the duty set forth in 37 C.F.R. § 1.27, the entitlement to small entity status is withdrawn.'
            entytxt = ''
            willpay = ''
            repay = ''
    
        if mergeinfo[4] == 'true':
            fee = mergeinfo[5]
            withtxt = ''
            entytxt = 'It has been brought to the attention of Applicant\'s Representatives that the above-identified application is eligible for small entity status in accordance with 37 C.F.R. § 1.27.'
            willpay = ''
            repay = ''
        
        if mergeinfo[1] == 'true' or mergeinfo[4] == 'true':
            deppay = 'Please charge '+ fee +' to Deposit Account '+ function_instance.depnumFill(matter_data) +' for the total deficiency payment owed resulting from the previous erroneous payment of small entity fees.'

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[7]))
        replace.update({
            'mailStopText' : mergeinfo[0],
            'entityWithdrawText' : withtxt,
            'willPayText' : willpay,
            'depPayText' : deppay,
            'entityEstablishText' : entytxt,
            'repayText' : repay,
            'depAccount' : function_instance.depnumFill(matter_data)
        })
        return replace
    
# MS Email - Send Formal Papers (Post-Filing)
class msformal:
    def msformal(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.counselfill(matter))
        replace.update({
            'userName' : ''
        })
        return replace
    
# Intel - Report out Final Office Action
class intelfoa:
    def intelfoa(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        wireless = ''
        if mergeinfo[0] == 'TRUE':
            duedate = ''
            wireless = 'We have received a Final Office Action in the above referenced matter. Per Intel\'s new instructions you are required to provide the WTI Committee a Proposed Strategy/Response including a forwarded copy of the report out letter, pending claims and Office Action. The proposed strategy should be reviewed by the SLW PM prior to sending to the client and should be based on \'The Rights Patents\' Initiative. \n\nPlease create a proposed strategy/response for sending to the client 7-14 days prior to the 2 month deadline of ' + duedate + '\n'

        act = False
        for code in ['FOAR', 'FOAR-PE']:
            try:
                activity = function_instance.getactivityid(matter_data, code)
                if activity:
                    act = True
            except:
                continue
            
        foardte = ''
        foar2 = ''
        foar3 = ''
        if act == True:
            foardte = activity.smryonevalue.strftime("%B %d, %Y")
            foar2 = foardte + relativedelta(months=2)
            foar3 = foardte + relativedelta(months=3)

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'Wireless' : wireless,
            'foarDate' : foardte,
            'foar3Mo' : foar3,
            'foar2Mo' : foar2
        })
        return replace
    
# Patent - Notice of Change of Counsel
class patchgcounsel:
    def patchgcounsel(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        try:
            TMm = Trademark.objects.using('FIP').get(matterid = matter_data.matterid)
            tmreg = TMm.registrationno
        except:
            tmreg = ''

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'userName' : '',
            'TMRegNo' : tmreg
        })
        return replace

# IDS - QPIDS Form (PTO/SB/09)
class Qp_Ids:
    def Qp_Ids(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)

        idsrad = mergeinfo[2]

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[1]))
        replace.update({
            'depAccount' : function_instance.depnumFill(matter_data),
            'SAName' : mergeinfo[0]
        })
        return replace

# Formal Document - Caterpillar Assignment
class catassn:
    def catassn(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)


        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update(function_instance.inventorInfo(matter , 1))
        replace.update({
            'countryName' : matter_data.countryname,
            'provText' : '',
            'ASSIGNORTEXT' : 'FULLNAME OF SOLE OR FIRST ASSIGNOR',
            'inventorcitizen' : ''
        })
        return replace
     
# Microsoft Application Filing Summary
class msfilingsummary:
    def msfilingsummary(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)


        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.inventorInfo(matter , 1))
        replace.update({
            'PubFig' : '',
            'priorityMatterList' : '',
            'Abstract' : ''
        })
        return replace
    
# NOV - Email Template
class novemail:
    def novemail(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        if mergeinfo[4] == '1':
            purpose = 'Reporting Only'

        if mergeinfo[4] == '2':
            purpose = 'Action Required'

        patent = function_instance.patentFill(matter_data)
        pubno = patent.pubno
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'Purpose' : purpose,
            'pubtxt' : 'Publication No.',
            'pct' : '',
            'pubNo' : pubno,
            'actionName' : (mergeinfo[1].split(';'))[0]
        })
        return replace

# PTO Form - Request for Deferral of Examination (PTO/SB/37)
class deferRequest:
    def deferRequest(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[1]))
        replace.update({
            'deferralMonths' : mergeinfo[0],
            'depAccount' : function_instance.depnumFill(matter_data)
        })
        return replace
    
# Letter - Blank Letter
class blankletter:
    def blankletter(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        try:
            sal = mergeinfo[0]
        except:
            sal = ''
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : sal,
            'userName' : '',
            'CSZ' : '',
            'workAddr' : '',
            'recipientTitle' : '',
            'ccTag' : '',
            'ccName' : ''
        })
        return replace

# Header - Amendment Under 1.312
class amend37cfr:
    def amend37cfr(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[2]))
        replace.update({
            'dateNOAR' : function_instance.formatDate(mergeinfo[0]),
            'SAName' : mergeinfo[1],
            'upperFirmName' : 'Schwegman Lundberg & Woessner, P.A.',
        })
        return replace

# DOCKETING:  Bar Date Questionnaire
class bardateq:
    def bardateq(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'userName' : '',
            'responseDate' : mergeinfo[0],
        })
        return replace

# FF Report Out - Decision to Grant (EP) - Need Unitary Patent Instructions
class tm_unitaryGrant:
    def tm_unitaryGrant(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        matter_data = function_instance.matterFill(matter)
        
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            
        })
        return replace

# Header - Appeal Brief (Notice of Appeal filed after 1-22-2012)
class AppealBrief3:
    def AppealBrief3(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        patxt = ''
        if mergeinfo[3] != '':
            patxt = 'in response to the Notice of Panel Decision from Pre-Appeal Brief Review mailed on '+ function_instance.formatDate(mergeinfo[2]) +' and further '

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[4]))
        replace.update(function_instance.assigneefill(matter, 1))
        replace.update({
            'noaDate' : function_instance.formatDate(mergeinfo[1]),
            'oaDate' : function_instance.formatDate(mergeinfo[0]),
            'paDecisionText' : patxt,
            'rejectClaims' : mergeinfo[3],
            'properAppellant' : 'Appellant',
            'requestText' : 'requests',
            'referText' : 'refers'
        })
        return replace

# Letter - Audit Letter
class auditletter:
    def auditletter(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'currentDate' : function_instance.formatDate(str(date.today())),
            'effectiveDate' : function_instance.formatDate(mergeinfo[0]),
            'billedFees' : mergeinfo[1],
            'unbilledFees' : mergeinfo[2],
            
        })
        return replace
    
# Letter - Request for Instructions (Non-PCT FF)
class nonpct:
    def nonpct(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'salutation' : '',
            'dueDate' : '',
            'requestDate' : '',
            'WAInformal'  : '',
            'earlyPriorFilingDate' : '',
            'earlyPrioSerialNo' : ''
        })
        return replace
    
# Formal Document - Purdue Assignment
class purdueassn:
    def purdueassn(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update(function_instance.inventorInfo(matter, 1))
        replace.update({

        })
        return replace

# PTO Form - Nonpublication Request (PTO/SB/35)
class nonpubrequest:
    def nonpubrequest(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.esigncheck(mergeinfo[0]))
        replace.update({
            'certificateText' : 'This paper or fee is being filed on the date indicated above using the USPTO\'s electronic filing system EFS-Web, and is addressed to The Commissioner for Patents, P.O. Box 1450, Alexandria, VA 22313-1450.',
            'expressMailText' : ''
        })
        return replace      
    
# Trademark - US Report Notice of Allowance ITU
class tm_noticeallow:
    def tm_noticeallow(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'statementUseExtDue' : function_instance.formatDate(mergeinfo[0]),
            'instDate' : function_instance.formatDate(mergeinfo[1]),
            'salutation' : '',
            'classCode' : '',
            'classDescription' : ''
        })
        return replace     
    
# Report Out - Original Letters Patent
class OriginalPatReportNew:
    def OriginalPatReportNew(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        replace = {}
        # Fill Data
        matter_data = function_instance.matterFill(matter)

        # May need editing
        utilityText1 = "The patent will remain in effect for a term of twenty years from the date of the earliest filing.  To maintain the patent for its entire term, maintenance fees must be paid when due.  The fees are due as follows:"
        utilityFee1 = "3-1/2 years from the issue date"
        utilityFee2 = "7-1/2 years from the issue date"
        utilityFee3 = "11-1/2 years from the issue date"
        
        try:
            actname = function_instance.getactivityid(matter_data, 'OLPR').name
        except:
            actname = ''
        try:    
            if matter_data.fileddate and matter_data.fileddate > datetime(2015, 5, 13):
                designtxt = 'The term of a design patent extends up to a maximum of 15 years from the date of issue.", "The term of a design patent extends up to a maximum of 14 years from the date of issue.'
            else:
                designtxt = ''
        except:
            designtxt = ''
            
        cultxt = ''
        if mergeinfo[0] == 'TRUE':
            cultxt = 'Prior instructions have been received acknowledging SLW responsibility for payment of the maintenance fees through our preferred 3rd party provider, Black Hills AI (www.blackhills.ai).  If for any reason this process is no longer valid, please reach out to us expeditiously to confirm new instructions.'
        else:
            cultxt = 'Maintenance fees may be submitted by any recognized party, including a patentee or third party. Generally we refer clients to Black Hills AI (www.blackhills.ai) for maintenance payment services. However, this is in no way an endorsement of their services and you may choose to pay the maintenance fees directly or may have another third party administer payment. Therefore, if you haven\'t already done so, please provide instructions regarding who will be handling your maintenance fee payments.'
            
        # Need to add use case for answer
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'activityname' : actname,
            'THIS.title'  : matter_data.title,
            'designText' : designtxt,
            'utilityText1' : utilityText1,
            'utilityFee1' : utilityFee1,
            'utilityFee2' : utilityFee2,
            'utilityFee3' : utilityFee3,
            'cutilityText2' : cultxt,
            'salutation' : ''
        })
        return replace 
    
# FF Report Out - Decision to Grant (EP) - NEW
class EPDecisiontoGrant:
    def EPDecisiontoGrant(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()
        
        actreq = ''
        curr = ''       
        cinst = ''
        if mergeinfo[0] == 'false' and mergeinfo[1] == 'false' and mergeinfo[4] == '' and mergeinfo[2] == '':
            actreq = ''
            curr = 'Please be advised that the product(s) covered by the above granted patent application may be eligible in certain European countries for a Supplementary Protection Certificate (SPC). Eligible technologies are those subject to premarket regulatory approval, such as medicinal or plant products.  If you would like more information about SPC eligibility or requirements, please contact your regulatory attorney(s).\n\n'
        if mergeinfo[0] == 'true' and mergeinfo[1] == 'false' and mergeinfo[4] == '':
            actreq = ''
            curr = 'In view of the current pending status of corresponding applications, you may be eligible for voluntary participation in the Patent Prosecution Highway (PPH) program to possibly reduce costs and obtain accelerated examination. Please contact us to discuss your options should you wish to further explore this program.\n\nPlease be advised that the product(s) covered by the above granted patent application may be eligible in certain European countries for a Supplementary Protection Certificate (SPC). Eligible technologies are those subject to premarket regulatory approval, such as medicinal or plant products.  If you would like more information about SPC eligibility or requirements, please contact your regulatory attorney(s).\n\n'
        if mergeinfo[0] == 'false' and mergeinfo[1] == 'true' and mergeinfo[4] == '':
            actreq = '\nACTION REQUIRED:  PROVIDE DIVISIONAL INSTRUCTIONS IMMEDIATELY\n\nIf you are interested in filing a divisional application, please provide your instructions by <<respDate>>. In the absence of your instructions, we will not file a divisional application.\n\n'
            curr = 'Please be advised that the product(s) covered by the above granted patent application may be eligible in certain European countries for a Supplementary Protection Certificate (SPC). Eligible technologies are those subject to premarket regulatory approval, such as medicinal or plant products.  If you would like more information about SPC eligibility or requirements, please contact your regulatory attorney(s).\n\n'
        if mergeinfo[0] == 'false' and mergeinfo[1] == 'false' and mergeinfo[4] != '':
            actreq = '\nACTION REQUIRED:  VALIDATION INSTRUCTIONS BY <<datePlus1mo>>\n\nWe note that instructions for validation have not yet been received. The deadline to validate the above patent in various designated states is <<dueDate>>. Please provide us with a list of countries in which the European patent should be perfected so we may timely attend to validation country requirements, including possible full patent translation and execution of country specific power of attorney documents.\n\n'
            curr = 'Please be advised that the product(s) covered by the above granted patent application may be eligible in certain European countries for a Supplementary Protection Certificate (SPC). Eligible technologies are those subject to premarket regulatory approval, such as medicinal or plant products.  If you would like more information about SPC eligibility or requirements, please contact your regulatory attorney(s).\n\n'
        if mergeinfo[0] == 'true' and mergeinfo[1] == 'true' and mergeinfo[4] == '':
            actreq = '\nACTION REQUIRED:  PROVIDE DIVISIONAL INSTRUCTIONS IMMEDIATELY\n\nIf you are interested in filing a divisional application, please provide your instructions by <<respDate>>. In the absence of your instructions, we will not file a divisional application.\n\n'
            curr = ' In view of the current pending status of corresponding applications, you may be eligible for voluntary participation in the Patent Prosecution Highway (PPH) program to possibly reduce costs and obtain accelerated examination. Please contact us to discuss your options should you wish to further explore this program.\n\nPlease be advised that the product(s) covered by the above granted patent application may be eligible in certain European countries for a Supplementary Protection Certificate (SPC). Eligible technologies are those subject to premarket regulatory approval, such as medicinal or plant products.  If you would like more information about SPC eligibility or requirements, please contact your regulatory attorney(s).\n\n'
        if mergeinfo[0] == 'true' and mergeinfo[1] == 'false' and mergeinfo[4] != '':
            actreq = '\nACTION REQUIRED:  VALIDATION INSTRUCTIONS BY <<datePlus1mo>>\n\nWe note that instructions for validation have not yet been received. The deadline to validate the above patent in various designated states is <<dueDate>>. Please provide us with a list of countries in which the European patent should be perfected so we may timely attend to validation country requirements, including possible full patent translation and execution of country specific power of attorney documents.\n\n'
            curr = 'In view of the current pending status of corresponding applications, you may be eligible for voluntary participation in the Patent Prosecution Highway (PPH) program to possibly reduce costs and obtain accelerated examination. Please contact us to discuss your options should you wish to further explore this program.\n\nPlease be advised that the product(s) covered by the above granted patent application may be eligible in certain European countries for a Supplementary Protection Certificate (SPC). Eligible technologies are those subject to premarket regulatory approval, such as medicinal or plant products.  If you would like more information about SPC eligibility or requirements, please contact your regulatory attorney(s).\n\n'
        if mergeinfo[0] == 'false' and mergeinfo[1] == 'true' and mergeinfo[4] != '':
            actreq = 'ACTION REQUIRED:  PROVIDE DIVISIONAL INSTRUCTIONS IMMEDIATELY\n\nIf you are interested in filing a divisional application, please provide your instructions by <<respDate>>. In the absence of your instructions, we will not file a divisional application.\n\nACTION REQUIRED:  VALIDATION INSTRUCTIONS BY <<datePlus1mo>>\n\nWe note that instructions for validation have not yet been received. The deadline to validate the above patent in various designated states is <<dueDate>>. Please provide us with a list of countries in which the European patent should be perfected so we may timely attend to validation country requirements, including possible full patent translation and execution of country specific power of attorney documents.\n\n'
            curr = 'Please be advised that the product(s) covered by the above granted patent application may be eligible in certain European countries for a Supplementary Protection Certificate (SPC). Eligible technologies are those subject to premarket regulatory approval, such as medicinal or plant products.  If you would like more information about SPC eligibility or requirements, please contact your regulatory attorney(s).\n\n'
        if mergeinfo[0] == 'true' and mergeinfo[1] == 'true' and mergeinfo[4] != '':
            actreq = '\nACTION REQUIRED:  PROVIDE DIVISIONAL INSTRUCTIONS IMMEDIATELY\n\nIf you are interested in filing a divisional application, please provide your instructions by <<respDate>>. In the absence of your instructions, we will not file a divisional application.\n\nACTION REQUIRED:  VALIDATION INSTRUCTIONS BY <<datePlus1mo>>\n\nWe note that instructions for validation have not yet been received. The deadline to validate the above patent in various designated states is <<dueDate>>. Please provide us with a list of countries in which the European patent should be perfected so we may timely attend to validation country requirements, including possible full patent translation and execution of country specific power of attorney documents.\n\n'
            curr = 'In view of the current pending status of corresponding applications, you may be eligible for voluntary participation in the Patent Prosecution Highway (PPH) program to possibly reduce costs and obtain accelerated examination. Please contact us to discuss your options should you wish to further explore this program.\n\nPlease be advised that the product(s) covered by the above granted patent application may be eligible in certain European countries for a Supplementary Protection Certificate (SPC). Eligible technologies are those subject to premarket regulatory approval, such as medicinal or plant products.  If you would like more information about SPC eligibility or requirements, please contact your regulatory attorney(s).\n\n'
            
        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update({
            'actionReq' : actreq,
            'currFutPend' : curr,
            'cinstEPVal' : cinst,
            'salutation' : ''
        })
        return replace
    
# LinkedIn Email - To Client
class litoclient:
    def litoclient(self, matter, mergeinfo, keys):
        function_instance = mergefunctions.mergefunctions()

        replace = {}
        replace.update(function_instance.mergebasic(keys, matter))
        replace.update(function_instance.linkedinRAfill(matter))
        replace.update({
            'Item being reported' : mergeinfo[1].split(';')[0]
        })
        return replace