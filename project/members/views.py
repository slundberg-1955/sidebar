from django.shortcuts import render
from django.http import JsonResponse
import importlib
from docxcompose.composer import Composer
from docx import Document as Document_compose
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.shortcuts import redirect
import random, string
from asgiref.sync import sync_to_async
import asyncio
from msgraph.generated.models.internet_message_header import InternetMessageHeader

from concurrent.futures import ThreadPoolExecutor
from .models import Matter
from .models import Rvwmatterinventors
from .models import MergeCategory
from .models import MergeRole
from .models import MergeDef
from .models import Orgprofile, Matterparticipant, Rvwmatterpersonnel, Contactinfo, Personprofile, Activity, Relatedmatter
from docx import Document
from typing import Any, List
import re
from datetime import datetime
import os
from .mergemethods.mergefunctions import mergefunctions
import json
import requests
from django.conf import settings
from .auth_helper import get_token
import base64

from msgraph import GraphServiceClient
from msgraph.generated.models.message import Message
from msgraph.generated.models.importance import Importance
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.file_attachment import FileAttachment
from .auth_helper import get_token
from azure.identity import DeviceCodeCredential
from azure.identity.aio import ClientSecretCredential
from azure.identity import InteractiveBrowserCredential

import urllib.parse

from python_docx_replace.paragraph import Paragraph

# Fills merges home screen
def members(request):
    if request.method == 'POST':
        matter = request.POST['matterInput']
        
        # MUST REMOVE
        if matter == '':
            matter = '1.003us1'
            
        mergeinfo = request.POST['merge_info']

        url = mergeDoc(matter, mergeinfo, request)
        return url

    mergedict = MergeDef.objects.using('SideBar').all()
    roles = MergeRole.objects.using('SideBar').all()
    categories = MergeCategory.objects.using('SideBar').all()

    return render(request, 'merge.html', {'mergedict': mergedict, 'roles': roles, 'categories': categories})

# Other pages
def matters(request):
    return render(request, 'matters.html')

def fip_reports(request):
    return render(request, 'fip_reports.html')

def merges(request):
    return render(request, 'merges.html')

def toolbox(request):
    return render(request, 'toolbox.html')

def checkMatter(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        try:
            matter = Matter.objects.using('FIP').get(hostmatterno = data)
            matterchk = 'true'
        except:
            matterchk = 'false'
    
        return JsonResponse({'message': f'{matterchk}'})

    else:
        return JsonResponse({'error': 'Invalid request method'})
        
def docx_replace2(doc, **kwargs: str):
    for key, value in kwargs.items():
        key = f"<<{key}>>"
        for p in Paragraph.get_all(doc):
            paragraph = Paragraph(p)
            paragraph.replace_key(key, str(value))

def docx_get_keys2(doc: Any) -> List[str]:
    result = set()  # unique items
    for p in Paragraph.get_all(doc):
        paragraph = Paragraph(p)
        matches = re.finditer(r"<<([^<>]+)>>", paragraph.get_text())
        for match in matches:
            result.add(match.groups()[0])
    return list(result)

def addinventors(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")

        maid = Matter.objects.using('FIP').get(hostmatterno = data).matterid
        inventors = Rvwmatterinventors.objects.using('FIP').get(matterid = maid)
        inventorsarr = inventors.inventor

        return JsonResponse({'message': f'{inventorsarr}'})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def addcorp(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")

        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        orgout = ''
        try:
            apppart = Matterparticipant.objects.using('FIP').get(matterid = matter.matterid, roleid = '56691')
            apporg = Orgprofile.objects.using('FIP').get(opid = apppart.contactid)
            apporgname = apporg.orgname
            orgout = orgout + 'Applicant: ' + apporgname + ';'
        except:
            orgout = ''

        try:
            assigneepart = Matterparticipant.objects.using('FIP').get(matterid = matter.matterid, roleid = '34606')
            assigneeorg = Orgprofile.objects.using('FIP').get(opid = assigneepart.contactid)
            assigneeorgname = assigneeorg.orgname
            orgout = orgout + 'Assignee: ' + assigneeorgname + ';'
        except:
            orgout = orgout + ''

        try:
            clpart = Matterparticipant.objects.using('FIP').get(matterid = matter.matterid, roleid = '34617')
            clorg = Orgprofile.objects.using('FIP').get(opid = clpart.contactid)
            clorgname = clorg.orgname
            orgout = orgout + 'Client: ' + clorgname + ';'
        except:
            orgout = orgout + ''

        try:
            prepart = Matterparticipant.objects.using('FIP').get(matterid = matter.matterid, roleid = '93476')
            preorg = Orgprofile.objects.using('FIP').get(opid = prepart.contactid)
            preorgname = preorg.orgname
            orgout = orgout + 'Previous Client/Matter Number: ' + preorgname + ';'
        except:
            orgout = orgout + ''

        """         
        try:
            fopart = Matterparticipant.objects.using('FIP').get(matterid = matter.matterid, roleid = '125766')
            foorg = Orgprofile.objects.using('FIP').get(opid = fopart.contactid)
            foorgname = foorg.orgname
            orgout = orgout + 'Foreign Associate: ' + foorgname + ';'
        except:
            orgout = orgout + 'fail;' """

        try:
            lpart = Matterparticipant.objects.using('FIP').get(matterid = matter.matterid, roleid = '34607')
            lorg = Orgprofile.objects.using('FIP').get(opid = lpart.contactid)
            lorgname = lorg.orgname
            orgout = orgout + 'Licensee: ' + lorgname
        except:
            orgout = orgout + ''

        return JsonResponse({'message': f'{orgout}'})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def addrecipients(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        
        # MUST REMOVE
        if data == '':
            data = '1.003us1'

        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        parts = Matterparticipant.objects.using('FIP').filter(matterid = matter.matterid)
        contacts = ''
        profile = ''
        names = ''
        roles = ''
        for part in parts:
            try:
                profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
                personnel = Rvwmatterpersonnel.objects.using('FIP').filter(matterid = matter.matterid, ppid = profile.ppid)
                # names = names + profile.fname + ' ' + profile.lname + ','
                fullname = profile.fname + ' ' + profile.lname
                if fullname in names:
                    i = names.count(fullname)
                    if i < len(personnel):
                        roles = roles + personnel[i].rolename + ','
                        names = names + fullname + ','
                    else:
                        roles = roles + personnel[0].rolename + ','
                        names = names + fullname + ','
                else:
                    names = names + fullname + ','
                    roles = roles + personnel[0].rolename + ','
            except:
                pass
            try:
                profile = Personprofile.objects.using('FIP').get(ppid = part.contactid)
                contacts = contacts + Contactinfo.objects.using('FIP').get(contactinfoid = profile.workcontactinfoid).email + ','
            except:
                contacts = contacts + ' '

        recout = '' 
        for name in names:
            recout = recout + name
        recout = recout + ';'
        for contact in contacts:
            recout = recout + contact
        recout = recout + ';'
        for role in roles:
            recout = recout + role
        
        return JsonResponse({'message': f'{recout}'})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
""" def addSA(request):
    if request.method == 'POST':
        #Find a better way to get SA
        SAs = Rvwmatterpersonnel.objects.using('FIP').filter(roleid = 34619, orgid = 4).distinct()
        SAarr = []  # Initialize an empty list
        for SA in SAs:
            SAarr.append(SA.personname)

        return JsonResponse({'message': f'{SAarr}'})
    
    else:
        return JsonResponse({'error': 'Invalid request method'}) """
    
def addPA(request):
    merge_fn = mergefunctions()
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        relatedmatters = Relatedmatter.objects.using('FIP').filter(primarymatterid = matter.matterid, relationdesc = 'Priority')
        serialnos = merge_fn.transform_serialnumber(matter.serialnumber) + '*'
        dates = matter.fileddate.strftime("%B %d, %Y") + '*'
        countries = matter.country + '*'

        for relatedmatter in relatedmatters:
            relmatter = Matter.objects.using('FIP').get(matterid = relatedmatter.relatedmatterid)
            serialnos = serialnos + merge_fn.transform_serialnumber(relmatter.serialnumber) + '*'
            dates = dates + relmatter.fileddate.strftime("%B %d, %Y") + '*'
            countries = countries + relmatter.country + '*'

        PAout = '' 
        for number in serialnos:
            PAout = PAout + number
        PAout = PAout + ';'
        for date in dates:
            PAout = PAout + date
        PAout = PAout + ';'
        for country in countries:
            PAout = PAout + country

        return JsonResponse({'message': f'{PAout}'})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def addRelatedMatter(request):
    merge_fn = mergefunctions()
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        relatedmatters = Relatedmatter.objects.using('FIP').filter(primarymatterid = matter.matterid)
        serialnos = merge_fn.transform_serialnumber(matter.serialnumber) + '*'
        hostmatters = matter.hostmatterno
        relationships = ''

        for relatedmatter in relatedmatters:
            relmatter = Matter.objects.using('FIP').get(matterid = relatedmatter.relatedmatterid)
            hostmatters = relmatter.hostmatterno
            try:
                serialnos = serialnos + merge_fn.transform_serialnumber(relmatter.serialnumber) + '*'
            except:
                serialnos = serialnos + ' *'
            relationships = relatedmatter.relationdesc

        PAout = '' 
        for hostmatter in hostmatters:
            PAout = PAout + hostmatter
        PAout = PAout + ';'
        for serial in serialnos:
            PAout = PAout + serial
        PAout = PAout + ';'
        for relationship in relationships:
            PAout = PAout + relationship

        return JsonResponse({'message': f'{PAout}'})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})

def addactivities(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        if data == '':
            data = '1.003us1'

        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        
        activityData = Activity.objects.using('FIP').filter(matterid = matter.matterid)

        names = ''
        comments = ''
        status = ''
        dates1 = ''
        dates2 = ''

        for activity in activityData:
            if activity.name is not None:
                names = names + activity.name + ','
            else:
                names = names + 'None,'
            if activity.notes is not None:
                comments = comments + activity.notes + ','
            else:
                comments = comments + 'None,'
            if activity.status is not None:
                status = status + activity.status + ','
            else:
                status = status + 'None,'

            if activity.smryonename is not None:
                dates1 = dates1 + activity.smryonename
            if activity.smryonelabel is not None:
                dates1 = dates1 + ' ' + activity.smryonelabel
            if activity.smryonevalue is not None:    
                dates1 = dates1 + ' ' + datetime.fromisoformat(str(activity.smryonevalue)).strftime('%m/%d/%Y') + ','
            else:
                dates1 = dates1 + ' ,'
            if str(activity.smrytwovalue) == '':
                if activity.smrytwoname is not None:
                    dates2 = dates2 + activity.smrytwoname
                if activity.smrytwolabel is not None:
                    dates2 = dates2 + ' ' + activity.smrytwolabel
                if activity.smrytwovalue is not None:    
                    dates2 = dates2 + ' ' + datetime.fromisoformat(str(activity.smrytwovalue)).strftime('%m/%d/%Y') + ','
                else:
                    dates2 = dates2 + ' ,'
            else:
                dates2 = dates2 + ' ,'

        actout = ''
        for name in names:
            actout = actout + name
        actout = actout + ';'
        for comment in comments:
            actout = actout + comment
        actout = actout + ';'
        for stat in status:
            actout = actout + stat
        actout = actout + ';'
        for date1 in dates1:
            actout = actout + date1
        actout = actout + ';'
        for date2 in dates2:
            actout = actout + date2
        actout = actout + ';'

        return JsonResponse({'message': f'{actout}'})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def displayMatter(request):
    tables_data = Matter.objects.all()
    return render(request, 'dbtest.html', {'tables_data': tables_data})

def WordMerger(docxpath, replace, output_path):
    doc = Document(docxpath)
    docx_replace2(doc, **replace)
    doc.save(output_path)
    
    #   NO SAVE WORD DOC
    #doc_io = BytesIO()
    #doc.save(doc_io)
    #doc_io.seek(0)
    #return doc_io
    
# Fix orgId
def DocumentReader(docxpath, mergemethod):
    doc = Document(docxpath)
    if mergemethod == 'olpemail':
        subject = doc.paragraphs[0].text.replace('Subject line:', '')
        body = doc.paragraphs[1].text.replace('- Direct Dial', '\n')
        body = body.replace('Body of email:', '')
        body = body + '\n'.join([p.text for p in doc.paragraphs[2:]])
        
    else:
        subject = doc.paragraphs[0].text.replace('Subject line:', '')
        body = '\n'.join([p.text for p in doc.paragraphs[5:]])
        
    return subject, body

def Email(body, subject, recipients, cc, bcc, attachment): 
    # ------ OLD EMAIL ------
    #pythoncom.CoInitialize()  
    #outlook = win32.Dispatch('outlook.application')
    #mail = outlook.CreateItem(0)
    #mail.Subject = subject
    #mail.Body = body
    #mail.To = recipients
    #if(attachment != ''):
    #    mail.Attachments.Add(attachment)

    #if cc:
    #    mail.CC = cc
    #if bcc:
    #    mail.BCC = bcc

    #mail.Display(True)
    
    # ------ NEW EMAIL ------
    link = create_outlook_web_link(subject, body, recipients, cc, bcc)
    #link = create_draft()
    return link
    
def create_outlook_web_link(subject, body, to, cc=None, bcc=None):
    base_url = "https://outlook.office.com/mail/deeplink/compose"
    params = {
        "to": to,
        "subject": subject,
        "body": body
    }
    if cc:
        params["cc"] = cc
    if bcc:
        params["bcc"] = bcc
    
    # Use urllib.parse.quote to ensure spaces are encoded as %20
    query_string = '&'.join([f"{key}={urllib.parse.quote(value, safe='')}" for key, value in params.items()])
    outlook_web_link = f"{base_url}?{query_string}"
    
    return outlook_web_link

def create_draft():    
    credentials = InteractiveBrowserCredential(
        client_id=os.getenv('CLIENT_ID'),
        tenant_id=os.getenv('TENANT_ID'),
    )
    
    scopes = ['https://graph.microsoft.com/.default']
    client = GraphServiceClient(credentials=credentials, scopes=scopes)

    request_body = Message(
        subject="9/8/2018: concert",
        body=ItemBody(
            content_type=BodyType.Html,
            content="The group represents Washington.",
        ),
        to_recipients=[
            Recipient(
                email_address=EmailAddress(
                    address="test@test123.com",
                ),
            ),
        ],
        internet_message_headers=[
            InternetMessageHeader(
                name="x-custom-header-group-name",
                value="Washington",
            ),
            InternetMessageHeader(
                name="x-custom-header-group-id",
                value="WA001",
            ),
        ],
    )

    async def create_draft():
        draft_message = await client.me.messages.post(request_body)
        return draft_message

    # Use ThreadPoolExecutor to run the async function in a synchronous context
    def run_async_function():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(create_draft())

    with ThreadPoolExecutor() as executor:
        draft_message = executor.submit(run_async_function).result()

    # Construct the URL to the draft
    draft_id = draft_message.id
    draft_url = f"https://outlook.office.com/mail/deeplink/compose/{draft_id}"
    return draft_url

def testview(request):
    return render(request, 'dbtest.html')

def find_checkbox_coordinates(element_coordinates):
    checkbox_coordinates = {}
    for element_name, (row, column) in element_coordinates.items():
        if "CheckBox" in element_name:
            checkbox_coordinates[element_name] = (row, column)
    return checkbox_coordinates

def combinedoc(path, method, mergeinfo, matter, email):
    doc1 = Document_compose(path)
    doc1.add_page_break()

    if method == 'issuefee':
        composer = Composer(doc1)
        doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'issuefeexmit3.docx'))
        if mergeinfo[6] == 'true':
            doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'issuefeexmit2.docx')) 
            doc3.add_page_break()
            composer.append(doc3)
            composer.append(doc2) 
        else:  
            composer.append(doc2)

    if method == 'applicationdata_new2' or method == 'applicationdata_updnew':
        doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2inventor.docx'))
        docend = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2end.docx'))
        composer = Composer(doc2)

        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        inventors = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34608')
        applicants = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '56691')
        assignees = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34606')
        invCount = len(inventors) + 1
        appCount = len(applicants) + 1
        assignCount = len(assignees) + 1

        for i in range(0, invCount):
            replace = {}
            if (method == 'applicationdata_updnew' and mergeinfo[0] == 'false') or invCount == 0:
                blank = {            
                    'inventorCnt' : '',
                    'inventor' : '',
                    'invpre' : '',
                    'inventorFirstName' : '',
                    'inventorMiddleInitial' : '',
                    'inventorLastName' : '',
                    'inventorSuffix' : '',
                    'inventorHomeCity' : '',
                    'inventorHomeState' : '',
                    'inventorHomeCountry' : '',
                    'inventorMailingStreet1' : '',
                    'inventorMailingStreet2' : '',
                    'inventorMailingCity' : '',
                    'inventorMailingState' : '',
                    'inventorMailingZip' : '',
                    'inventorMailingCountry' : ''
                    }
                replace.update(blank)
                invCount = 0
            else:  
                if i != 0:
                    replace.update(merge_fn.inventorInfo(matter, i))
            if i == 0 and invCount > 0:
                continue
            WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2inventorMultiple.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2inventorMultipleout.docx'))
            doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2inventorMultipleout.docx')) 
            composer.append(doc3)
        
        composer.append(doc1)
        
        for i in range(0, appCount):
            replace = {}
            if (method == 'applicationdata_updnew' and mergeinfo[4] == 'false') or appCount == 0:
                blank = {            
                    'applCnt' : '',
                    'applicantCity' : '',
                    'applicantState' : '',
                    'applicantZip' : '',
                    'applicantCountry' : '',
                    'applicantStreet1' : '',
                    'applicantStreet2' : '',
                    'applicant' : '',
                    'applicantName' : ''
                }
                replace.update(blank)
                appCount = 0
            else:
                if i != 0:
                    replace.update(merge_fn.applicantfill(matter, i))
            if i == 0 and appCount > 0:
                continue
            WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2applicantMulti.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2applicantMultipleout.docx'))
            doc4 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2applicantMultipleout.docx')) 
            composer.append(doc4)

        for i in range(0, assignCount):
            replace = {}
            if (method == 'applicationdata_updnew' and mergeinfo[5] == 'false') or assignCount == 0:
                blank = {            
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
                replace.update(blank)
                assignCount = 0
            else: 
                if i != 0:
                    replace.update(merge_fn.assigneefill(matter, i))
            if i == 0 and assignCount > 0:
                continue
            WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2assigneeMulti.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2assigneeMultipleout.docx'))
            doc5 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2assigneeMultipleout.docx')) 
            composer.append(doc5)
        
        composer.append(docend)
    
    if method == 'invchange':
        merge_fn = mergefunctions()
        doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'inventorchange.docx')) 
        docend = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'inventorchange_end.docx')) 
        composer = Composer(doc2)
        invlist = mergeinfo[2:]
        invlist = invlist[:-1]
        for inv in invlist:
            replace = {}
            replace.update(merge_fn.inventorInfoName(matter, inv))
            WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'inventorchange_multi.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'inventorchangeMultipleout.docx'))
            doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'inventorchangeMultipleout.docx')) 
            composer.append(doc3)
        
        composer.append(docend)
        
    if method == 'BSCCombinedAssnDec':
        composer = Composer(doc1)
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        inventors = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34608')
        invCount = len(inventors) + 1
        for i in range(1, invCount, 2):
            replace = {}
            replace.update(merge_fn.inventorInfoBSC(matter, i))
            WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'BSCCombinedAssnDecinventors.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'BSCCombinedAssnDecinventorsout.docx'))
            doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'BSCCombinedAssnDecinventorsout.docx')) 
            composer.append(doc2)

    if method == 'aiashortdecl':
        doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'miscellaneous', 'blank.docx')) 
        composer = Composer(doc2)
        merge_fn = mergefunctions()
        invsellist = mergeinfo[1:]
        invsellist = invsellist[:-1]
        for inv in invsellist:
            replace = {}
            replace.update(merge_fn.inventorInfoName(matter, inv))
            WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'aiaShortDeclaration_esign.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'aiaShortDeclaration_out.docx'))
            doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'aiaShortDeclaration_out.docx')) 
            composer.append(doc3)

    if email == 'TRUE':
        merge_fn = mergefunctions()
        doc2 = Document_compose(path)
        composer = Composer(doc2)
        replace = {}
        replace.update(merge_fn.cmgfill(matter))
        if method == 'msemails' or method == 'FFRptOutBasic' or method == 'honureport' or method == 'CommunicationLetter' or method == 'TM_ChgCounsel' or method == 'sendorderletter' or method == 'fa_confirm' or method == 'nikeaction_new':
            doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'reportletters', 'signoff2.docx'))
        else:
            WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'reportletters', 'signoff.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'emailout.docx'))
            doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'emailout.docx'))
        composer.append(doc3)
        
    composer.save("documents/multidocmerge/" + method +".docx")

def pathChanger(input_path, mergeinfo_list, mergefninfo):
    if mergeinfo_list[1] == 'ffSndItmsToAssoc':
        if mergefninfo[6] == '1':
            input_path = input_path.replace('ffSndItmsToAssoc.docx', 'ffSndItmsToAssoc_HONU.docx')
        if mergefninfo[6] == '2':
            input_path = input_path.replace('ffSndItmsToAssoc.docx', 'ffSndItmsToAssoc_NYHonu.docx')

    if mergeinfo_list[1] == 'TM_NoticeofPubRep':
        if mergefninfo[0] == 'NO':
            input_path = input_path.replace('NoticeofPubRep', 'NoticeofPubRep2')
            
    if mergeinfo_list[1] == 'priorexam2012':
        if mergefninfo[0] == '2':
            input_path = input_path.replace('priorexam2012_E1', 'priorexam2012_E2')
    
    if mergeinfo_list[1] == 'sendorderletter':
        if mergefninfo[2] == '1' or mergefninfo[2] == '2':
            input_path = input_path.replace('orderLetter.docx', 'orderLetterHonu.docx')
    
    return input_path

# New separate function for merging documents
def mergeDoc(matter , mergeinfo, request):
    mergeinfo_list = mergeinfo.split(",") 
    module_name = ".mergemethods.merges"
    class_name = mergeinfo_list[1]
    module = importlib.import_module(module_name, package='members')
    curMerge = getattr(module, class_name)
    merge_instance = curMerge()

    docpath = mergeinfo_list[0].split('/')
    
    input_path = os.path.join(settings.BASE_DIR, 'documents', docpath[0], docpath[1])
    output_path = os.path.join(settings.BASE_DIR, 'documents', 'merged', 'Document.docx')

    replace = {}
    mergefninfo = mergeinfo.split(",")
    mergefninfo.pop(0)
    mergefninfo.pop(0)
    mergefninfo.pop(0)
    
    contacts = mergeinfo_list[2]
    # Pop emails in merge data
    if contacts == 'TRUE' and mergeinfo_list[1] != 'reportprvassnnew':
        mergefninfo.pop(0)
        mergefninfo.pop(0)
        mergefninfo.pop(0)

    # without multiple docs
    doc = Document(input_path)
    keys = docx_get_keys2(doc)
    
    input_path = pathChanger(input_path, mergeinfo_list, mergefninfo)

    if mergeinfo_list[1] == 'pctcorrect':
        if mergefninfo[5] == 'true':
            pctext = mergeinfo.replace('pctcorrectdefects', 'PCTExtention')
            pctext = pctext.replace('pctcorrect', 'pctextention')
            mergeDoc(matter, pctext, '')

    if mergeinfo_list[1] == 'corrappln':
        if mergefninfo[1] != '' and int(mergefninfo[1]) > 0:
            extime = mergeinfo.replace('corrappln', 'exttimeCF')
            extime = extime.replace('communications', 'transmittal')
            mergeDoc(matter, extime, '')


    replace = getattr(merge_instance, class_name)(matter, mergefninfo, keys)

    # combine doc
    if contacts == 'TRUE':
        combinedoc(input_path, mergeinfo_list[1], mergefninfo, matter, contacts)
        input_path = os.path.join(settings.BASE_DIR, 'documents', 'multidocmerge', mergeinfo_list[1] + '.docx')
        doc = Document(input_path)

    # with multiple docs
    if mergeinfo_list[1] == 'issuefee':
        combinedoc(input_path, mergeinfo_list[1], mergefninfo, matter, contacts)
        input_path = os.path.join(settings.BASE_DIR, 'documents', 'multidocmerge', mergeinfo_list[1] + '.docx')
        doc = Document(input_path)
        isssubject = matter + ', Action Requested:  Review and signature of Issue Fee Transmittal'
        issbody = "SIGNING ATTORNEY CHECKLIST FOR ISSUE FEE PAYMENT FILING \n\nIssue Fee due: " + replace.get('dueDate') + "\n\nAction Requested: Review and Signature of Issue Fee Transmittal Documents\n\nInstructions to Signing Attorney: Prior to signature of this document, please consider the attached Attorney Checklist."
        issTO = ''
        issCC = ''
        issBCC = ''
        attachment = os.path.join(settings.BASE_DIR, 'documents', 'attachments', 'Notice of Allowance Review and Response.pdf')
        Email(issbody, isssubject, issTO, issCC, issBCC , attachment)

        if mergefninfo[5] == 'true':
            stateofallow = mergeinfo.replace('issuefeexmit', 'stateofallowcomments')
            stateofallow = stateofallow.replace('issuefee', 'stateofallow')
            mergeDoc(matter, stateofallow, '')
            
    if mergeinfo_list[1] == 'applicationdata_new2' or mergeinfo_list[1] == 'applicationdata_updnew' or mergeinfo_list[1] == 'invchange' or mergeinfo_list[1] == 'BSCCombinedAssnDec' or mergeinfo_list[1] == 'aiashortdecl':
        combinedoc(input_path, mergeinfo_list[1], mergefninfo, matter, contacts)
        input_path = os.path.join(settings.BASE_DIR, 'documents', 'multidocmerge', mergeinfo_list[1] + '.docx')
        doc = Document(input_path)

    # doc merges
    if contacts == "FALSE":
        WordMerger(input_path, replace, output_path)
        
        # ----- Local -----
        os.startfile(output_path)
        
        # ----- Azure Storage -----
        #file_name = os.path.basename(output_path)
        #file_name = file_name.split('.')
        #file_name[0] += ('-' + ''.join(random.choices(string.ascii_letters, k=6)))
        #file_name = file_name[0] + '.' + file_name[1]

        #with open(output_path, 'rb') as file:
        #    default_storage.save(file_name, ContentFile(file.read()))

        #blob_url = f"https://{os.getenv('AZURE_ACCOUNT_NAME')}.blob.core.windows.net/media/{file_name}"
        
        # webbrowser.open(blob_url)
        #return JsonResponse({'url': f'{blob_url}'})

    # outlook merges
    if contacts == "TRUE":
        WordMerger(input_path, replace, output_path)
        tolist = mergeinfo_list[3].split(';')
        cclist = mergeinfo_list[4].split(';')
        bcclist = mergeinfo_list[5].split(';')
        #tolist = ''
        #cclist = ''
        #bcclist = ''
        TO = ''
        CC = ''
        BCC = ''
        for to in tolist:
            if check_email(to):
                if TO != '':
                    TO += ' ;' + to
                else:
                    TO = to
                    
        for cc in cclist:
            if check_email(cc):
                if CC != '':
                    CC += '; ' + cc
                else:
                    CC = cc
                    
        for bcc in bcclist:
            if check_email(bcc):
                if BCC != '':
                    BCC += '; ' + bcc
                else:
                    BCC = bcc
        subject, body = DocumentReader(output_path, mergeinfo_list[1])
        # attachment = "Q:/Contract Developers/SideBar/Merges/Django/SideBar/project/documents/communications/AppealFwdFee.docx"
        contact = Email(body, subject, TO, CC, BCC, '')
        #contact = 'false'
        return JsonResponse({'url': f'{contact}'})

def check_email(email):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if re.fullmatch(pattern, email):
        return True
    else:
        return False
