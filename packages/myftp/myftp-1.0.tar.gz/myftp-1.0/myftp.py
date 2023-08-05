from ftplib import *
import os,readline
import sys
class myFtp:
    ftp = FTP()
    bIsDir = False
    path = ""
    def __init__(self, host, port='21'):
        #self.ftp.set_debuglevel(2)
        #self.ftp.set_pasv(0)      
        self.ftp.connect(host=host,timeout=10000)
    def Login(self, user, passwd):
        self.ftp.login(user=user, passwd=passwd )
        print (self.ftp.welcome)
        print('login sucess!')
    def DownLoadFile(self, LocalFile, RemoteFile):
        file_handler = open(LocalFile, 'wb')
        self.ftp.retrbinary( "RETR %s" %( RemoteFile ), file_handler.write ) 
        file_handler.close()
        return True
    
    def DownLoadFileTree(self, LocalDir, RemoteDir):
        #print ("remoteDir:", RemoteDir)
        if os.path.isdir( LocalDir ) == False:
            os.makedirs(LocalDir)
        #print(RemoteDir)
        self.ftp.cwd(RemoteDir)
        #print('Current dirs %s' % self.ftp.pwd())
        RemoteNames = self.ftp.nlst()  
        #print ("RemoteNames", RemoteNames)
        #print ('remot files %s' % self.ftp.nlst("/root/web/"))
        for file in RemoteNames:
            #print(file)
            Local = os.path.join(LocalDir, file )
            #print(Local)
            chang = os.path.join(RemoteDir,file )
            if self.isDir(chang):
             #   print('ok')
                self.DownLoadFileTree(Local, chang)                
            else:
                self.DownLoadFile( Local, chang)
        self.ftp.cwd( ".." )
    
    #def show(self, list):
        #result = list.lower().split( " " )
        #result = list.lower()
        #print(result)
     #   if self.path in result and  "<dir>" not in result:
      #      self.bIsDir = True
       #$ print(self.bIsDir)
     
    def isDir(self, path):
        if os.path.isdir(path) == True:
           self.bIsDir = True
        else:
            self.bIsDir = False
        return self.bIsDir

        #self.bIsDir = False
        #self.path = path
        #this ues callback function ,that will change bIsDir value
        #self.ftp.retrlines( 'LIST', self.show )
        #return self.bIsDir
    
    def close(self):
        self.ftp.quit()
    def UpLoadFileTree(self, LocalDir, RemoteDir):
        if os.path.isdir(LocalDir) == False:
            print( 'wrong')
       # else:
          #  self.ftp.cwd(LocalDir)
        if os.path.isdir(RemoteDir) == False:
            os.makedirs(RemoteDir)
        #print ("LocalDir:", LocalDir)
        LocalNames = os.listdir(LocalDir)
        #print ("locallist:", LocalNames)
        #print (RemoteDir)
        self.ftp.cwd(RemoteDir)
        for Local in LocalNames:
           src = os.path.join( LocalDir, Local)
          # print('local %s ' % src)
           chang = os.path.join(RemoteDir,Local)
           #print('remot %s' % chang)
           if os.path.isdir(src):
            self.UpLoadFileTree(src,chang)
           else:
            self.UpLoadFile(src,chang)
                
        self.ftp.cwd( ".." )
        #print ('Down Ok')
    def UpLoadFile(self, LocalFile, RemoteFile):
        if os.path.isfile( LocalFile ) == False:
            return False
        file_handler = open(LocalFile, "rb")
        self.ftp.storbinary('STOR %s'%RemoteFile, file_handler, 4096)
        file_handler.close()
	

ftp = myFtp('192.168.19.153')
#if __name__ == "__main__":
def quit():
	sys.exit(0)
def login():
    ftp.Login('root','root')
    #print (' login')
def put():
    print('\033[34mUping.....\033[m')
    ftp.UpLoadFileTree('main', "/dell" )
    print('Done')
def load():
    print('\033[34mDowning.....\033[m')
    ftp.DownLoadFileTree('/var/ftp/pub/dell','/root/web/')
    print ('Done')
def list():
    print ("""\033[;32mWelcome \033[0m\n""")
    print ("\t(1) login")
    print ("\t(2) put")
    print ("\t(3) load")
    print ("\t(4) quit")
    print ("\t(5) #transfer money")
    print ("\t(6) #query bill")
    while True:
       choices = raw_input('\033[32mChoice:\033[m').strip()
       if len(choices) == 0:continue
       if choices == '1':login()
       elif choices == '2':put()
       elif choices == '3':load()
       elif choices == '4':quit()
		#elif choices == '5':transferMoney()
		#print "\033[;31mPlease pay attention to the property security\033[0m"
list()
