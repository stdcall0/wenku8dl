const chalk = require('chalk')

module.exports = (verbose) => {
  return new function() {
    this.ERR = chalk.bgGray.bold.red("ERR")
    this.WRN = chalk.bgGray.bold.yellow("WRN")
    this.MSG = chalk.bold.whiteBright("MSG")
    this.DBG = chalk.bold.grey("DBG")
    this.INFO = chalk.bgGrey(" # ")

    const logger = (prefix) => {
      return (...args) => {
        console.log(prefix, ...args)
      }
    }

    this.error = logger(this.ERR)
    this.warn = logger(this.WRN)
    this.log = logger(this.MSG)
    this.info = logger(this.INFO)
    this.debug = verbose ? logger(this.DBG) : () => {}
  }
}
