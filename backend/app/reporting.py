"""One authorised population for search, report rows, CSV and printable output."""
from collections import Counter, defaultdict
from datetime import date, datetime, time, timezone
import csv
import html
import io
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
from fastapi import Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from pydantic import Field
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session
from .auth import Principal, get_db, principal, utc
from .coordination import pair_authorized, suggestion_view
from .models import CaseAction, CaseRecord, Institution, RelationshipDecision, RelationshipSuggestion, Resolution, Transfer, User
from .policies import can_read, grants, visible_cases
from .schemas import StrictInput
from .scheduling import context_now

INDIA=ZoneInfo('Asia/Kolkata')


class Filters(StrictInput):
    q:str=Field(default='',max_length=200)
    bureau:str=Field(default='all',max_length=50)
    institution:str=Field(default='all',max_length=50)
    region:str=Field(default='all',max_length=50)
    category:str=Field(default='all',max_length=80)
    lifecycle:str=Field(default='all',max_length=40)
    received_from:date|None=None
    received_to:date|None=None


def boundary(value):
    return datetime.combine(value,time(),INDIA).astimezone(timezone.utc)


def case_query(actor,filters,include_received=True):
    f=filters
    if f.received_from and f.received_to and f.received_from>=f.received_to:raise HTTPException(422,'Received end date must be after start; the end boundary is exclusive.')
    query=select(CaseRecord).join(Institution,Institution.id==CaseRecord.institution_id).where(visible_cases(actor))
    for column,value in [(CaseRecord.current_bureau_id,f.bureau),(CaseRecord.institution_id,f.institution),
                         (Institution.region_id,f.region),(CaseRecord.lifecycle,f.lifecycle)]:
        if value!='all':query=query.where(column==value)
    narrative=or_(CaseRecord.current_owner_id==actor.user.id,CaseRecord.id.in_(grants(actor,'N')))
    if f.category!='all':query=query.where(narrative,CaseRecord.category==f.category)
    if include_received:
        if f.received_from:query=query.where(CaseRecord.received_at>=boundary(f.received_from))
        if f.received_to:query=query.where(CaseRecord.received_at<boundary(f.received_to))
    if f.q:
        term='%'+f.q.replace('%','\\%').replace('_','\\_')+'%'
        query=query.where(or_(*[c.ilike(term,escape='\\') for c in [CaseRecord.public_id,CaseRecord.institution_id,Institution.name,Institution.city]],
            and_(narrative,or_(CaseRecord.subject.ilike(term,escape='\\'),CaseRecord.description.ilike(term,escape='\\')))))
    return query


def in_window(at,f):
    return (not f.received_from or utc(at)>=boundary(f.received_from)) and (not f.received_to or utc(at)<boundary(f.received_to))


def build_report(db,actor,filters):
    instant=context_now(db)
    base=list(db.scalars(case_query(actor,filters,False)))
    population=list(db.scalars(case_query(actor,filters)))
    ids={c.id for c in population};base_ids={c.id for c in base}
    rows=[];dimensions={key:Counter() for key in ['bureau','region','institution','status']};ageing=Counter({'0–7 days':0,'8–30 days':0,'31+ days':0})
    pending=disposed=under_review=overdue=missing_due=0
    for c in population:
        institution=db.get(Institution,c.institution_id);narrative=can_read(db,actor,c,'N')
        active=c.lifecycle!='DISPOSED';pending+=active;disposed+=not active;under_review+=c.lifecycle=='UNDER_REVIEW'
        is_overdue=bool(active and c.due_at and utc(c.due_at)<instant);overdue+=is_overdue;missing_due+=bool(active and not c.due_at)
        age=max(0,(instant-utc(c.received_at)).days) if active else None
        resolutions=list(db.scalars(select(Resolution).where(Resolution.case_id==c.id).order_by(Resolution.disposed_at.desc())))
        disposed_days=max(0,(utc(resolutions[0].disposed_at)-utc(c.received_at)).days) if not active and resolutions else None
        if age is not None:ageing['0–7 days' if age<=7 else '8–30 days' if age<=30 else '31+ days']+=1
        for key,value in [('bureau',c.current_bureau_id),('region',institution.region_id),('institution',institution.id),('status',c.lifecycle)]:dimensions[key][value]+=1
        rows.append({'id':c.public_id,'institution_id':institution.id,'institution':institution.name+', '+institution.city,'region':institution.region_id,
            'bureau':c.current_bureau_id,'owner':db.get(User,c.current_owner_id).display_name,'subject':c.subject if narrative else 'Restricted narrative',
            'category':c.category if narrative else 'Restricted','lifecycle':c.lifecycle,'received_date':utc(c.received_at).astimezone(INDIA).date().isoformat(),
            'due_at':utc(c.due_at).isoformat() if c.due_at else None,'overdue':is_overdue,'active_age_days':age,'disposal_elapsed_days':disposed_days,
            'next_action':c.next_action if narrative else 'Contact accountable officer'})
    disposal_events=list(db.scalars(select(Resolution).where(Resolution.case_id.in_(base_ids)))) if base_ids else []
    period_disposals=[r for r in disposal_events if in_window(r.disposed_at,filters)]
    reopened=list(db.scalars(select(CaseAction).where(CaseAction.case_id.in_(base_ids),CaseAction.kind=='REOPEN'))) if base_ids else []
    monthly=defaultdict(lambda:{'received':set(),'disposed':set(),'disposal_events':0,'reopening_events':0})
    quarterly=defaultdict(lambda:{'received':set(),'disposed':set(),'disposal_events':0,'reopening_events':0})
    def periods(at):
        local=utc(at).astimezone(INDIA)
        return local.strftime('%Y-%m'),f'{local.year}-Q{(local.month-1)//3+1}'
    for c in population:
        month,quarter=periods(c.received_at);monthly[month]['received'].add(c.id);quarterly[quarter]['received'].add(c.id)
    for r in period_disposals:
        month,quarter=periods(r.disposed_at)
        for d,k in [(monthly,month),(quarterly,quarter)]:d[k]['disposed'].add(r.case_id);d[k]['disposal_events']+=1
    for r in reopened:
        if in_window(r.created_at,filters):
            month,quarter=periods(r.created_at);monthly[month]['reopening_events']+=1;quarterly[quarter]['reopening_events']+=1
    def period_view(data):
        return [{'period':k,'new_receipts':len(v['received']),'distinct_disposals':len(v['disposed']),
            'disposal_events':v['disposal_events'],'reopening_events':v['reopening_events']} for k,v in sorted(data.items())]
    relationship_counts=Counter()
    seen=set()
    for s in db.scalars(select(RelationshipSuggestion).where(RelationshipSuggestion.left_id.in_(ids),RelationshipSuggestion.right_id.in_(ids)).order_by(RelationshipSuggestion.created_at.desc())) if ids else []:
        pair=(s.left_id,s.right_id)
        if pair in seen or not pair_authorized(db,actor,db.get(CaseRecord,s.left_id),db.get(CaseRecord,s.right_id)):continue
        seen.add(pair)
        if suggestion_view(db,actor,s)['stale']:continue
        decision=db.scalar(select(RelationshipDecision).where(RelationshipDecision.suggestion_id==s.id).order_by(RelationshipDecision.created_at.desc()).limit(1))
        relationship_counts[decision.label if decision and decision.action=='CONFIRM' else 'UNCONFIRMED']+=1
    transfer_count=sum(t.status=='ACCEPTED' and t.responded_at is not None and in_window(t.responded_at,filters)
        for t in db.scalars(select(Transfer).where(Transfer.case_id.in_(base_ids)))) if base_ids else 0
    total=len(population);distinct_disposed=len({r.case_id for r in period_disposals})
    return {'synthetic':True,'as_of':instant.isoformat(),'timezone':'Asia/Kolkata','filters':filters.model_dump(mode='json'),
        'scope':'Current authorised records/current owner; date window is received-date cohort. Current lifecycle is not a reconstructed historical snapshot.',
        'total':total,'pending':pending,'disposed':disposed,'under_review':under_review,'overdue':overdue,'missing_deadline':missing_due,
        'cohort_disposal_rate':disposed/total if total else None,'period_distinct_disposals':distinct_disposed,
        'disposal_to_receipt_ratio':distinct_disposed/total if total else None,'period_disposal_events':len(period_disposals),
        'historical_accepted_transfers':transfer_count,'dimensions':{k:dict(v) for k,v in dimensions.items()},'active_ageing':dict(ageing),
        'relationship_summary':dict(relationship_counts),'relationship_scope':'Only pair evidence explicitly authorised to this viewer; never added to lifecycle totals',
        'monthly':period_view(monthly),'quarterly':period_view(quarterly),'rows':sorted(rows,key=lambda r:r['id']),
        'formulas':{'partition':'pending + disposed = total; under_review and overdue overlap pending',
            'cohort_disposal_rate':'currently disposed received-date cohort / all received-date cohort cases; empty=N/A',
            'disposal_to_receipt_ratio':'distinct disposals during date window / new receipts during date window; can exceed100%; empty=N/A',
            'dates':'[received_from, received_to), midnight Asia/Kolkata; received_to is exclusive',
            'age':'completed elapsed24hour days; active as of context clock, disposed to latest resolution'}}


def csv_cell(value):
    text='' if value is None else str(value)
    return "'"+text if text.lstrip().startswith(('=','+','-','@','\t','\r')) else text


def register_reporting(app):
    @app.get('/api/reports')
    def reports(filters:Filters=Depends(),actor:Principal=Depends(principal),db:Session=Depends(get_db)):
        return build_report(db,actor,filters)

    @app.get('/api/reports/csv')
    def export(filters:Filters=Depends(),actor:Principal=Depends(principal),db:Session=Depends(get_db)):
        report=build_report(db,actor,filters);out=io.StringIO(newline='')
        fields=['id','institution_id','institution','region','bureau','owner','subject','category','lifecycle','received_date','due_at','overdue','active_age_days','disposal_elapsed_days','next_action']
        writer=csv.writer(out);writer.writerow(fields)
        for row in report['rows']:writer.writerow([csv_cell(row[k]) for k in fields])
        return Response(out.getvalue().encode('utf-8-sig'),media_type='text/csv',headers={'Content-Disposition':'attachment; filename="samanvay-synthetic-report.csv"'})

    @app.get('/api/reports/print',response_class=HTMLResponse)
    def printable(filters:Filters=Depends(),actor:Principal=Depends(principal),db:Session=Depends(get_db)):
        report=build_report(db,actor,filters);escape=lambda v:html.escape(str(v))
        body=''.join('<tr>'+''.join('<td>'+escape(r[k])+'</td>' for k in ['id','institution','bureau','owner','lifecycle','next_action'])+'</tr>' for r in report['rows'])
        document='<!doctype html><html lang="en"><meta charset="utf-8"><title>Samanvay synthetic scoped report</title><style>body{font:16px system-ui;margin:30px;color:#16324d}table{border-collapse:collapse;width:100%;font-size:12px}td,th{border:1px solid #bbb;padding:8px;text-align:left;overflow-wrap:anywhere}thead{display:table-header-group}@media print{body{margin:0}tr{break-inside:avoid}}</style><h1>Samanvay · synthetic scoped report</h1><p>No official integration. '+escape(report['scope'])+'</p><p>As of '+escape(report['as_of'])+' · Asia/Kolkata</p><p>Total '+str(report['total'])+' · Pending '+str(report['pending'])+' · Disposed '+str(report['disposed'])+'</p><p>Received window '+escape(filters.received_from)+' to '+escape(filters.received_to)+' (exclusive end).</p><table><thead><tr>'+''.join('<th scope="col">'+x+'</th>' for x in ['Case','Institution','Bureau','Owner','Lifecycle','Next action'])+'</tr></thead><tbody>'+body+'</tbody></table><p>Current-state cohort disposal rate: '+('N/A' if report['cohort_disposal_rate'] is None else str(round(report['cohort_disposal_rate']*100,2))+'%')+'. Under-review/overdue are pending subsets. No hidden records counted.</p></html>'
        back='/#/reports?'+urlencode({k:v for k,v in filters.model_dump(mode='json').items() if v is not None and v!='all'})
        document=document.replace('<h1>', '<p><a href="'+html.escape(back,quote=True)+'">Return to filtered reports</a></p><h1>',1)
        return HTMLResponse(document,headers={'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'"})
