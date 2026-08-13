package Practice_1;
import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.DataInputStream;
import java.io.InputStreamReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.net.UnknownHostException;

public class Client {
    
    private Socket s = null; // Socket
    private BufferedReader in = null; // input reader
    private DataOutputStream out = null; // output stream
    private DataInputStream serverIn = null;

    public Client(String addr, int port) {

        // Establish a connection
        try {
            s = new Socket(addr, port);
            System.out.println("Connected");

            // i/p from terminal
            in = new BufferedReader(new InputStreamReader(System.in));

            // sends o/p to the socket
            out = new DataOutputStream(s.getOutputStream());

            serverIn = new DataInputStream(new BufferedInputStream(s.getInputStream()));

        } catch (UnknownHostException k) {
            System.out.println(k);
            return;
        } catch (IOException e) {
            System.out.println(e);
            return;
        }

        String message = "";

        // keep reading ; stop when typed "stop"
        while (!message.equals("stop")) {
            try {
                message = in.readLine();
                out.writeUTF(message);
                String response = serverIn.readUTF();
                System.out.println("Server : " + response);
            } catch (IOException i) {
                System.out.println(i);
            }
        }

        // Close the connection
        try {
            in.close();
            out.close();
            s.close();
        } catch (IOException i) {
            System.out.println(i);
        }
    }

    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java Client <serverIP> <port>");
            return;
        }

        String addr = args[0];
        int port = Integer.parseInt(args[1]);

        new Client(addr, port);
    }
}
