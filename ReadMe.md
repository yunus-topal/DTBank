# DISCLAIMER

I used Microsoft SQL Server for this project and because of that, this project will not work on your computer. You need to change pyodbc.connect() parameters inside DTBank/main/urls.py with your database server parameters.

In order to build your database, you can use queries inside setups folder.

# CMPE 321 PROJECT 3 ReadME

This project is done by me and <a href="https://github.com/faruknane">Akif Faruk Nane</a> for our course CMPE 321.

Before you start, make sure that you are in the root directory (if you can seee manage.py then you are in the root directory.).
To start server, type "python manage.py runserver" to your cli. You will see couple lines flowing on your terminal.
You should see this line: "Starting development server at http://127.0.0.1:8000/" You can hold Ctrl and click this url
or just type it to your browser yourself. you will see a login page.

## Login Page

In order to log in, you need to type your username, password and you need to select your user type and click Login button.
You might notice there is another button, which is Flush Session. You can use it to log out.

## User Page

If you see a line like "Welcome user username/password/institue!" on top of the page then congrats, you succesfully logged in as a user.

After greeting line, you will notice 3 buttons next to each other.

- First one is Separately view, which will show you drugbank id, name, smiles, descriptions, target names and side effects of all drugs.
- Middle one is DOI's and contributors. That one will show you papers and their contributor authors.
- Last one is calculate points! That button will show you points of each Institute.

Below these, you will see a line like "Maybe something more specific?" and 8 specific question.

- First one will show you interacting drugs of a drug. You need to provide a drugbank id.
- Second one will show you all side effects of a drug. You need to provide a drugbank id.
- Third one wll show you interacting targets of a drug. You need to provide a drugbank id.
- Fourth one will show you interacting drugs of a protein. You need to provide a uniprot id.
- Fifth one will show you all drugs that have a specific side effect. You need to provide a umls_cui.
- Sixth one will show you all drugs that have your keyword in their description. You need to provide a keyword.
- Seventh one will show you drug(s) with the least amount of side effects that interact with a specific protein. You need to provide a uniprot id.
- The last one will filter proteins according to your minimum and maximum ranges.
  If you provide an invalid input, you will get an error message about it.

At the bottom, you will see this line:"Maybe matching drugs or protein?" and 2 buttons.

- First button will show you each protein, and every drug that have an effect on those proteins.
- Second button will show you each drugbank id with uniprot ids that bind those drugs.

# DBManager Page

If you see a line like "Welcome db manager username/password!" on top of the page then congrats, you succesfully logged in as a db manager.

After greeting line, you will see couple lists that has information about database.

- In Database managers list, you can see information about every manager that registered to system.
- In User list, you can see information about every user in the system and you can add new users to the system with the form below this list.
- In Drug Bank list, you can see information about every drug in the system and you can delete drugs with the form below.
- In the BindingDB list, you can see information about every reaction in the system and you can update affinity values of reactions with the form below.
- In the UniProt list, you can see information about every protein and you can delete a protein with the form below.
- In the Institution Scores list, you can see scores of every institution.
- In the Contributors list, you can see contributors of every paper and you can add or remove contributors with the forms below.
- In the SIDER list, you can see information about every side effect in the system.
