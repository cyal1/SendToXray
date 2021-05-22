#!python2
#!/usr/bin/env python2
# -*- coding:utf-8 -*-
from burp import IBurpExtender, ITab
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from javax.swing import JPanel
from javax.swing import JLabel,JTextField,JButton,JCheckBox
from requests import Request, Session
import socket


class BurpExtender(IBurpExtender, ITab, IContextMenuFactory):

    def __init__(self):
        self.proxy_host = '127.0.0.1'
        self.port = 9999

    def registerExtenderCallbacks(self, callbacks):
        self.messages = []
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.callbacks.setExtensionName('Send to XRAY')

        self.mainPanel = JPanel()
        self.testLabel = JLabel("XRAY Prxoy: ")
        self.testHost = JTextField(self.proxy_host,10)
        self.testPort = JTextField(str(self.port),4)
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

        self.proxy_host = self.testHost.getText().strip()

        port = self.testPort.getText().strip()
        if not port.isdigit():
            print "Proxy port error!"
            return
        self.proxy_port = int(port)

        sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

        try:
            sock.connect((self.proxy_host, self.proxy_port))

        except Exception as e:
            print "Connetion XRAY Error: " + e.__class__.__name__
            self.statusLabel.setText("fail")
            return False

        finally:
    		sock.close()

        print "Connetion XRAY Success!"
        self.statusLabel.setText("success")
        return True

    def eventHandler(self,x):

        messageInfo = self.messages[0]

        httpService = messageInfo.getHttpService()
        service = httpService.toString()

        requestInfo = self.helpers.analyzeRequest(messageInfo)

        raw_headers = requestInfo.headers

        method, url, protocol = raw_headers[0].split(" ")

        url = service + url

        headers = dict([[i[0],i[1].strip()] for i in [h.split(':',1) for h in raw_headers[1:]]])

        body = messageInfo.request[requestInfo.getBodyOffset():len(messageInfo.request)]

        proxies = {
          'http': 'http://{}:{}'.format(self.proxy_host, self.proxy_port),
          'https': 'http://{}:{}'.format(self.proxy_host, self.proxy_port),
        }

        s = Session()

        s.proxies.update(proxies)

        req = Request(method, url, data = body.tostring(), headers = headers)

        prepped = req.prepare()
        try:
            r = s.send(prepped,
                verify = False,
                allow_redirects = False,
                timeout = 3
            )
        except Exception as e:
            print e.__class__.__name__+": ", method, url
            self.statusCheck()
            return

        print method, url, protocol, r.status_code
        self.statusLabel.setText("success")

    def createMenuItems(self, invocation):

        self.menus = []
        self.menus.append(JMenuItem("Send to XRAY",None,actionPerformed=lambda x: self.eventHandler(x)))
        self.messages = invocation.getSelectedMessages()
        return self.menus
