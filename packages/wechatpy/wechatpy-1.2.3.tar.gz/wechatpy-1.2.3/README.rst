::

      ___       __   _______   ________  ___  ___  ________  _________  ________  ___    ___ 
     |\  \     |\  \|\  ___ \ |\   ____\|\  \|\  \|\   __  \|\___   ___\\   __  \|\  \  /  /|
     \ \  \    \ \  \ \   __/|\ \  \___|\ \  \\\  \ \  \|\  \|___ \  \_\ \  \|\  \ \  \/  / /
      \ \  \  __\ \  \ \  \_|/_\ \  \    \ \   __  \ \   __  \   \ \  \ \ \   ____\ \    / / 
       \ \  \|\__\_\  \ \  \_|\ \ \  \____\ \  \ \  \ \  \ \  \   \ \  \ \ \  \___|\/  /  /  
        \ \____________\ \_______\ \_______\ \__\ \__\ \__\ \__\   \ \__\ \ \__\ __/  / /    
         \|____________|\|_______|\|_______|\|__|\|__|\|__|\|__|    \|__|  \|__||\___/ /     
                                                                                \|___|/      

|Latest Version| |Build Status| |Build status| |codecov.io| |Scrutinizer
Code Quality| |Supported Python versions| |Supported Python
implementations|

微信(WeChat) 公众平台第三方 Python
SDK，实现了普通公众平台和企业号公众平台的解析消息、生成回复和主动调用等
API。

阅读文档：\ http://wechatpy.readthedocs.org/zh_CN/latest/

|Join the chat at https://gitter.im/messense/wechatpy|

安装
----

推荐使用 pip 进行安装:

::

    pip install wechatpy

升级版本：

::

    pip install -U wechatpy

从 0.8.0 版本开始，wechatpy 消息加解密同时兼容
`cryptography <https://github.com/pyca/cryptography>`__ 和
`PyCrypto <https://github.com/dlitz/pycrypto>`__, 优先使用 cryptography
库。因而不再强制依赖 PyCrypto
库。如需使用消息加解密（企业号平台必须），请自行安装 cryptography 或者
PyCrypto 库：

.. code:: bash

    # 安装 cryptography
    pip install cryptography>=0.8.2
    # 或者安装 PyCrypto
    pip install pycrypto>=2.6.1

    Tips: Windows 用户请先安装 PyCrypto 的二进制包后再使用 pip 安装
    wechatpy 。 PyCrypto Windows
    的二进制包可以在\ `这里 <http://www.voidspace.org.uk/python/pycrypto-2.6.1/>`__\ 下载。

使用示例
--------

使用示例参见 `examples <examples/>`__

贡献代码
--------

请阅读 `贡献代码指南 <CONTRIBUTING.md>`__

License
-------

The MIT License (MIT)

Copyright (c) 2014-2015 messense

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

.. |Latest Version| image:: https://pypip.in/version/wechatpy/badge.svg
   :target: https://pypi.python.org/pypi/wechatpy/
.. |Build Status| image:: https://travis-ci.org/jxtech/wechatpy.svg?branch=master
   :target: https://travis-ci.org/jxtech/wechatpy
.. |Build status| image:: https://ci.appveyor.com/api/projects/status/sluy95tvbe090af1/branch/master?svg=true
   :target: https://ci.appveyor.com/project/messense/wechatpy-den93/branch/master
.. |codecov.io| image:: http://codecov.io/github/messense/wechatpy/coverage.svg?branch=master
   :target: http://codecov.io/github/messense/wechatpy?branch=master
.. |Scrutinizer Code Quality| image:: https://scrutinizer-ci.com/g/jxtech/wechatpy/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/jxtech/wechatpy/?branch=master
.. |Supported Python versions| image:: https://pypip.in/py_versions/wechatpy/badge.svg
   :target: https://pypi.python.org/pypi/wechatpy/
.. |Supported Python implementations| image:: https://pypip.in/implementation/wechatpy/badge.svg
   :target: https://pypi.python.org/pypi/wechatpy/
.. |Join the chat at https://gitter.im/messense/wechatpy| image:: https://badges.gitter.im/Join%20Chat.svg
   :target: https://gitter.im/messense/wechatpy?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge
