# **Welcome to CRAPI!**

<br/>
**CRAPI** (spelled "crap-i" - and hoping not to be such one despite its name) or **Common Range API** is a library meant to ease the development in various areas of Linux and Windows using one common API. The library aims to be a highly stable version of common programming practices, constructs and OS native functions &amp; tools with a dedicated mindset in:

+  Portability in Windows since Windows API is huge and complicated
+  Portability in both OSes (Windows & Linux alike)
+  Performance

We aim to cover most common scenarios beyond the basic API mechanisms (i.e. building a multithreaded pipe server, Windows services/Linux daemon etc) that will be provided to you however not every scenario will be covered. Minimally, priority will be given to the foundation mechanisms so you may be able to build whatever you want (hopefully).

**Security issues** and **implementation correctness** are always a priority and will be taken into account however do note that until we reach a production/stable status we do not accept input but suggestions/comments and/or feedback are always welcome :)

## **Operating system support**
Windows 7/8/8.1/10, Windows Server 2008 R2/2012 R2/2016 & major Linux variants:<br/>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Debian 7.x and 8.x (untested) &amp; CentOS/RHEL 6.6 and 6.7 (tested).<br/>
Mac OS X is **NOT** supported (unless you buy me one maybe?).

## **Prerequisites**
+  Python 2.6 or 2.7 with latest version of pip, wheel and setuptools.<br/>
**Windows distributions**: Guess what? You need Mark Hammond's pywin32 module. Please use the one provided here: <a href="http://www.lfd.uci.edu/~gohlke/pythonlibs/#pywin32" target="_blank">pywin32-Build 219 by Christoph Gohlke</a> and make sure to follow the installation instructions correctly.<br/>

## **Why another library?**
How many times have you been forced to see this (non-parameterized example code for illustration purposes)?

```python
self.sa = win32security.SECURITY_ATTRIBUTES()
self.sa.bInheritHandle = True
self.__hPipe = win32pipe.CreateNamedPipe(
    '\\\\.\\pipe\\mypipe'
    win32pipe.PIPE_ACCESS_DUPLEX | win32file.FILE_FLAG_OVERLAPPED,
    win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE,
    win32pipe.PIPE_UNLIMITED_INSTANCES,
    65535,
    65535,
    60000,
    sa
)
```

or maybe this (from the MessageBroker library which uses MSMQ):

```python
pywintypes.com_error: (-2147352567, 'Exception occurred.', (0, u'MSMQQueueInfo',
u'The queue does not exist or you do not have sufficient permissions to perform'
'the operation.', None, 0, -1072824317), None)
```

A Python developer shouldn't have to figure this out especially when it's crafted in a non-Pythonic, untypical way.

Noone should have to do this. That's why we have attempted to do it FOR you WITHOUT you :P.

P.S.: The above are not meant to criticize Mark Hammond's __pywin32__ excellent library. Merely, they indicate the difficulties a developer has to deal with by being forced to have to use:

+ Non-portable code constructs due to multiple OSes with different APIs and native implementation.
+ Components which are difficult to understand to begin with since they require deep knowledge and understanding of an OS's internals and intricate mechanicms.

# **LICENSE**
It's based on Apache Software License 2.0 (ASF 2.0) so without suggesting that this constitutes a legal advice in any way, shape or form: Do whatever the f*** you want with it as long as you give us proper credit! :}

# **DISCLAIMER**
The authors strive for a stable and coherent source code base however it should be considered experimental and pre-alpha and, as such, not production-ready so use at your own risk! In addition, the authors makes no guarantees that the code is of top-notch quality (any Win folks here?). Patches are welcome (of course).<br/>
You have been (fore)warned!!! :]