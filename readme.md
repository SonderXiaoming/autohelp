# AutoHelp

## huannai分支上线，可看参考页面的源码

这是一个适用hoshinobot的自动帮助插件，改自xcw整合包的pages，安装之后会生成一个可供用户访问的帮助网页

### ★ 如果你喜欢的话，请给仓库点一个star支持一下23333 ★

## 本项目地址：

https://github.com/SonderXiaoming/autohelp

## 原理：

自动读取每个插件中的readme.md，整理并放到网页上

（主要解决目前原版帮助对于各种插件说明混乱的问题）

（主要适用于大部分插件都是git clone或者有写readme的习惯的人）

考虑到readme面向是开发者，

如果实在不方便用户阅读，可以手动写一份userreadme.md放入与readme同一文件夹

优先读取userreadme，如果两个都没有，网页上会显示为none

## 部署教程：

 将static文件夹放入与run.py同一目录下

之后将pages文件夹放入`hoshino/modules中

再用编辑器打开在pages文件templates中的help.html,在314行将127.0.0.1改为你的公网ip

接着打开pages文件中pages.py第7行将127.0.0.1改为你的公网ip

最后在 HoshinoBot\hoshino\config\\_*bot*_.py 文件的 MODULES_ON 加入 pages

重启 HoshinoBot

此插件调用了两个非常用库，如果没装，请依次使用如下命令安装依赖（其他你们应该装了，大概）

```
pip install markdown
pip install pathlib
```

（127.0.0.1仅供本地调试使用）

## 使用教程：

发送【帮助网页版】即可获取网址

（防止与原版冲突，有需要自行修改）

### 额外配置

在pages文件夹中service.json中

"MODULES"不用管，自动导入

"black_list":	不想某些插件显示在帮助页面上，输入插件所在文件夹名即可屏蔽掉这个插件

"modules_name"：本来想但懒得做，插件名字替换（考虑到部分插件可能名字比较奇特难懂）

## 更新日志

1.0：总算可以用了

## 已知问题（不会做，最好有大佬pr或提供思路）

1.iframe页面高度自定义

2.界面美化

## To do（懒得做。最好有大佬pr）

1.插件名字替换（考虑到部分插件可能名字比较奇特难懂）

## 参考效果

http://121.5.12.64:8080/huannai/help

（这是我自己的帮助，完整特化版，本项目属于阉割版，但是方便推广，操作相对简单，但这个网页源码会放进另一个分支）

（如果访问失败，是服务器挂了）

## 写在最后

本人水平有限，在写代码时隐约觉得可能有更好的实现方式，但由于目前知识水平限制，未能实现

如果有更好的思路，欢迎pr或者提出issue

这应该算本人第一个有点用的插件

（隐约感觉这个插件好像不安全）
