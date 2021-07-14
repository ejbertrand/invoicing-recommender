# invoicing-recommender

This is a Full-Stack Python developed web application made on Flask. 

It is built on top of Python (Flask + Jinja), using Javascript as API and HTML/CSS (Bootstrap) code.

The purpose is to build a basic system for registering transactions and generating a printable invoice for them, on PDF format as well as being capable of sending it directly to a printer.

**Current State:**
It can register different payment types, product categories and sub-categories, registration of transactions and view the history of transactions.
The product category/subcategory hierarchy was done using Adjacency-Lists on a SQL database and Stored Procedures (not included here).

**The project is still under development and is expected to include:**
- Invoice generation and printing on PDF format and physical printers as well.
- Recommender module (based on Machine Learning algorithms)
- Authentication/authorization of modules based on role

**In the future:**
Several robustness and security tests are going to be executed, as well as refactoring of the code. In the meantine, the important thing is to have an MPV :).
