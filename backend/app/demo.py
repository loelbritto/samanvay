"""Non-destructive isolated reset, explicit rehearsal grants, private backup/restore."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
from threading import Lock
import uuid
from alembic import command
from alembic.config import Config
from fastapi import Depends,HTTPException,Request
from pydantic import Field
from sqlalchemy import select,update
from sqlalchemy.orm import Session
from .auth import Principal,get_db,mutation
from .config import ROOT,Settings
from .database import make_database
from .models import (AccessGrant,AdministrativeEvent,Attachment,CapabilityGrant,CaseRecord,DemoContext,LoginSession,
    Notification,OutboxJob,User)
from .schemas import StrictInput
from .scheduling import is_admin,require_demo_controls
from .storage import private_path

CONTEXTS=(ROOT/'.demo-contexts').resolve()
BACKUPS=CONTEXTS/'backups'
PROVISION=Lock()


def context_settings(context_id):
    if not re.fullmatch(r'demo-[a-f0-9]{24}',context_id):raise ValueError('Invalid isolated context identifier')
    directory=(CONTEXTS/context_id).resolve()
    if not directory.is_relative_to(CONTEXTS) or directory==CONTEXTS:raise ValueError('Unsafe context path')
    return Settings(directory,'demo',demo_controls=True,context_id=context_id)


def identifier(key):
    if not re.fullmatch(r'[A-Za-z0-9_-]{8,80}',key):raise ValueError('Use an8–80character non-secret run key containing letters, digits, hyphen or underscore')
    return 'demo-'+hashlib.sha256(key.encode()).hexdigest()[:24]


def migrate(settings):
    engine,_=make_database(settings)
    config=Config(str(ROOT/'backend/alembic.ini'))
    with engine.begin() as connection:
        config.attributes['connection']=connection
        command.upgrade(config,'head')
    engine.dispose()


def new_context(key):
    if os.getenv('SAMANVAY_ENV','demo') not in {'demo','test'}:raise ValueError('Isolated context operations are disabled outside demo/test')
    settings=context_settings(identifier(key));directory=settings.data_dir
    with PROVISION:
        reused=directory.exists()
        if reused:
            marker=directory/'SYNTHETIC_CONTEXT.json'
            if not marker.is_file() or json.loads(marker.read_text(encoding='utf-8'))!={'context_id':settings.context_id,'synthetic':True}:
                raise ValueError('Existing/unfinished context was preserved; use another run key rather than overwrite it')
        else:directory.mkdir(parents=True,exist_ok=False)
        migrate(settings)
        engine,sessions=make_database(settings)
        from .seed import seed
        try:seed(settings,sessions)
        finally:engine.dispose()
    return {'context_id':settings.context_id,'data_dir':str(directory),'reused':reused,'previous_contexts_preserved':True}


def rehearsal_grants(settings,sessions,reason='Explicit synthetic rehearsal scope selected by local operator'):
    with sessions() as db:
        require_demo_controls(settings,db)
        coordinator=db.scalar(select(User).where(User.username=='coordinator@demo.test'))
        management=db.scalar(select(User).where(User.username=='management@demo.test'))
        admin=db.scalar(select(User).where(User.username=='admin@demo.test'))
        if not all([coordinator,management,admin]):raise ValueError('Seed the synthetic context first')
        for c in db.scalars(select(CaseRecord).where(CaseRecord.institution_id=='DEMO-INST-017',CaseRecord.synthetic.is_(True))):
            for data_class in ['N','I']:
                grant=db.scalar(select(AccessGrant).where(AccessGrant.user_id==coordinator.id,AccessGrant.case_id==c.id,AccessGrant.data_class==data_class))
                if grant:grant.expires_at=None
                else:db.add(AccessGrant(user_id=coordinator.id,case_id=c.id,data_class=data_class,reason=reason,granted_by=admin.id))
        for capability in ['CASE_METADATA']:
            if not db.scalar(select(CapabilityGrant.id).where(CapabilityGrant.user_id==management.id,CapabilityGrant.capability==capability,CapabilityGrant.scope_type=='INSTITUTION',CapabilityGrant.scope_id=='DEMO-INST-017')):
                db.add(CapabilityGrant(user_id=management.id,capability=capability,scope_type='INSTITUTION',scope_id='DEMO-INST-017',reason=reason))
        db.add(AdministrativeEvent(actor_id=admin.id,kind='SYNTHETIC_REHEARSAL_SCOPE',reason=reason,payload={'institution_id':'DEMO-INST-017','management':'M only','coordinator':'N/I to current synthetic cases only; no attachment grant'}))
        db.commit()


def storage_audit(settings):
    engine,sessions=make_database(settings)
    missing=[];changed=[];known=set()
    with sessions() as db:
        for item in db.scalars(select(Attachment)):
            known.add(item.storage_key)
            try:path=private_path(settings,item.storage_key)
            except ValueError:changed.append(item.id);continue
            if not path.is_file():missing.append(item.id)
            elif hashlib.sha256(path.read_bytes()).hexdigest()!=item.sha256:changed.append(item.id)
    extras=[p.name for p in settings.attachments_dir.iterdir() if p.is_file() and p.name not in known] if settings.attachments_dir.is_dir() else []
    engine.dispose()
    return {'passed':not missing and not changed,'missing_attachment_ids':missing,'changed_attachment_ids':changed,'unreferenced_files_preserved':extras,'files_deleted':0}


def backup(settings):
    if settings.environment not in {'demo','test'}:raise ValueError('Prototype backup disabled outside demo/test')
    source=settings.data_dir.resolve()
    if not (source==ROOT/'.local-data' or source.is_relative_to(CONTEXTS)):raise ValueError('This prototype backup accepts only its workspace local/isolated data directories')
    source_db=source/'samanvay.sqlite3'
    if not source_db.is_file():raise ValueError('No persistent source database found')
    with sqlite3.connect('file:'+source_db.as_posix()+'?mode=ro',uri=True) as check:
        if check.execute('SELECT count(*) FROM cases WHERE synthetic=0').fetchone()[0]:raise ValueError('Non-synthetic source refused before snapshot creation')
    backup_id='backup-'+uuid.uuid4().hex;directory=(BACKUPS/backup_id).resolve()
    assert directory.is_relative_to(BACKUPS.resolve()) and not directory.exists()
    directory.mkdir(parents=True)
    target=directory/'samanvay.sqlite3'
    with sqlite3.connect('file:'+source_db.as_posix()+'?mode=ro',uri=True) as src,sqlite3.connect(target) as dest:
        src.backup(dest);dest.execute('PRAGMA wal_checkpoint(TRUNCATE)');dest.execute('PRAGMA journal_mode=DELETE')
        assert dest.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
        assert dest.execute('PRAGMA foreign_key_check').fetchall()==[]
        if dest.execute('SELECT count(*) FROM cases WHERE synthetic=0').fetchone()[0]:raise ValueError('Non-synthetic data backup is outside this prototype procedure')
        attachments=dest.execute('SELECT storage_key,sha256 FROM attachments').fetchall()
        case_ids=[r[0] for r in dest.execute('SELECT public_id FROM cases ORDER BY public_id')]
        context=dest.execute('SELECT id FROM demo_context').fetchone()
        if not context:raise ValueError('Source context marker missing from database')
    (directory/'private-evidence').mkdir()
    hashes={}
    for key,digest in attachments:
        path=private_path(settings,key)
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Evidence missing or changed; incomplete backup preserved without success marker')
        shutil.copy2(path,directory/'private-evidence'/key);hashes[key]=digest
    manifest={'synthetic':True,'backup_id':backup_id,'source_context':context[0],'case_ids':case_ids,'database_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'private_file_sha256':hashes,'created_at_utc':datetime.now(timezone.utc).isoformat(),'source_records_preserved':True}
    (directory/'backup-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    return manifest


def restore(backup_id,key):
    if os.getenv('SAMANVAY_ENV','demo') not in {'demo','test'}:raise ValueError('Prototype restore disabled outside demo/test')
    if not re.fullmatch(r'backup-[a-f0-9]{32}',backup_id):raise ValueError('Invalid backup identifier')
    archive=(BACKUPS/backup_id).resolve()
    if not archive.is_relative_to(BACKUPS.resolve()):raise ValueError('Unsafe backup path')
    manifest_path=archive/'backup-manifest.json';manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    database=archive/'samanvay.sqlite3'
    if not database.resolve().is_relative_to(archive) or not manifest.get('synthetic') or hashlib.sha256(database.read_bytes()).hexdigest()!=manifest['database_sha256']:
        raise ValueError('Backup integrity check failed')
    settings=context_settings(identifier(key));directory=settings.data_dir
    manifest_hash=hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    with PROVISION:
        if directory.exists():
            provenance=directory/'RESTORED_FROM.json'
            if not provenance.is_file() or json.loads(provenance.read_text())!={'backup_id':backup_id,'manifest_sha256':manifest_hash}:
                raise ValueError('Existing target preserved; use a new restore key')
            return {'context_id':settings.context_id,'reused':True,'source_records_preserved':True}
        for key_name,digest in manifest['private_file_sha256'].items():
            if not re.fullmatch(r'[a-f0-9]{48}\.bin',key_name):raise ValueError('Unsafe private key in backup')
            path=(archive/'private-evidence'/key_name).resolve()
            if not path.is_relative_to(archive) or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Private evidence backup integrity failed')
        directory.mkdir(parents=True);shutil.copy2(database,directory/'samanvay.sqlite3');(directory/'private-evidence').mkdir()
        for key_name in manifest['private_file_sha256']:shutil.copy2(archive/'private-evidence'/key_name,directory/'private-evidence'/key_name)
        engine,sessions=make_database(settings)
        with sessions() as db:
            context=db.scalar(select(DemoContext));context.id=settings.context_id;context.clock_version+=1
            db.execute(update(LoginSession).values(revoked=True))
            db.execute(update(OutboxJob).where(OutboxJob.status=='RUNNING').values(status='PENDING',lease_until=None))
            db.execute(update(Notification).where(Notification.state=='DELIVERING').values(state='PENDING',lease_until=None))
            db.add(AdministrativeEvent(actor_id=None,kind='CONTEXT_RESTORED',reason='Verified private snapshot restored into a new context; previous context retained',payload={'backup_id':backup_id}))
            db.commit()
        engine.dispose()
        (directory/'SYNTHETIC_CONTEXT.json').write_text(json.dumps({'context_id':settings.context_id,'synthetic':True}),encoding='utf-8')
        (directory/'RESTORED_FROM.json').write_text(json.dumps({'backup_id':backup_id,'manifest_sha256':manifest_hash}),encoding='utf-8')
        migrate(settings)
    return {'context_id':settings.context_id,'reused':False,'source_records_preserved':True,'case_ids':manifest['case_ids']}


class ResetInput(StrictInput):
    run_key:str=Field(min_length=8,max_length=80)
    reason:str=Field(min_length=5,max_length=1000)


class ScopeInput(StrictInput):
    reason:str=Field(min_length=5,max_length=1000)


def register_demo(app):
    @app.post('/api/demo/new-context')
    def reset(data:ResetInput,request:Request,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        if not is_admin(actor):raise HTTPException(403,'Technical demo operation requires administration.')
        require_demo_controls(request.app.state.settings,db)
        try:result=new_context(data.run_key)
        except ValueError as error:raise HTTPException(422,str(error))
        db.add(AdministrativeEvent(actor_id=actor.user.id,kind='NEW_DEMO_CONTEXT',reason=data.reason,payload={'new_context_id':result['context_id'],'previous_context_preserved':True}))
        db.commit();return {k:v for k,v in result.items() if k!='data_dir'}

    @app.post('/api/demo/rehearsal-scope')
    def scope(data:ScopeInput,request:Request,actor:Principal=Depends(mutation),db:Session=Depends(get_db)):
        if not is_admin(actor):raise HTTPException(403,'Explicit synthetic scope operation requires administration.')
        require_demo_controls(request.app.state.settings,db)
        rehearsal_grants(request.app.state.settings,request.app.state.sessions,data.reason)
        return {'status':'Explicit isolated synthetic rehearsal scope applied; no case ownership changed','management_scope':'Pune metadata only','coordinator_scope':'Pune current synthetic case N/I; attachments remain separately protected'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    new=sub.add_parser('new');new.add_argument('--key',required=True)
    grant=sub.add_parser('rehearsal-grants');grant.add_argument('--context-id',required=True)
    save=sub.add_parser('backup');save.add_argument('--context-id')
    load=sub.add_parser('restore');load.add_argument('--backup-id',required=True);load.add_argument('--key',required=True)
    audit=sub.add_parser('audit-storage');audit.add_argument('--context-id')
    args=parser.parse_args()
    if args.command=='new':result=new_context(args.key)
    elif args.command=='restore':result=restore(args.backup_id,args.key)
    else:
        settings=context_settings(args.context_id) if args.context_id else Settings.from_env()
        if args.command=='backup':result=backup(settings)
        elif args.command=='audit-storage':result=storage_audit(settings)
        else:
            engine,sessions=make_database(settings);rehearsal_grants(settings,sessions);engine.dispose();result={'context_id':settings.context_id,'status':'Explicit synthetic rehearsal scope recorded'}
    print(json.dumps(result))


if __name__=='__main__':main()
