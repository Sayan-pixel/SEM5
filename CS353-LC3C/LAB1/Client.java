import java.io.*;
import java.net.*;

public class Client {
    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java Client <Server_IP> <Port>");
            return;
        }

        String serverIp = args[0];
        int port;

        try {
            port = Integer.parseInt(args[1]);
        } catch (NumberFormatException e) {
            System.out.println("Invalid port number.");
            return;
        }

        try (Socket socket = new Socket(serverIp, port);
             BufferedReader consoleReader = new BufferedReader(new InputStreamReader(System.in));
             BufferedReader socketReader = new BufferedReader(new InputStreamReader(socket.getInputStream()));
             PrintWriter socketWriter = new PrintWriter(socket.getOutputStream(), true)) {

            System.out.println("Connected to server");

            while (true) {
                System.out.print("Please enter the message to the server:\n");
                String message = consoleReader.readLine();
                if (message == null) {
                    break;
                }
                
                socketWriter.println(message);
                
                String reply = socketReader.readLine();
                if (reply == null) {
                    System.out.println("Server disconnected.");
                    break;
                }
                System.out.println("Server reply: " + reply);
            }

        } catch (IOException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
}
