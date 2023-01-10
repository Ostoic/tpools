# tpools
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A small, trio-based, asynchronous work-stealing concurrency scheduler. Its main purpose is to partition a computation into a number of tasks, and then only allow a given number of them to run at a time. This is particularly useful when a large number of tasks need to be spawned, but should be rate-limited for whatever reason.
