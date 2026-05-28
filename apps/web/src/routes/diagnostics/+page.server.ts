import type { HealthPayload } from '$lib/api/types';

export async function load({ fetch }) {
	const apiBase = process.env.API_INTERNAL_URL ?? 'http://localhost:8000';
	try {
		const response = await fetch(`${apiBase}/health`);
		if (!response.ok) {
			return {
				diagnostics: null as HealthPayload | null,
				apiReachable: false,
				errorMessage: 'Diagnostics endpoint returned an error status.'
			};
		}
		return {
			diagnostics: (await response.json()) as HealthPayload,
			apiReachable: true,
			errorMessage: null as string | null
		};
	} catch {
		return {
			diagnostics: null as HealthPayload | null,
			apiReachable: false,
			errorMessage: 'API service is unavailable.'
		};
	}
}
