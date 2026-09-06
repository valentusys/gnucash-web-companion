import { isRedirect } from '@sveltejs/kit';
import { apiFetch } from '$lib/api/server';

function calendarDate(value: unknown): value is string {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    const parsed = new Date(`${value}T00:00:00Z`);
    return !Number.isNaN(parsed.getTime()) && parsed.toISOString().slice(0, 10) === value;
}

// API local calendar is authoritative. Never derive installation "today" from a JS UTC instant.
export async function getReportingDate(fetchFn: typeof fetch, bookPrefix: string, token: string, summaryAsOf?: unknown): Promise<string | null> {
    if (calendarDate(summaryAsOf)) return summaryAsOf;
    try {
        const context = await apiFetch<{ as_of_date?: unknown }>(fetchFn, `${bookPrefix}/reports/reporting-date`, token);
        return calendarDate(context?.as_of_date) ? context.as_of_date : null;
    } catch (reason) {
        if (isRedirect(reason)) throw reason;
        return null;
    }
}
