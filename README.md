## 功能
```
实现Windows GUI应用启停及其他复杂操作的自动化功能
```

## 使用步骤
1）安装python/pywin32  
-> python 
点击下面的网址下载即可，本工具使用的版本是：2.7.9  
https://www.python.org/downloads/

-> pywin32  
在工具包tools\pywin32\目录下提供了pywin32 64bit安装程序（适用于python 2.7+），可以选择其中一个安装包来安装即可。 

2）配置XML文件  
具体配置方法参见帮助说明
```

## 使用方法
1）帮助说明  
（1）先将闲聊群置顶，否则可能找不到  
（2）<step action="run" func="启动应用">中设置蓝信安装位置，如D:\LanxinSoftCustom\main\LxMainNew.exe  
（3）<step action="moveto" func="移动到置顶群">中设置置顶闲聊群的坐标，可使用tools\实时鼠标位置\mousepoint.exe工具来获取位置  
（4）<step action="moveto" func="移动到文本框">中设置闲聊群聊天窗口的坐标  
（5）<step action="moveto" func="移动到发送按钮">中设置发送按钮的坐标  

2）用法示例  
-> 启动蓝信，执行内容 
```
python win_app_ops.py -a start -c lanxin.xml
```
