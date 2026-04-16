---
title: Linux异步IO
date: 2026-04-14 18:12:46
categories:
  - Linux
  - 系统编程
tags:
  - Linux
  - IO
---

# Linux 异步 IO

在 Linux 系统中，异步 IO (AIO) 是为了提高高并发场景下的吞吐量而设计的。它允许进程在发起 IO 请求后立即返回执行其他任务，待 IO 操作完成后再通过某种通知机制获知结果。

## AIO (Linux Native AIO)

### 实现原理
Linux Native AIO 通过一组系统调用（`io_setup`, `io_submit`, `io_getevents`, `io_destroy`）实现。
- **核心流程**：用户空间维护一个异步环境，通过 `io_submit` 将 IO 请求提交到内核，内核在后台执行 IO，完成后将结果存入环形缓冲区。
- **局限性**：要求文件必须以 `O_DIRECT` 模式打开（绕过 Page Cache），且对普通文件（Regular File）支持较好，对 Socket 等网络 IO 支持极差。

### 优势
- 减少了进程阻塞在 IO 等待上的时间。
- 对于高吞吐量的数据库系统（如 MySQL InnoDB）在处理大文件读写时有显著提升。

### 使用场景
- 传统关系型数据库存储后端。
- 需要进行大量 Direct IO 操作的高性能存储工具。

## io_uring (Modern Async IO)

### 实现原理
io_uring 是 Linux 5.1 引入的新一代异步接口，由 Jens Axboe 开发。
- **核心机制**：使用两个共享内存的环形队列：**Submission Queue (SQ)** 和 **Completion Queue (CQ)**。
- **无锁交互**：用户态将请求放入 SQ，内核从中取出并处理；完成后结果放入 CQ，用户态直接读取。这种机制极大减少了系统调用次数（syscall）和内核/用户态之间的数据拷贝。

### 优势
- **极高性能**：在极高并发下性能远超 AIO 和传统的 epoll。
- **通用性**：不仅支持文件 IO，还全面支持网络 Socket、Buffered IO 等。
- **低开销**：支持内核侧轮询（SQPOLL），进一步消除系统调用开销。

### 使用场景
- 高性能网络服务器（如 Nginx, Envoy, Caddy）。
- 现代数据库与 KV 存储（如 RocksDB, ScyllaDB）。
- 大规模并发的 IO 密集型服务。

## AIO vs io_uring

| 特性 | AIO | io_uring |
| :--- | :--- | :--- |
| **支持场景** | 仅限 Direct IO，对网络 IO 支持极差 | 支持 Buffered IO, Direct IO, 网络 IO, 各种系统调用 |
| **性能** | 中等，受限于频繁的系统调用 | 极高，通过共享 Ring Buffer 减少上下文切换 |
| **系统开销** | 每次提交需 syscall | 支持批处理甚至无 syscall（SQPOLL） |
| **稳定性** | 接口老旧，行为在某些文件系统下不可预测 | 设计现代，内核支持力度大，发展迅速 |

### 总结
AIO 是 Linux 异步 IO 的早期尝试，虽然在特定场景（Direct IO）下有效，但其局限性限制了它的普及。**io_uring** 则是 Linux 内核 IO 演进的里程碑，它解决了 AIO 的所有短板，成为目前 Linux 平台上高性能异步操作的事实标准。
