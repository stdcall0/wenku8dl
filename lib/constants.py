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

api = {
  "book": "https://www.wenku8.net/novel/%s/%d/",
  "info": "https://www.wenku8.net/book/%d.htm",
  "img": "https://img.wenku8.com/image/%s/%d/%ds.jpg",
  "login": "http://www.wenku8.net/login.php?do=submit",
  "search1": 'http://www.wenku8.net/modules/article/search.php?searchtype=articlename&searchkey=%s',
  "search2": 'http://www.wenku8.net/modules/article/search.php?searchtype=author&searchkey=%s',
  "txt": 'http://dl.wenku8.com/down.php?type=txt&id=%d'
} # Wenku8 页面地址

# Wenku8 图源前缀，将会下载以这些链接开头的图片
img_splits = ['http://pic.wenku8.com/pictures/', 'http://pic.wkcdn.com/pictures/', 'http://picture.wenku8.com/pictures/']
# 使用的 User-Agent
ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"}
# 使用到的 Content-Type
cts = {
  'post': {'Content-Type': 'application/x-www-form-urlencoded'},
  'formdata': {'Content-Type': 'multipart/form-data; boundary=--------------------------607040101744888865545920'}
}
# BeautifulSoup 使用的解析器。如果有也可以使用 lxml，速度更快
parser = "html.parser"
# EPUB 每个页面的模板
HTML = r"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>%s</title>
</head>
<body>
  <div>
    %s
  </div>
</body>
</html>"""
# EPUB 第一页的模板
INTRO = """<div class="center">
  <h1>%s</h1><br />
  <h3>Wenku8 ID: %d</h3><br />
  ♡Made with love by <i>wk8toepub</i>♡<br />
</div>"""
# EPUB 全局 css 样式
CSS = """body{padding:0;margin:0;line-height:1.2;text-align:justify}
p{text-indent:2em;display:block;line-height:1.3;margin-top:0.6em;margin-bottom:0.6em}
div{margin:0;padding:0;line-height:1.2;text-align:justify}
h1{font-size:1.4em;line-height:1.2;margin-top:1em;margin-bottom:1.2em;font-weight:bold;text-align:center !important;color:#000000}

.cover{margin:0;padding:0;text-indent:0;text-align:center !important}

.makertitle{font-size:1.3em;text-align: center !important;text-indent:0;font-weight:bold;margin-top:1em;margin-bottom:0.8em}
.infobox p{text-indent:0;line-height:1.1;margin:0;padding-left:3%;padding-right:3%}
.infobox p.top{border-top:1px solid #333;padding-top:0.2em}
.infobox p.bottom{border-bottom:1px solid #333;padding-bottom:0.2em}
.psline{margin-top:1em;margin-bottom:0.7em}

.bold{font-weight:bold}

.in0{text-indent:0}
.center{text-align:center !important;text-indent:0}
.left{text-align:left !important;text-indent:0}
.right{text-align:right !important;text-indent:0}
.italic{font-style:italic}
.oblique{font-style:oblique}

.tdtop{vertical-align:top}
.tdbottom{vertical-align:bottom}
.tdmiddle{vertical-align:middle}

.titlet1{color:#000000;margin-top:1.5em;margin-bottom:1.5em;font-size:1.6em}
.titlet2{font-size:0.9em}
.titlet3{color:#000000;font-size:1.0em;margin-top:-0.5em}

.notetag{font-size:0.8em;vertical-align:super;font-weight:bold;color:#960014;text-decoration:none}
.po{font-size:0.9em;color:#960014}

#toctitle{color:#000000;margin-top:1.5em;margin-bottom:1.5em}
#toctable{margin-left:auto;margin-right:auto;page-break-inside:auto}
.tocidprefix{width:2.5em}
.tocitem{padding:3px 0px}
.tocitem a{text-decoration:none;color:#000000}"""
