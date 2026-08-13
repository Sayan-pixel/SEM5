package Practice_1;

import java.io.BufferedInputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

public class Server1 {
    
    private Socket s = null; // socket init
    private ServerSocket ss = null; // sever-socket init
    private DataInputStream in = null; // i/p stream
    private DataOutputStream out = null; // o/p stream

    public Server1(int port) {

        try {
            ss = new ServerSocket(port);
            System.out.println("Server Started");

            System.out.println("Waiting for a client");

            s = ss.accept();
            System.out.println("Client Accepted");

            // Takes i/p from client socket
            in = new DataInputStream(new BufferedInputStream(s.getInputStream()));

            out = new DataOutputStream(s.getOutputStream());
            String message = "";

            // keep reading ; stop when typed "stop"
            while (!message.equals("stop")) {
                try {
                    message = in.readUTF();
                    System.out.println(message);
                    String reversed = new StringBuilder(message).reverse().toString();
                    out.writeUTF(reversed);
                } catch (IOException i) {
                    System.out.println(i);
                    break;
                }
            }

            System.out.println("Closing connection");

            // Close connection
            s.close();
            in.close();
        } catch (IOException i) {
            System.out.println(i);
        }
    }

    public static void main(String[] args) {
        
        new Server1(5600);
    }
}
