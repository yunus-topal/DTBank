from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.http import HttpResponse
from . import urls
import hashlib


def SHA256(ss):
    return hashlib.sha256(ss.encode('utf-8')).hexdigest()


def loggedas(request, ss):
    return "usertype" in request.session and request.session["usertype"] == ss

# Create your views here.


def loginpage(request):

    if request.method == "POST" and "flush" in request.POST:
        request.session.flush()
        return render(request, "main/login.html")
    elif request.method == "POST":
        cursor = urls.conn.cursor()
        if request.POST["usertype"] == "user":
            tablename = 'User'
        elif request.POST["usertype"] == "dbmanager":
            tablename = "Database_Manager"
        else:
            request.session["errormsg"] = "undefined user type!"
            return errorpage(request)

        hashed_password = SHA256(request.POST["password"])
        cursor.execute('SELECT * FROM [%s] where username=? and password=? ;' %
                       tablename, request.POST["username"], hashed_password)

        res = list(cursor.fetchall())
        cursor.close()
        if len(res) == 0:
            request.session["errormsg"] = "there is no user with the username of %s and the password of %s!" % (
                request.POST["username"], hashed_password)
            return errorpage(request)

        request.session["username"] = request.POST["username"]
        request.session["password"] = hashed_password
        request.session["usertype"] = request.POST["usertype"]

        if request.POST["usertype"] == "user":
            request.session["institute"] = res[0][2]
            return userpage(request)
        elif request.POST["usertype"] == "dbmanager":
            return dbmanagerpage(request)

    if request.method == "GET":
        return render(request, "main/login.html")

    request.session["errormsg"] = "unknown request type!"
    return errorpage(request)


def errorpage(request):
    if "errormsg" in request.session:
        return render(request, "main/error.html", {"errormsg": request.session["errormsg"]})
    else:
        return render(request, "main/error.html", {"errormsg": "there was no error message"})


def userpage(request):
    if loggedas(request, "user"):
        return render(request, "main/userpage.html",
                      {"username": request.session["username"],
                       "password": request.session["password"],
                       "institute": request.session["institute"]})
    else:
        request.session["errormsg"] = "not a user!"
        return errorpage(request)


def GetAll(a):
    cursor = urls.conn.cursor()
    cursor.execute(a)
    res = list(cursor.fetchall())
    cursor.close()
    return res


def dbmanagerpage(request):
    if loggedas(request, "dbmanager"):
        def getdict():
            return {
                "username": request.session["username"],
                "password": request.session["password"],
                "dbmanagertable": GetAll('SELECT * FROM [%s]' % "Database_Manager"),
                "drugbanktable": GetAll('SELECT * FROM [%s]' % "DrugBank"),
                "usertable": GetAll('SELECT * FROM [%s]' % "User"),
                "bindingdbtable": GetAll("""

Select reaction_id, measure, "affinity", target_prot_name, smiles, drugbank_id, uniprot_id, doi,
STRING_AGG(u.username, ';') as usernames, STRING_AGG(u.institute, ';') as institutions, STRING_AGG(u.author_name, ';') as authors
from 

(Select a.*, b.username, b.inst_name from 
(SELECT reaction_id, measure, "affinity", target_prot_name, smiles, drugbank_id, uniprot_id, doi FROM [BindingDB]) as a
inner join 
AuthorList as b
on a.doi = b.doi) as c
inner join
"User" as u
on u.username = c.username and u.institute = c.inst_name

group by reaction_id, measure, "affinity", target_prot_name, smiles, drugbank_id, uniprot_id, doi

                    """),
                "uniprottable": GetAll('SELECT * FROM [%s]' % "UniProt"),
                "authorlisttable": GetAll('SELECT * FROM [%s] order by doi desc' % "AuthorList"),
                "instscores": GetAll('SELECT * FROM calculate_contrib_score() order by puan_total DESC;'),
                "sidertable": GetAll('SELECT * FROM [%s]' % "SIDER")
            }

        msg = ""

        if request.method == "POST" and "type" in request.POST and request.POST["type"] == "adduser":

            try:
                cursor = urls.conn.cursor()
                cursor.execute('INSERT INTO "User" VALUES(?,?,?,?);',
                               request.POST["username"],
                               SHA256(request.POST["password"]),
                               request.POST["institute"],
                               request.POST["author_name"])
                cursor.commit()
                msg = "Added User!"
            except:
                msg = "Not added! Error Occured!"
            finally:
                cursor.close()

        elif request.method == "POST" and "type" in request.POST and request.POST["type"] == "deletedrug":
            try:
                cursor = urls.conn.cursor()
                cursor.execute('DELETE FROM "DrugBank" where drugbank_id = ?;',
                               request.POST["drugbank_id"])
                cursor.commit()
                #deletedrows = cursor.rowcount
                #print("------------>", cursor.rowcount)
                # if deletedrows == 0:
                #    msg = "No drug is deleted!"
                # else:
                msg = "Deleted Drug!"
            except:
                msg = "Can't Delete! Error Occured!"
            finally:
                cursor.close()

        elif request.method == "POST" and "type" in request.POST and request.POST["type"] == "affinityupdate":
            try:
                cursor = urls.conn.cursor()
                cursor.execute('UPDATE BindingDB set affinity = ? where reaction_id = ?;',
                               request.POST["affinity"],
                               request.POST["reaction_id"])

                cursor.commit()
                deletedrows = cursor.rowcount

                if deletedrows == 0:
                    msg = "No affinity of a drug is changed!"
                else:
                    msg = "Set Affinity!"
            except:
                msg = "Can't set Affinity! Error Occured!"
            finally:
                cursor.close()

        elif request.method == "POST" and "type" in request.POST and request.POST["type"] == "deleteuniprot":
            try:
                cursor = urls.conn.cursor()
                cursor.execute('DELETE FROM "UniProt" where uniprot_id = ?;',
                               request.POST["uniprot_id"])

                cursor.commit()
                deletedrows = cursor.rowcount

                msg = "Deleted UniProt!"
            except:
                msg = "Can't delete UniProt! Error Occured!"
            finally:
                cursor.close()

        elif request.method == "POST" and "type" in request.POST and request.POST["type"] == "addcontrib":
            try:
                cursor = urls.conn.cursor()
                cursor.execute('INSERT INTO "AuthorList" VALUES(?,?,?);',
                               request.POST["doi"],
                               request.POST["username"],
                               request.POST["inst_name"]
                               )

                cursor.commit()
                rows = cursor.rowcount

                if rows == 0:
                    msg = "Can't add the contributor!"
                else:
                    msg = "Added contributor!"
            except:
                msg = "Can't add the contributor! Error Occured!"
            finally:
                cursor.close()
        elif request.method == "POST" and "type" in request.POST and request.POST["type"] == "deletecontrib":
            try:
                cursor = urls.conn.cursor()
                cursor.execute('DELETE FROM "AuthorList" where doi=? and username = ? and inst_name = ?;',
                               request.POST["doi"],
                               request.POST["username"],
                               request.POST["inst_name"]
                               )

                cursor.commit()

                msg = "Deleted contributor!"
            except:
                msg = "Can't delete the contributor! Error Occured!"
            finally:
                cursor.close()

        dict = getdict()
        dict["TextMessage"] = msg
        return render(request, "main/dbmanagerpage.html", dict)

    request.session["errormsg"] = "not a db manager!"
    return errorpage(request)


# user functionalities:


def Convert(a):
    return a


def basicQuestions(request):
    if loggedas(request, "user") and "basicq" in request.GET:

        if request.GET["basicq"] == "separate":  # 1
            cursor = urls.conn.cursor()
            cursor.execute('EXEC separate')
            drugList = list(cursor.fetchall())

            return render(request, "main/basicAnswers.html", {"drugs": drugList})
        elif request.GET["basicq"] == "doi":
            cursor = urls.conn.cursor()
            cursor.execute(""" 
            SELECT al.doi,  STRING_AGG(u.author_name,' - ') AS "authors" FROM AuthorList as al 
            INNER JOIN "User" as u
            on u.username = al.username group by doi
            """)
            drugList = list(cursor.fetchall())
            return render(request, "main/basicAnswers.html", {"drugs": drugList})
        elif request.GET["basicq"] == "points":
            cursor = urls.conn.cursor()
            cursor.execute(
                'SELECT * FROM calculate_contrib_score() order by puan_total DESC;')
            drugList = list(cursor.fetchall())
            return render(request, "main/basicAnswers.html", {"drugs": drugList})

    else:
        request.session["errormsg"] = "not a user!"
        return errorpage(request)


def specificQuestions(request):
    if loggedas(request, "user") and "specificq" in request.GET:

        if request.GET["specificq"] == "interaction":
            cursor = urls.conn.cursor()
            cursor.execute(
                """SELECT drugbank_id, drug_name FROM 
(SELECT interaction FROM DrugBank WHERE drugbank_id=?) as i
INNER JOIN DrugBank as d
on i.interaction LIKE '%' + d.drugbank_id + '%'
;""", request.GET["drug_interact"])
            drugList = list(cursor.fetchall())

            if len(drugList) == 0:
                return render(request, "main/basicAnswers.html", {"drugs": ["there is no such drug!"]})
            return render(request, "main/basicAnswers.html", {"drugs": drugList})

        elif request.GET["specificq"] == "side_effect":
            cursor = urls.conn.cursor()
            cursor.execute(
                'SELECT umls_cui, side_effect_name FROM SIDER WHERE drugbank_id=?;', request.GET["drug_effect"])
            drugList = list(cursor.fetchall())
            drugList = Convert(drugList)

            if len(drugList) == 0:
                return render(request, "main/basicAnswers.html", {"drugs": ["there is no such drug!"]})
            return render(request, "main/basicAnswers.html", {"drugs": drugList})

        elif request.GET["specificq"] == "target_name":
            cursor = urls.conn.cursor()
            cursor.execute(
                'SELECT uniprot_id, target_prot_name FROM BindingDB WHERE drugbank_id=?;', request.GET["drug_target"])
            drugList = list(cursor.fetchall())
            drugList = Convert(drugList)

            if len(drugList) == 0:
                return render(request, "main/basicAnswers.html", {"drugs": ["there is no such drug!"]})
            return render(request, "main/basicAnswers.html", {"drugs": drugList})

        elif request.GET["specificq"] == "drug_ids":
            cursor = urls.conn.cursor()
            cursor.execute(
                """SELECT d.drugbank_id, d.drug_name FROM DrugBank as d
INNER JOIN 
(SELECT drugbank_id FROM BindingDB WHERE uniprot_id=?) as s
on d.drugbank_id = s.drugbank_id;""", request.GET["prot_drug"])
            drugList = list(cursor.fetchall())
            drugList = Convert(drugList)

            if len(drugList) == 0:
                return render(request, "main/basicAnswers.html", {"drugs": ["there is no such protein!"]})
            return render(request, "main/basicAnswers.html", {"drugs": drugList})

        elif request.GET["specificq"] == "side_effect_2":
            cursor = urls.conn.cursor()
            cursor.execute(
                """SELECT d.drugbank_id, d.drug_name FROM DrugBank as d
INNER JOIN
(SELECT drugbank_id FROM SIDER WHERE umls_cui =?) AS s
on s.drugbank_id = d.drugbank_id;""", request.GET["drug_effect_2"])
            drugList = list(cursor.fetchall())
            drugList = Convert(drugList)

            if len(drugList) == 0:
                return render(request, "main/basicAnswers.html", {"drugs": ["there is no side effect!"]})
            return render(request, "main/basicAnswers.html", {"drugs": drugList})

        elif request.GET["specificq"] == "keyword_search":
            cursor = urls.conn.cursor()
            cursor.execute(
                'SELECT drugbank_id, description FROM DrugBank WHERE description LIKE \'%' + request.GET["drug_keyword"]+'%\';')
            drugList = list(cursor.fetchall())
            drugList = Convert(drugList)

            if len(drugList) == 0:
                return render(request, "main/basicAnswers.html", {"drugs": ["there is no drug with that description!"]})
            return render(request, "main/basicAnswers.html", {"drugs": drugList})

        elif request.GET["specificq"] == "drug_last_v":
            cursor = urls.conn.cursor()
            cursor.execute('EXEC leastSideEffects @protein=?;',
                           request.GET["drug_last"])
            drugList = list(cursor.fetchall())
            drugList = Convert(drugList)

            if len(drugList) == 0:
                return render(request, "main/basicAnswers.html", {"drugs": ["there is no such protein!"]})
            return render(request, "main/basicAnswers.html", {"drugs": drugList})

        elif request.GET["specificq"] == "stored_v":
            cursor = urls.conn.cursor()
            cursor.execute('EXEC filter @type =?, @minvalue =?, @maxvalue = ?;',
                           request.GET["stored_1"], request.GET["stored_2"], request.GET["stored_3"])
            drugList = list(cursor.fetchall())

            result_list = ""
            drug_id = request.GET["stored_4"]
            for item in drugList:
                if item[0] == drug_id:
                    result_list = item
                    break

            if len(result_list) == 0:
                return render(request, "main/basicAnswers.html", {"drugs": ["there is no such drug with those affinity values!"]})

            return render(request, "main/basicAnswers.html", {"drugs": result_list})

    else:
        request.session["errormsg"] = "not a user!"
        return errorpage(request)


def matchingQuestions(request):
    if loggedas(request, "user") and "matchingq" in request.GET:

        if request.GET["matchingq"] == "side_effect_3":
            cursor = urls.conn.cursor()
            cursor.execute(""" 
            SELECT  x.uniprot_id, STRING_AGG(x.drugbank_id,',') as drug_ids FROM
(SELECT drugbank_id, uniprot_id FROM BindingDB group by drugbank_id, uniprot_id) as x group by x.uniprot_id HAVING COUNT(x.uniprot_id) >=1

UNION 

(SELECT uniprot_id, '' as drug_ids FROM UniProt where (
Select COunt(drugbank_id) from BindingDB where BindingDB.uniprot_id = UniProt.uniprot_id
) = 0
)

            """)
            drugList = list(cursor.fetchall())
            return render(request, "main/basicAnswers.html", {"drugs": drugList})

        elif request.GET["matchingq"] == "side_effect_4":
            cursor = urls.conn.cursor()
            cursor.execute("""
            SELECT  x.drugbank_id, STRING_AGG(x.uniprot_id,',') as proteins FROM
(SELECT drugbank_id, uniprot_id FROM BindingDB group by drugbank_id, uniprot_id) as x group by x.drugbank_id HAVING COUNT(x.drugbank_id) >=1

UNION 

(SELECT drugbank_id, '' as proteins FROM DrugBank where (
Select COunt(uniprot_id) from BindingDB where BindingDB.drugbank_id = DrugBank.drugbank_id
) = 0
)
                 """)
            drugList = list(cursor.fetchall())
            return render(request, "main/basicAnswers.html", {"drugs": drugList})
    else:
        request.session["errormsg"] = "not a user!"
        return errorpage(request)
