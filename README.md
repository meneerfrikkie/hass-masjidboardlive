![Integration Logo](https://github.com/meneerfrikkie/hass-masjidboardlive/blob/main/images/logo.png) 

# Masjid Board Live Home Assistant Custom Integration

## Overview

The **Masjid Board Live** custom integration allows you to display prayer times from your local masjid's online board directly in Home Assistant. It automatically retrieves prayer times, adhan (call to prayer), and jamaah (congregation) times, and refreshes them at a customizable interval.

This integration is ideal for users who want to keep track of prayer times in their Home Assistant dashboards.

---

## Features

- Displays prayer times including Adhan and Jamaah for Fajr, Zuhr, Asr, Maghrib, and Isha prayers.
- Customizable polling interval for prayer times.
- Automatically fetches and displays the masjid name from the board URL.

---

## Requirements

- **Home Assistant Core** 2024.11.0 or later

---

## Installation

### Manual Installation

1. Download or clone this repository.
2. Copy the `masjidboardlive` folder into your Home Assistant `custom_components` directory. The final path should be:
   <config_directory>/custom_components/masjidboardlive
where `<config_directory>` is your Home Assistant configuration directory.
3. Restart Home Assistant.

### Installation via HACS (Home Assistant Community Store)

Coming Soon!

---

## Configuration

After installation, you can configure the integration through the Home Assistant UI.

### Step 1: Adding the Integration

1. Go to **Settings > Devices & Services > Integrations**.
2. Click **+ Add Integration** and search for "Masjid Board Live".
3. Select the integration.

### Step 2: Entering Configuration Details

In the configuration form, provide the following:

- **Masjid Board URL**: Enter the URL of your masjid's online board (e.g., `https://masjidboardlive.com/boards/?robertsham-darul-uloom`).
- **Poll Interval (Optional)**: Set the interval (in seconds) for refreshing prayer times. The default is 600 seconds (10 minutes).

> **Note**: The integration will attempt to fetch the masjid's name automatically from the provided URL.

### Step 3: Completing Setup

Once configured, the integration will automatically fetch and display the prayer times from the specified masjid board URL. You’ll see a new device for your masjid with separate sensors for each prayer’s Adhan and Jamaah times.

---

## Usage

Once set up, the integration will create sensors for each prayer time. These sensors can be used in dashboards, automations, and notifications.

### Example Sensors Created:

- `<Masjid Name> Fajr Adhan Time`
- `<Masjid Name> Fajr Jamaah Time`
- `<Masjid Name> Zuhr Adhan Time`
- `<Masjid Name> Zuhr Jamaah Time`
- ...and so on for Asr, Maghrib, and Isha

---

## Troubleshooting

### Common Issues

- **Invalid URL**: If the URL provided is incorrect or the masjid name element is missing, you will see an error in the configuration step. Double-check the URL and ensure the page includes an element with the ID `masjidName2`.
- **Timeouts or Errors Fetching Data**: Network issues or an unreachable URL may cause fetch errors. Check your internet connection and confirm the masjid board is accessible online.

### Logs

To view integration logs for troubleshooting, go to **Settings > System > Logs** and look for entries related to `masjidboardlive`.

---

## Updating the Integration

To update the integration:

1. Download the latest version of the integration and replace the files in the `custom_components/masjidboardlive` folder.
2. Restart Home Assistant.

---

## Support

For issues or feature requests, please visit the [GitHub repository issues page](https://github.com/meneerfrikkie/hass-masjidboardlive/issues).

--- 

Enjoy using the Masjid Board Live custom integration in Home Assistant and stay on top of your local masjid prayer times!
