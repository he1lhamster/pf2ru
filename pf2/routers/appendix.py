import os

import aiosmtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any
from fastapi import APIRouter, Request, Depends, Form
from config import settings

from templatetags import NewTemplateResponse

router = APIRouter(
    prefix="",
    tags=["appendix", ],
)


@router.get("/licenses")
async def licenses(request: Request, ):
    return await NewTemplateResponse('licenses.html', {"request": request, })


@router.get("/appendix")
async def appendix(request: Request, ):
    return await NewTemplateResponse('appendix.html', {"request": request})


@router.get("/feedback")
async def feedback(request: Request, ):
    return await NewTemplateResponse('feedback.html', {"request": request, })


@router.get("/about")
async def get_about(request: Request, ):
    return await NewTemplateResponse('about.html', {"request": request, })


@router.post("/send-feedback")
async def send_feedback(theme: str = Form(...),
                        category: str = Form(...),
                        email: str = Form(...),
                        text_message: str = Form(...)):
    message = MIMEMultipart()
    message['Subject'] = theme
    message['From'] = formataddr(('Animal Messenger', settings.EMAIL_USER))
    message['To'] = 'v@pf2.ru'
    message['Reply-To'] = email
    message.attach(MIMEText(category + '\n' + text_message))

    try:
        await aiosmtplib.send(
            message,
            hostname=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            start_tls=True,
            username=settings.EMAIL_USER,
            password=settings.EMAIL_PASSWORD,
        )
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# REDO - mb class singletone for media management
media_manager = {
    'CharacterSheetEng-BW.pdf': ('Character Sheet ENG (BW)', 'Лист Персонажа ENG (ЧБ)'),
    'CharacterSheetRus.pdf': ('Character Sheet RUS', 'Лист Персонажа RUS'),
    'CharacterSheetEng.pdf': ('Character Sheet ENG ', 'Лист Персонажа ENG'),
    'CharacterSheetRus-BW.pdf': ('Character Sheet RUS (BW)', 'Лист Персонажа RUS (ЧБ)'),

    'actions1.3 - center.pdf': ('Actions Sheet Helper v1.3', 'Лист действий и занятий v1.3'),
    'actions1.3 - binder.pdf': (
        'Actions Sheet Helper v1.3 (binder orientation)', 'Лист действий и занятий v1.3 (для биндера)'),
}


@router.get("/files")
async def files(request: Request, ):
    lang = request.state.lang

    pc_sheets_path = os.listdir('media/pc_sheets')
    pc_sheets = []
    for file in pc_sheets_path:
        if file not in media_manager or not os.path.isfile(os.path.join('media/pc_sheets', file)):
            continue
        filename = media_manager[file][1] if lang == 'ru' else media_manager[file][0]
        pc_sheets.append({"filename": filename, "url": f"/media/pc_sheets/{file}"})

    actions_sheets_path = os.listdir('media/actions_sheets')
    actions_sheets = []
    for file in actions_sheets_path:
        if file not in media_manager or not os.path.isfile(os.path.join('media/actions_sheets', file)):
            continue
        filename = media_manager[file][1] if lang == 'ru' else media_manager[file][0]
        actions_sheets.append({"filename": filename, "url": f"/media/actions_sheets/{file}"})

    return await NewTemplateResponse('files.html', {"request": request,
                                                    "pc_sheets": pc_sheets,
                                                    "actions_sheets": actions_sheets,
                                                    }
                                     )


@router.get("/compendium")
async def get_compendium(request: Request, tab: str = None):
    from compendium import compendium
    return await NewTemplateResponse('compendium.html', {"request": request,
                                                         "c": compendium,
                                                         }
                                     )
