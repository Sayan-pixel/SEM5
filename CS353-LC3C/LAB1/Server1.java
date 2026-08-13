import java.io.*;
import java.net.*;

public class Server1 {
    public static void main(String[] args) {
        if (args.length != 1) {
            System.out.println("Usage: java Server1 <Port>");
            return;
        }

        int port;
        try {
            port = Integer.parseInt(args[0]);
        } catch (NumberFormatException e) {
            System.out.println("Invalid port number.");
            return;
        }

        try (ServerSocket serverSocket = new ServerSocket(port)) {
            System.out.println("Server1 listening on port " + port);

            while (true) {
                try (Socket clientSocket = serverSocket.accept()) {
                    System.out.println("Connected with client socket number " + clientSocket.getPort());

                    BufferedReader reader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()));
                    PrintWriter writer = new PrintWriter(clientSocket.getOutputStream(), true);

                    String message;
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

        } catch (IOException e) {
            System.out.println("Server exception: " + e.getMessage());
        }
    }
}
