import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async ({ locals, url }) => {
	return {
		authenticated: locals.authenticated ?? false,
		pathname: url.pathname
	};
};
