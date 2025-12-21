# Investments Module - Testing Plan

**Date:** 30 November 2025
**Module:** Investments (investments/)
**Testing Phase:** Phase 1-3 Completion Verification

---

## Test Environment Setup

### Prerequisites

- Django server running (`uv run python manage.py runserver`)
- User account created and logged in
- Database migrations applied
- No existing Investment data (or note existing data for reference)

### Test Data Requirements

Prepare the following test scenarios:

- **Broker1:** "Zerodha" (ID: ZER123, Demat: 1234567890)
- **Broker2:** "Groww" (ID: GRW456, Demat: 0987654321)
- **Inv1:** "Reliance Industries" (Stock, linked to Broker1)
- **Inv2:** "Nifty 50 ETF" (ETF, linked to Broker1)
- **Inv3:** "Gold Bees" (Gold, linked to Broker2)

---

## Test Cases

### 1. Navigation & Access

#### Test 1.1: Access Investment List Page

- **Action:** Navigate to `/investments/`
- **Expected:**
  - Investment list page loads successfully
  - Page title shows "Investments"
  - "Add Investment" button visible (if broker exists)
  - "Manage Brokers" button visible
  - Empty state shows if no investments exist
- **Status:** [x] Pass ☐ Fail

#### Test 1.2: Navigation Menu

- **Action:** Check header and sidebar for Investment menu item
- **Expected:**
  - "Investments" menu item present before "Transactions"
  - Links correctly to `/investments/`
- **Status:** [x] Pass ☐ Fail

---

### 2. Broker Management

#### Test 2.1: Create Broker

- **Action:**
  1. Click "Manage Brokers" -> "Add Broker"
  2. Fill details:
     - Name: "Zerodha"
     - User ID: "AB1234"
     - Demat Account: "1208123456789012"
  3. Submit form
- **Expected:**
  - Form submits successfully
  - Redirect to Broker List
  - Success message displayed
  - Broker appears in list with masked Demat number (ends in 9012)
- **Status:** [x] Pass ☐ Fail

#### Test 2.2: Edit Broker

- **Action:**
  1. Click Edit on "Zerodha"
  2. Change Name to "Kite by Zerodha"
  3. Submit
- **Expected:**
  - Changes saved successfully
  - Updated name visible in list
- **Status:** [x] Pass ☐ Fail

#### Test 2.3: Delete Broker

- **Action:**
  1. Click Delete on a Broker
  2. Confirm deletion
- **Expected:**
  - Broker deleted successfully
  - Removed from list
  - (Note: Should ideally warn if investments are linked - check behavior)
- **Status:** [x] Pass ☐ Fail

#### Test 2.4: Archive Broker

- **Action:**
  1. Click Archive on a Broker (e.g., "Kite by Zerodha")
  2. Confirm archival
- **Expected:**
  - Broker moved to "Archived Brokers" section
  - Success message displayed
  - "Archive" button no longer visible for this broker
  - "Delete" button still visible
- **Status:** [x] Pass ☐ Fail

---

### 3. Investment Management

#### Test 3.1: Create Investment (No Broker)

- **Action:** Try to create investment when no brokers exist
- **Expected:**
  - Redirect to "Add Broker" page
  - Warning message: "Please add a broker before creating an investment"
- **Status:** [x] Pass ☐ Fail

#### Test 3.2: Create Investment (Smart Form - New Asset)

- **Action:**
  1. Click "Add Investment"
  2. Fill details:
     - Broker: Select "Zerodha"
     - Name: "Tata Motors"
     - Symbol: "TATAMOTORS"
     - Type: Stock
     - Transaction Type: Buy
     - Price: ₹500
     - Quantity: 10
     - Fees: ₹10
     - Purchase Date: Today
  3. Submit
- **Expected:**
  - Investment created successfully
  - Redirect to Investment Detail page
  - Stats initialized:
    - Quantity: 10
    - Avg Price: ₹500
    - Total Invested: ₹5,010
- **Status:** [x] Pass ☐ Fail

#### Test 3.3: Edit Investment

- **Action:** Edit "Tata Motors", change type to "ETF"
- **Expected:**
  - Type updated successfully
- **Status:** [x] Pass ☐ Fail

---

### 4. Transaction Management (Buy/Sell)

#### Test 4.1: Add Subsequent Buy Transaction (Smart Form - Existing Asset)

- **Action:**
  1. Open "Tata Motors" detail
  2. Click "Add Transaction"
  3. **Verify:** Redirects to "Add Investment" form with Name="Tata Motors" and Broker="Zerodha" pre-filled.
  4. Fill details:
     - Transaction Type: Buy
     - Price: ₹600
     - Quantity: 10
     - Fees: ₹10
     - Purchase Date: Today
  5. Submit
- **Expected:**
  - Transaction recorded and appended to existing "Tata Motors" investment
  - Total Quantity: 20 (10 initial + 10 new)
  - Total Invested: ₹11,020 (5010 + 6010)
  - Avg Buy Price: ₹551
- **Status:** [x] Pass ☐ Fail

#### Test 4.2: Sell Transaction

- **Action:**
  1. Click "Add Transaction" on "Tata Motors"
  2. Select Transaction Type: **Sell**
  3. Quantity: 5
  4. Price: ₹700
  5. Fees: ₹5
  6. Submit
- **Expected:**
  - Transaction recorded successfully
  - Total Quantity: 15 (20 - 5)
  - Total Invested reduced proportionally (Avg Cost Method)
  - Realized P&L recorded (if implemented) or just holdings updated
- **Status:** [x] Pass ☐ Fail

#### Test 4.3: Sell More Than Owned (Validation)

- **Action:**
  1. Click "Add Transaction"
  2. Select Transaction Type: **Sell**
  3. Quantity: 50 (when owning 15)
  4. Submit
- **Expected:**
  - Form validation error: "Insufficient quantity. You own 15 units."
  - Transaction NOT saved
- **Status:** [x] Pass ☐ Fail

---

### 5. Transaction Editing

#### Test 5.1: Edit Buy Transaction

- **Action:**
  1. Open an investment detail page
  2. Click "Edit" on a buy transaction
  3. Change quantity from 10 to 15
  4. Change price from ₹500 to ₹550
  5. Submit
- **Expected:**
  - Transaction updated successfully
  - Holdings recalculated correctly
  - Average buy price updated
  - Total invested updated
- **Status:** [x] Pass ☐ Fail

#### Test 5.2: Edit Sell Transaction

- **Action:**
  1. Click "Edit" on a sell transaction
  2. Change quantity from 5 to 3
  3. Submit
- **Expected:**
  - Transaction updated successfully
  - Holdings recalculated (more units remain)
  - P&L calculations updated
- **Status:** [x] Pass ☐ Fail

#### Test 5.3: Edit Sell Transaction - Validation

- **Action:**
  1. Edit a sell transaction
  2. Change quantity to exceed available holdings
  3. Submit
- **Expected:**
  - Validation error displayed
  - Transaction NOT updated
  - Error message shows current holdings
- **Status:** [x] Pass ☐ Fail

#### Test 5.4: Edit Transaction Date

- **Action:**
  1. Edit a transaction
  2. Change the date to a different date
  3. Submit
- **Expected:**
  - Date updated successfully
  - Transaction list re-ordered by date
- **Status:** [x] Pass ☐ Fail

---

### 6. Auto-Delete Investment

#### Test 6.1: Delete Last Transaction

- **Action:**
  1. Create an investment with only 1 transaction
  2. Delete that transaction
  3. Confirm deletion
- **Expected:**
  - Transaction deleted
  - Investment automatically deleted
  - Success message: "Transaction deleted. Investment '[name]' was also deleted as it had no remaining transactions."
  - Redirected to investment list
- **Status:** [x] Pass ☐ Fail

#### Test 6.2: Delete All Transactions Sequentially

- **Action:**
  1. Create investment with 3 transactions
  2. Delete first transaction - verify investment remains
  3. Delete second transaction - verify investment remains
  4. Delete third (last) transaction
- **Expected:**
  - After first two deletions: Investment still exists
  - After last deletion: Investment auto-deleted
  - Appropriate success messages
- **Status:** [x] Pass ☐ Fail

---

### 7. Form Validation Edge Cases

#### Test 7.1: Negative Price Validation

- **Action:**
  1. Try to create transaction with negative price (e.g., -100)
  2. Submit
- **Expected:**
  - Validation error: "Price per unit cannot be negative"
  - Transaction NOT created
- **Status:** [x] Pass ☐ Fail

#### Test 7.2: Negative Fees Validation

- **Action:**
  1. Try to create transaction with negative fees (e.g., -10)
  2. Submit
- **Expected:**
  - Validation error: "Fees cannot be negative"
  - Transaction NOT created
- **Status:** [x] Pass ☐ Fail

#### Test 7.3: Zero Quantity Validation

- **Action:**
  1. Try to create transaction with quantity = 0
  2. Submit
- **Expected:**
  - Validation error: "Quantity must be greater than zero"
  - Transaction NOT created
- **Status:** [x] Pass ☐ Fail

#### Test 7.4: Duplicate Investment Name (Same Broker)

- **Action:**
  1. Create investment "Reliance" with Broker "Zerodha"
  2. Try to create another investment "Reliance" with same broker
  3. Add as Buy transaction
- **Expected:**
  - Transaction appended to existing investment
  - No duplicate investment created
  - Holdings updated correctly
- **Status:** [x] Pass ☐ Fail

#### Test 7.5: Symbol Field Validation

- **Action:**
  1. Create investment with special characters in symbol (e.g., "REL@#$")
  2. Create investment with very long symbol (>20 chars)
- **Expected:**
  - Special characters accepted (or appropriate validation)
  - Long symbols handled appropriately
- **Status:** [x] Pass ☐ Fail

---

### 8. Investment Status Management

#### Test 8.1: Change Investment Status to Archived

- **Action:**
  1. Edit an investment
  2. Change status from "Active" to "Archived"
  3. Submit
- **Expected:**
  - Status updated successfully
  - Investment no longer visible in active list
  - Investment visible when "Show Archived" toggle is clicked
- **Status:** [x] Pass ☐ Fail

#### Test 8.2: Unarchive Investment

- **Action:**
  1. Archive an investment (Test 8.1)
  2. Click "Show Archived" toggle
  3. Edit the archived investment
  4. Change status back to "Active"
  5. Submit
- **Expected:**
  - Status updated successfully
  - Investment no longer visible in archived list
  - Investment visible in active list (click "Show Active" to verify)
- **Status:** [x] Pass ☐ Fail

#### Test 8.3: Toggle Between Active and Archived Investments

- **Action:**
  1. Create at least 2 active investments and 1 archived investment
  2. On investment list page, click "Show Archived" button
  3. Verify archived investments are shown
  4. Click "Show Active" button
  5. Verify active investments are shown
- **Expected:**
  - Toggle button switches between "Show Archived" and "Show Active"
  - Only investments with selected status shown
  - Summary stats (Total Invested, Current Value, P&L) update based on visible investments
- **Status:** [x] Pass ☐ Fail

---

### 9. Broker-Investment Relationships

#### Test 9.1: Delete Broker with Linked Investments

- **Action:**
  1. Create broker with linked investments
  2. Try to delete the broker
- **Expected:**
  - Warning message or prevention
  - OR investments also deleted (document behavior)
- **Status:** [x] Pass ☐ Fail

#### Test 9.2: Archive Broker with Active Investments

- **Action:**
  1. Create a broker with active investments
  2. Try to archive the broker
- **Expected:**
  - Error message: "Cannot archive broker '[name]' because it has X active investment(s). Please archive all investments first."
  - Broker remains active
  - User must archive all investments before archiving the broker
- **Status:** [x] Pass ☐ Fail

#### Test 9.2.1: Archive Broker After Archiving Investments

- **Action:**
  1. Archive all investments linked to a broker
  2. Archive the broker
  3. Verify broker is in archived list
- **Expected:**
  - Broker archived successfully
  - Broker appears in "Archived Brokers" section
  - Archived broker not available for new investments
- **Status:** [x] Pass ☐ Fail

#### Test 9.2.2: Unarchive Broker

- **Action:**
  1. Archive a broker (with no active investments)
  2. Click "Unarchive" button on the archived broker
  3. Confirm unarchive action
- **Expected:**
  - Broker moved back to "Active Brokers" section
  - Success message displayed
  - Broker available for new investments again
- **Status:** [x] Pass ☐ Fail

#### Test 9.3: Filter Investments by Broker

- **Action:**
  1. Create investments across multiple brokers
  2. On investment list page, use the "Filter by Broker" dropdown
  3. Select a specific broker from the dropdown
  4. Verify only that broker's investments are shown
  5. Select "All Brokers" to show all investments again
- **Expected:**
  - Dropdown shows all active brokers
  - When a broker is selected, only investments from that broker are displayed
  - Summary stats update to reflect only the filtered investments
  - "Clear filter" link appears when a broker is selected
  - Investments correctly grouped by broker (even when filtered to one broker)
  - Filter works correctly with both active and archived investments
- **Status:** [x] Pass ☐ Fail

---

### 10. Security & Permissions

#### Test 10.1: User Isolation - Investments

- **Action:**
  1. Login as User A, create investment
  2. Logout, login as User B
  3. Try to access User A's investment URL directly
- **Expected:**
  - 404 or 403 error
  - User B cannot view User A's investment
- **Status:** ☐ Pass ☐ Fail

#### Test 10.2: User Isolation - Brokers

- **Action:**
  1. Login as User A, create broker
  2. Logout, login as User B
  3. Try to access User A's broker URL directly
- **Expected:**
  - 404 or 403 error
  - User B cannot view/edit User A's broker
- **Status:** ☐ Pass ☐ Fail

#### Test 10.3: User Isolation - Transactions

- **Action:**
  1. Login as User A, create transaction
  2. Logout, login as User B
  3. Try to edit/delete User A's transaction URL directly
- **Expected:**
  - 404 or 403 error
  - User B cannot modify User A's transaction
- **Status:** ☐ Pass ☐ Fail

#### Test 10.4: Unauthorized Access

- **Action:**
  1. Logout (not authenticated)
  2. Try to access investment list, broker list, etc.
- **Expected:**
  - Redirect to login page
  - Cannot access any investment pages
- **Status:** ☐ Pass ☐ Fail

---

### 11. Calculations & Portfolio Logic

#### Test 11.1: Current Value & Unrealized P&L

- **Action:**
  1. Edit Investment "Tata Motors"
  2. Update Current Price manually to ₹800
- **Expected:**
  - Current Value: ₹12,000 (15 qty \* ₹800)
  - Total Invested: ₹8,265 (15 qty \* ₹551 avg)
  - Unrealized P&L: +₹3,735
  - P&L Percentage calculated correctly
- **Status:** [x] Pass ☐ Fail

#### Test 11.2: Portfolio Summary (List View)

- **Action:** View Investment List
- **Expected:**
  - Total Invested: Sum of all investments
  - Total Current Value: Sum of all current values
  - Total P&L: Difference
- **Status:** [x] Pass ☐ Fail

#### Test 11.3: Buy → Sell All → Buy Again

- **Action:**
  1. Create investment with 10 units @ ₹100
  2. Sell all 10 units
  3. Buy 5 new units @ ₹150
- **Expected:**
  - After sell all: Holdings = 0, Invested = 0
  - After new buy: Holdings = 5, Avg Price = ₹150
  - Previous average price does NOT affect new calculation
- **Status:** [x] Pass ☐ Fail

#### Test 11.4: Multiple Sells to Zero

- **Action:**
  1. Create investment with 20 units
  2. Sell 10 units
  3. Sell 5 units
  4. Sell remaining 5 units
- **Expected:**
  - After each sell: Holdings decrease correctly
  - After final sell: Holdings = 0, Invested = 0
  - No negative values
- **Status:** [x] Pass ☐ Fail

#### Test 11.5: Fees Impact on Average Price

- **Action:**
  1. Buy 10 units @ ₹100 with ₹50 fees
  2. Verify average price calculation
- **Expected:**
  - Total Cost = (10 \* 100) + 50 = ₹1,050
  - Average Price = ₹1,050 / 10 = ₹105
  - Fees correctly included in cost basis
- **Status:** [x] Pass ☐ Fail

#### Test 11.6: Negative P&L Scenario

- **Action:**
  1. Buy 10 units @ ₹500
  2. Update current price to ₹300
- **Expected:**
  - Current Value: ₹3,000
  - Total Invested: ₹5,000
  - Unrealized P&L: -₹2,000 (negative, displayed in red)
  - P&L Percentage: -40%
- **Status:** [x] Pass ☐ Fail

#### Test 11.7: Proportional Cost Removal on Sell

- **Action:**
  1. Buy 10 units @ ₹100 (Total: ₹1,000)
  2. Buy 10 units @ ₹200 (Total: ₹2,000)
  3. Average = ₹150, Total Invested = ₹3,000
  4. Sell 10 units
- **Expected:**
  - Cost removed = 10 \* ₹150 = ₹1,500
  - Remaining: 10 units, ₹1,500 invested
  - Average remains ₹150
- **Status:** [x] Pass ☐ Fail

---

### 12. Dashboard Integration

#### Test 12.1: Net Worth Calculation

- **Action:** Check Dashboard Net Worth
- **Expected:**
  - Net Worth = Bank Balances + FD Maturity + **Investment Current Value**
  - Verify the math manually
- **Status:** [x] Pass ☐ Fail

#### Test 12.2: Total Accounts Card

- **Action:** Check "Total Accounts" card
- **Expected:**
  - Shows count of Investments (e.g., "1 Inv")
  - Correct pluralization
- **Status:** [x] Pass ☐ Fail

---

### 13. UI Features & Shortcuts

#### Test 13.1: Date Shortcut - Today

- **Action:**
  1. Open Add Investment form
  2. Click "Today" button for Purchase Date
- **Expected:**
  - Current date populated in field
  - Date matches system date
- **Status:** [x] Pass ☐ Fail

#### Test 13.2: Date Shortcut - Yesterday

- **Action:**
  1. Click "Yesterday" button for Purchase Date
- **Expected:**
  - Yesterday's date populated
  - Date = Today - 1 day
- **Status:** [x] Pass ☐ Fail

#### Test 13.3: Date Shortcut - Day Before Yesterday

- **Action:**
  1. Click "Day before yesterday" button
- **Expected:**
  - Date = Today - 2 days
- **Status:** [x] Pass ☐ Fail

#### Test 13.4: Pre-filled Symbol Field

- **Action:**
  1. Open investment detail
  2. Click "Add Transaction"
- **Expected:**
  - Symbol field pre-filled with investment symbol
  - Name and Broker also pre-filled
- **Status:** [x] Pass ☐ Fail

---

### 14. UI/UX & Edge Cases

#### Test 14.1: Empty States

- **Action:** View lists with no data
- **Expected:**
  - Broker List: "No brokers added"
  - Investment List: "No investments yet" -> "Add Broker" (if none) OR "Add Investment" (if broker exists)
- **Status:** [x] Pass ☐ Fail

#### Test 14.2: Dark Mode

- **Action:** Toggle Dark Mode
- **Expected:**
  - All investment pages styled correctly in dark mode
- **Status:** [x] Pass ☐ Fail

#### Test 14.3: Responsive Design

- **Action:** Check on mobile view
- **Expected:**
  - Tables scroll or stack
  - Cards display correctly
- **Status:** [x] Pass ☐ Fail

---

## Test Results Summary

| Category | Total Tests | Passed | Failed | Pending |\n| ----------------------- | ----------- | ------ | ------ | ------- |
| Navigation | 2 | 2 | 0 | 0 |
| Broker Mgmt | 4 | 4 | 0 | 0 |
| Investment Mgmt | 3 | 3 | 0 | 0 |
| Transactions (Buy/Sell) | 3 | 3 | 0 | 0 |
| Transaction Editing | 4 | 4 | 0 | 0 |
| Auto-Delete Investment | 2 | 2 | 0 | 0 |
| Form Validation | 5 | 5 | 0 | 0 |
| Investment Status | 5 | 5 | 0 | 0 |
| Broker-Investment Links | 5 | 5 | 0 | 0 |
| Security & Permissions | 4 | 0 | 0 | 4 |
| Calculations | 7 | 7 | 0 | 0 |
| Dashboard | 2 | 2 | 0 | 0 |
| UI Features & Shortcuts | 4 | 4 | 0 | 0 |
| UI/UX & Edge Cases | 3 | 3 | 0 | 0 |
| **TOTAL** | **53** | **49** | **0** | **4** |

---

## Issues Found

| Issue ID | Test Case | Severity | Description | Status |
| -------- | --------- | -------- | ----------- | ------ |
| INV-001  |           |          |             |        |

---

## Post-Testing Checklist

- [x] All critical flows verified (CRUD operations)
- [x] Transaction editing thoroughly tested
- [x] Auto-delete investment feature verified
- [x] Form validation edge cases tested
- [ ] Security & user isolation verified (Pending - documented in TODO.md)
- [x] Calculations verified against manual math
- [x] Dashboard numbers match investment totals
- [x] All date shortcuts working
- [x] Broker-investment relationships tested
- [x] Investment status management verified
- [ ] Ready for release (Pending security testing)

---

## Testing Priority

### Phase 1: Critical (Complete First)

- Security & Permissions (Tests 10.1-10.4)
- Transaction Editing (Tests 5.1-5.4)
- Auto-Delete Investment (Tests 6.1-6.2)
- Form Validation (Tests 7.1-7.5)

### Phase 2: High Priority

- Calculation Edge Cases (Tests 11.3-11.7)
- Investment Status Management (Tests 8.1-8.3)
- Broker-Investment Links (Tests 9.1-9.3)

### Phase 3: Medium Priority

- UI Features & Shortcuts (Tests 13.1-13.4)
- Additional edge cases and refinements
