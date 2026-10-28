import './styles.css';
import { useEffect, useState } from 'react';
import { Icon } from './components';
import Overview from './screens/Overview';
import { CaseDetail, CaseList, Intake } from './screens/Cases';
import { InstitutionList, InstitutionProfile } from './screens/Institutions';
import { Comparison, CoordinationList } from './screens/Coordination';
import { Notifications, PreviewStates, Reports, Settings } from './screens/Support';

const nav = ['Overview','Cases','Institutions','Coordination','Reports','Notifications','Settings'];
function currentRoute() { return window.location.hash.slice(1) || '/overview'; }
export default function PreviewApp() {
  const [route,setRoute] = useState(currentRoute);
  useEffect(()=>{const onHash=()=>setRoute(currentRoute());window.addEventListener('hashchange',onHash);return()=>window.removeEventListener('hashchange',onHash);},[]);
  const [path,queryString=''] = route.split('?');
  const parts = path.split('/').filter(Boolean);
  const section = parts[0] || 'overview';
  useEffect(()=>{document.title = `${section.charAt(0).toUpperCase()+section.slice(1)} · Samanvay synthetic preview`;document.getElementById('page-title')?.focus();window.scrollTo(0,0);},[route,section]);
  let screen;
  if(section==='overview') screen=<Overview/>;
  else if(section==='cases') screen=parts[1]==='new'?<Intake/>:parts[1]?<CaseDetail id={parts[1]} timeline={parts[2]==='timeline'}/>:<CaseList query={new URLSearchParams(queryString)}/>;
  else if(section==='institutions') screen=parts[1]?<InstitutionProfile id={parts[1]}/>:<InstitutionList/>;
  else if(section==='coordination') screen=parts[1]==='compare'?<Comparison/>:<CoordinationList/>;
  else if(section==='reports') screen=<Reports/>;
  else if(section==='notifications') screen=<Notifications/>;
  else if(section==='settings') screen=<Settings/>;
  else if(section==='preview-states') screen=<PreviewStates/>;
  else screen=<><h1 id="page-title" tabIndex={-1}>Page not found</h1><p>This route is not in the UI preview. <a href="#/overview">Return to Overview</a>.</p></>;
  return <>
    <a className="skip-link" href="#main-content" onClick={e=>{e.preventDefault();document.getElementById('main-content')?.focus();}}>Skip to main content</a>
    <aside className="sidebar"><a className="brand" href="#/overview" aria-label="Samanvay overview"><span className="brand-symbol"><Icon name="coordination" size={25}/></span><span>Samanvay<small>Institution coordination</small></span></a><div className="sidebar-caption">WORKSPACE</div><nav aria-label="Main navigation">{nav.map(label=><a key={label} href={`#/${label.toLowerCase()}`} aria-current={section===label.toLowerCase()?'page':undefined}><Icon name={label.toLowerCase()}/><span>{label}</span>{label==='Coordination'&&<span className="nav-count">1</span>}</a>)}</nav><div className="sidebar-bottom"><span className="prototype-label">STUDENT PROTOTYPE</span><p>Connected work.<br/>Clear responsibility.</p><a href="#/preview-states"><Icon name="info" size={16}/>Preview states</a></div></aside>
    <div className="workspace"><div className="prototype-banner"><Icon name="info" size={16}/><strong>Synthetic UI reference</strong><span>Authored fixtures · no live integrations · no changes are saved</span><a href="/">Open database workspace</a></div><header className="topbar"><p>Institution complaint coordination <span className="topbar-divider">/</span> <strong>{section==='preview-states'?'Preview states':nav.find(label=>label.toLowerCase()===section)??'Preview'}</strong></p><div className="persona"><span className="avatar">DC</span><div><strong>Demo coordinator</strong><span>Illustrative scope · no sign-in</span></div></div></header><main id="main-content" tabIndex={-1} key={route}>{screen}<footer className="page-footer"><span>Samanvay · Stage 1 UI reference</span><span>All institutions, people and allegations are fictional.</span></footer></main></div>
  </>;
}
