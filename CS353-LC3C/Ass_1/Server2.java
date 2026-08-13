package Ass_1;

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

public class Server2 {

    private ServerSocket serverSocket;

    public Server2(int port) {
        try {
            serverSocket = new ServerSocket(port);
            System.out.println("Server Started...");
            System.out.println("Waiting for clients...");

            while (true) {
                Socket clientSocket = serverSocket.accept();

                System.out.println("New client connected: "
                        + clientSocket.getInetAddress());

                ClientHandler handler = new ClientHandler(clientSocket);
                handler.start();
            }

        } catch (IOException e) {
            System.out.println(e);
        }
    }

    public static void main(String[] args) {
        new Server2(5600);
    }
}

class ClientHandler extends Thread {

    private Socket socket;
    private DataInputStream in;
    private DataOutputStream out;

    public ClientHandler(Socket socket) {
        this.socket = socket;
    }

    @Override
    public void run() {

        try {
            in = new DataInputStream(
                    new BufferedInputStream(socket.getInputStream()));

            out = new DataOutputStream(socket.getOutputStream());

            while (true) {

                String message = in.readUTF();

                System.out.println(
                        "[" + socket.getInetAddress() + "] : " + message);

                // Reverse the string
                String reversed = new StringBuilder(message)
                        .reverse()
                        .toString();

                // Send reversed string back
                out.writeUTF(reversed);
                out.flush();
            }

        } catch (IOException e) {
            System.out.println("Client disconnected : "
                    + socket.getInetAddress());
        } finally {

            try {
                if (in != null)
                    in.close();

                if (out != null)
                    out.close();

                if (socket != null)
                    socket.close();

            } catch (IOException e) {
                System.out.println(e);
            }
        }
    }
}