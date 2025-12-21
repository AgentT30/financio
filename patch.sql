-- Restore soft-deleted transaction without affecting balance
-- First, find the transaction ID you want to restore:
-- SELECT id, datetime_ist, transaction_type, amount, purpose, deleted_at 
-- FROM transactions 
-- WHERE deleted_at IS NOT NULL 
-- ORDER BY deleted_at DESC;

-- Then restore it by setting deleted_at to NULL (replace <transaction_id> with actual ID):
-- UPDATE transactions 
-- SET deleted_at = NULL, updated_at = NOW()
-- WHERE id = <transaction_id>;

-- Example: To restore transaction with ID 1:
-- UPDATE transactions 
-- SET deleted_at = NULL, updated_at = NOW()
-- WHERE id = 1;
