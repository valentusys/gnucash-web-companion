export type Book = {
	id: number;
	name: string;
	storage_type: string;
	uri_or_path: string;
	base_currency: string | null;
	is_default: boolean;
	is_archived: boolean;
	access_role: 'owner' | 'editor' | 'viewer' | null;
	read_only: boolean;
	status: string;
	management_actions: string[];
};

export type Account = {
	id: string;
	name: string;
	full_name: string;
	type: string;
	currency: string;
	balance: string;
	placeholder: boolean;
	hidden: boolean;
	parent_id: string | null;
};

export type AccountTreeNode = Account & {
	children: AccountTreeNode[];
};

export type TransactionSplit = {
	account_id: string;
	account_name: string;
	memo: string;
	reconcile_state?: string;
	amount: string;
	currency: string;
};

export type TransactionListItem = {
	id: string;
	date: string;
	description: string;
	amount: string;
	currency: string;
	account_id: string;
	account_name: string;
	counter_account_name: string;
};

export type TransactionDetail = {
	id: string;
	date: string;
	description: string;
	currency: string;
	splits: TransactionSplit[];
};

export type ScheduledTransactionRecurrence = {
	period_type: string;
	multiplier: number | null;
	period_start: string | null;
	weekend_adjust: string;
};

export type ScheduledTransaction = {
	id: string;
	name: string;
	enabled: boolean;
	start_date: string | null;
	end_date: string | null;
	last_occurred: string | null;
	num_occurrences: number | null;
	remaining_occurrences: number | null;
	auto_create: boolean;
	auto_notify: boolean;
	advance_create_days: number | null;
	advance_notify_days: number | null;
	instance_count: number | null;
	has_template_account: boolean;
	recurrence: ScheduledTransactionRecurrence[];
	limitations: string[];
};

export type PaginatedTransactions = {
	items: TransactionListItem[];
	limit: number;
	offset: number;
	total: number;
};

export type ReportSummary = {
	currency: string;
	net_worth: string;
	assets: string;
	liabilities: string;
	income_this_month: string;
	expenses_this_month: string;
	as_of_date: string;
	reporting_basis: string;
	includes_currency_conversion: boolean;
	limitations: string[];
};

export type ExpenseByAccount = {
	account_id: string;
	account_name: string;
	total: string;
	currency: string;
};

export type CashflowData = {
	date_from: string;
	date_to: string;
	currency: string;
	inflow: string;
	outflow: string;
	net: string;
};

export type CashflowPeriod = {
	month: string;
	inflow: string;
	outflow: string;
	net: string;
};

export type TransactionValidationResult = {
	valid: boolean;
	errors: string[];
	warnings: string[];
	summary: Record<string, unknown>;
};

export type TransactionWriteResult = {
	transaction_id: string;
	backup_path: string;
	audit_log_id: number | null;
};
