from email.message import EmailMessage

import smtplib

remitente = "docentes.1@cbtis085.edu.mx"
destinatario = "jalmx89@gmail.com"
mensaje = "¡Hola, mundo!"
email = EmailMessage()
email["From"] = remitente
email["To"] = destinatario
email["Subject"] = "Correo de prueba"
email.set_content(mensaje)
smtp = smtplib.SMTP_SSL("smtp.gmail.com")

smtp.login(remitente, "kBu>757RC*0v>X")

smtp.sendmail(remitente, destinatario, email.as_string())

smtp.quit()
