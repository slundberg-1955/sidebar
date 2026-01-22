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
from msgraph.generated.models.internet_message_header import InternetMessageHeader

from django.http import HttpResponse
from django.http import HttpResponseRedirect
#from dotenv import load_dotenv
from django.db import connections
#import win32com.client as win32
#import pythoncom
from urllib.parse import quote
import mimetypes
from io import BytesIO

import io
import zipfile


from concurrent.futures import ThreadPoolExecutor
from .models import Matter
from .models import Rvwmatterinventors
from .models import MergeCategory
from .models import MergeRole
from .models import MergeDef
from .models import Orgprofile, Matterparticipant, Rvwmatterpersonnel, Contactinfo, Personprofile, Activity, Relatedmatter, FvContact4
from docx import Document
from typing import Any, List
import re
from datetime import datetime, timedelta, date
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
from azure.identity import InteractiveBrowserCredential

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import asyncio
import time

from msal import ConfidentialClientApplication
from azure.core.credentials import AccessToken

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential, ClientSecretCredential
from azure.storage.blob import BlobClient, BlobServiceClient, generate_blob_sas, BlobSasPermissions

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

    mergedict = MergeDef.objects.using('SideBar').filter(operational="TRUE").order_by('mergename')
    roles = MergeRole.objects.using('SideBar').all()
    categories = MergeCategory.objects.using('SideBar').all()
 
    return render(request, 'merge.html', {'mergedict': mergedict, 'roles': roles, 'categories': categories})

# Health Check
def health_check(request):
    return HttpResponse("Healthy", status=200)

# Other pages
def matters(request):
    return render(request, 'matters.html')

def fip_reports(request):
    return render(request, 'fipreports.html')

def merges(request):
    mergedict = MergeDef.objects.using('SideBar').filter(operational="TRUE").order_by('mergename')
    roles = MergeRole.objects.using('SideBar').all()
    categories = MergeCategory.objects.using('SideBar').all()
 
    return render(request, 'merge.html', {'mergedict': mergedict, 'roles': roles, 'categories': categories})

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
    
def addassignee(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(data)
        roleordernos = ''
        profiles = ''

        assignees = Matterparticipant.objects.using('FIP').filter(matterid=matter_data.matterid, roleid='34606')
        i = 0
        for assignee in assignees:
            if i == 0:
                profiles = profiles + Orgprofile.objects.using('FIP').get(opid = assignee.contactid).orgname 
                roleordernos = roleordernos + str(assignee.roleorderno)
                i = 1
            else:
                profiles = profiles + ';' + Orgprofile.objects.using('FIP').get(opid = assignee.contactid).orgname
                roleordernos = roleordernos + ';' + str(assignee.roleorderno)
   
        return JsonResponse({'message': {'assignees': profiles, 'ordernos': roleordernos}})
    
def addcorp(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")

        results = []
        names = []
        roles = []
        roleids = []
        roleorders = []
        if data != '':
            query = f"""
                SELECT  
                    CAST(orgname as varchar(500)) AS orgname, 
                    role.name AS rolename,
                    role.roleid,
                    mp.roleorderno
                FROM matterparticipant mp 
                    JOIN orgprofile op ON mp.contactid = op.opid
                    JOIN contactinfo ci on op.contactinfoid = ci.contactinfoid
                    JOIN country ON ci.country = country.code
                    JOIN role ON mp.roleid = role.roleid
                WHERE op.opid <>  32
                and matterid IN 
                (SELECT matterid from matter where hostmatterno LIKE '{data}')
                ORDER BY rolename
            """
                
            with connections['FIP'].cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

            for result in results:
                fullname, rolename, roleid, roleorder = result
                if (fullname, rolename) not in zip(names, roles):
                    names.append(fullname)
                    roles.append(rolename + ': ' + fullname)
                    roleids.append(roleid)
                    roleorders.append(roleorder)

        # Format the results for printing
        names = '; '.join(str(name).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for name in names)
        roles = '; '.join(str(role).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for role in roles)
        roleids = '; '.join(str(roleid).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for roleid in roleids)
        roleorders = '; '.join(str(roleorder).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for roleorder in roleorders)
        
        print(names + ' ' + roles)
    
        return JsonResponse({'message': {'names': names, 'roles': roles, 'roleids': roleids, 'roleorders': roleorders}})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def addrecipients(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        
        # MUST REMOVE
        if data == '':
            data = '1.003us1'
        
        results = []
        names = []
        emails = []
        roles = []
        if data != '':
            query = f"""
                SELECT 
                    CONCAT(pp.fname, ' ', pp.lname) AS fullname,
                    ci.email,
                    rp.rolename
                FROM Matter m
                JOIN Matterparticipant mp ON mp.matterid = m.matterid
                JOIN Personprofile pp ON pp.ppid = mp.contactid
                LEFT JOIN Contactinfo ci ON ci.contactinfoid = pp.workcontactinfoid
                LEFT JOIN Rvwmatterpersonnel rp ON rp.matterid = m.matterid AND rp.ppid = pp.ppid
                WHERE m.hostmatterno = '{data}'
                ORDER BY rolename;
            """
                
            with connections['FIP'].cursor() as cursor:
                cursor.execute(query)
                results = cursor.fetchall()

            for result in results:
                fullname, email, rolename = result
                if (fullname, email, rolename) not in zip(names, emails, roles):
                    names.append(fullname)
                    emails.append(email)
                    roles.append(rolename)

        # Format the results for printing
        names = '; '.join(str(name).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for name in names)
        emails = '; '.join(str(email).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for email in emails)
        roles = '; '.join(str(role).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for role in roles)
    
        return JsonResponse({'message': {'names': names, 'emails': emails, 'roles': roles}})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def addSA(request):
    if request.method == 'POST':
        # Query the database for distinct personLastNameFirstName values, sorted by fName
        SAs = (Rvwmatterpersonnel.objects.using('FIP')
               .filter(roleid=34619, orgid=4)
               .values('fname', 'lname')
               .distinct()
               .order_by('fname'))

        # Extract the required values into a list of concatenated strings
        SAarr = [f"{SA['fname']} {SA['lname']}" for SA in SAs]

        return JsonResponse({'message': SAarr})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})

def fillstateofallow(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        merge_fn = mergefunctions()

        # Get NOAR date
        try:
            noaractivity = merge_fn.getactivityid(matter, 'NOAR')
            dateNOAR = noaractivity.smryonevalue.isoformat()
        except:
            dateNOAR = ''

        return JsonResponse({'message': {'noardate': dateNOAR}})
    else:
        return JsonResponse({'message': {'noardate': ''}})
    
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
    
def addPCTSA(request):
    if request.method == 'POST':
        FVDatas = FvContact4.objects.using('FIP').filter(pct_signor='1')
        PCTout = set()

        for FVData in FVDatas:
            try:
                profile = Personprofile.objects.using('FIP').get(ppid=FVData.recordid, disableaccess=False)
                full_name = profile.fname + ' ' + profile.lname
                PCTout.add(full_name)
            except:
                pass

        return JsonResponse({'message': list(PCTout)})
    else:
        return JsonResponse({'error': 'Invalid request method'})
    
def fillissuefee(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        merge_fn = mergefunctions()

        # previously paid
        # Only in past
        try:
            feeactivity = merge_fn.getactivityid(matter, 'IFEE')
            dateIssueFee = feeactivity.smryonevalue.isoformat()
            if feeactivity.smryonevalue.date() > date.today():
                dateIssueFee = ''
        except:
            dateIssueFee = ''

        # withdraw filed
        try:
            feeactivity = merge_fn.getactivityid(matter, 'PWFI')
            dateWithdraw = feeactivity.smryonevalue.isoformat()
        except:
            dateWithdraw = ''

        # withdraw mailed
        try:
            feeactivity = merge_fn.getactivityid(matter, 'NOWI')
            dateWithdrawMail = feeactivity.smryonevalue.isoformat()
        except:
            dateWithdrawMail = ''

        return JsonResponse({'message': {'dissfee': dateIssueFee, 'withdraw': dateWithdraw, 'withdrawM': dateWithdrawMail}})
    else:
        return JsonResponse({'message': {'dissfee': '', 'withdraw': ''}})
    
def addRelatedMatter(request):
    merge_fn = mergefunctions()
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        
        family = re.sub(r'[^a-zA-Z]', '', data)
        
        query = f"""
            SELECT relationship.relationdesc, cast(hostmatterno as varchar(15)) as hostmatterno,
            cast(fmtserialno as varchar(30)) as fmtserialno, stageDescription
            FROM matter
            left JOIN patent on matter.matterid = patent.matterid
            left join country on matter.country = country.code
            left JOIN relatedmatter on matter.matterid = relatedmatter.relatedmatterid
            left JOIN relationship on relationtype = relationid
            WHERE primarymatterid = {matter.matterid}
            AND orgid = 4
            AND hostMatterNo like '%{family}%'
        """
                
        with connections['FIP'].cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        matternos = []
        serialnos = []
        relationships = []

        for result in results:
            relationship, hostmatter, serialno, desc = result
            matternos.append(hostmatter)
            serialnos.append(serialno)
            relationships.append(str(relationship) + '/' + str(desc))
        
        matternos = '; '.join(str(id).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for id in matternos)
        serialnos = '; '.join(str(id).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for id in serialnos)
        relationships = '; '.join(str(rel).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for rel in relationships)

        return JsonResponse({'message': {'matternos': matternos, 'serialnos': serialnos, 'relationships': relationships}})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})

def addactivities(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        if data == '':
            data = '1.003us1'

        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        
        query = f"""
            SELECT 
                name, 
                CASE 
                    WHEN notes IS NULL THEN '' 
                    ELSE CAST(notes AS VARCHAR(8000)) 
                END AS notes, 
                status, 
                smryonelabel,
                smryonevalue,
                smrytwolabel,
                smrytwovalue,
                activityid
            FROM activity 
            WHERE matterid = {matter.matterid}
            ORDER BY 
                CASE 
                    WHEN name = 'Matter Management' THEN '3000-01-01' 
                    ELSE smryonevalue 
                END DESC;
        """
                
        with connections['FIP'].cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()

        names = []
        notes = []
        status = []
        smryonelabels = []
        smrytwolabels = []
        actids = []

        for result in results:
            name, note, stat, smryonelabel, smryonevalue, smrytwolabel, smrytwovalue, actid = result
            names.append(name)
            notes.append(note)
            status.append(stat)
            smryone = ''
            smrytwo = ''
            if smryonelabel != '' and smryonelabel != None and smryonevalue != None and smryonevalue != '':
                smryone = str(smryonelabel) + ': ' + str(smryonevalue.strftime("%m/%d/%Y"))
            if smrytwolabel != '' and smrytwolabel != None and smrytwovalue != None and smrytwovalue != '':
                smrytwo = str(smrytwolabel) + ': ' + str(smrytwovalue.strftime("%m/%d/%Y"))
    
            smryonelabels.append(smryone)
            smrytwolabels.append(smrytwo)
            actids.append(actid)
        
        names = '; '.join(str(na).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for na in names)
        notes = '; '.join(str(no).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for no in notes)
        status = '; '.join(str(st).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for st in status)
        smryonelabels = '; '.join(str(smryone).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for smryone in smryonelabels)
        smrytwolabels = '; '.join(str(smrytwo).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for smrytwo in smrytwolabels)
        actids = '; '.join(str(id).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for id in actids)

        return JsonResponse({'message': {'names': names, 'notes': notes, 'status': status, 'smryonelabels' : smryonelabels, 'smrytwolabels' : smrytwolabels, 'actids' : actids}})
    
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

def Email(body, subject, recipients, cc, bcc, attachments, request): 
    # ------LOCAL EMAIL ------
    # pythoncom.CoInitialize()  
    # outlook = win32.Dispatch('outlook.application')
    # mail = outlook.CreateItem(0)
    # mail.Subject = subject
    # mail.Body = body
    # mail.To = recipients
    # if attachments:
    #     for file_path in attachments:
    #         if os.path.isfile(file_path):
    #             mail.Attachments.Add(file_path)

    # if cc:
    #    mail.CC = cc
    # if bcc:
    #    mail.BCC = bcc

    # mail.Display(True)
    
    # ------ NEW EMAIL ------
    link = create_draft(body, subject, recipients, cc, bcc, attachments, request)
    return link

def create_draft(body, subject, tolist, cclist, bcclist, attachments, request):   
    #load_dotenv()
    
    # Managed Identity Auth
    #credentials = ManagedIdentityCredential()
    
    # Client Secret Auth
    tenant_id = os.getenv('TENANT_ID')
    client_id = os.getenv('MICROSOFT_PROVIDER_CLIENT_ID')
    client_secret = os.getenv('MICROSOFT_PROVIDER_AUTHENTICATION_SECRET')
    credentials = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret)

    scopes = ['https://graph.microsoft.com/.default']

    client = GraphServiceClient(credentials=credentials, scopes=scopes)

    # Convert strings to lists if needed (similar to get_attachments)
    if isinstance(tolist, str):
        tolist = [tolist] if tolist else []
    if isinstance(cclist, str):
        cclist = [cclist] if cclist else []
    if isinstance(bcclist, str):
        bcclist = [bcclist] if bcclist else []
    
    to_recipients = [
        Recipient(email_address=EmailAddress(address=email))
        for email in tolist if check_email(email)
    ]

    cc_recipients = [
        Recipient(email_address=EmailAddress(address=email))
        for email in cclist if check_email(email)
    ]
    bcc_recipients = [
        Recipient(email_address=EmailAddress(address=email))
        for email in bcclist if check_email(email)
    ]
    # Check if body contains HTML tags
    has_html = bool(re.search(r'<[^>]+>', body))
    body_type = BodyType.Html if has_html else BodyType.Text
    
    # Clean up HTML formatting - remove newlines between HTML tags (whitespace doesn't affect rendered HTML)
    if body_type == BodyType.Html:
        # Remove newlines that are between HTML tags (formatting newlines in HTML source)
        # This preserves intentional <br> tags but removes source code formatting newlines
        body = re.sub(r'>\s*\n\s*<', '><', body)
        # Remove leading/trailing whitespace and newlines
        body = body.strip()
    else:
        # For plain text, convert newlines to <br> tags for HTML email
        body = body.replace('\n', '<br>')
        body_type = BodyType.Html  # Switch to HTML since we added <br> tags

    request_body = Message(
        subject=subject,
        body=ItemBody(
            content_type=body_type,
            content=body,
        ),
        
        to_recipients=to_recipients,
        cc_recipients=cc_recipients,
        bcc_recipients=bcc_recipients,
        
        #attachments=get_attachments(attachments)
    )

    async def create_draft():
        user_email = request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME')
        # Create draft message first (without attachments)
        draft_message = await client.users.by_user_id(user_email).messages.post(request_body)
        #draft_message = await client.me.messages.post(request_body)
        
        # Add attachments after creating the draft
        attachment_objects = get_attachments(attachments)
        print(f"Attempting to add {len(attachment_objects)} attachment(s) to draft message {draft_message.id}")
        if attachment_objects:
            for attachment in attachment_objects:
                try:
                    await client.users.by_user_id(user_email).messages.by_message_id(draft_message.id).attachments.post(attachment)
                    print(f"Successfully added attachment: {attachment.name}")
                except Exception as e:
                    print(f"Error adding attachment {attachment.name}: {str(e)}")
                    import traceback
                    traceback.print_exc()
        else:
            print("No attachments to add (attachment_objects is empty)")
        
        return draft_message

    def run_async_function():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(create_draft())

    with ThreadPoolExecutor() as executor:
        draft_message = executor.submit(run_async_function).result()

    # Construct the URL to the draft
    draft_id = draft_message.id
    print(draft_id)
    #draft_url = f"https://outlook.office365.com/mail/compose/{draft_id}?ItemID={draft_id}"
    draft_url = draft_message.web_link
    return draft_url

def get_attachments(attachments):
    attachment_objects = []
    if not attachments:
        print("get_attachments: No attachments provided")
        return attachment_objects

    if isinstance(attachments, str):
        attachments = [attachments]
    
    print(f"get_attachments: Processing {len(attachments)} attachment(s)")
    try:
        for file_path in attachments:
            if not file_path:
                print("get_attachments: Skipping empty file path")
                continue
            
            print(f"get_attachments: Processing attachment: {file_path}")
                
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"Warning: Attachment file does not exist: {file_path}")
                continue
            
            if not os.path.isfile(file_path):
                print(f"Warning: Attachment path is not a file: {file_path}")
                continue
            
            try:
                file_name = os.path.basename(file_path)
                mime_type, _ = mimetypes.guess_type(file_path)
                mime_type = mime_type or "application/octet-stream"
                
                print(f"get_attachments: Reading file {file_name} (type: {mime_type})")
                with open(file_path, "rb") as f:
                    content_bytes = f.read()
                
                print(f"get_attachments: File size: {len(content_bytes)} bytes")
                
                # Microsoft Graph FileAttachment expects content_bytes as raw bytes
                # The SDK will handle base64 encoding internally when sending to the API
                attachment = FileAttachment(
                    odata_type="#microsoft.graph.fileAttachment",
                    name=file_name,
                    content_type=mime_type,
                    content_bytes=content_bytes
                )
                attachment_objects.append(attachment)
                print(f"Successfully prepared attachment: {file_name}")
            except Exception as e:
                print(f"Error processing attachment {file_path}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
    except Exception as e:
        print(f"Error in get_attachments: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"get_attachments: Returning {len(attachment_objects)} attachment object(s)")
    return attachment_objects

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

    if method == 'issuefee':
        doc1.add_page_break()
        composer = Composer(doc1)
        #doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'issuefeexmit3.docx'))
        doc2 = Document_compose(get_template_docx('communications', 'issuefeexmit3.docx'))
        if mergeinfo[4] == 'true':
            #doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'issuefeexmit2.docx'))
            doc3 = Document_compose(get_template_docx('communications', 'issuefeexmit2.docx'))
            doc3.add_page_break()
            composer.append(doc3)
            composer.append(doc2) 
        else:  
            composer.append(doc2)

    if method == 'missingpartsNw':
        doc1.add_page_break()
        composer = Composer(doc1)

        try:
            enddoc_index = mergeinfo.index('ENDDOC')
        except ValueError:
            enddoc_index = None

        try:
            endfee_index = mergeinfo.index('ENDFEE')
        except ValueError:
            endfee_index = None

        # Determine the later of the two indices
        if enddoc_index is not None and endfee_index is not None:
            split_index = max(enddoc_index, endfee_index)
            mergeinfo = mergeinfo[split_index + 1:]
        elif enddoc_index is not None:
            mergeinfo = mergeinfo[enddoc_index + 1:]
        elif endfee_index is not None:
            mergeinfo = mergeinfo[endfee_index + 1:]
        else:
            mergeinfo = mergeinfo

        minfo7 = int(mergeinfo[9]) if mergeinfo[9] else 0
        if int(minfo7) > 0:
            #doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'MissingPartsXmit2.docx'))
            doc2 = Document_compose(get_template_docx('communications', 'MissingPartsXmit2.docx'))
            doc2.add_page_break()
            composer.append(doc2)

        minfo11 = int(mergeinfo[11]) if mergeinfo[11] else 0
        minfo12 = int(mergeinfo[12]) if mergeinfo[12] else 0
        minfo13 = int(mergeinfo[13]) if mergeinfo[13] else 0
        minfo14 = int(mergeinfo[14]) if mergeinfo[14] else 0
        if minfo11 > 0 or minfo12 > 0 or minfo13 > 0 or minfo14 > 0:
            #doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'MissingPartsXmit3.docx'))
            doc3 = Document_compose(get_template_docx('communications', 'MissingPartsXmit3.docx'))
            doc3.add_page_break()
            composer.append(doc3)

        #doc4 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'MissingPartsXmit4.docx'))
        doc4 = Document_compose(get_template_docx('communications', 'MissingPartsXmit4.docx'))
        composer.append(doc4)

    if method == 'applicationdata_new2' or method == 'applicationdata_updnew':
        doc1.add_page_break()
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
        doc1.add_page_break()
        merge_fn = mergefunctions()
        #doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'inventorchange.docx')) 
        #docend = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'inventorchange_end.docx')) 
        doc2 = Document_compose(get_template_docx('communications', 'inventorchange.docx'))
        docend = Document_compose(get_template_docx('communications', 'inventorchange_end.docx'))
        composer = Composer(doc2)
        invlist = mergeinfo[2:]
        invlist = invlist[:-1]
        for inv in invlist:
            replace = {}
            replace.update(merge_fn.inventorInfoName(matter, inv))
            WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'inventorchange_multi.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'inventorchangeMultipleout.docx'))
            #get_template_docx('communications', 'inventorchange_multi.docx')
            doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'inventorchangeMultipleout.docx')) 
            composer.append(doc3)
        
        composer.append(docend)
        
    if method == 'BSCCombinedAssnDec':
        doc1.add_page_break()
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
        doc1.add_page_break()
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
            
    if method == 'assignment2016':
        doc1.add_page_break()
        composer = Composer(doc1)
        if mergeinfo[1] == 'true':
            doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'assignment2012_acc.docx')) 
            doc2.add_page_break()
            composer.append(doc2)
            
    if method == 'appdataupdate':
        doc1.add_page_break()
        composer = Composer(doc1)
        for i in range(int(mergeinfo[7])):
            doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_Updated_RPOAstage.docx')) 
            composer.append(doc2)
            
        doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_Updated_RPOAstageA.docx')) 
        doc3.add_page_break()
        composer.append(doc3)
        
    if method == 'recordation':
        use_second_list2 = False
        merge_fn = mergefunctions()
        composer = Composer(doc1)
        rolelist = []
        for i in range(5, len(mergeinfo), 2):
            if mergeinfo[i - 1] == "STARTNXT" or mergeinfo[i - 1] == "SELASSIGNEE":
                use_second_list2 = True
                
            if use_second_list2:
                rolelist.append(mergeinfo[i + 1])
        try:
            rolelist = rolelist[1:]
        except:
            rolelist = []

        i = 0
        for roleid in rolelist:       
            replace = {}
            if mergeinfo[0] == '2':
                replace.update(merge_fn.recordationRoleFill(matter, roleid))
            else:
                replace.update(merge_fn.assigneefill(matter, roleid))
            if i == 0:
                i = 1
                WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'miscellaneous', 'RecordationCoverSheet_Supplement.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'RecordationCoverSheet_Supplementout.docx'))
                doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'RecordationCoverSheet_Supplementout.docx')) 
            else:
                WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'miscellaneous', 'RecordationCoverSheet_Supplement1.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'RecordationCoverSheet_Supplement1out.docx'))
                doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'RecordationCoverSheet_Supplement1out.docx')) 
            composer.append(doc3)

    if email == 'TRUE':
        doc1.add_page_break()
        merge_fn = mergefunctions()
        doc2 = Document_compose(path)
        composer = Composer(doc2)
        replace = {}
        replace.update(merge_fn.cmgfill(matter))
        if method == 'msemails' or method == 'FFRptOutBasic' or method == 'honureport' or method == 'CommunicationLetter' or method == 'TM_ChgCounsel' or method == 'sendorderletter' or method == 'fa_confirm' or method == 'nikeaction_new' or method == 'patchgcounsel' or method == 'idsmemo' or method == 'ffOfficeActRcvd' or method == 'EPDecisiontoGrant' or method == 'litoclient':
            doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'reportletters', 'signoff2.docx'))
        else:
            WordMerger(os.path.join(settings.BASE_DIR, 'documents', 'reportletters', 'signoff.docx'), replace, os.path.join(settings.BASE_DIR, 'documents', 'temp', 'emailout.docx'))
            doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'temp', 'emailout.docx'))
        composer.append(doc3)
        
    composer.save("documents/multidocmerge/" + method +".docx")

def pathChanger(input_path, mergeinfo_list, mergefninfo, matter):
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
    
    if mergeinfo_list[1] == 'DraftOAInstruct':
        if mergefninfo[2] == '1':
            input_path = input_path.replace('ltrffDraftOaInstructions_2', 'ltrffDraftOaInstructions_HONU')
        if mergefninfo[2] == '2':
            input_path = input_path.replace('ltrffDraftOaInstructions_2', 'ltrffDraftOaInstructions_NYHonu')
            
    if mergeinfo_list[1] == 'ffOlp':
        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        if matter_data.country == 'CN' or matter_data.country == 'KR':
            input_path = input_path.replace('ffOLP', 'FFOLP_PTA')

    if mergeinfo_list[1] == 'blankletter':
        if mergefninfo[0] == 'TRUE':
            input_path = input_path.replace('BlankLetterContact.docx', 'BlankLetterAssociate.docx')

    if mergeinfo_list[1] == 'ownerchange':
        if mergefninfo[1] == 'FALSE' or mergefninfo[1] == 'false':
            input_path = input_path.replace('ownershipchange_fax.docx', 'ownershipchange_inv.docx')

    return input_path

# New separate function for merging documents
def mergeDoc(matter, mergeinfo, request):
    merge_fn = mergefunctions()
    mergeinfo_list = mergeinfo.split(",") 
    module_name = ".mergemethods.merges"
    class_name = mergeinfo_list[1]
    module = importlib.import_module(module_name, package='members')
    curMerge = getattr(module, class_name)
    merge_instance = curMerge()

    docpath = mergeinfo_list[0].split('/')

    replace = {}
    mergefninfo = mergeinfo.split(",")
    mergefninfo.pop(0)
    mergefninfo.pop(0)
    mergefninfo.pop(0)
    
    contacts = mergeinfo_list[2]
    # Pop emails in merge data
    if contacts == 'TRUE' and mergeinfo_list[1] != 'reportprvassnnew' and mergeinfo_list[1] != 'blankletter':
        mergefninfo.pop(0)
        mergefninfo.pop(0)
        mergefninfo.pop(0)

    if mergeinfo_list[1] == 'blankletter':
        mergefninfo.append(request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME'))

    docpath[1] = pathChanger(docpath[1], mergeinfo_list, mergefninfo, matter)

    #input_path = os.path.join(settings.BASE_DIR, 'documents', docpath[0], docpath[1])
    input_path = get_template_docx(docpath[0].lower(), docpath[1])
    output_path = os.path.join(settings.BASE_DIR, 'documents', 'merged', 'Document.docx')
    #input_path = merge_fn.find_case_insensitive_path(input_path)

    # without multiple docs
    doc = Document(input_path)
    keys = docx_get_keys2(doc)

    replace = getattr(merge_instance, class_name)(matter, mergefninfo, keys)

    # combine doc
    if contacts == 'TRUE':
        combinedoc(input_path, mergeinfo_list[1], mergefninfo, matter, contacts)
        input_path = os.path.join(settings.BASE_DIR, 'documents', 'multidocmerge', mergeinfo_list[1] + '.docx')
        doc = Document(input_path)

    # with multiple docs
    issuefee_email_url = None
    if mergeinfo_list[1] == 'issuefee':
        combinedoc(input_path, mergeinfo_list[1], mergefninfo, matter, contacts)
        input_path = os.path.join(settings.BASE_DIR, 'documents', 'multidocmerge', mergeinfo_list[1] + '.docx')
        doc = Document(input_path)
        isssubject = matter + ', Action Requested:  Review and signature of Issue Fee Transmittal'
        #issbody = "SIGNING ATTORNEY CHECKLIST FOR ISSUE FEE PAYMENT FILING \n\nIssue Fee due: " + replace.get('dueDate') + "\n\nAction Requested: Review and Signature of Issue Fee Transmittal Documents\n\nInstructions to Signing Attorney: Prior to signature of this document, please consider the attached Attorney Checklist."
        issemail_template_doc = get_template_docx('attachments', 'issuefeeEmail.docx')
        issemail_template_doc.seek(0)
        
        # Get duedate tag using the new function
        duedate_replace = merge_fn.getDuedateTag(matter)
        
        # Save template to temp file first
        temp_template_path = os.path.join(settings.BASE_DIR, 'documents', 'temp', 'issuefeeEmail_template.docx')
        os.makedirs(os.path.dirname(temp_template_path), exist_ok=True)
        with open(temp_template_path, 'wb') as f:
            f.write(issemail_template_doc.read())
        
        # Fill the issuefeeEmail.docx with duedate
        filled_email_path = os.path.join(settings.BASE_DIR, 'documents', 'temp', 'issuefeeEmail_filled.docx')
        WordMerger(temp_template_path, duedate_replace, filled_email_path)
        
        # Extract body text from the filled document
        filled_doc = Document(filled_email_path)
        issbody = '\n'.join([p.text for p in filled_doc.paragraphs])
        
        WAdata = merge_fn.WAfill('', matter)
        issTO = WAdata['WAEmail']
        if issTO == 'NO WORKING ATTORNEY EMAIL':
            issTO = ''
        issCC = ''
        issBCC = ''
        attachment = os.path.join(settings.BASE_DIR, 'documents', 'attachments', 'Notice of Allowance Review and Response.pdf')
        #attachment = get_template_docx('attachments', 'Notice of Allowance Review and Response.pdf')
        issuefee_email_url = Email(issbody, isssubject, issTO, issCC, issBCC , attachment, request)
            
    if mergeinfo_list[1] == 'assignment2016':
        if mergefninfo[0] == '1':
            input_path = input_path.replace('2012_2', '2012_not')
        if mergefninfo[0] == '2':
            input_path = input_path.replace('2012_2', '2012_att')
            
    if mergeinfo_list[1] == 'applicationdata_new2' or mergeinfo_list[1] == 'invchange' or mergeinfo_list[1] == 'applicationdata_updnew' or mergeinfo_list[1] == 'BSCCombinedAssnDec' or mergeinfo_list[1] == 'aiashortdecl' or mergeinfo_list[1] == 'assignment2016' or mergeinfo_list[1] == 'appdataupdate' or mergeinfo_list[1] == 'recordation' or mergeinfo_list[1] == 'missingpartsNw':
        combinedoc(input_path, mergeinfo_list[1], mergefninfo, matter, contacts)
        input_path = os.path.join(settings.BASE_DIR, 'documents', 'multidocmerge', mergeinfo_list[1] + '.docx')
        doc = Document(input_path)

    # doc merges
    if contacts == "FALSE":
        WordMerger(input_path, replace, output_path)

        ownerchange_email_url = None
        if mergeinfo_list[1] == 'ownerchange':
            twowk = (datetime.today() + timedelta(weeks=2)).strftime("%m/%d/%Y")
            matter_data = merge_fn.matterFill(matter)
            ownsubject = merge_fn.clientMatterNo(matter_data) + ', Action Requested:  Review and signature of Communication Re:  92bis - Please return for filing by ' + twowk
            email_template_doc = get_template_docx('attachments', 'ownerchangeEmail.docx')
            email_template_doc.seek(0)
            owndoc = Document(email_template_doc)
            # Extract body text from all paragraphs
            ownbody = '\n'.join([p.text for p in owndoc.paragraphs])

            ownTO = ''
            ownCC = ''
            ownBCC = ''
            attachment = output_path
            ownerchange_email_url = Email(ownbody, ownsubject, ownTO, ownCC, ownBCC , attachment, request)

        # ----- Azure Storage -----
        file_name = os.path.basename(output_path)
        file_name = file_name.split('.')
        #file_name[0] += ('-' + mergeinfo_list[1] + '-' + ''.join(random.choices(string.ascii_letters, k=6)))
        file_name[0] += ('-' + mergeinfo_list[1] + '-' + matter)
        file_name = file_name[0] + '.' + file_name[1]
        
        storage_account_url = f"https://{os.getenv('AZURE_ACCOUNT_NAME')}.blob.core.windows.net"
        container_name = 'media'
        start = time.time()
        try:
            credential = ManagedIdentityCredential()
            print(f"Credential setup: {time.time() - start:.2f}s")

            blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
            print(f"Blob client setup: {time.time() - start:.2f}s")

            with open(output_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"Upload time: {time.time() - start:.2f}s")
        
            # Authenticate using managed identity
            blob_client = BlobClient(storage_account_url, container_name, file_name, credential=credential)

            # Download the blob content
            stream = blob_client.download_blob()
            data = stream.readall()
            
            print('merge name:' + mergeinfo_list[1])

            doc_type = mergeinfo_list[1]
            if doc_type == 'corrappln':
                try:
                    index = mergefninfo.index('ENDDOC')
                    second_array = mergefninfo[index + 1:]
                except ValueError:
                    # 'ENDDOCS' not found
                    second_array = mergefninfo
                mergefninfo = second_array

            if doc_type == 'missingpartsNw':
                try:
                    enddoc_index = mergefninfo.index('ENDDOC')
                except ValueError:
                    enddoc_index = None

                try:
                    endfee_index = mergefninfo.index('ENDFEE')
                except ValueError:
                    endfee_index = None

                # Determine the later of the two indices
                if enddoc_index is not None and endfee_index is not None:
                    split_index = max(enddoc_index, endfee_index)
                    mergefninfo = mergefninfo[split_index + 1:]
                elif enddoc_index is not None:
                    mergefninfo = mergefninfo[enddoc_index + 1:]
                elif endfee_index is not None:
                    mergefninfo = mergefninfo[endfee_index + 1:]
                else:
                    mergefninfo = mergefninfo  # No change

            multidoc = (
                (doc_type == 'corrappln' and mergefninfo[0] != '') or
                (doc_type == 'pctcorrect' and mergefninfo[3] == 'true') or
                (doc_type == 'expressaban' and (mergefninfo[1] == '1' or mergefninfo[1] == '2' or mergefninfo[1] == '3')) or
                (doc_type == 'issuefee' and mergefninfo[3] == 'true') or
                (doc_type == 'missingpartsNw' and mergefninfo[1] != '')
            )

            # Check if this is multi-doc
            if not multidoc:
                # Special handling for issuefee - return both document and email URL
                if doc_type == 'issuefee' and issuefee_email_url is not None:
                    data_base64 = base64.b64encode(data).decode('utf-8')
                    return JsonResponse({
                        'document_data': data_base64,
                        'document_filename': file_name,
                        'email_url': issuefee_email_url,
                        'document_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    })
                if doc_type == 'ownerchange' and ownerchange_email_url is not None:
                    data_base64 = base64.b64encode(data).decode('utf-8')
                    return JsonResponse({
                        'document_data': data_base64,
                        'document_filename': file_name,
                        'email_url': ownerchange_email_url,
                        'document_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    })
                # Return the first document as a download (optional)
                response = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
                response['Content-Disposition'] = f'attachment; filename={file_name}'
                response.set_cookie('downloadComplete', 'true')
                print("First document saved in session. Returning it.")
                return response

            if multidoc:
                if mergeinfo_list[1] == 'corrappln':
                    try:
                        extmergeinfo = mergeinfo.split(',')
                        index = extmergeinfo.index('ENDDOC')
                        second_array = ','.join(extmergeinfo[:3] + extmergeinfo[index + 1:])
                    except ValueError:
                        # 'ENDDOCS' not found
                        second_array = mergeinfo
                    mergeinfo = second_array

                    extime = mergeinfo.replace('corrappln', 'exttimeCF')
                    extime = extime.replace('communications', 'transmittal')
                    extime = extime.split(',')
                    extime = ','.join(extime[:3] + [mergefninfo[0]] + extime[10:])
                    data2, file_name2 = mergemultidoc(matter, extime)

                if mergeinfo_list[1] == 'missingpartsNw':
                    extmergeinfo = mergeinfo.split(',')
                    try:
                        enddoc_index = extmergeinfo.index('ENDDOC')
                    except ValueError:
                        enddoc_index = None

                    try:
                        endfee_index = extmergeinfo.index('ENDFEE')
                    except ValueError:
                        endfee_index = None

                    # Determine the later of the two indices
                    if enddoc_index is not None and endfee_index is not None:
                        split_index = max(enddoc_index, endfee_index)
                        mergeinfo = ','.join(extmergeinfo[:3] + extmergeinfo[split_index + 1:])
                    elif enddoc_index is not None:
                        mergeinfo = ','.join(extmergeinfo[:3] + extmergeinfo[enddoc_index + 1:])
                    elif endfee_index is not None:
                        mergeinfo = ','.join(extmergeinfo[:3] + extmergeinfo[endfee_index + 1:])
                    else:
                        pass

                    extime = mergeinfo.replace('missingpartsxmit', 'exttimeCF')
                    extime = extime.replace('missingpartsNw', 'exttimeCF')
                    extime = extime.replace('communications', 'transmittal')
                    extime = extime.split(',')
                    extime = ','.join(extime[:3] + [mergefninfo[1]] + extime[19:])
                    data2, file_name2 = mergemultidoc(matter, extime)

                if mergeinfo_list[1] == 'pctcorrect':
                    pctext = mergeinfo.replace('pctcorrectdefects', 'PCTExtension')
                    pctext = pctext.replace('pctcorrect', 'pctextension')
                    data2, file_name2 = mergemultidoc(matter, pctext)

                if mergeinfo_list[1] == 'expressaban':
                    if mergefninfo[1] == '1':
                        aban2 = mergeinfo.replace('ExpressAbanAdd.docx', 'ExpAbanAvoidPub.docx')
                        aban2 = aban2.replace('expressaban', 'expressaban2')
                    if mergefninfo[1] == '2':
                        aban2 = mergeinfo.replace('ExpressAbanAdd.docx', 'ExpAbanRefund.docx')
                        aban2 = aban2.replace('expressaban', 'expressaban2')
                    if mergefninfo[1] == '3':
                        aban2 = mergeinfo.replace('ExpressAbanAdd.docx', 'Express_Abandonment.docx')
                        aban2 = aban2.replace('expressaban', 'expressaban2')
                    data2, file_name2 = mergemultidoc(matter, aban2)

                if mergeinfo_list[1] == 'issuefee':
                    stateofallow = mergeinfo.replace('issuefeexmit', 'stateofallowcomments')
                    stateofallow = stateofallow.replace('issuefee', 'stateofallow')
                    data2, file_name2 = mergemultidoc(matter, stateofallow)

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    zip_file.writestr(file_name, data)
                    zip_file.writestr(file_name2, data2)

                zip_buffer.seek(0)
                zip_data = zip_buffer.read()
                
                # Special handling for issuefee - return both zip and email URL
                if mergeinfo_list[1] == 'issuefee' and issuefee_email_url is not None:
                    zip_data_base64 = base64.b64encode(zip_data).decode('utf-8')
                    zip_filename = mergeinfo_list[1] + '-' + matter + '-documents.zip'
                    return JsonResponse({
                        'document_data': zip_data_base64,
                        'document_filename': zip_filename,
                        'email_url': issuefee_email_url,
                        'document_type': 'application/zip'
                    })
                
                response = HttpResponse(zip_data, content_type="application/zip")
                response['Content-Disposition'] = 'attachment; filename=' + mergeinfo_list[1] + '-' + matter + '-documents.zip'
                response.set_cookie('downloadComplete', 'true')
                print("Returning zipped documents.")
                return response

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

    # outlook merges
    if contacts == "TRUE":
        WordMerger(input_path, replace, output_path)
        
        tolist = [email.strip() for email in mergeinfo_list[3].split(';') if email.strip()]
        cclist = [email.strip() for email in mergeinfo_list[4].split(';') if email.strip()]
        bcclist = [email.strip() for email in mergeinfo_list[5].split(';') if email.strip()]
        
        subject, body = DocumentReader(output_path, mergeinfo_list[1])

        attachmethods = [
            'ptorecdReport', 'basicreport', 'PCTRptOutMiscItmsRcvd', 'PCTRptOutBasicLtr',
            'FFRptOutBasic', 'honureport', 'ffMiscItemsRcvd', 'miscitemsdue',
            'tm_basicreport', 'ffOfficeActRcvdAuNz', 'tmrecdReport', 'ffMiscItemsDue',
            'msemails', 'fa_confirm', 'nikeaction_new', 'retainer', 'novemail', 'idsmemo',
            'micnffallow', 'ffOfficeActRcvd'
        ]
        
        i = 0
        if mergeinfo_list[1] == 'idsmemo':
            i = 7

        if (mergeinfo_list[1] in attachmethods) and (mergefninfo[2 + i] != 'NoAttachSelected'):
            print(mergefninfo[2 + i])
            attachids = mergefninfo[2 + i].split(';')
            attachnames = mergefninfo[3 + i].split(';')
            
            attachpaths = get_documents(attachids, attachnames)
        else:
            attachpaths = []
        
        contact = Email(body, subject, tolist, cclist, bcclist, attachpaths, request)
        
        return JsonResponse({'url': f'{contact}'})

def mergemultidoc(matter, mergeinfo):
    merge_fn = mergefunctions()
    mergeinfo_list = mergeinfo.split(",") 
    module_name = ".mergemethods.merges"
    class_name = mergeinfo_list[1]
    module = importlib.import_module(module_name, package='members')
    curMerge = getattr(module, class_name)
    merge_instance = curMerge()

    docpath = mergeinfo_list[0].split('/')
    
    #input_path = os.path.join(settings.BASE_DIR, 'documents', docpath[0], docpath[1])
    input_path = get_template_docx(docpath[0], docpath[1])
    output_path = os.path.join(settings.BASE_DIR, 'documents', 'merged', 'Document.docx')
    #input_path = merge_fn.find_case_insensitive_path(input_path)

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

    replace = getattr(merge_instance, class_name)(matter, mergefninfo, keys)

    if contacts == "FALSE":
        WordMerger(input_path, replace, output_path)
        # ----- Azure Storage -----
        file_name = os.path.basename(output_path)
        file_name = file_name.split('.')
        #file_name[0] += ('-' + mergeinfo_list[1] + '-' + ''.join(random.choices(string.ascii_letters, k=6)))
        file_name[0] += ('-' + mergeinfo_list[1] + '-' + matter)
        file_name = file_name[0] + '.' + file_name[1]
        
        storage_account_url = f"https://{os.getenv('AZURE_ACCOUNT_NAME')}.blob.core.windows.net"
        container_name = 'media'
        start = time.time()
        try:
            credential = ManagedIdentityCredential()
            print(f"Credential setup: {time.time() - start:.2f}s")

            blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
            print(f"Blob client setup: {time.time() - start:.2f}s")

            with open(output_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"Upload time: {time.time() - start:.2f}s")
        
            # Authenticate using managed identity
            blob_client = BlobClient(storage_account_url, container_name, file_name, credential=credential)

            # Download the blob content
            stream = blob_client.download_blob()
            data = stream.readall()

            return data, file_name

        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

def check_email(email):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if re.fullmatch(pattern, email):
        return True
    else:
        return False

def get_doc_names(request):
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        actids = request.POST.get('actids')
        actids = actids.replace('"', "")
        
        actlist = actids.split(';')
        
        print(actids)
        
        # report = await execute_report(data)
        # await asyncio.sleep(30)
        # await fetch_report(report)        

        results = []
        seen_ids = set()
        logical_names = []
        attachment_ids = []
        if actids != '':
            for act in actlist:
                query = f"""
                    SELECT CAST(subject AS VARCHAR(8000)) as subject, attachment.attachmentid
                    FROM objectposting 
                        JOIN posting on objectposting.postid = posting.postid
                        JOIN containedattachment on posting.acid = containedattachment.containerid
                        JOIN attachment on containedattachment.attachmentid = attachment.attachmentid
                    Where locationid = {act}
                        AND objtype = 28
                        AND posting.type = 'D'
                        AND subject NOT LIKE '%Postcard%'
                        AND subject NOT LIKE '%e-receipt%'
                        and physicalname not like '%.eml'
                        and physicalname like '%.%'
                    """
                
                with connections['FIP'].cursor() as cursor:
                    #cursor.execute(query, (10920,))
                    cursor.execute(query)
                    results = cursor.fetchall()
                    

                for result in results:
                    logical_name, attachment_id = result
                    if attachment_id not in seen_ids:
                        seen_ids.add(attachment_id)
                        logical_names.append(logical_name)
                        attachment_ids.append(attachment_id)

        # Format the results for printing
        logical_names = '; '.join(str(name).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for name in logical_names)
        attachment_ids = '; '.join(str(id).replace('(', '').replace(')', '').replace("'", '').replace(',', '') for id in attachment_ids)
    
        return JsonResponse({'message': {'names': logical_names, 'ids': attachment_ids}})
    
    else:
        return JsonResponse({'error': 'Invalid request method'})

def get_token():
    # Read the public key from a file
    public_key_pem_str = os.getenv("FIP_REST_PEM")
    access_token = os.getenv("FIP_REST_TOKEN")
    
    rest_api_token = access_token
    public_key_obj = serialization.load_pem_public_key(
        public_key_pem_str.encode(),
        backend=default_backend()
    )
    # Create the JSON to be encrypted for the authorization token
    token_data = json.dumps({
        "restApiToken": rest_api_token,
        "timestamp": int(time.time() * 1000)
    })
    encrypted_bytes = public_key_obj.encrypt(
        token_data.encode(),
        padding.PKCS1v15()
    )
    encrypted_auth_token = base64.b64encode(encrypted_bytes).decode()

    headers = {
        'Authorization': encrypted_auth_token,
        'X-FIP-API-TOKEN': rest_api_token,
    }
    
    return headers

def get_documents(documentids, documentnames):
    attachpaths = []
    for i, document in enumerate(documentids):
        headers = get_token()
        api_url = f"https://api.foundationip.com/fip-rest/v1/documents/{document}"
        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            content = response.content

            filepath = os.path.join(settings.BASE_DIR, 'attachments', documentnames[i])
            with open(filepath, 'wb') as file:
                file.write(content)
                print(f"Document saved as {documentnames[i]}")
            attachpaths.append(filepath)
        else:
            print(f"Error: {response.status_code}, {response.text}")
    
    return attachpaths

def download_doc(filename):
    account_url = f"https://{os.getenv('AZURE_ACCOUNT_NAME')}.blob.core.windows.net"
    container_name = "media"

    try:
        # Authenticate using managed identity
        credential = ManagedIdentityCredential()
        blob_client = BlobClient(account_url, container_name, filename, credential=credential)

        # Download the blob content
        stream = blob_client.download_blob()
        data = stream.readall()

        # Return the file as a download
        response = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        quoted_filename = quote(filename)
        response['Content-Disposition'] = f'attachment; filename={quoted_filename}'
        return response
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
    
def get_blob_document(container_name, file_name, storage_account_url):
    start = time.time()
    if storage_account_url == '':
        storage_account_url = f"https://{os.getenv('AZURE_ACCOUNT_NAME')}.blob.core.windows.net"
    try:
        # Set up managed identity credential
        credential = ManagedIdentityCredential()
        print(f"Credential setup: {time.time() - start:.2f}s")

        # Create blob service client
        blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
        print(f"Blob client setup: {time.time() - start:.2f}s")

        # Download the blob content as bytes
        stream = blob_client.download_blob()
        document_bytes = stream.readall()
        print(f"Download time: {time.time() - start:.2f}s")

        return BytesIO(document_bytes)

    except Exception as e:
        print(f"Error: {e}")
        return None

def get_template_docx(*path_parts):
    blob_path = "/".join(path_parts)
    print('Azure storage: ' + blob_path)
    return get_blob_document('templates', blob_path, '')

def edit_template(request):
    mergedict = MergeDef.objects.using('SideBar').filter(operational="TRUE").order_by('mergename')
    roles = MergeRole.objects.using('SideBar').all()
    categories = MergeCategory.objects.using('SideBar').all()

    return render(request, 'edittemplate.html', {'mergedict': mergedict, 'roles': roles, 'categories': categories})

def download_template(request):
    if request.method == 'GET':
        file_name = request.GET.get('file_name', '')
        if not file_name:
            return HttpResponse("Error: file_name parameter is required", status=400)
        
        storage_account_url = f"https://{os.getenv('AZURE_ACCOUNT_NAME')}.blob.core.windows.net"
        container_name = 'templates'  # Templates are stored in 'templates' container
        start = time.time()
        try:
            credential = ManagedIdentityCredential()

            # Authenticate using managed identity
            blob_client = BlobClient(storage_account_url, container_name, file_name, credential=credential)

            # Download the blob content
            stream = blob_client.download_blob()
            data = stream.readall()
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)

        # Extract just the filename for the download
        download_filename = os.path.basename(file_name)
        response = HttpResponse(data, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response['Content-Disposition'] = f'attachment; filename={download_filename}'
        response.set_cookie('downloadComplete', 'true')
        print("Template downloaded. Returning it.")
        return response
    else:
        return HttpResponse("Error: GET method required", status=405)

def upload_template(request):
    if request.method == 'POST' and request.FILES.get('document'):
        try:
            # Get the original file path from POST data (where it was downloaded from)
            original_file_path = request.POST.get('original_file_path', '')
            if not original_file_path:
                return JsonResponse({"message": "Error: original_file_path parameter is required"}, status=400)
            
            storage_account_url = f"https://{os.getenv('AZURE_ACCOUNT_NAME')}.blob.core.windows.net"
            container_name = 'templates'  # Upload edited templates back to templates container
            start = time.time()
            file = request.FILES['document']
            
            credential = ManagedIdentityCredential()
            print(f"Credential setup: {time.time() - start:.2f}s")

            blob_service_client = BlobServiceClient(account_url=storage_account_url, credential=credential)
            # Use the original file path to upload back to the same location
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=original_file_path)
            print(f"Blob client setup: {time.time() - start:.2f}s")

            blob_client.upload_blob(file, overwrite=True)
            print(f"Upload time: {time.time() - start:.2f}s")
            print(f"File uploaded to: {container_name}/{original_file_path}")

            return JsonResponse({"message": "File uploaded successfully!", "file_name": original_file_path})
        except Exception as e:
            return JsonResponse({"message": f"Error uploading file: {str(e)}"}, status=500)
    else:
        return JsonResponse({"message": "No file provided or invalid request method"}, status=400)
