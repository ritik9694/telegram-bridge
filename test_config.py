try:
    import config

    print("Configuration loaded successfully!")
    print("Xenovra URL:", config.XENOVRA_URL)
    print("Session:", config.SESSION_NAME)
    print("Download directory:", config.DOWNLOAD_DIR)
    print("Max concurrent downloads:", config.MAX_CONCURRENT_DOWNLOADS)

except Exception as error:
    print("Configuration error:", error)

