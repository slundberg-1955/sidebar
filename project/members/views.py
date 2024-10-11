from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.template import loader
import ast
import importlib
from docxcompose.composer import Composer
from docx import Document as Document_compose

from .models import Matter
from .models import Rvwmatterinventors
from .models import MergeCategory
from .models import MergeRole
from .models import MergeDef
from .models import Orgprofile, Matterparticipant, Rvwmatterpersonnel, Contactinfo, Personprofile, Activity, Relatedmatter
from docx import Document
from typing import Any, List
import re
import win32com.client as win32
from datetime import datetime
import os
import pythoncom
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from lxml import etree
from .mergemethods.mergefunctions import mergefunctions

from python_docx_replace.paragraph import Paragraph

def members(request):
    if request.method == 'POST':
        matter = request.POST['matterInput']
        mergeinfo = request.POST['merge_info']

        mergeDoc(matter, mergeinfo)

    mergedict = MergeDef.objects.using('SideBar').all()
    roles = MergeRole.objects.using('SideBar').all()
    categories = MergeCategory.objects.using('SideBar').all()

    return render(request, 'merge.html', {'mergedict': mergedict, 'roles': roles, 'categories': categories})

def matters(request):
    return render(request, 'matters.html')

def fip_reports(request):
    return render(request, 'fip_reports.html')

def merges(request):
    return render(request, 'merges.html')

def toolbox(request):
    return render(request, 'toolbox.html')

def transform_serialnumber(s):
    part1 = s[:2]
    part2 = s[2:]
    part2 = part2[:-3] + ',' + part2[-3:]

    result = part1 + '/' + part2
    return result

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
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        relatedmatters = Relatedmatter.objects.using('FIP').filter(primarymatterid = matter.matterid, relationdesc = 'Priority')
        serialnos = transform_serialnumber(matter.serialnumber) + '*'
        dates = matter.fileddate.strftime("%B %d, %Y") + '*'
        countries = matter.country + '*'

        for relatedmatter in relatedmatters:
            relmatter = Matter.objects.using('FIP').get(matterid = relatedmatter.relatedmatterid)
            serialnos = serialnos + transform_serialnumber(relmatter.serialnumber) + '*'
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
    if request.method == 'POST':
        data = request.POST.get('matterno')
        data = data.replace('"', "")
        matter = Matter.objects.using('FIP').get(hostmatterno = data)
        relatedmatters = Relatedmatter.objects.using('FIP').filter(primarymatterid = matter.matterid)
        serialnos = transform_serialnumber(matter.serialnumber) + '*'
        hostmatters = matter.hostmatterno
        relationships = ''

        for relatedmatter in relatedmatters:
            relmatter = Matter.objects.using('FIP').get(matterid = relatedmatter.relatedmatterid)
            hostmatters = relmatter.hostmatterno
            try:
                serialnos = serialnos + transform_serialnumber(relmatter.serialnumber) + '*'
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
    pythoncom.CoInitialize()  
    outlook = win32.Dispatch('outlook.application')
    mail = outlook.CreateItem(0)
    mail.Subject = subject
    mail.Body = body
    mail.To = recipients
    if(attachment != ''):
        mail.Attachments.Add(attachment)

    if cc:
        mail.CC = cc
    if bcc:
        mail.BCC = bcc

    mail.Display(True)

def testview(request):
    return render(request, 'dbtest.html')

def find_checkbox_coordinates(element_coordinates):
    checkbox_coordinates = {}
    for element_name, (row, column) in element_coordinates.items():
        if "CheckBox" in element_name:
            checkbox_coordinates[element_name] = (row, column)
    return checkbox_coordinates

def combinedoc(path, method, mergeinfo, matter):
    doc1 = Document_compose(path)
    doc1.add_page_break()

    if method == 'issuefee':
        composer = Composer(doc1)
        doc2 = Document_compose("C:/Users/jaburns/SideBar/project/documents/communications/issuefeexmit3.docx")
        if mergeinfo[6] == 'true':
            doc3 = Document_compose("C:/Users/jaburns/SideBar/project/documents/communications/issuefeexmit2.docx") 
            doc3.add_page_break()
            composer.append(doc3)
            composer.append(doc2) 
        else:  
            composer.append(doc2)

    if method == 'applicationdata_new2' or method == 'applicationdata_updnew':
        doc2 = Document_compose("C:/Users/jaburns/SideBar/project/documents/formaldocuments/ApplicationDataSheet_NEW2inventor.docx") 
        docend = Document_compose("C:/Users/jaburns/SideBar/project/documents/formaldocuments/ApplicationDataSheet_NEW2end.docx") 
        composer = Composer(doc2)

        merge_fn = mergefunctions()
        matter_data = merge_fn.matterFill(matter)
        inventors = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34608')
        applicants = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '56691')
        assignees = Matterparticipant.objects.using('FIP').filter(matterid = matter_data.matterid, roleid = '34606')
        invCount = len(inventors) + 1
        appCount = len(applicants) + 1
        assignCount = len(assignees) + 1

        for i in range(1, invCount):
            replace = {}
            replace.update(merge_fn.inventorInfo(matter, i))
            WordMerger('C:/Users/jaburns/SideBar/project/documents/formaldocuments/ApplicationDataSheet_NEW2inventorMultiple.docx', replace, 'C:/Users/jaburns/SideBar/project/documents/temp/ApplicationDataSheet_NEW2inventorMultipleout.docx')
            doc3 = Document_compose("C:/Users/jaburns/SideBar/project/documents/temp/ApplicationDataSheet_NEW2inventorMultipleout.docx") 
            composer.append(doc3)
        
        composer.append(doc1)
        
        for i in range(1, appCount):
            replace = {}
            replace.update(merge_fn.applicantfill(matter, i))
            WordMerger('C:/Users/jaburns/SideBar/project/documents/formaldocuments/ApplicationDataSheet_NEW2applicantMulti.docx', replace, 'C:/Users/jaburns/SideBar/project/documents/temp/ApplicationDataSheet_NEW2applicantMultipleout.docx')
            doc4 = Document_compose("C:/Users/jaburns/SideBar/project/documents/temp/ApplicationDataSheet_NEW2applicantMultipleout.docx") 
            composer.append(doc4)

        for i in range(1, assignCount):
            replace = {}
            replace.update(merge_fn.assigneefill(matter, i))
            WordMerger('C:/Users/jaburns/SideBar/project/documents/formaldocuments/ApplicationDataSheet_NEW2assigneeMulti.docx', replace, 'C:/Users/jaburns/SideBar/project/documents/temp/ApplicationDataSheet_NEW2assigneeMultipleout.docx')
            doc5 = Document_compose("C:/Users/jaburns/SideBar/project/documents/temp/ApplicationDataSheet_NEW2assigneeMultipleout.docx") 
            composer.append(doc5)
        
        composer.append(docend)
    
    if method == 'invchange':
        merge_fn = mergefunctions()
        doc2 = Document_compose("C:/Users/jaburns/SideBar/project/documents/communications/inventorchange.docx") 
        docend = Document_compose("C:/Users/jaburns/SideBar/project/documents/communications/inventorchange_end.docx") 
        composer = Composer(doc2)
        invlist = mergeinfo[2:]
        invlist = invlist[:-1]
        for inv in invlist:
            replace = {}
            replace.update(merge_fn.inventorInfoName(matter, inv))
            WordMerger('C:/Users/jaburns/SideBar/project/documents/communications/inventorchange_multi.docx', replace, 'C:/Users/jaburns/SideBar/project/documents/temp/inventorchangeMultipleout.docx')
            doc3 = Document_compose("C:/Users/jaburns/SideBar/project/documents/temp/inventorchangeMultipleout.docx") 
            composer.append(doc3)
        
        composer.append(docend)
        
    method_paths = {
        'olpemail': "C:/Users/jaburns/SideBar/project/documents/reportletters/OLPemail.docx",
        'rptissuefee': "C:/Users/jaburns/SideBar/project/documents/reportletters/IssueFee.docx",
        'filerectreportNw2': "C:/Users/jaburns/SideBar/project/documents/reportletters/filingreceipt.docx",
        'PCTRptFileOfApp': "C:/Users/jaburns/SideBar/project/documents/reportletters/PCTRptApplicationFiled.docx",
        'basicreport': "C:/Users/jaburns/SideBar/project/documents/reportletters/basicreportout.docx",
        'prvAppReport': "C:/Users/jaburns/SideBar/project/documents/reportletters/prvappfiled_new.docx",
        'recordedassnreport': "C:/Users/jaburns/SideBar/project/documents/reportletters/recordedassignment.docx",
        'issuereport': "C:/Users/jaburns/SideBar/project/documents/reportletters/issuenotify.docx",
        'nonfinalreportFp': "C:/Users/jaburns/SideBar/project/documents/reportletters/NonFinalOaFp.docx",
        'ptorecdReport': "C:/Users/jaburns/SideBar/project/documents/reportletters/PTO_Received.docx",
        'RepNoticeofAllow': "C:/Users/jaburns/SideBar/project/documents/reportletters/noticeofallowanceUpdate.docx",
        'adobesign': "C:/Users/jaburns/SideBar/project/documents/letters/AdobeSignEmail.docx",
        'appReportFp': "C:/Users/jaburns/SideBar/project/documents/reportletters/appfiledFp.docx",
        'advisoryreport': "C:/Users/jaburns/SideBar/project/documents/reportletters/advisoryaction.docx",
        'cocReportEmail': "C:/Users/jaburns/SideBar/project/documents/reportletters/CocEmail.docx",
        'reportprvassnnew': "C:/Users/jaburns/SideBar/project/documents/letters/ProvisionalAssignmentNoLabel.docx",
        'LtrSendFmlDocNew': "C:/Users/jaburns/SideBar/project/documents/letters/LtrSendFmlDocNew.docx",
        'PCTAsgnPOALetter': "C:/Users/jaburns/SideBar/project/documents/letters/PCTAsgnPOALetter.docx",
        'correctdefects': "C:/Users/jaburns/SideBar/project/documents/reportletters/PCTcorrectDefects.docx"
    }

    if method in method_paths:
        merge_fn = mergefunctions()
        doc2 = Document_compose(method_paths[method])
        composer = Composer(doc2)
        replace = {}
        replace.update(merge_fn.cmgfill(matter))
        WordMerger('C:/Users/jaburns/SideBar/project/documents/reportletters/signoff.docx', replace, 'C:/Users/jaburns/SideBar/project/documents/temp/emailout.docx')
        doc3 = Document_compose("C:/Users/jaburns/SideBar/project/documents/temp/emailout.docx")
        composer.append(doc3)
        
    composer.save("documents/multidocmerge/" + method +".docx")

# New separate function for merging documents
def mergeDoc(matter , mergeinfo):
    mergeinfo_list = mergeinfo.split(",") 
    module_name = ".mergemethods.merges"
    class_name = mergeinfo_list[1]
    module = importlib.import_module(module_name, package='members')
    curMerge = getattr(module, class_name)
    merge_instance = curMerge()

    input_path = "C:/Users/jaburns/SideBar/project/documents/" + mergeinfo_list[0]
    output_path = 'C:/Users/jaburns/SideBar/project/documents/Merged/Document.docx'

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

    if mergeinfo_list[1] == 'pctcorrect':
        if mergefninfo[5] == 'true':
            pctext = mergeinfo.replace('pctcorrectdefects', 'PCTExtention')
            pctext = pctext.replace('pctcorrect', 'pctextention')
            mergeDoc(matter, pctext)

    if mergeinfo_list[1] == 'corrappln':
        if mergefninfo[1] != '' and int(mergefninfo[1]) > 0:
            extime = mergeinfo.replace('corrappln', 'exttimeCF')
            extime = extime.replace('communications', 'transmittal')
            mergeDoc(matter, extime)

    replace = getattr(merge_instance, class_name)(matter, mergefninfo, keys)

    merge_strings = ['applicationdata_new2', 'applicationdata_updnew', 'invchange', 'olpemail', 'rptissuefee', 'filerectreportNw2', 'PCTRptFileOfApp', 'basicreport', 'prvAppReport', 'recordedassnreport', 'issuereport', 'nonfinalreportFp', 'ptorecdReport', 'RepNoticeofAllow', 'adobesign', 'appReportFp', 'advisoryreport', 'cocReportEmail', 'reportprvassnnew', 'LtrSendFmlDocNew', 'PCTAsgnPOALetter', 'correctdefects']

    # combine doc
    if mergeinfo_list[1] in merge_strings:
        combinedoc(input_path, mergeinfo_list[1], mergefninfo, matter)
        input_path = f"C:/Users/jaburns/SideBar/project/documents/multidocmerge/{mergeinfo_list[1]}.docx"
        doc = Document(input_path)

    # with multiple docs
    if mergeinfo_list[1] == 'issuefee':
        combinedoc(input_path, mergeinfo_list[1], mergefninfo, matter)
        input_path = "C:/Users/jaburns/SideBar/project/documents/multidocmerge/" + mergeinfo_list[1] + ".docx"
        doc = Document(input_path)
        isssubject = matter + ', Action Requested:  Review and signature of Issue Fee Transmittal'
        issbody = "SIGNING ATTORNEY CHECKLIST FOR ISSUE FEE PAYMENT FILING \n\nIssue Fee due: " + replace.get('dueDate') + "\n\nAction Requested: Review and Signature of Issue Fee Transmittal Documents\n\nInstructions to Signing Attorney: Prior to signature of this document, please consider the attached Attorney Checklist."
        issTO = ''
        issCC = ''
        issBCC = ''
        attachment = 'C:/Users/jaburns/SideBar/project/documents/attachments/Notice of Allowance Review and Response.pdf'
        Email(issbody, isssubject, issTO, issCC, issBCC , attachment)

        if mergefninfo[5] == 'true':
            stateofallow = mergeinfo.replace('issuefeexmit', 'stateofallowcomments')
            stateofallow = stateofallow.replace('issuefee', 'stateofallow')
            mergeDoc(matter, stateofallow)
            
    doccount = 0
    success = False

    while not success:
        try:
            WordMerger(input_path, replace, output_path)
            success = True
        except:
            doccount += 1
            output_path = output_path.replace('Document.docx', f'Document{doccount}.docx')
            continue

    # doc merges
    if contacts == "FALSE":
        os.startfile(output_path)

    # outlook merges
    if contacts == "TRUE":
        if check_email(mergeinfo_list[3]):
            TO = mergeinfo_list[3]
        else:
            TO = ' '

        if check_email(mergeinfo_list[4]):
            CC = mergeinfo_list[4]
        else:
            CC = ' '

        if check_email(mergeinfo_list[5]):
            BCC = mergeinfo_list[5]
        else:
            BCC = ' '

        subject, body = DocumentReader(output_path, mergeinfo_list[1])
        # attachment = "Q:/Contract Developers/SideBar/Merges/Django/SideBar/project/documents/communications/AppealFwdFee.docx"
        Email(body, subject, TO, CC, BCC, '')

def check_email(email):
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

    if re.fullmatch(pattern, email):
        return True
    else:
        return False
