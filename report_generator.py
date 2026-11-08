"""Offline PDF invoice export for DineFlow."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import database as db

def generate_invoice(bill_id):
    bill=next((b for b in db.bills() if b['id']==bill_id),None)
    if not bill: raise ValueError('Bill not found.')
    out=Path(__file__).parent/'generated_invoices';out.mkdir(exist_ok=True);path=out/f"DineFlow_{bill['bill_no']}.pdf"
    styles=getSampleStyleSheet();title=styles['Title'];title.textColor=colors.HexColor('#A87909')
    story=[Paragraph('DineFlow',title),Paragraph('SMART RESTAURANT OPERATIONS',styles['Heading3']),Spacer(1,12),Paragraph(f"<b>Invoice:</b> {bill['bill_no']}<br/><b>Table:</b> {bill['label']}<br/><b>Guest:</b> {bill['customer_name'] or 'Guest'}<br/><b>Status:</b> {bill['status']}",styles['BodyText']),Spacer(1,12)]
    data=[['Item','Qty','Unit price','Amount']]
    for i in db.bill_items(bill_id): data.append([i['item_name'],str(i['quantity']),db.money(i['unit_price_paise']),db.money(i['quantity']*i['unit_price_paise'])])
    data += [['','','Subtotal',db.money(bill['subtotal_paise'])],['','','GST (5%)',db.money(bill['tax_paise'])],['','','TOTAL',db.money(bill['total_paise'])]]
    t=Table(data,colWidths=[2.6*inch,.6*inch,1.4*inch,1.4*inch]);t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1C1C1C')),('TEXTCOLOR',(0,0),(-1,0),colors.HexColor('#FFFFFF')),('BACKGROUND',(0,-1),(-1,-1),colors.HexColor('#F5D47A')),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#CCCCCC')),('ALIGN',(1,0),(-1,-1),'RIGHT'),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold'),('PADDING',(0,0),(-1,-1),7)]));story += [t,Spacer(1,18),Paragraph('Thank you for dining with DineFlow.',styles['BodyText'])]
    SimpleDocTemplate(str(path),pagesize=A4,rightMargin=38,leftMargin=38,topMargin=38,bottomMargin=38).build(story);return path
