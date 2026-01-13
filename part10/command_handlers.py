class ConfigCommandHandler:
    def __init__(self, command: str, attr_name: str, allowed_values: list, display_values=None):
        """
        command: the text the user types, e.g. ":highlight"
        attr_name: the attribute in config to update, e.g. "highlight"
        allowed_values: list of allowed string values, e.g. ["on", "off"]
        display_values: optional mapping of stored value -> display value
        """
        self.command = command
        self.attr_name = attr_name
        self.allowed_values = [v.upper() for v in allowed_values]  # case-insensitive comparison
        self.display_values = display_values or {}

    def handle(self, raw_input: str, config) -> bool:
        """
        Returns True if the command was handled, False otherwise.
        """
        if not raw_input.startswith(self.command):
            return False

        parts = raw_input.split()
        if len(parts) != 2:
            print(f"Usage: {self.command} {'|'.join(self.allowed_values)}")
            return True

        value = parts[1].upper()
        if value not in self.allowed_values:
            print(f"Usage: {self.command} {'|'.join(self.allowed_values)}")
            return True

        # Convert to boolean if needed
        if isinstance(getattr(config, self.attr_name), bool):
            setattr(config, self.attr_name, value == "ON")
        else:
            setattr(config, self.attr_name, value)

        display_value = self.display_values.get(value, value)
        print(f"{self.attr_name.replace('_', ' ').capitalize()} set to {display_value}")
        return True


highlight_handler = ConfigCommandHandler(
    command=":highlight",
    attr_name="highlight",
    allowed_values=["on", "off"],
    display_values={"ON": "ON", "OFF": "OFF"}
)

search_mode_handler = ConfigCommandHandler(
    command=":search-mode",
    attr_name="search_mode",
    allowed_values=["AND", "OR"]
)

hl_mode_handler = ConfigCommandHandler(
    command=":hl-mode",
    attr_name="highlight_mode",
    allowed_values=["DEFAULT", "GREEN"]
)