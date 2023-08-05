import platform
if platform.machine() == "armv7l":
    import r2_ds18b20 as bus
elif platform.machine() == "armv6l":
    import r1_ds18b20 as bus
else:
    print("Could not import ds18b20, your CPU is not armv7l or armv6l")
