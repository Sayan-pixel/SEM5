# Lab 1: Socket Programming (Java)

This directory contains the Java implementation for Lab 1: UNIX socket programming client-server chat. 
It replaces the traditional C/C++ process forking (`fork()`) approach with Java Threads for the concurrent server.

## Files
- `Client.java`: The client program that connects to a server, prompts the user for string input, and prints the server's reply.
- `Server1.java`: The single-process (iterative) server that handles only one client at a time and returns reversed strings.
- `Server2.java`: The multi-process (concurrent) server that spawns a new thread for each new client request, allowing multiple clients to chat with the server simultaneously.

## How to Compile
Open a terminal in this directory and run:
```bash
javac Client.java
javac Server1.java
javac Server2.java
```

## How to Run

### Example with Server1 (Iterative)
1. **Start the server:**
   ```bash
   java Server1 5555
   ```
2. **Start the client (in another terminal):**
   ```bash
   java Client 127.0.0.1 5555
   ```
3. Type a message in the client terminal and press Enter. You should receive the reversed string.

### Example with Server2 (Concurrent)
1. **Start the server:**
   ```bash
   java Server2 5555
   ```
2. **Start multiple clients (in different terminals):**
   ```bash
   java Client 127.0.0.1 5555
   ```
3. Both clients can now chat with the server at the same time without waiting for each other.
