import assert from 'node:assert/strict';

async function key(cdp,name,code) {
    await cdp.send('Input.dispatchKeyEvent',{type:'keyDown',key:name,code:name,windowsVirtualKeyCode:code,nativeVirtualKeyCode:code,...(name==='Enter'?{text:'\r',unmodifiedText:'\r'}:{})});
    await cdp.send('Input.dispatchKeyEvent',{type:'keyUp',key:name,code:name,windowsVirtualKeyCode:code});
}
async function tabTo(cdp,selector) {
    for(let i=0;i<70;i++) {
        await key(cdp,'Tab',9);
        if(await cdp.evaluate(`document.activeElement?.matches(${JSON.stringify(selector)})`)) return;
    }
    assert.fail('Keyboard Tab must reach '+selector);
}
async function controls(cdp,selector) {
    return cdp.evaluate(`Array.from(document.querySelectorAll(${JSON.stringify(selector)})).filter(el=>el.getClientRects().length).map(el=>{
        const r=el.getBoundingClientRect(), hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);
        return {tag:el.tagName,label:el.innerText||el.getAttribute('aria-label')||el.name,rect:{x:r.x,y:r.y,right:r.right,bottom:r.bottom,width:r.width,height:r.height},inside:r.x>=-1&&r.y>=-1&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1,hit:!!hit&&(hit===el||el.contains(hit))};
    })`);
}
export async function verifyHeader(cdp,base,locale,password,saveScreenshot) {
    const cases=[];
    // CDP effective CSS viewport at browser-zoom-equivalent 200%; not pinch scaling.
    // Real-phone and native browser chrome zoom are not claimed by this harness.
    for(const zoom of [1,2]) for(const physicalWidth of [1440,320,390,768,1024,1280,1920]) {
        const width=Math.floor(physicalWidth/zoom),height=Math.floor(1000/zoom);
        // Do not test a 160px layout as a 320px phone: 200% cases cover desktop reflow.
        if(zoom===2&&physicalWidth<768) continue;
        await cdp.send('Emulation.setDeviceMetricsOverride',{width,height,deviceScaleFactor:zoom,mobile:false});
        await cdp.navigate(base+'/dashboard');await cdp.wait('document.querySelector("main")');
        const mobile=width<768;
        if(mobile) {
            await tabTo(cdp,'[data-mobile-more]'); await key(cdp,'Enter',13);
            await cdp.wait('document.querySelector("[data-mobile-menu]")');
        }
        const selector=mobile?'[data-mobile-nav] a,[data-mobile-nav] button,[data-mobile-nav] select':'header a,header button,header select';
        const geometry=await controls(cdp,selector);
        assert.ok(geometry.length>=7,'Navigation and session controls must remain accessible');
        const logout=mobile?'[data-mobile-menu] form[action="/logout"] button':'header form[action="/logout"] button';
        for(const item of [...await controls(cdp,logout),...geometry]) assert.ok(item.inside&&item.hit,JSON.stringify({locale,physicalWidth,zoom,item}));
        if ([390,1440].includes(physicalWidth)) await saveScreenshot(`header-${locale}-${physicalWidth}-zoom${zoom}.png`);
        await tabTo(cdp,logout);
        assert.ok(await cdp.evaluate('document.activeElement.matches(":focus-visible") && getComputedStyle(document.activeElement).outlineStyle!=="none"'),'Keyboard focus is visibly outlined');
        if(mobile) {
            await key(cdp,'Escape',27); await cdp.wait('!document.querySelector("[data-mobile-menu]")');
            assert.ok(await cdp.evaluate('document.activeElement.matches("[data-mobile-more]")'),'Escape returns focus to menu trigger');
            await key(cdp,'Enter',13);await cdp.wait('document.querySelector("[data-mobile-menu]")');
            await tabTo(cdp,logout);
        }
        // Only session logout/login; never call a book mutation endpoint.
        await key(cdp,'Enter',13);await cdp.wait('location.pathname==="/login" && document.querySelector("input[name=username]")');
        await cdp.evaluate(`document.querySelector('input[name=username]').value='admin';document.querySelector('input[name=password]').value=${JSON.stringify(password)};document.querySelector('button[type=submit]').click()`);
        await cdp.wait('location.pathname==="/dashboard" && document.querySelector("main")');
        cases.push({locale,physicalWidth,zoom,effectiveWidth:width,controls:geometry,logout_login:'PASS'});
    }
    return cases;
}
