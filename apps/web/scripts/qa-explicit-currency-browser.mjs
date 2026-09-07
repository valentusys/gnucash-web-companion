import assert from 'node:assert/strict';

// Called only by the generated-book real-backend read-only runner.
export async function verifyExplicitCurrency(cdp, apiRequests, getPreview, ids, configureSyntheticCurrency) {
    const fill = async (values) => cdp.evaluate(`((values) => {
        for (const [selector,value] of values) {
            const el=document.querySelector(selector);
            el.value=value;
            el.dispatchEvent(new Event(el.tagName==='SELECT'?'change':'input',{bubbles:true}));
        }
    })(${JSON.stringify(values)})`);
    const submitPreview = async () => {
        const before = cdp.loadCount;
        await cdp.evaluate(`document.querySelector('button[formaction="?/preview"]').click()`);
        for (let i=0;i<150 && cdp.loadCount===before;i++) await new Promise(done=>setTimeout(done,100));
        assert.ok(cdp.loadCount>before,'preview response must finish before asserting returned state');
    };
    const selects = ['select[name=split_account_id]', 'fieldset:nth-of-type(2) select[name=split_account_id]'];
    await fill([['#transaction-currency','USD']]);
    for (const selector of selects) {
        const options = await cdp.evaluate(`Array.from(document.querySelector(${JSON.stringify(selector)}).options).filter(o=>!o.disabled).map(o=>o.value)`);
        for (const id of [ids.usd,ids.usd_savings]) assert.ok(options.includes(id), 'QA-08 eligible USD accounts must remain selectable after explicit currency change');
    }
    const optionsRequest = apiRequests.filter(r=>r.path.endsWith('/accounts/options')).at(-1);
    assert.equal(optionsRequest.query.purpose,'transaction_create_preview');
    assert.equal(optionsRequest.query.limit,'200');
    assert.equal(optionsRequest.query.currency,undefined,'reporting default must not restrict account scope');
    await fill([['#transaction-date','2026-09-01'],['#transaction-description','SYNTHETIC explicit currency preview'],
        ['input[name=split_amount]','-1.2300'],['fieldset:nth-of-type(2) input[name=split_amount]','1.2300']]);
    // The existing backend contract requires explicit book metadata configuration.
    // No configuration is inferred or written by the product form.
    await fill(selects.map((selector,i)=>[selector,[ids.usd,ids.usd_savings][i]]));
    await submitPreview();
    await cdp.wait('Boolean(document.querySelector("#transaction-create-error-summary"))');
    assert.equal(apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview')).at(-1).status,422);
    assert.equal(apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview')).at(-1).error_code,'COMMODITY_MISMATCH');
    assert.equal(await cdp.evaluate('document.querySelector("#transaction-currency").value'),'USD');
    const cases = [];
    for (const [currency,accountIds] of [['USD',[ids.usd,ids.usd_savings]],['RUB',[ids.cash,ids.savings]]]) {
        configureSyntheticCurrency(currency); // isolated fixture setup, not a browser/API write
        await fill([['#transaction-currency',currency],...selects.map((selector,i)=>[selector,accountIds[i]])]);
        const before = apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview')).length;
        await submitPreview();
        await cdp.wait('Boolean(document.querySelector("#normalized-preview")) && !document.querySelector("#transaction-create-error-summary")');
        const requests = apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview'));
        assert.equal(requests.length,before+1);
        assert.equal(requests.at(-1).status,200);
        const preview = getPreview();
        assert.equal(preview.currency,currency);
        assert.deepEqual(preview.splits.map(s=>s.account.id),accountIds);
        assert.deepEqual(preview.splits.map(s=>s.amount),['-1.2300','1.2300']);
        assert.equal(preview.preview_only,true);
        assert.equal(preview.confirm_allowed,false);
        assert.equal(await cdp.evaluate('document.querySelector("#transaction-currency").value'),currency);
        assert.equal(await cdp.evaluate(`document.querySelectorAll('#confirm-create-form,button[formaction="?/confirm"]').length`),0);
        cases.push({currency,preview_status:200,exact_amounts:true,controlled_accounts:true,confirm_allowed:false});
    }
    // Offering multiple currencies must not weaken the backend commodity check.
    configureSyntheticCurrency('USD');
    await fill([['#transaction-currency','USD']]); // current accounts are RUB
    const before = apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview')).length;
    await submitPreview();
    await cdp.wait('Boolean(document.querySelector("#transaction-create-error-summary"))');
    const requests = apiRequests.filter(r=>r.path.endsWith('/transactions/create-preview'));
    assert.equal(requests.length,before+1);
    assert.equal(requests.at(-1).status,422);
    assert.equal(requests.at(-1).error_code,'COMMODITY_MISMATCH');
    assert.equal(await cdp.evaluate('Boolean(document.querySelector("#normalized-preview"))'),false);
    assert.equal(await cdp.evaluate('document.querySelector("#transaction-currency").value'),'USD');
    for (const [index,selector] of selects.entries()) {
        assert.equal(await cdp.evaluate(`document.querySelector(${JSON.stringify(selector)}).value`),[ids.cash,ids.savings][index]);
        const options = await cdp.evaluate(`Array.from(document.querySelector(${JSON.stringify(selector)}).options).map(o=>o.value)`);
        assert.ok(options.includes(ids.usd) && options.includes(ids.usd_savings),'USD accounts remain available on returned invalid draft');
    }
    configureSyntheticCurrency(null); // restore inferred-default setup for book-switch/locales
    return {cases,unconfigured_currency_status:422,mismatched_currency_status:422,explicit_choice_preserved:true};
}
