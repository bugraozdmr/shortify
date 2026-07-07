package com.shortify.utils;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Properties;

public class ConfigManager {
    private static final String CONFIG_DIR = System.getProperty("user.home") + "/.shortify";
    private static final String CONFIG_FILE = CONFIG_DIR + "/config.properties";

    private static final String KEY_API_URL = "api.url";
    private static final String DEFAULT_API_URL = "http://127.0.0.1:8000";

    private Properties properties;

    // Singleton instance
    private static ConfigManager instance;

    private ConfigManager() {
        properties = new Properties();
        loadConfig();
    }

    public static ConfigManager getInstance() {
        if (instance == null) {
            instance = new ConfigManager();
        }
        return instance;
    }

    private void loadConfig() {
        File dir = new File(CONFIG_DIR);
        if (!dir.exists()) {
            dir.mkdirs();
        }

        File file = new File(CONFIG_FILE);
        if (!file.exists()) {
            // Create default config
            setApiUrl(DEFAULT_API_URL);
        } else {
            try (FileInputStream in = new FileInputStream(file)) {
                properties.load(in);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private void saveConfig() {
        File file = new File(CONFIG_FILE);
        try (FileOutputStream out = new FileOutputStream(file)) {
            properties.store(out, "Shortify Application Settings");
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public String getApiUrl() {
        return properties.getProperty(KEY_API_URL, DEFAULT_API_URL);
    }

    public void setApiUrl(String url) {
        properties.setProperty(KEY_API_URL, url);
        saveConfig();
    }
}
