# invoicing-recommender

This is a full-stack Python developed web application.

It is built on top of Python (Flask + Jinja), using Javascript as API and HTML/CSS (Bootstrap) code.

The purpose of this project is to build an invoicing system, capable of registering transactions using different products/sub-products and payment types. Additionally, the invoice should be printable on PDF format as well as being able to send it directly to a printer. Finally, using the history and client behavior, the plan is for the system itself to recommend products based on previous client behavior as well as demographic data.

**---- RELEASE v1.0 ----**

**Home page:**
1. Restructure the form structure, buttons, and details table.
2. New Transaction: Create new session variables and show form
3. Cancel Transaction: Clean session variables and clean form.
4. Add Item: Update session and table
5. Delete Item: Update session and table
6. Close Transaction: Clean form and session, register the transaction into the DB.
7. Generate Invoice: Validate the information that was input, before generating the invoice (it's format)
8. Session: Maintain session data when the transaction is Active
9. Clean information on service/sub-service dropdowns once an item has been added to the details table.

**Services:**
1. Adequate home page to show services / sub-services in a dynamic form
2. Adequate the transactions page to show the services / sub-services of each transaction
3. Adequate the Services Configuration page to register new service/sub-services combination
4. Modal to confirm the deletion of a service/sub-service.

**Invoicing:**
1. Generate an invoice with all the details (the template is not uploaded for copyright reasons).
2. Show hour in the invoice, according to the timezone, and saving the same hour of the generation of the invoice into the database when the transaction is closed.

**Payments:**
Modal for deleting payment form

**Transaction History:**
Register the username that did the transaction

**Login:**
When logged in, if the login page is called, redirect to the home page.

**Database:**
Changed the database columns that store monetary data. Setting them to Numerical datatype (Decimal) and using two numbers after the decimal point.

**Best practices:**
1. Using config file to import into Flask
2. Several bugs were solved.
