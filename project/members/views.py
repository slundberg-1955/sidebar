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

from copy import deepcopy
from lxml import etree as lxml_etree

from concurrent.futures import ThreadPoolExecutor
from .models import Matter
from .models import Rvwmatterinventors
from .models import MergeCategory
from .models import MergeRole
from .models import MergeDef
from .models import Orgprofile, Matterparticipant, Rvwmatterpersonnel, Contactinfo, Personprofile, Activity, Relatedmatter, FvContact4, Rvworgpersonnel
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
from django.db.models import Q

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

def _iter_table_paragraphs(table):
    """Yield all paragraphs in a table and in any nested tables inside its cells."""
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                yield p
            for nested in getattr(cell, 'tables', []):
                yield from _iter_table_paragraphs(nested)

def _docx_paragraphs_with_headers_footers(doc):
    """Yield all paragraphs in document body, tables (including nested), and headers/footers."""
    # Body paragraphs (what Paragraph.get_all(doc) uses)
    for p in Paragraph.get_all(doc):
        yield p
    # Paragraphs inside tables (and nested tables)
    for table in getattr(doc, 'tables', []):
        yield from _iter_table_paragraphs(table)
    for section in doc.sections:
        for header in (section.header, section.footer):
            for p in header.paragraphs:
                yield p
        if getattr(section, 'different_first_page_header_footer', False):
            for attr in ('first_page_header', 'first_page_footer'):
                header = getattr(section, attr, None)
                if header is not None:
                    for p in header.paragraphs:
                        yield p

def docx_replace2(doc, **kwargs: str):
    replace_items = [(k, str(v)) for k, v in kwargs.items() if k is not None and k != ""]
    if not replace_items:
        return
    for p in _docx_paragraphs_with_headers_footers(doc):
        # Skip paragraphs that cannot contain merge tags (avoids Paragraph + N replace_key calls per para)
        try:
            if "<<" not in (p.text or ""):
                continue
        except Exception:
            pass
        paragraph = Paragraph(p)
        for key, value in replace_items:
            paragraph.replace_key(f"<<{key}>>", value)

def docx_get_keys2(doc: Any) -> List[str]:
    result = set()  # unique items
    for p in _docx_paragraphs_with_headers_footers(doc):
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
    
# def addSA(request):
#     if request.method == 'POST':
#         # Query the database for distinct personLastNameFirstName values, sorted by fName
#         SAs = (Rvwmatterpersonnel.objects.using('FIP')
#                .filter(roleid=34619, orgid=4, registrationno__isnull=False)
#                .exclude(rolename='Inactive Personnel')
#                .values('fname', 'lname')
#                .distinct()
#                .order_by('fname'))

#         # Extract the required values into a list of concatenated strings
#         SAarr = [f"{SA['fname']} {SA['lname']}" for SA in SAs]

#         return JsonResponse({'message': SAarr})
    
#     else:
#         return JsonResponse({'error': 'Invalid request method'})

def addSA(request):
    if request.method == 'POST':
        # Pull distinct first/last names for contact attorneys and attorneys
        attorneys = (
            Rvworgpersonnel.objects.using('FIP')
            .filter(
                Q(rolename__in=['contact attorney', 'attorney']),
                access='Granted',
                orgid='4'
            )
            .exclude(fname__isnull=True)
            .exclude(lname__isnull=True)
            .exclude(lname='Test')
            .values('fname', 'lname')
            .distinct()
            .order_by('fname', 'lname')
        )

        # Build array of "First Last"
        names = [f"{a['fname']} {a['lname']}" for a in attorneys]

        return JsonResponse({'message': names})
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

def remove_paragraph_after_last_table(doc):
    body = doc.element.body
    elements = list(body)

    for i in range(len(elements) - 1):
        if elements[i].tag.endswith('tbl') and elements[i + 1].tag.endswith('p'):
            body.remove(elements[i + 1])
            break  # only remove the first paragraph after the last table

    return doc

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

        minfo11 = int(mergeinfo[12]) if len(mergeinfo) > 12 and mergeinfo[12] else 0
        minfo12 = int(mergeinfo[13]) if len(mergeinfo) > 13 and mergeinfo[13] else 0
        minfo13 = int(mergeinfo[14]) if len(mergeinfo) > 14 and mergeinfo[14] else 0
        minfo14 = int(mergeinfo[15]) if len(mergeinfo) > 15 and mergeinfo[15] else 0
        if minfo11 > 0 or minfo12 > 0 or minfo13 > 0 or minfo14 > 0:
            #doc3 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'MissingPartsXmit3.docx'))
            doc3 = Document_compose(get_template_docx('communications', 'MissingPartsXmit3.docx'))
            doc3.add_page_break()
            composer.append(doc3)

        #doc4 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'communications', 'MissingPartsXmit4.docx'))
        doc4 = Document_compose(get_template_docx('communications', 'MissingPartsXmit4.docx'))
        composer.append(doc4)

    if method == 'applicationdata_new2' or method == 'applicationdata_updnew':
        t0 = time.time()
        print(f"[applicationdata_updnew] START combinedoc block, method={method}, mergeinfo={mergeinfo}")
        update_suffix = '_update' if method == 'applicationdata_updnew' else ''
        #doc1.add_page_break()
        # applicationdata_new2: check boxes 2, 3, 4 on doc1 (original ApplicationDataSheet) before adding inventors/etc.
        if method == 'applicationdata_new2' and len(mergeinfo) >= 7:
            app_new2_temp = os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2_middle_temp.docx')
            os.makedirs(os.path.dirname(app_new2_temp), exist_ok=True)
            doc1.save(app_new2_temp)
            if mergeinfo[6] in ('true', True):
                check_checkbox_at_position_xmlsafe(app_new2_temp, 2, checked=True)
            if mergeinfo[2] in ('true', True):
                check_checkbox_at_position_xmlsafe(app_new2_temp, 3, checked=True)
            if mergeinfo[3] in ('true', True):
                check_checkbox_at_position_xmlsafe(app_new2_temp, 4, checked=True)
            check_checkbox_at_position_xmlsafe(app_new2_temp, 5, checked=True)
            doc1 = Document_compose(app_new2_temp)

        doc2 = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2inventor.docx'))
        docend = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2end.docx'))
        composer = Composer(doc2)
        print(f"[applicationdata_updnew] Docs loaded {time.time()-t0:.2f}s")

        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        print(f"[applicationdata_updnew] matterFill done {time.time()-t0:.2f}s")

        # For applicationdata_updnew: only query participants for sections that are selected
        # For applicationdata_new2: need_inv always True; need_app/need_assign from radio (incapp/incnon/noapp/both)
        if method == 'applicationdata_new2':
            need_inv = True
            if len(mergeinfo) > 7:
                radio_val = (mergeinfo[7] or '').lower().strip()
                need_app = radio_val in ('incapp', 'both')
                need_assign = radio_val in ('incnon', 'both')
            else:
                need_app = need_assign = False
        else:
            need_inv = mergeinfo[0] == 'true' if len(mergeinfo) > 0 else False
            need_app = mergeinfo[4] == 'true' if len(mergeinfo) > 4 else False
            need_assign = mergeinfo[5] == 'true' if len(mergeinfo) > 5 else False

        # Inventor mailing address source: applicationdata_updnew uses mergeinfo[8] (apprad);
        # applicationdata_new2 derives from mergeinfo[4] (client) and mergeinfo[5] (app) checkboxes
        if method == 'applicationdata_new2' and len(mergeinfo) > 5:
            if mergeinfo[4] == 'true':
                mailing_source = 'client'
            elif mergeinfo[5] == 'true':
                mailing_source = 'applicant'
            else:
                mailing_source = 'home'
        else:
            mailing_source = (mergeinfo[8] or 'home').lower().strip() if len(mergeinfo) > 8 else 'home'
            if mailing_source not in ('home', 'client', 'applicant'):
                mailing_source = 'home'

        inv_blank = {
            'inventorCnt': '', 'inventor': '', 'invpre': '', 'inventorFirstName': '',
            'inventorMiddleInitial': '', 'inventorLastName': '', 'inventorSuffix': '',
            'inventorHomeCity': '', 'inventorHomeState': '', 'inventorHomeCountry': '',
            'inventorMailingStreet1': '', 'inventorMailingStreet2': '', 'inventorMailingCity': '',
            'inventorMailingState': '', 'inventorMailingZip': '', 'inventorMailingCountry': ''
        }
        inv_template = os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2inventorMultiple' + update_suffix + '.docx')
        inv_temp_out = os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2inventorMultipleout.docx')

        print(f"[applicationdata_updnew] Inventors: need_inv={need_inv} {time.time()-t0:.2f}s")
        if not need_inv:
            WordMerger(inv_template, dict(inv_blank), inv_temp_out)
            composer.append(Document_compose(inv_temp_out))
        else:
            inv_replacements = merge_fn.inventorInfoBulk(matter_data, method, mailing_address_source=mailing_source)
            print(f"[applicationdata_updnew] inventorInfoBulk returned {len(inv_replacements)} inventors {time.time()-t0:.2f}s")
            for i, replace in enumerate(inv_replacements):
                WordMerger(inv_template, replace, inv_temp_out)
                if method in ('applicationdata_new2', 'applicationdata_updnew'):
                    country = (replace.get('inventorHomeCountry') or '').strip().lower()
                    is_us = 'united states' in country or country in ('us', 'usa', 'u.s.', 'u.s.a.')
                    check_checkbox_at_position_xmlsafe(inv_temp_out, 1, checked=is_us)
                    check_checkbox_at_position_xmlsafe(inv_temp_out, 2, checked=not is_us)
                composer.append(Document_compose(inv_temp_out))
                if (i + 1) % 5 == 0:
                    print(f"[applicationdata_updnew] Inventor block {i+1}/{len(inv_replacements)} {time.time()-t0:.2f}s")
        print(f"[applicationdata_updnew] Inventors done {time.time()-t0:.2f}s")
        composer.append(doc1)

        # Domestic Benefit/National Stage Information
        # mergeinfo[0]
        try:
            if method == 'applicationdata_updnew' and len(mergeinfo) > 6:
                raw = (mergeinfo[6] or '').strip()
                n_rpoa = int(raw) if raw else 0
            else:
                n_rpoa = int(mergeinfo[0]) if (len(mergeinfo) > 0 and mergeinfo[0] not in (None, '')) else 0
        except (ValueError, TypeError):
            n_rpoa = 0
        rpoa_count = 1 if n_rpoa <= 1 else n_rpoa
        rpoa_template = os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_Updated_RPOAstage.docx')
        rpoa_template2 = os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_Updated_RPOAstageblank.docx')
        if n_rpoa == 0 and method == 'applicationdata_updnew':
            composer.append(Document_compose(rpoa_template2))
        else:
            for _ in range(rpoa_count):
                composer.append(Document_compose(rpoa_template))

        # Foreign priority / filing info: first row uses foreign1 template; additional rows use foreignmulti (like inventor multiples).
        foreign_replacements = merge_fn.foreignfillBulk(matter)
        foreign_template = os.path.join(
            settings.BASE_DIR, 'documents', 'formaldocuments',
            'ApplicationDataSheet_NEW2Bforeign1.docx',
        )
        foreign_multi_template = os.path.join(
            settings.BASE_DIR, 'documents', 'formaldocuments',
            'ApplicationDataSheet_NEW2Bforeignmulti.docx',
        )
        foreign_temp_out = os.path.join(
            settings.BASE_DIR, 'documents', 'temp',
            'ApplicationDataSheet_NEW2Bforeign1out.docx',
        )
        foreign_multi_temp_out = os.path.join(
            settings.BASE_DIR, 'documents', 'temp',
            'ApplicationDataSheet_NEW2Bforeignmultiout.docx',
        )
        foreign_blank = {
            'foreignNo': '',
            'foreignCntry': '',
            'foreignFiledDate': '',
        }
        # applicationdata_updnew: domestic stage count mergeinfo[6] is 0 or blank → one foreign1 page with empty tags only (no FIP foreign rows).
        if method == 'applicationdata_updnew' and n_rpoa == 0:
            WordMerger(foreign_template, dict(foreign_blank), foreign_temp_out)
            composer.append(Document_compose(foreign_temp_out))
        else:
            foreign_replacements = merge_fn.foreignfillBulk(matter)
            if len(foreign_replacements) == 1:
                WordMerger(foreign_template, foreign_replacements[0], foreign_temp_out)
                composer.append(Document_compose(foreign_temp_out))

            elif len(foreign_replacements) > 1:
                WordMerger(foreign_template, foreign_replacements[0], foreign_temp_out)
                doc = Document_compose(foreign_temp_out)
                doc = remove_paragraph_after_last_table(doc)
                composer.append(doc)
                for replace in foreign_replacements[1:]:
                    WordMerger(foreign_multi_template, replace, foreign_multi_temp_out)
                    doc = Document_compose(foreign_multi_temp_out)
                    doc = remove_paragraph_after_last_table(doc)
                    composer.append(doc)

        B_template = os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2B.docx')
        if mergeinfo[3] in ('true', True) and method == 'applicationdata_new2':
            check_checkbox_at_position_xmlsafe(B_template, 2, checked=True)
            check_checkbox_at_position_xmlsafe(B_template, 3, checked=True)
        composer.append(Document_compose(B_template))

        app_blank = {
            'applCnt': '', 'applicantCity': '', 'applicantState': '', 'applicantZip': '',
            'applicantCountry': '', 'applicantStreet1': '', 'applicantStreet2': '',
            'applicant': '', 'applicantName': ''
        }
        app_template = os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2applicantMulti' + update_suffix + '.docx')
        app_temp_out = os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2applicantMultipleout.docx')

        print(f"[applicationdata_updnew] Applicants: need_app={need_app} {time.time()-t0:.2f}s")
        if not need_app:
            WordMerger(app_template, dict(app_blank), app_temp_out)
            composer.append(Document_compose(app_temp_out))
        else:
            app_replacements = merge_fn.applicantfillBulk(matter_data)
            print(f"[applicationdata_updnew] applicantfillBulk returned {len(app_replacements)} applicants {time.time()-t0:.2f}s")
            assignee_names = {str(r.get('assignee') or r.get('assigneeName') or '').strip() for r in merge_fn.assigneefillBulk(matter_data)}
            for replace in app_replacements:
                WordMerger(app_template, replace, app_temp_out)
                if method in ('applicationdata_new2', 'applicationdata_updnew'):
                    applicant_name = str(replace.get('applicant') or replace.get('applicantName') or '').strip()
                    is_also_assignee = applicant_name and applicant_name in assignee_names
                    check_checkbox_at_position_xmlsafe(app_temp_out, 1, checked=is_also_assignee)
                    is_org = replace.get('applicantIsOrg') in (True, 'true', 'True')
                    check_checkbox_at_position_xmlsafe(app_temp_out, 8, checked=is_org)
                composer.append(Document_compose(app_temp_out))
        print(f"[applicationdata_updnew] Applicants done {time.time()-t0:.2f}s")

        # Page break after applicant information
        doc_app_break = Document_compose(os.path.join(settings.BASE_DIR, 'documents', 'miscellaneous', 'blank.docx'))
        doc_app_break.add_page_break()
        composer.append(doc_app_break)

        assign_blank = {
            'assigneeCnt': '', 'assigneeName': '', 'assigneeStreet': '', 'assigneeCity': '',
            'assigneeState': '', 'assigneeZip': '', 'assigneeCountry': '', 'assigneeStreet1': '',
            'assigneeStreet2': '', 'assignee': '', 'assigneeAddress': '', 'assigneeStateInc': ''
        }
        assign_template = os.path.join(settings.BASE_DIR, 'documents', 'formaldocuments', 'ApplicationDataSheet_NEW2assigneeMulti' + update_suffix + '.docx')
        assign_temp_out = os.path.join(settings.BASE_DIR, 'documents', 'temp', 'ApplicationDataSheet_NEW2assigneeMultipleout.docx')

        print(f"[applicationdata_updnew] Assignees: need_assign={need_assign} {time.time()-t0:.2f}s")
        if not need_assign:
            WordMerger(assign_template, dict(assign_blank), assign_temp_out)
            composer.append(Document_compose(assign_temp_out))
        else:
            assign_replacements = merge_fn.assigneefillBulk(matter_data)
            print(f"[applicationdata_updnew] assigneefillBulk returned {len(assign_replacements)} assignees {time.time()-t0:.2f}s")
            for replace in assign_replacements:
                WordMerger(assign_template, replace, assign_temp_out)
                if method in ('applicationdata_new2', 'applicationdata_updnew'):
                    is_org = replace.get('assigneeIsOrg') in (True, 'true', 'True')
                    check_checkbox_at_position_xmlsafe(assign_temp_out, 1, checked=is_org)
                composer.append(Document_compose(assign_temp_out))
        print(f"[applicationdata_updnew] Assignees done {time.time()-t0:.2f}s")

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

    if method == 'generalxmitCF':
        composer = Composer(doc1)

        # UI indices for generalxmitCF:
        # [5] recalc fees, total claims (6), highest total (7), independent (8), highest independent (9)
        # 32 payload fields before optional exttimeCF: [29] pre-appeal conf., [30] pre-appeal pages, [31] other text; [4] = Mar2013 fees (1.111 or 41.41)
        recalc_fees = (
            len(mergeinfo) > 5 and str(mergeinfo[5]).strip().lower() == 'true'
        )
        add_claim_amend = recalc_fees

        claim_amend_doc = get_template_docx('transmittal', 'generaltrasmittalCLAMEND.docx')
        end_doc = get_template_docx('transmittal', 'generaltransmittalEND.docx')

        if add_claim_amend:
            composer.append(Document_compose(claim_amend_doc))

        # Always append END/signature document.
        composer.append(Document_compose(end_doc))

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
        
    if method == 'applicationdata_updnew' or method == 'applicationdata_new2':
        t_save = time.time()
        print(f"[{method}] combinedoc: saving composer to multidocmerge {method}.docx")
    composer.save("documents/multidocmerge/" + method +".docx")
    if method == 'applicationdata_updnew' or method == 'applicationdata_new2':
        print(f"[{method}] combinedoc: composer.save done {time.time()-t_save:.2f}s")

def pathChanger(input_path, mergeinfo_list, mergefninfo, matter):
    if mergeinfo_list[1] == 'applicationdata_updnew' and input_path.endswith('.docx'):
        input_path = input_path[:-5] + '_update.docx'
        
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
    generalxmit_has_ext = False
    applicationdata_updnew_corrapplicant = False
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

    # generalxmitCF: extension-of-time UI appends 10 exttimeCF fields after 31 generalxmit fields (merge class + combinedoc only use generalxmit).
    if mergeinfo_list[1] == 'generalxmitCF':
        mergefninfo, gx_addl_doc_flat = _generalxmit_split_enddoc_docs(mergefninfo)
        # Emails already popped above; transmittal core is always 32 tokens before optional exttimeCF (10).
        gx_end = 32
        if len(mergefninfo) > gx_end:
            generalxmit_has_ext = True
            mergefninfo = mergefninfo[:gx_end]
        if gx_addl_doc_flat:
            mergefninfo = list(mergefninfo) + ['DOCEXTRA'] + gx_addl_doc_flat

    if mergeinfo_list[1] == 'blankletter':
        mergefninfo.append(request.headers.get('X-MS-CLIENT-PRINCIPAL-NAME'))

    if mergeinfo_list[1] == 'applicationdata_updnew':
        applicationdata_updnew_corrapplicant = (
            len(mergefninfo) > 4
            and str(mergefninfo[4]).strip().lower() == 'true'
        )

    docpath[1] = pathChanger(docpath[1], mergeinfo_list, mergefninfo, matter)

    #input_path = os.path.join(settings.BASE_DIR, 'documents', docpath[0], docpath[1])
    input_path = get_template_docx(docpath[0].lower(), docpath[1])
    output_path = os.path.join(settings.BASE_DIR, 'documents', 'merged', 'Document.docx')
    #input_path = merge_fn.find_case_insensitive_path(input_path)

    # without multiple docs
    doc = Document(input_path)
    keys = docx_get_keys2(doc)

    if mergeinfo_list[1] == 'applicationdata_updnew':
        t_merge = time.time()
        print(f"[mergeDoc] applicationdata_updnew: calling merge class applicationdata_updnew")
    replace = getattr(merge_instance, class_name)(matter, mergefninfo, keys)
    if mergeinfo_list[1] == 'applicationdata_updnew':
        print(f"[mergeDoc] applicationdata_updnew: merge class done {time.time()-t_merge:.2f}s")

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
            
    if mergeinfo_list[1] == 'applicationdata_new2' or mergeinfo_list[1] == 'invchange' or mergeinfo_list[1] == 'applicationdata_updnew' or mergeinfo_list[1] == 'BSCCombinedAssnDec' or mergeinfo_list[1] == 'aiashortdecl' or mergeinfo_list[1] == 'assignment2016' or mergeinfo_list[1] == 'appdataupdate' or mergeinfo_list[1] == 'recordation' or mergeinfo_list[1] == 'missingpartsNw' or mergeinfo_list[1] == 'generalxmitCF':
        t_comb = time.time()
        print(f"[mergeDoc] applicationdata_updnew: calling combinedoc for {mergeinfo_list[1]} matter={matter}")
        combinedoc(input_path, mergeinfo_list[1], mergefninfo, matter, contacts)
        print(f"[mergeDoc] applicationdata_updnew: combinedoc done {time.time()-t_comb:.2f}s")
        input_path = os.path.join(settings.BASE_DIR, 'documents', 'multidocmerge', mergeinfo_list[1] + '.docx')
        doc = Document(input_path)

    # doc merges
    if contacts == "FALSE":
        if mergeinfo_list[1] == 'applicationdata_updnew':
            t_wm = time.time()
            print(f"[mergeDoc] applicationdata_updnew: calling WordMerger on combined doc")
        WordMerger(input_path, replace, output_path)
        if mergeinfo_list[1] == 'applicationdata_updnew':
            print(f"[mergeDoc] applicationdata_updnew: WordMerger done {time.time()-t_wm:.2f}s")

        # Statement373c: checkboxes based on recordation and reel/frame
        if mergeinfo_list[1] == 'Statement373c':
            # Box 10: when "There is a recordation occurring..." is selected
            if mergefninfo and mergefninfo[0] in ('true', True):
                check_checkbox_at_position_xmlsafe(output_path, 10, checked=True)
            # Box 7: exactly one reel/frame pair; Box 8: more than one reel/frame pair
            reel_frame_count = merge_fn.statement373c_reel_frame_count(matter)
            print(reel_frame_count)
            if reel_frame_count == 1:
                check_checkbox_at_position_xmlsafe(output_path, 7, checked=True)
            elif reel_frame_count > 1:
                check_checkbox_at_position_xmlsafe(output_path, 8, checked=True)

        # PTOAIA82: check one of boxes 6–9 per radio selection (Inventor=6, Legal Rep=7, Assignee=8, Proprietary Interest=9)
        if mergeinfo_list[1] == 'PTOAIA82' and len(mergefninfo) > 1:
            rad = (mergefninfo[1] or '').strip()
            if rad == '1':
                check_checkbox_at_position_xmlsafe(output_path, 6, checked=True)
            elif rad == '2':
                check_checkbox_at_position_xmlsafe(output_path, 7, checked=True)
            elif rad == '3':
                check_checkbox_at_position_xmlsafe(output_path, 8, checked=True)
            elif rad == '4':
                check_checkbox_at_position_xmlsafe(output_path, 9, checked=True)

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

            ownTO = merge_fn.SAEmailFill(mergefninfo[2])
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
                (doc_type == 'missingpartsNw' and (
                    mergefninfo[1] != '' or
                    (len(mergefninfo) > 10 and mergefninfo[10] and str(mergefninfo[10]).strip())
                )) or
                (doc_type == 'generalxmitCF' and generalxmit_has_ext) or
                (doc_type == 'applicationdata_updnew' and applicationdata_updnew_corrapplicant)
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

                    data2 = None
                    file_name2 = None
                    data3 = None
                    file_name3 = None

                    if mergefninfo[1] != '':
                        extime = mergeinfo.replace('missingpartsxmit', 'exttimeCF')
                        extime = extime.replace('missingpartsNw', 'exttimeCF')
                        extime = extime.replace('communications', 'transmittal')
                        extime = extime.split(',')
                        extime = ','.join(extime[:3] + [mergefninfo[1]] + extime[19:])
                        data2, file_name2 = mergemultidoc(matter, extime)

                    commfr_has_value = len(mergefninfo) > 10 and mergefninfo[10] and str(mergefninfo[10]).strip()
                    if commfr_has_value:
                        ebdfee_str = 'communications/EBDfee.docx,EBDfeeCF,FALSE,' + ','.join(mergefninfo)
                        data3, file_name3 = mergemultidoc(matter, ebdfee_str)

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

                if mergeinfo_list[1] == 'generalxmitCF' and generalxmit_has_ext:
                    # Second document must use the extension-of-time Word template and exttimeCF merge only
                    # (same transmittal catalog as corrappln/missingpartsNw after communications→transmittal).
                    # Replacing only the method name leaves the general transmittal .docx in field [0]; build path explicitly.
                    parts = mergeinfo.split(',')
                    orig_path = parts[0]
                    if '/' in orig_path:
                        folder, _base = orig_path.rsplit('/', 1)
                    else:
                        folder = 'transmittal'
                    folder = folder.replace('communications', 'transmittal')
                    ext_template_path = f'{folder}/exttimeCF.docx'

                    contacts_flag = (parts[2] if len(parts) > 2 else '') or ''
                    email_offset = 3 if contacts_flag == 'TRUE' else 0
                    tail = parts[3 + email_offset :]
                    core_for_ext, _gx_docseg = _generalxmit_split_enddoc_docs(tail)
                    ext_fields = (
                        core_for_ext[32:42] if len(core_for_ext) >= 32 else []
                    )
                    while len(ext_fields) < 10:
                        ext_fields.append('')
                    if contacts_flag == 'TRUE' and len(parts) > 5:
                        header = [ext_template_path, 'exttimeCF', parts[2], parts[3], parts[4], parts[5]]
                    else:
                        header = [ext_template_path, 'exttimeCF', parts[2]]
                    extime = ','.join(header + ext_fields)
                    data2, file_name2 = mergemultidoc(matter, extime)

                if mergeinfo_list[1] == 'applicationdata_updnew' and applicationdata_updnew_corrapplicant:
                    esign_val = mergefninfo[7] if len(mergefninfo) > 7 else 'true'
                    corrapplicant_merge = ','.join(
                        ['ptoforms/corrapplicant.docx', 'corrapplicant', 'FALSE', str(esign_val)]
                    )
                    data2, file_name2 = mergemultidoc(matter, corrapplicant_merge)

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    zip_file.writestr(file_name, data)
                    if mergeinfo_list[1] == 'missingpartsNw':
                        if data2 is not None and file_name2 is not None:
                            zip_file.writestr(file_name2, data2)
                        if data3 is not None and file_name3 is not None:
                            zip_file.writestr(file_name3, data3)
                    else:
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

# Namespaces used by WordprocessingML
NS = {
    'w':   'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'mc':  'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'r':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

def _first_text_run(elem):
    """Return (node, inner_text) for the first <w:t> inside elem, else (None, None)."""
    for t in elem.findall('.//w:t', namespaces=NS):
        return t, (t.text or '')
    return None, None

def _first_symbol_run(elem):
    """Return the first <w:sym> element inside elem, else None."""
    for s in elem.findall('.//w:sym', namespaces=NS):
        return s
    return None

def _first_run_and_rpr(elem):
    """
    Return (first_run, first_rPr_clone_or_None) under elem.
    We clone rPr so we can reuse style when inserting new content.
    """
    r = elem.find('.//w:r', namespaces=NS)
    if r is None:
        return None, None
    rpr = r.find('w:rPr', namespaces=NS)
    return r, deepcopy(rpr) if rpr is not None else None

def _ensure_r_with_text(parent, text_char, rpr=None):
    """Create a <w:r>[<w:rPr>]<w:t>char</w:t></w:r> and append to parent."""
    r = lxml_etree.SubElement(parent, f"{{{NS['w']}}}r")
    if rpr is not None:
        r.append(rpr)
    t = lxml_etree.SubElement(r, f"{{{NS['w']}}}t")
    t.text = text_char
    # Preserve spacing per Word best practice
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return r

def _ensure_p_with_r_and_text(parent, text_char, rpr=None):
    """Create <w:p><w:r>[<w:rPr>]<w:t>char</w:t></w:r></w:p> and append to parent."""
    p = lxml_etree.SubElement(parent, f"{{{NS['w']}}}p")
    _ensure_r_with_text(p, text_char, rpr=rpr)
    return p

def check_checkbox_at_position_xmlsafe(docx_path, position, checked=True):
    """
    Toggle the content-control checkbox at 1-based 'position' in a DOCX (in place):
      1) Sets <w14:checked w14:val="1|0">
      2) Updates the visible glyph in <w:sdtContent> to match checkedState/uncheckedState.

    Run/block-aware insertion avoids Word's 'unreadable content' repair.
    """

    if not os.path.isfile(docx_path):
        print("ERROR: input file not found.")
        return

    # 1) Read original DOCX contents
    with zipfile.ZipFile(docx_path, 'r') as zin:
        entries = {zi.filename: zin.read(zi.filename) for zi in zin.infolist()}

    if 'word/document.xml' not in entries:
        print("ERROR: word/document.xml not found in the DOCX.")
        return

    # 2) Parse document.xml with lxml (preserves namespace prefixes on serialize)
    try:
        parser = lxml_etree.XMLParser(recover=True, remove_blank_text=False)
        root = lxml_etree.fromstring(entries['word/document.xml'], parser=parser)
    except lxml_etree.XMLSyntaxError as e:
        print("ERROR: document.xml is not valid XML (may have been previously corrupted).")
        print("Details:", e)
        return

    # 3) Gather all <w:sdt> that have a <w14:checkbox> in <w:sdtPr>
    sdts = []
    for sdt in root.findall('.//w:sdt', namespaces=NS):
        sdtPr = sdt.find('w:sdtPr', namespaces=NS)
        if sdtPr is None:
            continue
        checkbox = sdtPr.find('w14:checkbox', namespaces=NS)
        if checkbox is not None:
            sdts.append((sdt, sdtPr, checkbox))

    if not sdts:
        print("No checkbox content controls found. These may be glyph-only boxes; different approach needed.")
        return

    # Resolve index
    idx = len(sdts) - 1 if position == -1 else max(0, min(position - 1, len(sdts) - 1))

    sdt, sdtPr, checkbox = sdts[idx]

    # 4) Determine state codepoints (hex or decimal accepted) and font
    cs = checkbox.find('w14:checkedState', namespaces=NS)
    ucs = checkbox.find('w14:uncheckedState', namespaces=NS)
    cs_val = cs.get(f"{{{NS['w14']}}}val") if cs is not None else '2611'    # ☑ default
    ucs_val = ucs.get(f"{{{NS['w14']}}}val") if ucs is not None else '2610'  # ☐ default
    # Prefer font declared on state (e.g., "MS Gothic") if present
    state_font = (cs.get(f"{{{NS['w14']}}}font") if cs is not None and cs.get(f"{{{NS['w14']}}}font")
                  else (ucs.get(f"{{{NS['w14']}}}font") if ucs is not None and ucs.get(f"{{{NS['w14']}}}font") else None))

    def _code_to_char(code_str):
        try:
            return chr(int(code_str, 16))
        except Exception:
            try:
                return chr(int(code_str, 10))
            except Exception:
                return '☑'

    checked_char   = _code_to_char(cs_val)
    unchecked_char = _code_to_char(ucs_val)
    desired_char   = checked_char if checked else unchecked_char

    # 5) Set <w14:checked w14:val="1|0">
    chk = checkbox.find('w14:checked', namespaces=NS)
    val = '1' if checked else '0'
    if chk is None:
        chk = lxml_etree.SubElement(checkbox, f"{{{NS['w14']}}}checked")
    chk.set(f"{{{NS['w14']}}}val", val)

    # 6) Update visible glyph inside <w:sdtContent> (run/block aware)
    sdtContent = sdt.find('w:sdtContent', namespaces=NS)
    if sdtContent is None:
        print("WARNING: <w:sdtContent> not found; cannot update visible glyph.")
    else:
        # Prefer updating an existing text or symbol
        t_node, _ = _first_text_run(sdtContent)
        if t_node is not None:
            t_node.text = desired_char
            t_node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        else:
            sym = _first_symbol_run(sdtContent)
            if sym is not None:
                sym.set(f"{{{NS['w']}}}char", f"{ord(desired_char):04X}")
            else:
                # Prepare rPr: clone an existing run's rPr or synthesize from state font (if given)
                _, first_rpr = _first_run_and_rpr(sdtContent)
                if first_rpr is None and state_font:
                    first_rpr = lxml_etree.Element(f"{{{NS['w']}}}rPr")
                    rfonts = lxml_etree.SubElement(first_rpr, f"{{{NS['w']}}}rFonts")
                    rfonts.set(f"{{{NS['w']}}}ascii", state_font)
                    rfonts.set(f"{{{NS['w']}}}hAnsi", state_font)

                # Detect content level: block vs run
                has_block = sdtContent.find('w:p', namespaces=NS) is not None or sdtContent.find('w:tbl', namespaces=NS) is not None
                has_run   = sdtContent.find('w:r', namespaces=NS) is not None

                if has_run and not has_block:
                    # RUN-LEVEL SDT: insert a <w:r> directly (valid)
                    _ensure_r_with_text(sdtContent, desired_char, rpr=first_rpr)
                else:
                    # BLOCK-LEVEL SDT (or empty): insert a proper paragraph
                    _ensure_p_with_r_and_text(sdtContent, desired_char, rpr=first_rpr)

    # 7) Serialize with lxml (preserves namespace prefixes - avoids Word "unreadable content")
    new_xml = lxml_etree.tostring(
        root, encoding='utf-8', xml_declaration=True,
        method='xml', standalone=None, pretty_print=False
    )
    entries['word/document.xml'] = new_xml

    # Important: ensure the read zip is closed before writing (it is, due to context manager)
    with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as zout:
        for name, data in entries.items():
            zout.writestr(name, data)

def generalxmit_extension_fee(request):
    """
    Return statutory extension fee for generalxmitCF from merge_fees (same rules as merges.generalxmitCF).
    POST: matterno (JSON-stringified matter #), months (1-5).
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    raw = request.POST.get('matterno')
    if raw is None:
        return JsonResponse({'error': 'matterno required'}, status=400)
    matter = raw.replace('"', '').strip()
    months_raw = (request.POST.get('months') or '').strip()
    if not matter:
        return JsonResponse({'fee': '', 'ok': False, 'message': 'No matter number'})
    if not months_raw:
        return JsonResponse({'fee': '', 'ok': True})
    try:
        m = int(months_raw)
    except ValueError:
        return JsonResponse({'error': 'invalid months'}, status=400)
    if m < 1 or m > 5:
        return JsonResponse({'fee': '', 'ok': True})

    merge_fn = mergefunctions()
    try:
        matter_data = merge_fn.matterFill(matter)
    except Exception:
        return JsonResponse({'fee': '', 'ok': False, 'message': 'Matter not found'})

    desc = (matter_data.mattertypedescription or '')
    is_provisional = 'PROV' in desc.upper()
    nonprov_ext_rule = {1: 28, 2: 31, 3: 34, 4: 37, 5: 40}
    prov_ext_rule = {1: 55, 2: 57, 3: 59, 4: 61, 5: 63}
    ext_rule_map = prov_ext_rule if is_provisional else nonprov_ext_rule
    rid = ext_rule_map.get(m)
    if not rid:
        return JsonResponse({'fee': '', 'ok': True})

    amt = merge_fn.merge_fee_amount(rid, matter)
    if amt is None:
        return JsonResponse({'fee': '', 'ok': False, 'message': 'Fee lookup failed'})
    return JsonResponse({'fee': f'{amt:.2f}', 'ok': True})

def _generalxmit_split_enddoc_docs(mergefninfo):
    """
    Additional Documents appends 'ENDDOC' and doc/page pairs. That often runs *before* Continue on
    the transmittal modal, so the payload is ...doc1,pg1,...,ENDDOC,cert,duedate,...
    Split into (core_fields_for_generalxmit, flat_doc_pairs_before_or_after_marker).
    """
    mi = list(mergefninfo)
    try:
        di = mi.index('ENDDOC')
    except ValueError:
        return mi, []
    before = mi[:di]
    after = mi[di + 1 :]

    def _gx_core_start(seg):
        return bool(seg) and str(seg[0]).strip().lower() in ('true', 'false')

    if _gx_core_start(after):
        return after, before
    if _gx_core_start(before):
        return before, after
    return mi, []
