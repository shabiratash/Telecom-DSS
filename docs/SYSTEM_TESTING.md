# System Testing Documentation

**Project:** Afghanistan Telecom Churn Prediction and Retention System (ATCPRS)
**Date:** June 22, 2026
**Purpose:** Comprehensive test cases for system validation

---

## Test Case Summary

| Test Case ID | Module | Status |
|--------------|--------|--------|
| TC-001 | Authentication | Pending |
| TC-002 | Customer Management | Pending |
| TC-003 | Single Customer Churn Prediction | Pending |
| TC-004 | Batch Prediction | Pending |
| TC-005 | Retention Recommendation | Pending |
| TC-006 | AI Explainability | Pending |
| TC-007 | What-If Simulator | Pending |
| TC-008 | Customer Health Score | Pending |
| TC-009 | Early Warning System | Pending |
| TC-010 | Dashboard Analytics | Pending |
| TC-011 | Report Generation | Pending |
| TC-012 | Financial Impact Analysis | Pending |

---

## TC-001: Login

**Objective:** Verify that users can successfully log in to the system with valid credentials

**Preconditions:**
- Application is running on http://localhost:5000
- Database is populated with admin user
- MySQL server is running

**Test Steps:**
1. Open web browser and navigate to http://localhost:5000
2. Verify login page is displayed
3. Enter username: `admin`
4. Enter password: `admin123`
5. Click "Login" button
6. Verify successful login and redirect to dashboard

**Expected Result:**
- User is successfully authenticated
- Session is created
- User is redirected to dashboard page
- Dashboard displays with KPIs and charts

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-002: Customer Management

**Objective:** Verify CRUD operations for customer records

**Preconditions:**
- User is logged in as admin
- Database contains provinces data

**Test Steps:**
1. Navigate to "Customers" page from sidebar
2. Click "Add Customer" button
3. Fill in all required fields:
   - Age: 35
   - Gender: Male
   - Province: Kabul
   - Area Type: Urban
   - Network Quality: Good
   - Internet Type: 4G
   - Call Drop Rate: 2.5
   - Recharge Amount: 500
   - Recharge Frequency: 4
   - Payment Method: Cash
   - Tenure Months: 24
   - Inactive Days: 5
   - Complaint Count: 1
   - Tower Availability: High
   - Competitor Offer Exposure: No
   - Discount Usage: No
4. Click "Save" button
5. Verify customer is added to the list
6. Click "Edit" on the newly created customer
7. Modify Age to 36
8. Click "Update" button
9. Verify changes are saved
10. Click "Delete" button
11. Confirm deletion
12. Verify customer is removed from the list

**Expected Result:**
- Customer is successfully added to database
- Customer details are displayed in the list
- Customer can be edited and changes are saved
- Customer can be deleted and removed from database
- All operations complete without errors

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-003: Single Customer Churn Prediction

**Objective:** Verify single customer churn prediction functionality

**Preconditions:**
- User is logged in as admin
- ML model is trained and available
- Database contains customer data

**Test Steps:**
1. Navigate to "Prediction" page from sidebar
2. Fill in the 15-feature prediction form:
   - Age: 30
   - Gender: Female
   - Province: Herat
   - Area Type: Urban
   - Network Quality: Average
   - Internet Type: 3G
   - Call Drop Rate: 5.0
   - Recharge Amount: 300
   - Recharge Frequency: 2
   - Payment Method: Mobile Money
   - Tenure Months: 12
   - Inactive Days: 15
   - Complaint Count: 3
   - Tower Availability: Medium
   - Competitor Offer Exposure: Yes
   - Discount Usage: No
3. Click "Predict Churn" button
4. Verify prediction results are displayed
5. Check churn probability is between 0-100%
6. Verify risk level is displayed (Low/Medium/High/Critical)
7. Verify health score is displayed (0-100)
8. Verify health status is displayed (Critical/Warning/Good/Excellent)
9. Verify feature contributions are shown
10. Verify retention recommendations are provided

**Expected Result:**
- Prediction completes successfully
- Churn probability is calculated and displayed
- Risk level is correctly classified
- Health score is calculated and displayed
- Health status is correctly categorized
- Feature contributions are visualized
- 3-4 retention recommendations are provided
- No errors occur during prediction

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-004: Batch Prediction

**Objective:** Verify batch prediction from CSV upload functionality

**Preconditions:**
- User is logged in as admin
- ML model is trained and available
- CSV file with customer data is available

**Test Steps:**
1. Navigate to "Prediction" page from sidebar
2. Scroll to "Batch Prediction" section
3. Click "Upload CSV" button
4. Select a valid CSV file with customer data
5. Click "Predict" button
6. Verify batch prediction starts
7. Wait for prediction to complete
8. Verify results are displayed in a table
9. Verify each customer has churn probability
10. Verify each customer has risk level
11. Verify results can be downloaded

**Expected Result:**
- CSV file is uploaded successfully
- Batch prediction processes all records
- Results are displayed in a table
- Each customer has churn probability and risk level
- Results can be downloaded as CSV
- No errors occur during batch processing

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-005: Retention Recommendation

**Objective:** Verify retention recommendation generation

**Preconditions:**
- User is logged in as admin
- ML model is trained and available
- Prediction has been performed

**Test Steps:**
1. Navigate to "Prediction" page
2. Perform a churn prediction (TC-003)
3. Scroll to "Recommendations" section
4. Verify recommendations are displayed
5. Check for Support Interventions category
6. Check for Engagement Strategies category
7. Check for Discount Offers category
8. Check for Loyalty Programs category
9. Verify recommendations are relevant to risk factors
10. Verify recommendations are actionable

**Expected Result:**
- 3-4 recommendations are displayed
- Recommendations are categorized by type
- Recommendations are relevant to customer's risk factors
- Recommendations are specific and actionable
- No duplicate recommendations are shown
- Recommendations align with churn probability

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-006: AI Explainability

**Objective:** Verify AI explainability feature with feature contributions

**Preconditions:**
- User is logged in as admin
- ML model is trained and available
- Prediction has been performed

**Test Steps:**
1. Navigate to "Prediction" page
2. Perform a churn prediction (TC-003)
3. Scroll to "AI Explainability" section
4. Verify feature contributions are displayed
5. Check for progress bars showing feature impact
6. Verify feature contribution chart is rendered
7. Check chart is a doughnut/pie chart
8. Verify chart shows feature importance percentages
9. Hover over chart segments to see details
10. Verify contributions sum to 100%

**Expected Result:**
- Feature contributions are displayed
- Progress bars show positive/negative impact
- Feature contribution chart is rendered correctly
- Chart shows feature importance percentages
- Chart is interactive (hover details)
- Total contributions equal 100%
- Chart colors are distinct and readable
- No errors in chart rendering

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-007: What-If Simulator

**Objective:** Verify What-If Simulator functionality

**Preconditions:**
- User is logged in as admin
- ML model is trained and available
- Database contains customer data

**Test Steps:**
1. Navigate to "What-If Simulator" from sidebar
2. Select a customer from dropdown
3. Verify current customer state is displayed
4. Modify a feature value (e.g., increase recharge frequency)
5. Click "Simulate" button
6. Verify new prediction is displayed
7. Check for risk improvement/degradation
8. Verify impact breakdown cards are shown
9. Compare current vs simulated state
10. Reset to original values
11. Verify prediction returns to original

**Expected Result:**
- Customer selection loads customer data
- Current state is displayed correctly
- Feature modification is possible
- Simulation completes successfully
- New prediction is displayed
- Risk change is calculated and shown
- Impact breakdown cards are displayed
- Comparison between states is clear
- Reset functionality works correctly

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-008: Customer Health Score

**Objective:** Verify customer health score calculation and display

**Preconditions:**
- User is logged in as admin
- Database contains customer data

**Test Steps:**
1. Navigate to "Customers" page
2. Click on a customer to view profile
3. Verify health score badge is displayed
4. Check health score is between 0-100
5. Verify health status is displayed (Critical/Warning/Good/Excellent)
6. Verify badge color matches status:
   - Critical: Red
   - Warning: Orange
   - Good: Green
   - Excellent: Blue
7. Navigate to Dashboard
8. Check top risk customers table
9. Verify health column is displayed
10. Verify health badges are shown

**Expected Result:**
- Health score is calculated correctly
- Health score is between 0-100
- Health status is correctly categorized
- Badge color matches health status
- Health badge is displayed on customer profile
- Health badge is displayed on dashboard
- Health badge is displayed on prediction results
- Health score calculation is consistent across views

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-009: Early Warning System

**Objective:** Verify early warning system functionality

**Preconditions:**
- User is logged in as admin
- customer_risk_history table exists
- Risk history data is available

**Test Steps:**
1. Navigate to "Early Warning" from sidebar
2. Verify "Active Alerts" section is displayed
3. Check for customers with risk increase >20%
4. Verify alert level is shown (Critical/High/Medium)
5. Verify previous and current risk scores are displayed
6. Check "Recent Warnings" section
7. Verify recent warnings from risk history are shown
8. Check "Top Risk Customers" section
9. Verify top risk customers are listed
10. Verify risk trend data is displayed
11. Verify timestamps are shown correctly

**Expected Result:**
- Active alerts are displayed
- Alert levels are correctly classified
- Risk increase is calculated correctly
- Recent warnings are shown from history
- Top risk customers are listed
- Risk trend data is displayed
- Timestamps are in correct format
- No errors in data retrieval
- Alerts are sorted by risk increase

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-010: Dashboard Analytics

**Objective:** Verify dashboard analytics and visualizations

**Preconditions:**
- User is logged in as admin
- Database contains customer data

**Test Steps:**
1. Navigate to "Dashboard" page
2. Verify KPI cards are displayed:
   - Total Customers
   - Churned Customers
   - Active Customers
   - Average Recharge
   - Average Complaints
   - High Risk Customers
3. Verify KPI values are accurate
4. Check pie chart for churn distribution
5. Verify bar chart for province risk ranking
6. Check line chart for trends
7. Verify top risk customers table
8. Verify health column in table
9. Check chart interactivity (hover, tooltips)
10. Verify charts render without errors

**Expected Result:**
- All KPI cards are displayed
- KPI values are accurate and match database
- Pie chart shows churn distribution
- Bar chart shows province risk ranking
- Line chart shows trends
- Top risk customers table is populated
- Health badges are displayed
- Charts are interactive
- No rendering errors
- Charts are responsive to screen size

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-011: Report Generation

**Objective:** Verify report generation functionality

**Preconditions:**
- User is logged in as admin
- Database contains customer data

**Test Steps:**
1. Navigate to "Reports" from sidebar
2. Select "PDF Report" option
3. Configure report parameters:
   - Date range
   - Province filter
   - Churn status filter
4. Click "Generate Report" button
5. Verify PDF report is generated
6. Download and open PDF
7. Verify report contains:
   - Title
   - KPIs
   - Charts
   - Customer data
8. Select "Excel Report" option
9. Configure parameters
10. Click "Generate Report"
11. Verify Excel file is generated
12. Download and open Excel
13. Verify data is correctly formatted
14. Select "CSV Report" option
15. Generate and download CSV
16. Verify CSV format is correct

**Expected Result:**
- PDF report is generated successfully
- PDF contains all required sections
- PDF formatting is correct
- Excel report is generated successfully
- Excel data is correctly formatted
- CSV report is generated successfully
- CSV format is valid
- All report types can be downloaded
- No errors during generation
- File sizes are reasonable

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## TC-012: Financial Impact Analysis

**Objective:** Verify financial impact analysis functionality

**Preconditions:**
- User is logged in as admin
- Database contains customer data
- ML model is trained

**Test Steps:**
1. Navigate to "Financial Impact" from sidebar
2. Verify KPI cards are displayed:
   - High Risk Customers
   - Avg Revenue/Customer
   - Monthly Revenue Risk
   - Yearly Revenue Risk
3. Verify KPI values are calculated correctly
4. Check province revenue risk table
5. Verify table columns:
   - Province
   - Total Customers
   - Active Customers
   - Churned Customers
   - Churn Rate
   - Avg Revenue
   - Yearly Risk
6. Verify revenue risk distribution chart
7. Check chart is a doughnut chart
8. Verify chart shows top 10 provinces
9. Verify chart colors are distinct
10. Verify chart is interactive

**Expected Result:**
- KPI cards are displayed
- KPI values are calculated correctly
- Province table is populated
- Table columns are correct
- Churn rate is color-coded
- Revenue risk is highlighted
- Chart is rendered correctly
- Chart shows top 10 provinces
- Chart is interactive
- No errors in data retrieval
- Financial calculations are accurate

**Actual Result:** [To be filled during testing]

**Status:** [PASS/FAIL]

---

## Test Execution Summary

### Test Statistics

| Metric | Count |
|--------|-------|
| Total Test Cases | 12 |
| Passed | 0 |
| Failed | 0 |
| Pending | 12 |
| Pass Rate | 0% |

### Module Coverage

| Module | Test Cases | Coverage |
|--------|------------|----------|
| Authentication | 1 | 100% |
| Customer Management | 1 | 100% |
| Prediction | 2 | 100% |
| ML Center | 0 | 0% |
| Analytics | 1 | 100% |
| Early Warning | 1 | 100% |
| Financial Impact | 1 | 100% |
| Reports | 1 | 100% |
| What-If Simulator | 1 | 100% |
| Health Score | 1 | 100% |
| AI Explainability | 1 | 100% |
| Retention Engine | 1 | 100% |

### Known Issues

*No known issues at this time.*

### Test Environment

- **Operating System:** Windows 10/11
- **Python Version:** 3.10+
- **MySQL Version:** 5.7+
- **Browser:** Chrome/Firefox/Edge
- **Test Date:** [To be filled]

---

## Test Execution Instructions

### Pre-Test Setup

1. Ensure MySQL server is running
2. Create database using `sql/schema.sql`
3. Seed provinces using `sql/seed_provinces.sql`
4. Generate dataset using `python generate_dataset.py`
5. Seed database using `python seed_db.py`
6. Train model using `python -m ml.train`
7. Add risk history table using `sql/add_customer_risk_history.sql`
8. Start application using `python app.py`

### Test Execution

1. Execute test cases in order (TC-001 to TC-012)
2. Fill in "Actual Result" for each test case
3. Mark "Status" as PASS or FAIL
4. Document any deviations from expected results
5. Capture screenshots for failed tests
6. Log any errors or exceptions encountered

### Post-Test Cleanup

1. Stop application
2. Review test results
3. Document any bugs found
4. Create bug reports for failed tests
5. Update test documentation as needed

---

## Test Sign-Off

**Tester Name:** ______________________

**Test Date:** ______________________

**Test Environment:** ______________________

**Overall Result:** ______________________

**Comments:** ______________________

**Approver:** ______________________

**Approval Date:** ______________________
