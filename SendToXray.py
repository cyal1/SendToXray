#!python2
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from burp import IBurpExtender, ITab
from burp import IContextMenuFactory

# from java.awt import Color
from javax.swing import JMenuItem
from javax.swing import JPanel
from javax.swing import JLabel,JTextField,JButton
import socket
# import urllib
# import urllib2
# import ssl
# try:
#  _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#  # Legacy Python that doesn't verify HTTPS certificates by default
#  pass
# else:
#  # Handle target environment that doesn't support HTTPS verification
#  ssl._create_default_https_context = _create_unverified_https_context

class BurpExtender(IBurpExtender, ITab, IContextMenuFactory):

    def registerExtenderCallbacks(self, callbacks):
        self.messages = []
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('Send to XRAY')
        self.mainPanel = JPanel()
        self.testLabel = JLabel("XRAY Prxoy: ")
        self.testHost = JTextField("127.0.0.1",10)
        self.testPort = JTextField("9999",4)
        self.statusLabel = JLabel("")
        # self.testPort.setForeground(Color.RED);
        self.testBtn = JButton('check', actionPerformed=self.statusCheck)
        self.mainPanel.add(self.testLabel)
        self.mainPanel.add(self.testHost)
        self.mainPanel.add(self.testPort)
        self.mainPanel.add(self.testBtn)
        self.mainPanel.add(self.statusLabel)
        self.callbacks.customizeUiComponent(self.mainPanel)
        self.callbacks.addSuiteTab(self)
        self.callbacks.registerContextMenuFactory(self)
        print 'Welcome to Send to XRAY!'
        print 'The default XRAY prxoy is 127.0.0.1:9999'
        print 'Modify it to the "XRAY Proxy" Tab'
        self.statusCheck()

    def getTabCaption(self):
        return 'XRAY Proxy'

    def getUiComponent(self):
        return self.mainPanel

    def statusCheck(self,event=None):
        proxy_host = self.testHost.getText()
        proxy_port = int(self.testPort.getText())
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            sock.connect((proxy_host, proxy_port))
        except Exception as e:
            sock.close()
            print "Connetion XRAY Error: "+str(e)
            self.statusLabel.setText("fail")
            return
        print "Connetion XRAY Success!"
        self.statusLabel.setText("success")
        sock.close()

    def eventHandler(self,x):
        proxy_host = self.testHost.getText()
        proxy_port = int(self.testPort.getText())
        for m in self.messages:
            h = self.helpers.analyzeRequest(m)
            t = m.getRequest()
        r = t.tostring()
        url = str(h.getUrl())
        # headers = h.getHeaders()
        # method = h.getMethod()

        # body = r[h.bodyOffset:]
        # print url
        # headerd = {}
        # for x in headers[1:]:
        #     print x
        #     x,b = x.split(":",1)
        # if url.startswith("https"):
        #     opener=urllib2.build_opener(urllib2.ProxyHandler({"https":"127.0.0.1:9999"}))
        # else:
        #     opener=urllib2.build_opener(urllib2.ProxyHandler({"http":"127.0.0.1:9999"}))

        # req = urllib2.Request(url,data=body,headers=headerd)
        # req.get_method = lambda: method
        # print opener.open(req).read()
        
        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        try:
            sock.connect((proxy_host, proxy_port))
        except Exception:
            sock.close()
            print "Connetion Error: Please check your xray proxy settings!"
            self.statusLabel.setText("fail")
            return
        sock.send(r)
        sock.close()
        print "Send to XRAY: "+url

    def createMenuItems(self, invocation):

        self.menus = []
        self.menus.append(JMenuItem("Send to XRAY",None,actionPerformed=lambda x: self.eventHandler(x)))
        self.messages = invocation.getSelectedMessages()
        return self.menus
