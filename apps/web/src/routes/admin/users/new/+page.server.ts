import { fail, redirect } from '@sveltejs/kit';
import {
	adminApiMutationFetch,
	getAuthToken,
	getCurrentUser,
	isCurrentUserAdmin
} from '$lib/api/server';
import type { AdminProblemCode, AdminUserDetail } from '$lib/api/types';
import type { Cookies } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

type SafeCreateForm = {
	username: string;
	displayName: string;
	isAdmin: boolean;
};

function textField(form: FormData, name: string): string {
	return String(form.get(name) ?? '').trim();
}

function secretField(form: FormData, name: string): string {
	return String(form.get(name) ?? '');
}

function safeCreateForm(form: FormData): SafeCreateForm {
	return {
		username: textField(form, 'username'),
		displayName: textField(form, 'display_name'),
		isAdmin: form.get('is_admin') === 'on'
	};
}

async function requireAdmin(fetchFn: typeof fetch, token: string, cookies: Cookies): Promise<boolean> {
	const currentUser = await getCurrentUser(fetchFn, token, cookies);
	return isCurrentUserAdmin(currentUser);
}

export const load: PageServerLoad = async ({ cookies, parent }) => {
	getAuthToken(cookies);
	const layoutData = await parent();
	return {
		isAdmin: isCurrentUserAdmin(layoutData.currentUser)
	};
};

export const actions: Actions = {
	create: async ({ cookies, fetch, request }) => {
		const token = getAuthToken(cookies);
		if (!(await requireAdmin(fetch, token, cookies))) {
			return fail(403, { adminErrorCode: 'admin_required' satisfies AdminProblemCode });
		}
		const form = await request.formData();
		const formState = safeCreateForm(form);
		const initialPassword = secretField(form, 'initial_password');
		if (!formState.username || !formState.displayName || !initialPassword) {
			return fail(400, {
				adminErrorCode: (!initialPassword ? 'password_policy' : 'display_name_invalid') satisfies AdminProblemCode,
				createRequest: formState
			});
		}

		const result = await adminApiMutationFetch<AdminUserDetail>(fetch, token, '/admin/users', 'POST', {
			username: formState.username,
			display_name: formState.displayName,
			password: initialPassword,
			is_admin: formState.isAdmin
		}, cookies);
		if (!result.ok) {
			return fail(result.status, {
				adminErrorCode: result.message,
				createRequest: formState
			});
		}
		throw redirect(303, `/admin/users/${result.payload.id}?admin_success=user_created`);
	}
};
