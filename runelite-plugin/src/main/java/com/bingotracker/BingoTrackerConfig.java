package com.bingotracker;

import lombok.Getter;
import net.runelite.client.config.Config;
import net.runelite.client.config.ConfigGroup;
import net.runelite.client.config.ConfigItem;
import net.runelite.client.config.ConfigSection;

@ConfigGroup("bingotracker")
public interface BingoTrackerConfig extends Config
{
    @ConfigSection(
        name = "Server Settings",
        description = "Backend server configuration",
        position = 0
    )
    String serverSection = "server";

    @ConfigSection(
        name = "Discord Webhooks",
        description = "Discord webhook URLs",
        position = 1
    )
    String discordSection = "discord";

    @ConfigSection(
        name = "Bingo Settings",
        description = "Bingo board settings",
        position = 2
    )
    String bingoSection = "bingo";

    @ConfigSection(
        name = "Drop Filters",
        description = "Item drop filter settings",
        position = 3
    )
    String filterSection = "filters";

    // Server Settings
    @ConfigItem(
        keyName = "serverUrl",
        name = "Server URL",
        description = "URL of the BINGO Tracker backend server",
        section = serverSection,
        position = 0
    )
    default String serverUrl()
    {
        return "http://localhost:5000";
    }

    @ConfigItem(
        keyName = "boardName",
        name = "Board Name",
        description = "Name of the bingo board you're participating in",
        section = serverSection,
        position = 1
    )
    default String boardName()
    {
        return "";
    }

    @ConfigItem(
        keyName = "teamName",
        name = "Team Name",
        description = "Name of your team",
        section = serverSection,
        position = 2
    )
    default String teamName()
    {
        return "";
    }

    @ConfigItem(
        keyName = "boardPassword",
        name = "Board Password",
        description = "Password for the bingo board",
        section = serverSection,
        position = 3
    )
    default String boardPassword()
    {
        return "";
    }

    // Discord Webhooks
    @ConfigItem(
        keyName = "webhookUrls",
        name = "Webhook URL(s)",
        description = "Discord webhook URLs (one per line)",
        section = discordSection,
        position = 0
    )
    default String webhookUrls()
    {
        return "";
    }

    @ConfigItem(
        keyName = "sendEmbeds",
        name = "Send Embeds",
        description = "Send rich embed messages instead of plain text",
        section = discordSection,
        position = 1
    )
    default boolean sendEmbeds()
    {
        return true;
    }

    @ConfigItem(
        keyName = "sendScreenshots",
        name = "Send Screenshots",
        description = "Automatically send screenshots with drop notifications",
        section = discordSection,
        position = 2
    )
    default boolean sendScreenshots()
    {
        return true;
    }

    @ConfigItem(
        keyName = "sendToServer",
        name = "Send to Server",
        description = "Send drop data to the backend server",
        section = discordSection,
        position = 3
    )
    default boolean sendToServer()
    {
        return true;
    }

    // Bingo Settings
    @ConfigItem(
        keyName = "autoCheckTiles",
        name = "Auto-Check Tiles",
        description = "Automatically check tiles when conditions are met",
        section = bingoSection,
        position = 0
    )
    default boolean autoCheckTiles()
    {
        return true;
    }

    @ConfigItem(
        keyName = "notifyTileCompletion",
        name = "Notify on Completion",
        description = "Send notification when you complete a tile",
        section = bingoSection,
        position = 1
    )
    default boolean notifyTileCompletion()
    {
        return true;
    }

    // Drop Filters
    @ConfigItem(
        keyName = "minRarity",
        name = "Min Rarity (1/x)",
        description = "Minimum drop rarity to notify (e.g., 64 for 1/64)",
        section = filterSection,
        position = 0
    )
    default int minRarity()
    {
        return 64;
    }

    @ConfigItem(
        keyName = "minValue",
        name = "Min Value (GP)",
        description = "Minimum item value to notify",
        section = filterSection,
        position = 1
    )
    default int minValue()
    {
        return 10000;
    }

    @ConfigItem(
        keyName = "whitelistedItems",
        name = "Whitelisted Items",
        description = "Items to always notify (one per line)",
        section = filterSection,
        position = 2
    )
    default String whitelistedItems()
    {
        return "";
    }

    @ConfigItem(
        keyName = "blacklistedItems",
        name = "Blacklisted Items",
        description = "Items to never notify (one per line)",
        section = filterSection,
        position = 3
    )
    default String blacklistedItems()
    {
        return "";
    }

    @ConfigItem(
        keyName = "alwaysSendUniques",
        name = "Always Send Uniques",
        description = "Always send notifications for unique drops",
        section = filterSection,
        position = 4
    )
    default boolean alwaysSendUniques()
    {
        return true;
    }
}
