# AutoHelp

# 这是为演示网页源码，需要大量针对自己bot的特色修改，请不要直接使用（别被我发现，不然我一定狠狠嘲笑你）

仅提供主要功能autohelp的配置方法，其他请自行修改（本人水平有限，不提供前端相关开发知识，当然，问了我也会尽量回复）

这是一个适用hoshinobot的自动帮助插件，改自xcw整合包的pages，安装之后会生成一个可供用户访问的帮助网页

### ★ 如果你喜欢的话，请给仓库点一个star支持一下23333 ★

## 本项目地址：

https://github.com/SonderXiaoming/autohelp

## 原理：

自动读取每个插件中的readme.md或service中的help，整理并放到网页上

（可通过pages第11行SERVICE_MODE调整）

（主要解决目前原版帮助对于各种插件说明混乱的问题）

（主要适用于大部分插件都是git clone或者有写readme的习惯的人）

以下（用service_mode的人可以无视）

考虑到readme面向是开发者，

如果实在不方便用户阅读，可以手动写一份userreadme.md放入与readme同一文件夹

优先读取userreadme，如果两个都没有，网页上会显示为none

## 部署教程：

 将static文件夹放入与run.py同一目录下

之后将pages文件夹放入`hoshino/modules中

接着打开pages文件中pages.py第10行将127.0.0.1改为你的公网ip

最后在 HoshinoBot\hoshino\config\\_*bot*_.py 文件的 MODULES_ON 加入 pages

重启 HoshinoBot

此插件调用了非常用库，如果没装，请依次使用如下指示安装依赖（其他你们应该装了，大概）

打开pages，点击上方菜单“文件”，选择打开powershell

安装依赖国内源：（选其中一个复制粘贴，再点回车即可）

清华大学镜像：python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

阿里云的镜像：python -m pip install -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

（127.0.0.1仅供本地调试使用）

## 使用教程：

发送【帮助】即可获取网址

### 额外配置

replace.json（按照实例，插件原名：插件替换名）

用来替换你不满意的名字

black.json

用来隐藏你不想出现在网页上的插件

## 更新日志

1.0：总算可以用了

1.1: 修复表格渲染问题，感谢 [@BlueDeer233](https://github.com/BlueDeer233)

2.0 大更新，感谢[@Lanly109](https://github.com/Lanly109)

1. 网站从客户端渲染改成服务端渲染

2. 新增了选择放出modules还是services的帮助选项。

3. 新增markdown的css样式

4. 帮助文案的高度可以自适应

5. 扩大了搜索范围，先前搜索范围仅限于基础功能和彩蛋，现在将指令文档也纳入搜索范围

6. 插件按照插件名的字典序进行排序排列

2.1：修复帮助页面搜索功能，美化界面 感谢[@Lanly109](https://github.com/Lanly109)

## 已知问题（不会做，最好有大佬pr或提供思路）

1.界面美化（~~这玩意当然越好看越花哨越好，不然怎么显得牛逼呢~~）

2.service按modules分类

## 参考效果

http://121.5.12.64:8080/huannai/help

（这是我自己的帮助，完整特化版，另一分支属于阉割版，但是方便推广，操作相对简单，但这个网页源码是这一个分支）

（如果访问失败，是服务器挂了）

## 特别感谢

[@sanshanya](https://github.com/sanshanya) 的[xcw整合包](https://github.com/pcrbot/hoshino_xcw)

我也是根据这个里面pages插件为基础进行修改

（虽然他已经跑路了，确实，原神真好玩）

## 写在最后

本人水平有限，仅仅提供想法，实现总有办法的

如果有更好的思路，欢迎pr或者提出issue

这应该算本人第一个有点用的插件

（隐约感觉这个插件好像不安全）
