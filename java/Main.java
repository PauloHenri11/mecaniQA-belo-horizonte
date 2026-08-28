import com.sun.net.httpserver.HttpServer;

import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.nio.charset.StandardCharsets;

public class Main {

    public static void main(String[] args) throws Exception {

        HttpServer server = HttpServer.create(
                new InetSocketAddress(8080),
                0
        );

        server.createContext("/", exchange -> {

            String mensagem = "MecaniQA Java API funcionando";

            byte[] resposta =
                    mensagem.getBytes(StandardCharsets.UTF_8);

            exchange.sendResponseHeaders(
                    200,
                    resposta.length
            );

            try (OutputStream os = exchange.getResponseBody()) {
                os.write(resposta);
            }
        });

        server.start();

        System.out.println(
                "MecaniQA API rodando na porta 8080"
        );
    }
}