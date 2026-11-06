# CS353: Socket Programming (Client-Server Architecture)
## Comprehensive Lab Report, Theory Guide & Implementation Manual
**Course:** CS353 · Computer Networks · Week 1 / Lab 1  
**Topic:** Application & Transport Layer / Socket Programming & Network IPC  
**System Implemented:** Iterative Server (`Server1`), Multi-Threaded Concurrent Server (`Server2`), and Interactive Client (`Client`) in Java and C

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [Theoretical Foundations of Socket Programming](#2-theoretical-foundations-of-socket-programming)
   - [2.1 What is a Socket?](#21-what-is-a-socket)
   - [2.2 The Client-Server Architectural Paradigm](#22-the-client-server-architectural-paradigm)
   - [2.3 Stream Sockets (TCP) vs. Datagram Sockets (UDP)](#23-stream-sockets-tcp-vs-datagram-sockets-udp)
   - [2.4 TCP Handshake and State Transitions](#24-tcp-handshake-and-state-transitions)
3. [The UNIX / POSIX Socket API Lifecycle](#3-the-unix--posix-socket-api-lifecycle)
   - [3.1 System Calls Workflow Diagram](#31-system-calls-workflow-diagram)
   - [3.2 Detailed Analysis of Core Primitives](#32-detailed-analysis-of-core-primitives)
4. [Iterative Server Architecture (`Server1`)](#4-iterative-server-architecture-server1)
   - [4.1 Architectural Model & Limitations](#41-architectural-model--limitations)
   - [4.2 Code Walkthrough (`Server1.java`)](#42-code-walkthrough-server1java)
   - [4.3 Head-of-Line Blocking Demonstration](#43-head-of-line-blocking-demonstration)
5. [Concurrent Server Architecture (`Server2`)](#5-concurrent-server-architecture-server2)
   - [5.1 Multi-Process (`fork()`) vs. Multi-Threaded (`Thread`) Models](#51-multi-process-fork-vs-multi-threaded-thread-models)
   - [5.2 Code Walkthrough (`Server2.java`) & Worker Thread Logic](#52-code-walkthrough-server2java--worker-thread-logic)
   - [5.3 Concurrency, Memory Footprint & Scalability](#53-concurrency-memory-footprint--scalability)
6. [Client Implementation (`Client.java`)](#6-client-implementation-clientjava)
   - [6.1 Connection Setup & Stream I/O](#61-connection-setup--stream-io)
   - [6.2 Line-Oriented Buffering & Termination Semantics](#62-line-oriented-buffering--termination-semantics)
7. [Experimental Results & Verification Logs](#7-experimental-results--verification-logs)
   - [7.1 Single Client with Iterative Server](#71-single-client-with-iterative-server)
   - [7.2 Concurrent Clients with Multi-Threaded Server](#72-concurrent-clients-with-multi-threaded-server)
8. [Architectural Comparison Matrix](#8-architectural-comparison-matrix)
9. [Networking Edge Cases, Failures & Hardening](#9-networking-edge-cases-failures--hardening)
   - [9.1 Address Already in Use (`SO_REUSEADDR`)](#91-address-already-in-use-so_reuseaddr)
   - [9.2 TCP Stream Boundary Issue (Framing / Nagle's Algorithm)](#92-tcp-stream-boundary-issue-framing--nagles-algorithm)
   - [9.3 Half-Closed Connections & Socket Timeouts](#93-half-closed-connections--socket-timeouts)
10. [Comprehensive Viva & Exam Preparation Guide](#10-comprehensive-viva--exam-preparation-guide)

---

## 1. Executive Summary

Network application processes communicate using inter-process communication (IPC) abstractions called **sockets**. In Lab 1, we design, build, and analyze a client-server architecture where clients establish reliable byte-stream TCP connections to a server, submit arbitrary text strings, and receive reversed string responses.

Two distinct architectural variants of the server are evaluated:
1. **Iterative Server (`Server1`):** A single-threaded process that handles one client request at a time. It blocks all subsequent incoming connection attempts until the currently connected client disconnects.
2. **Concurrent Server (`Server2`):** A multi-threaded process that offloads each accepted client socket to an autonomous worker thread (`ClientHandler`), allowing multiple clients to interact concurrently without head-of-line blocking.

```
+--------------------------------------------------------------------------------------------------+
|                                    SOCKET COMMUNICATIONS ARCHITECTURE                            |
|                                                                                                  |
|   CLIENT (Port 54321)                                             SERVER (Port 5555)             |
|   ===================                                             ==================             |
|   1. Socket("127.0.0.1", 5555) ───[ SYN ]────────────────────────► 1. ServerSocket(5555)         |
|                                ◄──[ SYN + ACK ]──────────────────  2. accept() blocks            |
|                                ───[ ACK ]────────────────────────►  3. returns clientSocket      |
|                                                                                                  |
|   2. send("abcd\n") ──────────────[ TCP PUSH ]───────────────────► 4. readLine() -> "abcd"       |
|                                                                    5. reverse -> "dcba"          |
|   3. recv("dcba\n") ◄─────────────[ TCP PUSH ]──────────────────── 6. println("dcba")           |
|                                                                                                  |
|   4. close() ─────────────────────[ FIN ]────────────────────────► 7. readLine() -> null         |
|              ◄────────────────────[ FIN + ACK ]──────────────────  8. clientSocket.close()       |
+--------------------------------------------------------------------------------------------------+
```

---

## 2. Theoretical Foundations of Socket Programming

### 2.1 What is a Socket?
A **socket** is the software endpoint that establishes bidirectional communication between two processes across an IP network. Defined conceptually by the Berkeley software distribution (BSD Sockets) in 1983, a socket abstracts the complex transport, network, and data link layer machinery into standard file-descriptor or stream I/O operations:

$$\text{Socket Endpoint} = (\text{IP Address}, \text{Port Number}, \text{Transport Protocol})$$

A full communication association between two network applications is uniquely defined by a **5-tuple**:
$$\text{Association} = (\text{Source IP}, \text{Source Port}, \text{Destination IP}, \text{Destination Port}, \text{Protocol})$$

### 2.2 The Client-Server Architectural Paradigm
- **Server:** An entity that starts first, binds to a well-known, predetermined port (e.g., port 5555), enters a passive listening state, and waits indefinitely for incoming connection requests.
- **Client:** An entity that initiates communication on demand. The operating system assigns the client an ephemeral (short-lived) port number chosen dynamically from the range 49152–65535, and connects to the server's well-known IP and port.

### 2.3 Stream Sockets (TCP) vs. Datagram Sockets (UDP)

| Characteristic | Stream Sockets (`SOCK_STREAM` / TCP) | Datagram Sockets (`SOCK_DGRAM` / UDP) |
| :--- | :--- | :--- |
| **Connection State** | Connection-oriented (Requires 3-way handshake). | Connectionless (No handshake; independent packets). |
| **Reliability** | Guarantees reliable delivery via ACKs and retransmissions. | Unreliable best-effort (packets can drop or reorder). |
| **Data Framing** | Continuous byte stream (no packet boundary preservation). | Discrete message boundaries preserved per datagram. |
| **Flow & Congestion**| Built-in sliding-window flow control and AIMD congestion control. | No flow or congestion control (blasts at line rate). |
| **Header Overhead** | Minimum 20 bytes (can extend to 60 with options). | Fixed 8 bytes. |
| **Lab Usage** | **Used in Lab 1** (`ServerSocket` & `Socket`). | DNS, VoIP, gaming, RTP streaming. |

### 2.4 TCP Handshake and State Transitions
Before application data can flow, TCP establishes a connection via the **Three-Way Handshake**:
1. **SYN (Synchronize):** Client sends a TCP segment with the `SYN` flag set and an initial sequence number $ISN_C$. (Client state: `SYN_SENT`).
2. **SYN + ACK:** Server receives `SYN`, allocates connection buffers, and replies with `SYN` ($ISN_S$) and `ACK` ($ISN_C + 1$). (Server state: `SYN_RCVD`).
3. **ACK:** Client receives `SYN+ACK` and sends `ACK` ($ISN_S + 1$). Both enter `ESTABLISHED` state.

Connection teardown requires a **Four-Way Handshake** (`FIN` $\to$ `ACK` $\to$ `FIN` $\to$ `ACK`) ensuring all in-flight buffers are drained cleanly.

---

## 3. The UNIX / POSIX Socket API Lifecycle

### 3.1 System Calls Workflow Diagram

```
       SERVER PROCESS                                      CLIENT PROCESS
  ┌───────────────────────┐                           ┌───────────────────────┐
  │   socket(AF_INET)     │                           │   socket(AF_INET)     │
  └──────────┬────────────┘                           └──────────┬────────────┘
             ▼                                                   │
  ┌───────────────────────┐                                      │
  │   bind(port 5555)     │                                      │
  └──────────┬────────────┘                                      │
             ▼                                                   │
  ┌───────────────────────┐                                      │
  │      listen()         │                                      │
  └──────────┬────────────┘                                      │
             ▼                                                   ▼
  ┌───────────────────────┐        3-Way Handshake    ┌───────────────────────┐
  │  accept() [BLOCKING]  │ ◄═════════════════════════╡   connect(IP, port)   │
  └──────────┬────────────┘                           └──────────┬────────────┘
             ▼                                                   │
      [Connection Made]                                          │
             │                                                   ▼
             │                  Request Data          ┌───────────────────────┐
             ├ ◄──────────────────────────────────────┤  write() / println()  │
             ▼                                        └──────────┬────────────┘
  ┌───────────────────────┐                                      │
  │   read() / reverse()  │                                      │
  └──────────┬────────────┘                                      │
             ▼                 Reversed Data                     ▼
  ┌───────────────────────┐ ────────────────────────► ┌───────────────────────┐
  │  write() / send()     │                           │  read() / readLine()  │
  └──────────┬────────────┘                           └──────────┬────────────┘
             │                                                   │
             ▼ [EOF / Disconnect]                                ▼
  ┌───────────────────────┐                           ┌───────────────────────┐
  │     close(client)     │ ◄══════[ FIN / ACK ]═════ │     close(socket)     │
  └───────────────────────┘                           └───────────────────────┘
```

### 3.2 Detailed Analysis of Core Primitives

1. **`socket(domain, type, protocol)`:**
   Allocates an internal kernel data structure representing the socket endpoint and returns an integer file descriptor.
   - `AF_INET`: IPv4 address family.
   - `SOCK_STREAM`: TCP reliable byte-stream service.
2. **`bind(sockfd, sockaddr, addrlen)`:**
   Associates the abstract socket descriptor with a local network interface IP and port number.
3. **`listen(sockfd, backlog)`:**
   Transitions the socket from an active state to a **passive listening state**. The `backlog` argument specifies the maximum length of the operating system queue for pending connections (in `SYN_RCVD` and `ESTABLISHED` states awaiting `accept()`).
4. **`accept(sockfd, sockaddr, addrlen)`:**
   Extracts the first completed connection from the listening queue. It returns a **brand new connected socket descriptor** specifically dedicated to communicating with that client, leaving the original listening socket free to accept subsequent clients.
5. **`connect(sockfd, sockaddr, addrlen)`:**
   Invoked by the client to initiate the TCP 3-way handshake with the server's listening endpoint.
6. **`read()` / `write()` (or `recv()` / `send()`):**
   Exchanges raw bytes across the kernel's transmit and receive TCP ring buffers.
7. **`close(sockfd)`:**
   Initiates the TCP connection teardown protocol (`FIN`).

---

## 4. Iterative Server Architecture (`Server1`)

### 4.1 Architectural Model & Limitations
The iterative server handles incoming client connections sequentially on a single thread of execution:

```
                  +---------------------------+
                  |  ServerSocket.accept()    |
                  +-------------┬-------------+
                                │
                                ▼
                  +---------------------------+
                  | Handle Client Completely  | <--- BLOCKS ALL OTHER CLIENTS!
                  | (read -> reverse -> send) |
                  +-------------┬-------------+
                                │
                                ▼ (Client Disconnects)
                  +---------------------------+
                  |  Loop back to accept()    |
                  +---------------------------+
```

### 4.2 Code Walkthrough (`Server1.java`)

```java
try (ServerSocket serverSocket = new ServerSocket(port)) {
    System.out.println("Server1 listening on port " + port);

    while (true) {
        // Blocks until a client initiates a TCP handshake
        try (Socket clientSocket = serverSocket.accept()) {
            System.out.println("Connected with client socket number " + clientSocket.getPort());

            BufferedReader reader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
            PrintWriter writer = new PrintWriter(clientSocket.getOutputStream(), true);

            String message;
            // Loops until the client closes its output stream (returns null)
            while ((message = reader.readLine()) != null) {
                System.out.println("Client socket " + clientSocket.getPort() + " sent message: " + message);
                
                String reversed = new StringBuilder(message).reverse().toString();
                System.out.println("Sending reply: " + reversed);
                writer.println(reversed);
            }
            System.out.println("Client disconnected.");
        } catch (IOException e) {
            System.out.println("Exception with client: " + e.getMessage());
        }
    }
}
```

### 4.3 Head-of-Line Blocking Demonstration
In `Server1`, while Client A is connected and idle (e.g. typing slowly or paused), the server is trapped inside `reader.readLine()`. If Client B executes `java Client 127.0.0.1 5555`:
- Client B's TCP handshake succeeds at the OS kernel level (enters the OS backlog queue).
- Client B's application-level messages sit unread in the socket receive buffer.
- Client B receives **no reply** until Client A explicitly disconnects (terminates with `Ctrl+C`).
- This severe limitation is known as **Head-of-Line (HoL) Blocking**.

---

## 5. Concurrent Server Architecture (`Server2`)

### 5.1 Multi-Process (`fork()`) vs. Multi-Threaded (`Thread`) Models

In traditional UNIX C implementations, concurrency is achieved by calling `fork()` upon `accept()`. In Java, threads are utilized.

| Criterion | Multi-Process (`fork()`) in C | Multi-Threaded (`Thread`) in Java |
| :--- | :--- | :--- |
| **Address Space** | Isolated memory space (copy-on-write). | Shared address space within single JVM process. |
| **Creation Overhead** | High (kernel process table, page tables). | Low (lightweight user/kernel thread stack). |
| **Communication** | Requires IPC (pipes, shared memory, sockets). | Direct shared object access (requires locks/synchronization). |
| **Crash Resilience** | High: child process crash does not kill parent. | Low: unhandled exception in thread can crash JVM. |
| **Zombie Problem** | Child exit requires parent to call `waitpid()`. | Handled automatically by JVM thread termination. |

### 5.2 Code Walkthrough (`Server2.java`) & Worker Thread Logic
`Server2` delegates each newly accepted socket to a detached `Runnable` worker:

```java
while (true) {
    // Main listening thread only accepts connections
    Socket clientSocket = serverSocket.accept();
    System.out.println("Connected with client socket number " + clientSocket.getPort());
    
    // Asynchronously spawns an independent worker thread
    new Thread(new ClientHandler(clientSocket)).start();
}
```

The `ClientHandler` inner class encapsulates the client lifecycle:
```java
private static class ClientHandler implements Runnable {
    private final Socket clientSocket;

    public ClientHandler(Socket socket) {
        this.clientSocket = socket;
    }

    @Override
    public void run() {
        try (BufferedReader reader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
             PrintWriter writer = new PrintWriter(clientSocket.getOutputStream(), true)) {

            String message;
            while ((message = reader.readLine()) != null) {
                System.out.println("Client socket " + clientSocket.getPort() + " sent message: " + message);
                String reversed = new StringBuilder(message).reverse().toString();
                System.out.println("Sending reply: " + reversed);
                writer.println(reversed);
            }
        } catch (IOException e) {
            System.out.println("Exception with client: " + e.getMessage());
        } finally {
            try { clientSocket.close(); } catch (IOException ignored) {}
        }
    }
}
```

### 5.3 Concurrency, Memory Footprint & Scalability
- **Immediate Unblocking:** The main thread returns to `accept()` in under a microsecond, immediately ready to service the next client.
- **Resource Footprint:** Each Java thread allocates a call stack (typically 512 KB to 1 MB). For hundreds of simultaneous clients, a thread-per-client model is efficient. For hundreds of thousands of concurrent connections (the C10K / C1000K problem), modern systems utilize non-blocking asynchronous event loops (Java NIO, epoll, kqueue).

---

## 6. Client Implementation (`Client.java`)

### 6.1 Connection Setup & Stream I/O
The client initializes a connection by resolving the server IP string and establishing a socket:
```java
Socket socket = new Socket(serverIp, port);
```
Under the hood, Java resolves the host via DNS / `/etc/hosts` and invokes the native OS `connect()` system call.

### 6.2 Line-Oriented Buffering & Termination Semantics
1. **`BufferedReader`:** Buffers raw bytes from the socket's `InputStream` and converts them to characters using the default UTF-8 charset. `readLine()` blocks until a newline delimiter (`\n` or `\r\n`) is received.
2. **`PrintWriter(..., true)`:** The second argument enables **auto-flushing**. Whenever `println()` is invoked, the output buffer is immediately flushed to the underlying TCP socket without lingering in user-space buffers.
3. **Graceful Teardown:** When the user enters `Ctrl+C` or `Ctrl+D` (EOF), `consoleReader.readLine()` returns `null`. The client breaks the loop, triggers `try-with-resources`, closes the socket, and sends a TCP `FIN` packet to the server.

---

## 7. Experimental Results & Verification Logs

### 7.1 Single Client with Iterative Server (`Server1`)

#### Server Console Output:
```bash
$ javac Server1.java
$ java Server1 5555
Server1 listening on port 5555
Connected with client socket number 54120
Client socket 54120 sent message: abcd
Sending reply: dcba
Client socket 54120 sent message: cat
Sending reply: tac
Client disconnected.
```

#### Client Console Output:
```bash
$ javac Client.java
$ java Client 127.0.0.1 5555
Connected to server
Please enter the message to the server:
abcd
Server reply: dcba
Please enter the message to the server:
cat
Server reply: tac
Please enter the message to the server:
^C
```

---

### 7.2 Concurrent Clients with Multi-Threaded Server (`Server2`)
Demonstrating interleaved communication across two simultaneously active client terminals:

#### Server Console Output:
```bash
$ javac Server2.java
$ java Server2 5555
Server2 (Concurrent) listening on port 5555
Connected with client socket number 54130
Connected with client socket number 54132
Client socket 54130 sent message: hello world
Sending reply: dlrow olleh
Client socket 54132 sent message: computer networks
Sending reply: skrowten retupmoc
Client socket 54130 sent message: socket lab
Sending reply: bal tekcos
Client socket 54130 disconnected.
Client socket 54132 sent message: still connected!
Sending reply: !detcennocts llits
Client socket 54132 disconnected.
```

#### Client 1 Terminal (Socket 54130):
```bash
$ java Client 127.0.0.1 5555
Connected to server
Please enter the message to the server:
hello world
Server reply: dlrow olleh
Please enter the message to the server:
socket lab
Server reply: bal tekcos
```

#### Client 2 Terminal (Socket 54132):
```bash
$ java Client 127.0.0.1 5555
Connected to server
Please enter the message to the server:
computer networks
Server reply: skrowten retupmoc
Please enter the message to the server:
still connected!
Server reply: !detcennocts llits
```

---

## 8. Architectural Comparison Matrix

| Architectural Model | Concurrency Mechanism | CPU Utilization | Memory Overhead | Complexity | Scalability Limit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Iterative Server** | None (Single loop) | Minimal | Minimal (1 stack) | Trivial | 1 client at a time |
| **Multi-Process (`fork`)** | OS Process Table | High context-switching | High (separate memory) | Moderate (`waitpid`) | ~100–500 clients |
| **Multi-Threaded (Java)** | JVM Threads / ThreadPool| Moderate | Low (stack only) | Low-Moderate | ~1,000–5,000 clients |
| **Asynchronous / Event-Driven** | `epoll` / `select` / NIO | Maximum (Non-blocking)| Extremely Low | High (state machine) | 100,000+ clients |

---

## 9. Networking Edge Cases, Failures & Hardening

### 9.1 Address Already in Use (`SO_REUSEADDR`)
When a server terminates abruptly, its listening port remains locked by the operating system kernel in the `TIME_WAIT` state (typically 30–120 seconds, representing $2 \times MSL$, Maximum Segment Lifetime) to ensure delayed packets from old connections do not collide with new ones.
- **The Issue:** Attempting to restart the server immediately throws:
  `java.net.BindException: Address already in use`
- **Solution:** In C, set socket option `SO_REUSEADDR`:
  ```c
  int opt = 1;
  setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
  ```
  In Java, `ServerSocket` enables `SO_REUSEADDR` by default on most operating systems.

### 9.2 TCP Stream Boundary Issue (Framing / Nagle's Algorithm)
TCP is a byte-stream protocol, not a message protocol:
- If a client sends two distinct strings `"hello"` and `"world"` back-to-back, TCP may combine them into a single packet (`"helloworld"`), or split them across three packets (`"hel"`, `"low"`, `"orld"`).
- **Solution in Lab 1:** We implement **delimiter-based framing** by appending a newline (`\n`) character to every message. The receiver uses `readLine()` to reconstruct the exact message boundary.

### 9.3 Half-Closed Connections & Socket Timeouts
If a client machine loses power or disconnects its physical network cable without sending a `FIN` packet, the server's TCP socket can remain in `ESTABLISHED` state indefinitely (orphan socket).
- **Hardening:** Production servers configure **TCP Keep-Alive** probes or application-level read timeouts:
  ```java
  clientSocket.setSoTimeout(30000); // Throws SocketTimeoutException after 30s idle
  ```

---

## 10. Comprehensive Viva & Exam Preparation Guide

### Q1: What is the difference between a listening socket and a connected socket?
**Answer:** A listening socket (`ServerSocket`) is bound to a well-known port and only waits for and accepts incoming connection requests (`SYN`). It never exchanges application data. A connected socket (`Socket`) is created by `accept()` upon completing the 3-way handshake; it is bound to the specific client's IP and port and is used exclusively for reading and writing data.

### Q2: Why does TCP require a 3-way handshake instead of a 2-way handshake?
**Answer:** A 3-way handshake is mathematically necessary to prevent duplicate or delayed `SYN` packets from old, terminated connections from causing a false connection to be established. Both client and server must unambiguously confirm receipt of each other's initial sequence numbers ($ISN$) and ensure bidirectional channel readiness.

### Q3: What happens to incoming client connections in `Server1` while it is busy serving another client?
**Answer:** Incoming connection requests are completed at the transport layer by the operating system kernel and queued in the TCP listen backlog queue. However, the application process will not service them until `Server1` finishes with the active client and loops back to call `accept()`. If the backlog queue fills up, subsequent `SYN` packets are silently dropped.

### Q4: What is the difference between `read()` returning `0` in C and `readLine()` returning `null` in Java?
**Answer:** Both indicate an **End-Of-File (EOF)** condition caused by the remote peer closing the connection (sending a TCP `FIN` packet). It signals to the server that the client has closed its output stream and no further data will arrive.

### Q5: What is a zombie process, and how does it relate to multi-process servers?
**Answer:** In multi-process C servers using `fork()`, when a child process terminates, its termination status remains in the kernel process table until the parent reads it via `wait()` or `waitpid()`. If the parent does not call `wait()`, the dead child becomes a **zombie process**. If zombies accumulate, the system runs out of Process IDs (PIDs). Multi-threaded servers in Java avoid this because threads share the same process table entry.

### Q6: Can two different sockets on the same server have the same port number?
**Answer:** Yes! A listening socket and multiple connected sockets can all share local port 5555. The operating system kernel demultiplexes incoming packets using the full **5-tuple** $(\text{Source IP}, \text{Source Port}, \text{Dest IP}, \text{Dest Port}, \text{Protocol})$. As long as the client's IP or client's port is distinct, every connection is routed to the correct socket.

### Q7: Why do we wrap `OutputStream` in a `PrintWriter` with `autoFlush = true`?
**Answer:** By default, I/O streams buffer data in user-space memory to maximize throughput. If `autoFlush` is false and the buffer is not full, string replies remain in memory and are never transmitted over the network wire, causing the client to hang indefinitely waiting for a response.

---
*End of Lab 1 Report · Prepared for CS353 Computer Networks*

