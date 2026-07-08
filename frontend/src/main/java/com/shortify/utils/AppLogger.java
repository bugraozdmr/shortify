package com.shortify.utils;

import java.io.File;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.*;

public class AppLogger {
    private static Logger logger;
    private static final String LOG_FILE = "logs/frontend.log";

    static {
        try {
            File logDir = new File("logs");
            if (!logDir.exists()) {
                logDir.mkdirs();
            }

            logger = Logger.getLogger("ShortifyFrontend");
            logger.setUseParentHandlers(false); // Console'a varsayılan çirkin formati basmasin

            // File Handler
            FileHandler fileHandler = new FileHandler(LOG_FILE, true); // true = append
            fileHandler.setFormatter(new CustomFormatter());
            logger.addHandler(fileHandler);

            // Console Handler (Terminalde de güzel görünsün)
            ConsoleHandler consoleHandler = new ConsoleHandler();
            consoleHandler.setFormatter(new CustomFormatter());
            logger.addHandler(consoleHandler);

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void info(String message) {
        logger.info(message);
    }

    public static void warning(String message) {
        logger.warning(message);
    }

    public static void error(String message, Throwable t) {
        logger.log(Level.SEVERE, message, t);
    }
    
    public static void error(String message) {
        logger.severe(message);
    }

    // İstekleri loglamak için özel metod
    public static void logRequest(String method, String url, String payload) {
        String logMsg = String.format("OUTGOING REQUEST => [%s] %s", method, url);
        if (payload != null && !payload.isEmpty()) {
            logMsg += " | PAYLOAD: " + payload;
        }
        logger.info(logMsg);
    }

    // Yanıtları loglamak için özel metod
    public static void logResponse(int statusCode, String body) {
        String logMsg = String.format("RECEIVED RESPONSE <= STATUS: %d | BODY: %s", statusCode, body);
        if (statusCode >= 200 && statusCode < 300) {
            logger.info(logMsg);
        } else {
            logger.warning(logMsg);
        }
    }

    // Custom Formatter for readable logs
    private static class CustomFormatter extends Formatter {
        private static final SimpleDateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

        @Override
        public String format(LogRecord record) {
            StringBuilder sb = new StringBuilder();
            sb.append("[")
              .append(dateFormat.format(new Date(record.getMillis())))
              .append("] [")
              .append(record.getLevel().getName())
              .append("] ")
              .append(record.getMessage())
              .append(System.lineSeparator());

            if (record.getThrown() != null) {
                sb.append("EXCEPTION: ").append(record.getThrown().toString()).append(System.lineSeparator());
                for (StackTraceElement element : record.getThrown().getStackTrace()) {
                    sb.append("\tat ").append(element.toString()).append(System.lineSeparator());
                }
            }
            return sb.toString();
        }
    }
}
