#!c:/Python27/python
# -*- coding:Utf-8 -*-

import cgi
import cgitb; cgitb.enable()
import MySQLdb
import sys, os
import session, time
import re
import sys, os
sys.path.append(os.environ['DOCUMENT_ROOT'])
import session, time
from random import randint
import sha, time, Cookie, os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import hashlib


cookie = Cookie.SimpleCookie()
string_cookie = os.environ.get('HTTP_COOKIE')
#cookie.load(string_cookie)
#sid = cookie['sid'].value
db = MySQLdb.connect("127.0.0.1", "root", "", "utilisateurs")
form = cgi.FieldStorage() 
titre1="Page de Connexion"
erreur = ""
patternNom = "^[a-zA-Z\\'-]+$"
patternMail = "^[a-z0-9._-]+@[a-z0-9._-]{2,}\.[a-z]{2,4}$"
patternMdp = "^[a-zA-Z0-9]{4,}$"
sess = session.Session(expires=0*0*0*10, cookie_path='/')
msg = MIMEMultipart()
hash_mdp = ""



def printHead():
    print "Content-Type: text/html\n"
    print "<head>"
    print '<meta charset="UTF-8">'
    print '<link rel="stylesheet" type="text/css" href="connexion.css"/>'
    print ("<TITLE>Gestion des utilisateurs</TITLE>")
    print "</head>"
    #print (form)
    
    
	
    
		
def test_donnees_formulaire():
	global sess
	global erreur
	if (len(form) == 0 or form.has_key("deconnexion") or len(sess.data)<0 or form.has_key("retour_connexion")):
		sess.data["statut"] = "deconnecte"
		printConnexion()
	elif (form.has_key("inscription")):
		print_inscription()
	elif (form.has_key("mdp_oublier")):
		mdp_oublier()
	elif (form.has_key("email_oublier")):
		verif_email_oublier(form.getvalue("email_oublier"))
	elif (form.has_key("retour_admin") or form.has_key("retour_utilisateur")):
		if(form.has_key("retour_admin")):
			printAdmin()
		else:
			print_utilisateur()	
	elif (form.has_key("email_connexion") and form.has_key("mdp_connexion")):
		email = form.getvalue("email_connexion")
		mdp = form.getvalue("mdp_connexion")
		m = hashlib.md5()
		m.update(mdp)
		cursor = db.cursor()
		cursor.execute("SELECT * FROM utilisateur4 WHERE email= '"+email+"' AND mdp ='"+m.hexdigest()+"'")
		rows = cursor.fetchall()
		if rows:
			for  row in rows:
				sess.data["statut"] = "connecte"
				sess.data["donnees_utilisateur"] = row[0:6]
				if row[5] == 1:
					printAdmin()
				else:
					print_utilisateur()
		else:
			printConnexion()
			erreur = "<div id= incorrect>email ou mot de passe incorrect !</div>"
	elif (form.has_key("connexion") and not form.has_key("ajouter")):
		printConnexion()
		erreur = "<div id= incorrect>tous les champs doivent être renseignés !</div>"
	elif (form.has_key("nom_ajout") and form.has_key("prenom_ajout") and form.has_key("email_ajout")):
		verification_formulaire_ajout()
	elif (form.has_key("enregistrer")):
		if(form.has_key("nom_inscription") and form.has_key("prenom_inscription") and form.has_key("email_inscription") and form.has_key("mdp_inscription")):
			verification_formulaire_inscription()
		else:
			print_inscription()
			erreur = "<div id= incorrect>tous les champs doivent être renseignés</div>"
	elif (form.has_key("email_amodifier") or form.has_key("mdp_amodifier")):
		modification_donnes()
	elif (form.has_key("nouvel_email") or form.has_key("nouvel_mdp")):
		editUser()
	elif (form.has_key("nouvel_email_admin") or form.has_key("nouvel_mdp_admin") or form.has_key("modifier_email_admin") or form.has_key("modifier_mdp_admin")):
		editUser_admin()
	elif (form.has_key("modifier_mdp") or form.has_key("modifier_email")):
		modification_donnes()
		erreur = "<div id= incorrect>tous les champs doivent être renseignés</div>"
	elif (form.has_key("email_amodifier_admin") or form.has_key("mdp_amodifier_admin")):
		modification_donnes_admin()
	elif (form.has_key("action")):
		if(form.getvalue("action") == "supprimer"):
			verif_suppression()
		elif(form.getvalue("action") == "modifier"):
			verif_modification()
	elif (form.has_key("passer_admin")):
		passage_admin()
	elif (form.has_key("choix_suppression")):
		if(form.getvalue("choix_suppression") == "oui"):
			suppression_utilisateur()
		else:
			printAdmin()
			erreur="<div id=incorrect> Suppression annulée</div>"
	else:
		printAdmin()
		erreur = "<div id= incorrect>Tous les champs doivent être renseignés</div>"
def envoyerEmail(email, action,mdp):
	global erreur
	
	message =""
	msg = MIMEMultipart()
	msg['From'] = 'thomasecalle@hotmail.fr'
	msg['To'] = email
	if (action == "inscription"):
		msg['Subject'] = 'Inscription M2L'
		message = "bonjour, merci de votre inscription, votre mot de passe est  : \n "+mdp
	elif ( action == "ajout"):
		msg['Subject'] = 'Bienvenue chez la M2L'
		message = "vous avez ete inscrit au portail utilisateur de la M2L. Voici votre mot de passe : "+mdp+ "   \n vous pourrez changer votre mot de passe en vous connectant !"
	elif (action == "email_oublier"):
		msg['Subject'] = 'Nouveau mot de passe'
		message = "Voici votre nouveau mot de passe, vous pourrez le changer en vous connectant ! \n "+mdp
	msg.attach(MIMEText(message))
	mailserver = smtplib.SMTP('smtp.live.com', 25)
	mailserver.ehlo()
	mailserver.starttls()
	mailserver.login('thomasecalle@hotmail.fr', 'aurumpotestasest')
	mailserver.sendmail(msg["From"], msg["To"], msg.as_string())
	mailserver.quit()
	
	
	
	
		
def printConnexion():
		sess.data.clear()
		valeur_mail = ""
		if (form.has_key("email_connexion")):
			valeur_mail = form.getvalue("email_connexion")
		print "<h1>Page de Connexion</h1>"
		print "<div id=Menu>"
		print "<table id=connexion>"
		print '<form action="test_new.py" method="post">' \
						+ '<tr><td><div id= email>Email : <td><input id=caseE type="email" name="email_connexion" placeholder="Adresse Email" value="'+valeur_mail+'"/></div></tr><BR>' \
						+ '<tr><td><div id= mdp>Mot de Passe : <td><input id=caseP type="password" name="mdp_connexion" placeholder="Mot de Passe" /></div></tr><BR>' \
						+  '<tr><td><input id=boutonC type="submit" value="Se connecter" name="connexion" /></td><td><input id=boutonI type="submit" value="S\'inscrire" name="inscription"></td><td><input id=boutonI type="submit" value="Mot de passe oublié" name="mdp_oublier"></td></form></tr><a  href="aide.html" target="_blank">Aide</a>'
		print "</table>"
def mdp_oublier():
	print "<h1>Mot de passe oublié ?</h1>"
	print "<div id=menu>"
	print "<table id=MotDePasseOublie>"
	print "<form method='post'>"
	print "<tr><td><label for='email_oublier'> Veuillez indiquer votre adresse email</label></td><td><input id=caseE type='email' name='email_oublier' placeholder='Adresse Email' id='email_oublier'></td></tr><tr><td><input id=boutonI type='submit' value='valider'></td><td><input id= BoutonReMotDe type='submit' value='retour' name='retour_connexion'></td></tr>"
	print "</form>"
	print "<tr><td><p> Un nouveau mot de passe vous sera envoyer </p></td></tr></table>"
	print "</div>"

def verif_email_oublier(email):
	global erreur
	
	if (re.match(patternMail,email)):
		cursor = db.cursor()
		cursor.execute("SELECT * FROM utilisateur4 WHERE email='"+email+"'")
		rows = cursor.fetchall()
		if (rows):
			mdp_provisoire = randint(1000,1000000)
			mdp_hash = hashlib.md5()
			mdp_hash.update(str(mdp_provisoire))
			cursor.execute ("UPDATE utilisateur4 set mdp='"+str(mdp_hash.hexdigest())+"' WHERE email='"+email+"'")
			db.commit()
			envoyerEmail(email,"email_oublier",str(mdp_provisoire))
			erreur = "<div id=incorrect>Vous avez recu un email contenant votre nouveau mot de passe</div>"
			printConnexion()
		else:
			erreur = "<div id=incorrect>Adresse Mail non valide</div>"
			mdp_oublier()
					
		
def printAdmin():
	print "<h1>Bienvenue sur votre espace administrateur "+ sess.data["donnees_utilisateur"][2]+"</h1>"
	print_formulaire_admin()
	print_bdd()
	
	
	
def print_inscription():
	
	valeur_nom = ""
	valeur_prenom = ""
	valeur_mail = ""
	valeur_mdp =""
	if (form.has_key("nom_inscription")):
		valeur_nom = form.getvalue("nom_inscription")
	if (form.has_key("prenom_inscription")):
		valeur_prenom = form.getvalue("prenom_inscription")
	if (form.has_key("email_inscription")):
		valeur_mail = form.getvalue("email_inscription")
	
		
	print "<h2> Inscription</h2>"
	print "<div id=Menu>"
	print "<table>"
	print '<form action="test_new.py" method="post">' \
				+ '<tr><td>Nom : <td><input id=caseE type="text" name="nom_inscription" placeholder="Mon nom" value="'+str(valeur_nom)+'"/><BR></tr>' \
				+ '<tr><td>Prénom : <td><input id=caseE type="text" name="prenom_inscription" placeholder="Mon prenom" value="'+str(valeur_prenom)+'"/><BR></tr>' \
				+ '<tr><td>Email : <td><input id=caseE type="email" name="email_inscription" placeholder="Mon email" value="'+str(valeur_mail)+'"/><BR></tr>' \
				+ '<tr><td>Mot de passe : <td><input id=caseE type="password" name="mdp_inscription" placeholder="Mon mot de passe"/><BR></tr>' \
				+  '<td><input id= BoutonEn type="submit" value="enregistrer" name="enregistrer"/></form>'
	print "<td><form method='post' ><input id= BoutonRe type='submit' value='retour' name='retour_connexion'></form>"
	print "</table>"
	
def print_formulaire_admin():
	valeur_nom = ""
	valeur_prenom = ""
	valeur_mail = ""
	if (form.has_key("nom_ajout")):
		valeur_nom = form.getvalue("nom_ajout")
	if (form.has_key("prenom_ajout")):
		valeur_prenom = form.getvalue("prenom_ajout")
	if (form.has_key("email_ajout")):
		valeur_mail = form.getvalue("email_ajout")
	print "<div id=Menu>"
	print "<h3> Ajouter un utilisateur </h3>"
	print "<table id=AjoutUtiAdmin>"
	print '<form action="test_new.py" method="post">' \
				+ '<tr><td>Nom : <td><input id=caseE type="text" name="nom_ajout" placeholder="Nom Utilisateur" value="'+str(valeur_nom)+'"/><BR></td></tr>' \
				+ '<tr><td>Prénom : <td><input id=caseE type="text" name="prenom_ajout" placeholder="Prenom Utilisateur" value="'+str(valeur_prenom)+'"/><BR><td><input id= BoutonAjout type="submit" value="Ajouter" name="ajouter" /></td></tr>' \
				+ '<tr><td>Email : <td><input id=caseE type="email" name="email_ajout" placeholder="Email Utilisateur" value="'+str(valeur_mail)+'"/><BR></td><td><form method ="post" action="test_new.py"><input id=deconnexionAjoutUti type="submit" value="deconnexion" name="deconnexion"></form></td></tr>' \
				+ '</form>'
	print "<td>"
	print "</table>"
				
def print_bdd():
	print "<h5> Liste des utilisateurs </h5>"
	cursor = db.cursor()
	cursor.execute ("SELECT * FROM utilisateur4 WHERE not (admin=1)")
	rows = cursor.fetchall()
	print "<form method='get' action='test_new.py'>"
	print "<table id=Liste><thead><tr><th>Nom</th><th>Prénom</th><th>Email</th></tr></thead>"
	print "<tbody>"
	for row in rows:
		print "<tr><td>"+row[1]+"</td><td>"+row[2]+"</td><td>"+row[3]+"</td><td><a href = test_new.py?action=supprimer&amp;utilisateur_supp="+str(row[0])+">Supprimer</a></td><td><a href = test_new.py?action=modifier&amp;utilisateur_modif="+str(row[0])+">Modifier</a></td></tr>"
	print "</tbody></table></form>"
	print "</div>"

def verification_formulaire_ajout():
	global erreur
	nom = form.getvalue("nom_ajout").lower()
	prenom = form.getvalue("prenom_ajout").lower()
	email = form.getvalue("email_ajout").lower()
	if (re.match(patternNom,nom) and re.match(patternNom,prenom)):
		if (re.match(patternMail,email)):
			ajout_utilisateur(nom,prenom,email,"mdp")
		else:
			printAdmin()
			erreur = "<div id= incorrect>Email invalide !</div>"
	else:
		printAdmin()
		erreur = "<div id= incorrect>Les noms et prénoms doivent être composés de lettres uniquement</div>"
def verification_formulaire_inscription():
	global erreur
	nom =  form.getvalue("nom_inscription").lower()
	prenom =  form.getvalue("prenom_inscription").lower()
	email =  form.getvalue("email_inscription").lower()
	mdp =  form.getvalue("mdp_inscription")
	if (re.match(patternNom,nom) and re.match(patternNom,prenom)):
		if (re.match(patternMail,email)):
			if (re.match(patternMdp,mdp)):
				ajout_utilisateur(nom,prenom,email,mdp)
			else:
				print_inscription()
				erreur ="<div id= incorrect>Votre mot de passe doit contenir au moins 4 caractères/chiffres</div>"
		else:
			print_inscription()
			erreur = "<div id= incorrect>Email invalide !</div>"
	else:
		print_inscription()
		erreur = "<div id= incorrect>Les noms et prénoms doivent être composés de lettres uniquement</div>"
	
	
def ajout_utilisateur(nom,prenom,email,mdp):
	global erreur
	mdp_provisoire = randint(1000,1000000)
	mdp_hash = hashlib.md5()
	test = mdp
	
	
	if (test == "mdp"):
		mdp = str(mdp_provisoire)
		mdp_hash.update(mdp)
		sql = "INSERT INTO utilisateur4 (nom, prenom, email, mdp, admin) VALUES ('"+nom+ "', '"+prenom+ "', '"+email+ "', '"+str(mdp_hash.hexdigest())+"', 0)"
	else:	
		mdp_hash.update(mdp)
		sql = "INSERT INTO utilisateur4 (nom, prenom, email, mdp, admin) VALUES ('"+nom+ "', '"+prenom+ "', '"+email+ "', '"+str(mdp_hash.hexdigest())+"', 0)"
	recherche_sql = "SELECT * FROM utilisateur4 where email='"+email+"'"
	cursor = db.cursor()
	cursor.execute(recherche_sql)
	rows = cursor.fetchall()
	if(rows):
		erreur = "<div id= incorrect>Adresse Mail déjà utilisée</div>"
		if (test != "mdp"):
			print_inscription()
		else:
			printAdmin()
	else:
		cursor.execute(sql)
		db.commit()
		if (test != "mdp"):
			envoyerEmail(email,"inscription",test)
			erreur = "<div id= incorrect>Inscription effectuée</div>"
			printConnexion()
		else:
			envoyerEmail(email,"ajout",mdp)
			erreur = "<div id= incorrect>Ajout d'utilisateur effectué</div>"
			printAdmin()
		
def print_utilisateur():
	cursor = db.cursor()
	cursor.execute ("SELECT * FROM utilisateur4 WHERE  id='"+str(sess.data["donnees_utilisateur"][0])+"'")
	rows = cursor.fetchall()
	for row in rows:
		print "<h1>Ma page utilisateur</h1>"
		print "<div id=Menu>"
		print "<h4>Bonjour : "+row[2]+ " "+row[1].upper()+"</h4>"
		print "<p id=infoUti>Voici vos informations actuelles :</p>"
		print "<form method ='post' action ='test_new.py'>"
		print "<table id=utilisateur><tr><td>Email:<td>Mot de passe:</tr>"
		print "<tr><td>"+row[3]+"</td><td>******</td>"
		print "<tr><td><input id=modifier type='submit' name='email_amodifier' value='modifier'><td><input id=modifier type='submit' name='mdp_amodifier' value='modifier'>"
		print "</table>"
		print ("<form method ='post' action='test_new.py'><input id=deconnexion type='submit' value='deconnexion' name='deconnexion'></form>")
		print "</form>"
def verif_modification():
	cursor = db.cursor()
	cursor.execute ("SELECT * FROM utilisateur4 WHERE  id='"+str(form.getvalue("utilisateur_modif"))+"'")
	rows = cursor.fetchall()
	sess.data["id_modif"] = form.getvalue("utilisateur_modif")
	for row in rows:
		print "<h1>Informations utilisateur</h1>"
		print "<div id =Menu>"
		print "<h4>Utilisateur: "+row[2]+ " "+row[1].upper()+"</h4>"
		print "<p id=Texte>Voici ses informations actuelles :</p>"
		print ("<form method ='post' action='test_new.py'><input id=deconnexionModif type='submit' value='deconnexion' name='deconnexion'><input id=retour type='submit' value='retour' name='retour_admin'></form>")
		print "<form method ='post' action ='test_new.py'>"
		print "<table id=Modif><tr><td>Email<td>Mot de passe</tr>"
		print "<tr><td>"+row[3]+"</td><td>******</td>"
		print "<tr><td><input class=boutonModifUtili type='submit' name='email_amodifier_admin' value='modifier'></td><td><input class=boutonModifUtili type='submit' name='mdp_amodifier_admin' value='modifier'></td><td><input id=boutonModifUtiliAd type='submit' name='passer_admin' value='Passer Admin'></td></tr>"
		print "</table>"
		print "</form>"
		print "</div>"
def passage_admin():
	global erreur
	id = sess.data["id_modif"]
	cursor = db.cursor()
	cursor.execute("UPDATE utilisateur4 SET admin=1 WHERE id='"+str(id)+"'")
	db.commit()
	printAdmin()
	erreur = "<div id= incorrect>L'utilisateur est devenu admin </div>"
	
def verif_suppression():
	cursor = db.cursor()
	cursor.execute ("SELECT * FROM utilisateur4 WHERE id='"+form.getvalue("utilisateur_supp")+"'")
	rows = cursor.fetchall()
	sess.data["id_supp"] = form.getvalue("utilisateur_supp")
	for row in rows:
		print "<h1>Suppression Utilisateur</h1>"
		print "<div id=Menu>"
		print ("<form method ='post' action='test_new.py'><input id=deconnexion type='submit' value='deconnexion' name='deconnexion'><input id=retour_changement type='submit' value='retour' name='retour_admin'></form>")
		print "<div id=suppression_text>"
		print "Souhaitez-vous réelement supprimer cet utilisateur ?  "+row[1].upper()+" "+row[2]
		print "<form action='test_new.py' method='post'>"
		print "<input type='radio' name='choix_suppression' value='oui'>Oui"
		print "<input type='radio' name='choix_suppression' value='non'>Non"
		print "<input id=boutonI type='submit' name='choix_supp' value='valider'>"
		print "</div>"
		print "</div>"
		
def suppression_utilisateur():
	global erreur
	uid = sess.data["id_supp"]
	cursor = db.cursor()
	if cursor.execute( "DELETE FROM utilisateur4 WHERE not(admin = 1) and id = '" + str(uid)+"'"):
		db.commit()
		erreur = "<div id= incorrect>Suppression d'utilisateur effectué</div>"
		printAdmin()
	else:
		printAdmin()
		erreur = "<div id= incorrect>la supppression a échoué</div>"
	
	
def modification_donnes_admin():
	print "<h1>Modification</h1>"
	print "<div id=Menu>"
	print "<form method='post' action='test_new.py'><table id=ModificationDonnesAdmin><tr>"
	if (form.has_key("email_amodifier_admin")  or form.has_key("modifier_email_admin")):
		print "<td><label for='nouvel_email'>Nouvel email</label></td><td><input id=caseE type='email' name='nouvel_email_admin' id='nouvel_email'></td>"
		print "<td><input class=AppliquerModif type='submit' value='appliquer' name='modifier_email_admin'></td><td><input id=retour type='submit' value='retour' name='retour_admin'></td></tr>"
	else:
		print "<td><label for='nouvel_mdp'>Nouveau mot de passe</label></td><td><input id=caseE type='password' name='nouvel_mdp_admin' id='nouvel_mdp'></td></tr>"
		print "<tr><td><label for='nouvel_mdp2'>Saisir à nouveau le mot de passe</label></td><td><input id=caseE type='password' name='nouvel_mdp2_admin' id='nouvel_mdp2'>"
		print "<tr><td><input class=AppliquerModif type='submit' value='appliquer' name='modifier_mdp_admin'>"
		print "<td><form method ='post' action='test_new.py'><input id=deconnexionAdModif type='submit' value='deconnexion' name='deconnexion'></td><td><input id=retour type='submit' value='retour' name='retour_admin'></td></form>"
	print "</td></tr></table></form></div>"
def modification_donnes():
	print "<h1>Modification</h1>"
	print "<div id=Menu>"
	print "<form method='post' action='test_new.py'><table id=changement><tr><td>"
	if (form.has_key("email_amodifier") or form.has_key("modifier_email")):
		print "<td><label for='nouvel_email'>Nouvel email</label></td><td><input id=caseE type='email' name='nouvel_email' id='nouvel_email'>"
		print "<td><input id=appliquer type='submit' value='appliquer' name='modifier_email'>"
	else:
		print "<tr><td><label for='nouvel_mdp'>Nouveau mot de passe</label></td><td><input id=caseE type='password' name='nouvel_mdp' id='nouvel_mdp'></td></tr>"
		print "<tr><td><label for='nouvel_mdp2'>Saisir à nouveau le  mot de passe</label></td><td><input id=caseE type='password' name='nouvel_mdp2' id='nouvel_mdp2'>"
		print "<tr><td><input id=appliquer type='submit' value='appliquer' name='modifier_mdp'>"
	print "</td></tr></table></form>"
	print ("<form method ='post' action='test_new.py'><input id=deconnexion type='submit' value='deconnexion' name='deconnexion'><input id=retour_changement type='submit' value='retour' name='retour_utilisateur'></form>")
	print "</div>"

def editUser():
	global erreur
	cursor = db.cursor()
	if (form.has_key("nouvel_email")):
		nouvel_email = form.getvalue("nouvel_email")
		if (re.match(patternMail,nouvel_email)):
			cursor.execute("UPDATE utilisateur4 SET email='"+nouvel_email+"' WHERE id='"+str(sess.data["donnees_utilisateur"][0])+"'")
			db.commit()
			print_utilisateur()
			erreur = "<div id= incorrect>Email correctement modifié</div>"
		else:
			modification_donnes()
			erreur = "<div id= incorrect>Adresse mail incorrect</div>"
	elif (form.has_key("nouvel_mdp") and form.has_key("nouvel_mdp2")):
		nouvel_mdp = form.getvalue("nouvel_mdp")
		nouvel_mdp2 = form.getvalue("nouvel_mdp2")
		if (nouvel_mdp == nouvel_mdp2):
			if (re.match(patternMdp,nouvel_mdp)):
				mdp_hash = hashlib.md5()
				mdp_hash.update(nouvel_mdp)
				cursor.execute("UPDATE utilisateur4 SET mdp='"+str(mdp_hash.hexdigest())+"' WHERE id='"+str(sess.data["donnees_utilisateur"][0])+"'")
				db.commit()
				print_utilisateur()
				erreur = "<div id= incorrect>Mot de passe correctement modifié</div>"
			else:
				modification_donnes()
				erreur = "<div id= incorrect>Votre mot de passe doit contenir au moins 4 lettres/chiffres</div>"
		else:
			modification_donnes()
			erreur = "<div id= incorrect>Les mots de passe ne sont pas identiques !</div>"
def editUser_admin():
		global erreur
		cursor = db.cursor()
		if (form.has_key("nouvel_email_admin")):
			nouvel_email = form.getvalue("nouvel_email_admin")
			if (re.match(patternMail,nouvel_email)):
				cursor.execute("UPDATE utilisateur4 SET email='"+nouvel_email+"' WHERE id='"+str(sess.data["id_modif"])+"'")
				db.commit()
				printAdmin()
				erreur = "<div id= incorrect>Email correctement modifié"
			else:
				modification_donnes_admin()
				erreur = "<div id= incorrect>Adresse mail incorrect"
		elif (form.has_key("nouvel_mdp_admin") and form.has_key("nouvel_mdp2_admin")):
			nouvel_mdp = form.getvalue("nouvel_mdp_admin")
			nouvel_mdp2 = form.getvalue("nouvel_mdp2_admin")
			if (nouvel_mdp == nouvel_mdp2):
				if (re.match(patternMdp,nouvel_mdp)):
					mdp_hash = hashlib.md5()
					mdp_hash.update(nouvel_mdp)
					cursor.execute("UPDATE utilisateur4 SET mdp='"+str(mdp_hash.hexdigest())+"' WHERE id='"+str(sess.data["id_modif"])+"'")
					db.commit()
					printAdmin()
					erreur = "<div id= incorrect>Mot de passe correctement modifié</div>"
				else:
					modification_donnes_admin()
					erreur = "<div id= incorrect>Votre mot de passe doit contenir au moins 4 lettres/chiffres</div>"
			else:
				modification_donnes_admin()
				erreur = "<div id= incorrect>Les mots de passe ne sont pas identiques !</div>"
		else:
			modification_donnes_admin()
			erreur = "<div id= incorrect>Tous les champs doivent être renseignés</div>"
			
printHead()

test_donnees_formulaire()


if(erreur):
	print erreur

	

print "</div>"
db.close()


