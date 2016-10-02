import os, getopt, sys
from os.path import basename
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import json
def getFileData(filePath):
		lines = ""
		if os.path.exists(filePath):
				f = open(filePath, 'r')
				for line in f.readlines():
						lines += (str(line).replace('\n','')+'\n')
		return lines

def getFileDataAsList(filePath):
		lines = []
		if os.path.exists(filePath):
				f = open(filePath, 'r')
				for line in f.readlines():
						lines.append(str(line).replace('\n',''))
		return lines


def getEmailsFromFile(filePath):
		lines = []
		if os.path.exists(filePath):
				f = open(filePath, 'r')
				for line in f.readlines():
						lines.append(line)
		return lines




def sendMail(email_ids,body,subject):
		# To use files take a file argunment in the function
		email_json = json.load(open('EMAIL_CONFIG','r'))
		fromEmail=email_json['email']
		fromPassword=email_json['pass']
		msg = MIMEMultipart()
		msg['From'] = fromEmail
		msg['To'] = listToString(email_ids)
		msg['Subject'] = subject

		msg.attach(MIMEText(body, 'plain'))
		# for f in files or []:
		#     with open(f, "rb") as fil:
		#         part = MIMEApplication(
		#             fil.read(),
		#             Name=basename(f)
		#         )
		#         part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
		#         msg.attach(part)


			# for f in fileNames:
			#     msg.attach(MIMEBase('text',file(f).read()))


		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(fromEmail, fromPassword)
		x = server.sendmail(fromEmail, email_ids, msg.as_string('utf-8'))
		server.quit()
		return

def listToString(myList):
			str = ''
			for l in myList:
					str+=(','+l)
			return str[1:].replace('\n','')



# def main(argv):
# 		message = None
# 		emailIds = []
# 		attachments = []
# 		useremail = None
# 		password = None
# 		subject = None

# 		try:
# 			opts, args = getopt.getopt(argv,"hf:m:s:e:u:p:l:a:",["--help","file=","message=","subject=","emails=","username=","password=","emailfilepath=","attachmentspath="])
# 		except getopt.GetoptError:
# 			print 'sendEmail.py -f <FilePath> -m<Message> -s<Subject> -e<Email Ids("," Seperated) -u<UserEmail> -p<Password> -l<EmailsFilePath> -a<AttachmentsListFilePath>'
# 			sys.exit(2)
# 		for opt, arg in opts:
# 			if opt in ("-h", "--help"):
# 				 print 'sendEmail.py -f <FilePath> -m<Message> -s<Subject> -e<Email Ids("," Seperated) -u<UserEmail> -p<Password> -l<EmailsFilePath> -a<AttachmentsListFilePath>'
# 				 sys.exit()
# 			elif opt in ("-f", "--file"):
# 				 filePath = arg
# 				 message = getFileData(filePath)
# 			elif opt in ("-m", "--message"):
# 				 message = arg
# 			elif opt in ("-s", "--subject"):
# 				 subject = arg
# 			elif opt in ("-p", "--password"):
# 				 password = arg
# 			elif opt in ("-u", "--useremail"):
# 				 useremail = arg
# 			elif opt in ("-e", "--emails"):
# 				 emailIds = arg.split(",")
# 			elif opt in ("-l", "--emailfilepath"):
# 				 emailIds = getEmailsFromFile(arg)
# 			elif opt in ("-a", "--attachmentspath"):
# 				 attachments = getFileDataAsList(arg)

# 		if len(emailIds) is 0:
# 				print 'Error : Either give emails or filepath'
# 				return
# 		if message is None:
# 				print 'Error : Either give message or filepath'
# 				return
# 		if subject is None:
# 				print 'Error : No subject given'
# 				return
# 		if useremail is None:
# 				print 'Error : No Useremail id'
# 				return
# 		if password is None:
# 				print 'Error : No Password given'
# 				return

# 		sendMail(emailIds,message,subject,useremail,password,attachments)
# 		return


if __name__ == "__main__":
		 main(sys.argv[1:])









