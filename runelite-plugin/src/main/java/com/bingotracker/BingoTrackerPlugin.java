package com.bingotracker;

import com.google.inject.Provides;
import lombok.extern.slf4j.Slf4j;
import net.runelite.api.*;
import net.runelite.api.events.*;
import net.runelite.client.config.ConfigManager;
import net.runelite.client.eventbus.Subscribe;
import net.runelite.client.plugins.Plugin;
import net.runelite.client.plugins.PluginDescriptor;
import net.runelite.client.ui.DrawManager;
import net.runelite.client.util.ImageCapture;
import okhttp3.*;

import javax.inject.Inject;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

@Slf4j
@PluginDescriptor(
    name = "BINGO Tracker",
    description = "Track bingo tiles and send drop notifications",
    tags = {"bingo", "discord", "tracking", "drops"}
)
public class BingoTrackerPlugin extends Plugin
{
    private static final MediaType JSON = MediaType.get("application/json; charset=utf-8");

    @Inject
    private Client client;

    @Inject
    private BingoTrackerConfig config;

    @Inject
    private DrawManager drawManager;

    @Inject
    private ImageCapture imageCapture;

    @Inject
    private OkHttpClient httpClient;

    private Set<String> whitelistedItems;
    private Set<String> blacklistedItems;

    @Provides
    BingoTrackerConfig provideConfig(ConfigManager configManager)
    {
        return configManager.getConfig(BingoTrackerConfig.class);
    }

    @Override
    protected void startUp() throws Exception
    {
        log.info("BINGO Tracker started!");
        updateItemLists();
    }

    @Override
    protected void shutDown() throws Exception
    {
        log.info("BINGO Tracker stopped!");
    }

    private void updateItemLists()
    {
        whitelistedItems = new HashSet<>(Arrays.asList(
            config.whitelistedItems().toLowerCase().split("\\r?\\n")
        ));
        blacklistedItems = new HashSet<>(Arrays.asList(
            config.blacklistedItems().toLowerCase().split("\\r?\\n")
        ));
    }

    @Subscribe
    public void onItemContainerChanged(ItemContainerChanged event)
    {
        // Check for loot in inventory
        if (event.getContainerId() == InventoryID.INVENTORY.getId())
        {
            // This is a simplified check - in production, you'd want to track changes
            // and identify newly acquired items
        }
    }

    @Subscribe
    public void onChatMessage(ChatMessage event)
    {
        // Listen for drop messages, collection log, etc.
        if (event.getType() != ChatMessageType.GAMEMESSAGE && 
            event.getType() != ChatMessageType.SPAM)
        {
            return;
        }

        String message = event.getMessage();
        
        // Check for valuable drop messages
        if (message.contains("Valuable drop:") || 
            message.contains("Untradeable drop:") ||
            message.contains("You have a funny feeling"))
        {
            handleDropMessage(message);
        }
    }

    @Subscribe
    public void onWidgetLoaded(WidgetLoaded event)
    {
        // Check for collection log interface, loot chest, etc.
        // This can be used to detect specific drops or completions
    }

    private void handleDropMessage(String message)
    {
        // Parse the drop message
        // This is simplified - you'd want more robust parsing
        String itemName = extractItemName(message);
        
        if (itemName == null || itemName.isEmpty())
        {
            return;
        }

        // Check if we should notify about this drop
        if (shouldNotify(itemName))
        {
            sendDropNotification(itemName, 1, message);
        }
    }

    private String extractItemName(String message)
    {
        // Extract item name from message
        // This is a placeholder - implement proper parsing
        if (message.contains("Valuable drop:"))
        {
            String[] parts = message.split("Valuable drop: ");
            if (parts.length > 1)
            {
                String item = parts[1].split(" \\(")[0];
                return item;
            }
        }
        return null;
    }

    private boolean shouldNotify(String itemName)
    {
        String itemLower = itemName.toLowerCase();
        
        // Check blacklist
        if (blacklistedItems.contains(itemLower))
        {
            return false;
        }
        
        // Check whitelist
        if (whitelistedItems.contains(itemLower))
        {
            return true;
        }
        
        // Check for unique items (simplified)
        if (config.alwaysSendUniques() && isUniqueItem(itemName))
        {
            return true;
        }
        
        // Additional value/rarity checks would go here
        return false;
    }

    private boolean isUniqueItem(String itemName)
    {
        // Check if item is a unique drop
        // This is simplified - you'd want a comprehensive list
        String lower = itemName.toLowerCase();
        return lower.contains("sigil") || 
               lower.contains("ancestral") ||
               lower.contains("twisted") ||
               lower.contains("elder");
    }

    private void sendDropNotification(String itemName, int quantity, String message)
    {
        Player player = client.getLocalPlayer();
        if (player == null)
        {
            return;
        }

        String playerName = player.getName();
        
        // Take screenshot if enabled
        if (config.sendScreenshots())
        {
            drawManager.requestNextFrameListener(image -> {
                CompletableFuture.runAsync(() -> {
                    try
                    {
                        sendDropWithScreenshot(playerName, itemName, quantity, image);
                    }
                    catch (Exception e)
                    {
                        log.error("Error sending drop notification", e);
                    }
                });
            });
        }
        else
        {
            sendDropWithoutScreenshot(playerName, itemName, quantity);
        }
    }

    private void sendDropWithScreenshot(String playerName, String itemName, int quantity, BufferedImage screenshot)
    {
        // In a real implementation, you'd upload the screenshot to an image host
        // and include the URL in the notification
        sendDropWithoutScreenshot(playerName, itemName, quantity);
    }

    private void sendDropWithoutScreenshot(String playerName, String itemName, int quantity)
    {
        // Send to backend server
        if (config.sendToServer() && !config.serverUrl().isEmpty())
        {
            sendToServer(playerName, itemName, quantity);
        }

        // Send to Discord webhooks
        String[] webhooks = config.webhookUrls().split("\\r?\\n");
        for (String webhook : webhooks)
        {
            if (!webhook.trim().isEmpty())
            {
                sendToDiscord(webhook.trim(), playerName, itemName, quantity);
            }
        }
    }

    private void sendToServer(String playerName, String itemName, int quantity)
    {
        try
        {
            String json = String.format(
                "{\"playerName\":\"%s\",\"itemName\":\"%s\",\"quantity\":%d,\"teamName\":\"%s\"}",
                playerName, itemName, quantity, config.teamName()
            );

            RequestBody body = RequestBody.create(json, JSON);
            Request request = new Request.Builder()
                .url(config.serverUrl() + "/api/drops")
                .post(body)
                .build();

            httpClient.newCall(request).enqueue(new Callback()
            {
                @Override
                public void onFailure(Call call, IOException e)
                {
                    log.error("Failed to send drop to server", e);
                }

                @Override
                public void onResponse(Call call, Response response)
                {
                    log.info("Drop sent to server: {}", itemName);
                    response.close();
                }
            });
        }
        catch (Exception e)
        {
            log.error("Error sending to server", e);
        }
    }

    private void sendToDiscord(String webhookUrl, String playerName, String itemName, int quantity)
    {
        try
        {
            String content;
            if (config.sendEmbeds())
            {
                content = String.format(
                    "{\"embeds\":[{\"title\":\"🎉 %s Drop!\",\"color\":65280,\"fields\":[" +
                    "{\"name\":\"Player\",\"value\":\"%s\",\"inline\":true}," +
                    "{\"name\":\"Item\",\"value\":\"%s x%d\",\"inline\":true}," +
                    "{\"name\":\"Team\",\"value\":\"%s\",\"inline\":true}" +
                    "]}]}",
                    itemName, playerName, itemName, quantity, config.teamName()
                );
            }
            else
            {
                content = String.format(
                    "{\"content\":\"🎉 **%s** received **%s x%d** [Team: %s]\"}",
                    playerName, itemName, quantity, config.teamName()
                );
            }

            RequestBody body = RequestBody.create(content, JSON);
            Request request = new Request.Builder()
                .url(webhookUrl)
                .post(body)
                .build();

            httpClient.newCall(request).enqueue(new Callback()
            {
                @Override
                public void onFailure(Call call, IOException e)
                {
                    log.error("Failed to send to Discord", e);
                }

                @Override
                public void onResponse(Call call, Response response)
                {
                    log.info("Drop sent to Discord: {}", itemName);
                    response.close();
                }
            });
        }
        catch (Exception e)
        {
            log.error("Error sending to Discord", e);
        }
    }
}
