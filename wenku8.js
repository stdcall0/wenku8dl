const Promise = require('bluebird')
const axios = require('axios')
const chalk = require('chalk')
const cheerio = require('cheerio')
const iconv = require('iconv-lite')
const fs = Promise.promisifyAll(require('fs'))

const Url = require('url')
const path = require('path')
const qstring = require('querystring')

class Novel {
  constructor(obj) {
    Object.assign(this, obj)
  }
}

module.exports = (logger, sc, opts) => {
  return new function() {
    this.logger = logger
    this.opt = opts
    this.sc = sc
    this.get = async (url) => {
      let $ = await axios.get(url, {responseType: 'arraybuffer'}).catch(() => {
        this.logger.error(`failed to GET url: ${url}`)
      })
      if (!$ || !$.data) return ""

      return cheerio.load(iconv.decode($.data, 'gbk'))
    }
    this.mkdir = async (id, name) => {
      try {
        await fs.statAsync(path.join(process.cwd(), './novels'))
      } catch (e) {
        await fs.mkdirAsync(path.join(process.cwd(), './novels'))
      }
      try {
        await fs.statAsync(path.join(process.cwd(), `./novels/${id} - ${name}`))
      } catch (e) {
        await fs.mkdirAsync(path.join(process.cwd(), `./novels/${id} - ${name}`))
      }
    }
    this.download = async (id) => {
      const url = `https://www.wenku8.net/book/${id}.htm`
      let $ = await this.get(url)

      let novel = new Novel({
        id: id,
        name: $('b').eq(2).text(),
        desc: $('.hottext:nth-of-type(4)').nextAll('span').text(),
        bookUrl: url,
        tocUrl: $('#content').children().first().children().eq(5).children().children().first().find('a').attr("href"),
        chapterCount: 0,
        downloadedCount: 0
      })
      this.logger.debug("Getting novel info:", novel)
      this.logger.log(`${novel.id} - ${novel.name}: getting chapters...`)

      this.mkdir(novel.id, novel.name)

      if (novel.tocUrl !== undefined) { 
        let tocBaseUrl = novel.tocUrl.substring(0, novel.tocUrl.lastIndexOf('/'))
        $ = await this.get(novel.tocUrl)

        for (let [index, item] of Object.entries($('table td a'))) {
            index = parseInt(index)
            let href = $(item).attr('href')
            if (href) {
              ++novel.chapterCount
              let url = `${tocBaseUrl}/${href}`
              let title = $(item).text()
              this.logger.debug(`Chapter ${title}: ${url}`)
              this.sc.add(async () => {
                this.logger.log(`${novel.id} - ${novel.name}: downloading: ${index + 1}`)
                let $$ = await this.get(url)
                return fs.writeFileAsync(path.join(process.cwd(), `./novels/${novel.id} - ${novel.name}/${index+1}.md`), `${title}\n` + $$('#content').text().replace('本文来自 轻小说文库(http://www.wenku8.com)', '').replace('最新最全的日本动漫轻小说 轻小说文库(http://www.wenku8.com) 为你一网打尽！', ''))
              }).then(() => {
                this.logger.log(`${novel.id} - ${novel.name}: downloaded: ${index + 1}`)
                ++novel.downloadedCount
              }).catch((e) => {
                this.logger.error(`${novel.id} - ${novel.name}: failed to download: ${index + 1}: ${e}`)
              })
            }
        }
      }
      return novel
    }
  }
}
