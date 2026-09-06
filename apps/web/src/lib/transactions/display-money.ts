import type { MoneyDTO, TransactionListItem } from '$lib/api/types';
import type { MessageKey } from '$lib/i18n';

type DisplayMoney = { money: MoneyDTO | null; label: MessageKey; account: string };

// Never infer a monetary basis from direction status or the first split.
export function transactionDisplayMoney(tx: Partial<TransactionListItem>): DisplayMoney {
    const account = tx.representative_account?.display_name || tx.representative_account?.name || tx.account_display_name || tx.account_name || tx.account_id || '';
    switch (tx.amount_basis) {
        case 'neutral_magnitude':
            return { money: tx.representative_amount ?? null, label: 'transactions.amount.neutral', account };
        case 'selected_accounts':
            return { money: tx.matched_amount ?? null, label: (tx.matched_account_ids?.length ?? 0) > 1 ? 'transactions.amount.selectedAccounts' : 'transactions.amount.selectedAccount', account };
        case 'income':
        case 'expense':
            return { money: tx.matched_amount ?? null, label: `transactions.amount.${tx.amount_basis}`, account };
        default:
            // Older account-list DTOs explicitly associate signed amount/currency with account_id.
            // Explorer DTOs (including legacy representative_split) must never use this fallback.
            if (!tx.amount_basis && !tx.direction && typeof tx.amount === 'string' && typeof tx.currency === 'string') {
                return { money: { amount: tx.amount, currency: tx.currency }, label: 'transactions.amount.selectedAccount', account };
            }
            return { money: null, label: 'transactions.direction.amountHidden', account };
    }
}
