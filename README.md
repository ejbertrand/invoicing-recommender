# invoicing-recommender

This is a full-stack Python developed web application.

It is built on top of Python (Flask + Jinja), using Javascript as API and HTML/CSS (Bootstrap) code.

The purpose of this project is to build an invoicing system, capable of registering transactions using different products/sub-products and payment types. Additionally, the invoice should be printable on PDF format as well as being able to send it directly to a printer. Finally, using the history and client behavior, the plan is for the system itself to recommend products based on previous client behavior as well as demographic data.

**Current State:**

It can register different payment types, product categories and sub-categories, registration of transactions and view the history of transactions.
The product category/subcategory hierarchy was done using Adjacency-Lists on a SQL database and Stored Procedures (not included here).

**The project is still under development and is expected to include:**

- Invoice generation and printing on PDF format and physical printers as well.
- Recommender module (based on Machine Learning algorithms)
- Authentication/authorization of modules based on role

**In the future:**

Several robustness and security tests are going to be executed, as well as refactoring of the code. In the meantine, the important thing is to have an MPV :).
