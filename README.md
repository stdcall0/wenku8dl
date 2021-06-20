# wenku8dl
## 轻小说文库下载器
---

原作者: chiro2001 [点我](https://github.com/chiro2001/Wenku8ToEpub)

由于原版用不了了，魔改了一下代码，并且做了各种调整。

注意：和原版不一样的地方是小说的每一卷为一本书，而不是原来的所有卷放到一本书里。

目前还不能下载无版权书~~懒得写~~，可以去原地址看看。

可以通过编辑 `lib\constants.py` 中的 `options` 来调整选项，说明见文件注释。

### 使用说明
需要 `Python 3.9+`

下载本仓库（或克隆）后，打开命令提示符

然后输入 `pip install` 安装依赖

依赖安装完后，输入 `python main.py <arg1> <arg2> ...` 就可以开始下载了

参数可以是小说编号，也可以是关键字。如果是编号会自动下载对应小说；如果是关键字会搜索并下载所有搜索到的小说。

多个参数用空格隔开。

### Screenshots
![screenshot gif](https://proj.imchinanb.xyz/wk8o.gif)
![screenshot gif](https://proj.imchinanb.xyz/epub.gif)

### TODO
- [ ] 下载无版权小说
- [x] 优化输出排版
