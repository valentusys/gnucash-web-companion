import assert from 'node:assert/strict';
export async function verifyUx(cdp,base,locale,cases,saveScreenshot) {
    for(const [width,height] of [[320,800],[390,844]]) for(const path of ['/transactions?date_from=2026-09-01&date_to=2026-09-30&page_size=20','/transactions/new','/accounts']) {
        await cdp.send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:1,mobile:false});
        await cdp.navigate(base+path);await cdp.wait('document.querySelector("main")');
        const result=await cdp.evaluate(`(()=>{
            const visible=el=>el&&el.getBoundingClientRect().width>0&&el.getBoundingClientRect().height>0;
            const box=el=>el?{top:el.getBoundingClientRect().top,bottom:el.getBoundingClientRect().bottom}:null;
            const main=document.querySelector('main'), text=main.innerText;
            const isNew=location.pathname.endsWith('/new'),isAccounts=location.pathname==='/accounts';
            const start=isNew?document.querySelector('#transaction-date'):isAccounts?document.querySelector('#account-query'):main.querySelector('form[action="/transactions"]');
            const row=isNew?start:isAccounts?main.querySelector('[data-account-row]'):Array.from(main.querySelectorAll('a')).find(a=>/^\\/transactions\\/[0-9a-f]{32}(?:\\?|$)/.test(a.getAttribute('href')||'')&&visible(a));
            const footer=document.querySelector('[data-mobile-nav]');
            return {lang:document.documentElement.lang,start:box(start),row:box(row),bottom:footer?.getBoundingClientRect().top??innerHeight,technical:/\\b(GET|cursor|SSR|endpoint|exact parity|CREATE|PATCH|DELETE|batch)\\b/i.test(text),english:${JSON.stringify(locale)}==='ru'&&/This month|Last month|Preview new transaction|Book:|Review books|Clear filters|Account explorer|Bounded account|server-filtered|candidates/.test(text),closedHelp:!!main.querySelector('details[data-technical-info]:not([open])'),overflow:document.documentElement.scrollWidth>innerWidth+1};
        })()`);
        result.width=width;result.height=height;result.path=path;result.locale=locale;cases.push(result);
        await saveScreenshot(`ux-${locale}-${width}-${path.startsWith('/accounts')?'accounts':path.startsWith('/transactions/new')?'form':'transactions'}.png`);
    }
    await cdp.navigate(base+'/transactions?date_from=2026-09-01&date_to=2026-09-30&page_size=20');
    await cdp.wait('document.querySelector("details[data-filter-controls]")');
    await cdp.evaluate('document.querySelector("details[data-technical-info] summary").focus()');
    await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13,text:'\r'});
    await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
    await cdp.wait('document.querySelector("details[data-technical-info]").open');
    await cdp.evaluate('document.querySelector("details[data-technical-info] summary").click();document.querySelector("details[data-filter-controls] summary").click()');
    await cdp.wait('document.querySelector("details[data-filter-controls]").open');
    await cdp.evaluate(`const form=document.querySelector('form[action="/transactions"]');form.querySelector('#tx-query').value='QA12-NO-RESULT';form.querySelector('button[type="submit"]').click()`);
    await cdp.wait(`new URL(location.href).searchParams.get('query')==='QA12-NO-RESULT' && document.querySelector('main [role="status"]')`);
    assert.equal(await cdp.evaluate('document.documentElement.lang'),locale);
    await cdp.navigate(base+'/transactions?date_from=2026-09-01&date_to=2026-09-30&page_size=20&cursor=invalid-QA12');
    await cdp.wait('document.querySelector("main [role=alert]")');
    if(locale==='ru') assert.doesNotMatch(await cdp.evaluate('document.querySelector("main [role=alert]").innerText'),/[a-z]/i,'Russian malformed-cursor error must be localized');
    assert.equal(await cdp.evaluate('Boolean(document.querySelector("main [role=alert]").closest("details:not([open])"))'),false,'Real error must remain outside closed disclosures');
    await cdp.navigate(base+'/transactions?date_from=2026-09-01&date_to=2026-09-30&page_size=0');
    await cdp.wait('document.querySelector("main [role=alert]")');
    if(locale==='ru') assert.doesNotMatch(await cdp.evaluate('document.querySelector("main [role=alert]").innerText'),/[a-z]/i,'Russian invalid-filter error must be localized');
    const failures=cases.filter(x=>x.locale===locale&&(x.lang!==locale||x.technical||x.english||!x.closedHelp||x.overflow||!x.start||!x.row||x.start.top<0||x.start.top>=x.bottom||x.row.top>=x.bottom));
    assert.deepEqual(failures,[],'QA-12 primary task and beginning of results must be visible before technical help');
}
