# wenku8dl
## 轻小说文库下载器
---

原作者: chiro2001 [点我](https://github.com/chiro2001/Wenku8ToEpub)

由于原版用不了了，魔改了一下代码，并且做了各种调整。

注意：和原版不一样的地方是小说的每一卷为一本书，而不是原来的所有卷放到一本书里。

目前还不能下载无版权书~~懒得写~~，可以去原地址看看。

可以通过编辑 `lib\constants.py` 中的 `options` 来调整选项，选项说明如下:
```python3
options = {
  "forceCover": False, # 强制 epub 使用图书封面，而非从插图中自动推断。
  "moreAuthor": False, # 添加贡献者与发布者到 EPUB 元数据中。
  "moreMeta": True, # 添加最后更新日期与简介到 EPUB 元数据中。
  "downloadImage": True, # 下载图像到 EPUB 文件中。
  "noImage": False, # 去除所有图像，包括未下载图像时的原链接。
  "simplifyTitle": True, # 简化标题。如 刀剑神域(SAO／ALO／GGO／UW) -> 刀剑神域，弱角友崎同学(弱势角色友崎君) -> 弱角友崎同学。
  'chapterPool': True, # 多线程下载章节。
  'imgPool': False, # 多线程下载图片。不建议开启，因为更慢。 
  "account": ['lanceliang', '1352040930lxr'], # 搜索用到的账号密码。默认值来自原脚本。
  "debug": False, # 调试模式，会将日志等级调到 debug.
  "outputDir": "output" # 输出文件夹
}
```

### 使用说明
需要 `Python 3.9+`

下载本仓库（或克隆）后，打开命令提示符

然后输入 `pip install` 安装依赖

依赖安装完后，输入 `python main.py <arg1> <arg2> ...` 就可以开始下载了

参数可以是小说编号，也可以是关键字。如果是编号会自动下载对应小说；如果是关键字会搜索并下载所有搜索到的小说。

多个参数用空格隔开。

### Screenshots
![screenshot gif](https://proj.imchinanb.xyz/wk8.gif)
![screenshot gif](https://proj.imchinanb.xyz/epub.gif)

### TODO
- [ ] 下载无版权小说
- [ ] 优化输出排版
