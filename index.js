#!/usr/bin/env node

const proc = require('process')
const program = require('commander')
const chalk = require('chalk')
const getLogger = require('./logging')
const wenku8 = require('./wenku8')
const { assert } = require('console')

program
  .version("1.0.0")
  .usage("[options] <novelID> [moreIDs ...]")
  .option("-v, --verbose", 'enable verbose logging', false)
  .option("-t, --thread <thread>", 'count of threads of the scheduler', 30)
  .parse(proc.argv)

const logger = getLogger(program.opts().verbose)
let sc = new (require('./scheduler'))(parseInt(program.opts().thread))
const ids = program.args

if (!ids.length) {
  logger.error("At least 1 novel ID is required. Exiting...")
} else {
  const wk = wenku8(logger, sc, program.opts())
  let f = []

  ids.forEach(idStr => {
    logger.debug("Processing IDstr:", idStr)
    let id = -1
    try {
      id = parseInt(idStr)
      assert(id != -1)
    }
    catch (e) {
      logger.error(idStr, "is not a valid ID. Ignoring...")
    }
    
    logger.debug("Processing ID:", id)
    f.push(wk.download(id))
  })

  process.on('exit', () => {
    logger.log(`Summary: (of ${f.length} books)`)
    f.forEach((x) => {
      logger.log(`${x.id} - ${x.name}: ${x.downloadedCount} / ${x.chapterCount}`)
    })
  })
}

