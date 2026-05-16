export type Book = {
	id: number;
	name: string;
	storage_type: string;
	uri_or_path: string;
	base_currency: string | null;
	is_default: boolean;
	is_archived: boolean;
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
